# emacs this is -*-python-*-

from . import X
from . import xcb
from ctypes import POINTER, c_int, c_uint32, c_char
from ctypes import byref, cast
from passlib.apps import custom_app_context as pwd_context
import argparse
import getpass
import os
import sys
import time

# pwd length limit to prevent memory exhaustion (and therefore
# possible failure due to OOM killing)
PWD_LENGTH_LIMIT = 100 * 1024

# timeout algorithm constants
TIMEOUTPERATTEMPT = 30000
MAXGOODWILL = TIMEOUTPERATTEMPT * 5
INITIALGOODWILL = MAXGOODWILL
GOODWILLPORTION = 0.3


# Invisible mouse pointer
EMPTY_CURSOR = {
    "width": 1,
    "height": 1,
    "x_hot": 1,
    "y_hot": 1,
    "fg_bitmap": bytes([0x00]),
    "bg_bitmap": bytes([0x00]),
    "color_mode": "named",
    "bg_color": "steelblue3",
    "fg_color": "grey25"
}

UNCHANGED_CURSOR = None

XDG_CONFIG_HOME = os.environ.get('XDG_CONFIG_HOME') or \
                    os.path.expanduser('~/.config')
PASSWD_FILE = os.path.join(XDG_CONFIG_HOME, 'simplelock/passwd')

def panic(message, exit_code=1):
    """Print an error message to stderr and exit"""
    print(message, file=sys.stderr)
    sys.exit(exit_code)


def authenticate(passwd: bytes):
    with open(PASSWD_FILE) as inp:
        hash = inp.read()
    ok = pwd_context.verify(passwd.decode('UTF8'), hash)
    return ok


def event_loop(display, conn, ic):

    # main event loop
    pwd = []
    timeout = 0
    goodwill = INITIALGOODWILL

    while True:
        with xcb.wait_for_event(conn) as event:
            if event.contents.response_type == xcb.KEY_PRESS:
                xcb_key_press_event = cast(event,
                                           POINTER(xcb.KeyPressEvent)).contents
                time_stamp = xcb_key_press_event.time
                if time_stamp < timeout:
                    continue

                x_key_press_event = X.KeyEvent.from_xcb_event(display,
                                                              xcb_key_press_event)

                status = X.Status()
                keysym = X.Keysym()
                size = 0
                buf = bytearray(size)

                length = X.utf8_lookup_string(ic, byref(x_key_press_event), None,
                                              size, byref(keysym), byref(status))
                if status.value == X.BUFFER_OVERFLOW:
                    buf = bytearray(length)
                    buf_p = cast((c_char * length).from_buffer(buf),
                                 POINTER(c_char))
                    length = X.utf8_lookup_string(ic, byref(x_key_press_event),
                                                  buf_p, length, byref(keysym),
                                                  byref(status))

                status = status.value
                keysym = keysym.value
                if status == X.LOOKUP_BOTH or status == X.LOOKUP_KEYSYM:
                    if keysym == X.K_Escape or keysym == X.K_Clear:
                        pwd = []
                        continue
                    elif keysym == X.K_Delete or keysym == X.K_BackSpace:
                        if pwd:
                            pwd.pop()
                        continue
                    elif keysym == X.K_LineFeed or keysym == X.K_Return:
                        if authenticate(b''.join(pwd)):
                            break
                        else:
                            pwd = []
                            if timeout:
                                goodwill += time_stamp - timeout
                                if goodwill > MAXGOODWILL:
                                    goodwill = MAXGOODWILL
                            timeout = -int(goodwill * GOODWILLPORTION)
                            goodwill += timeout
                            timeout += time_stamp + TIMEOUTPERATTEMPT
                            continue

                if status == X.LOOKUP_BOTH or status == X.LOOKUP_CHARS:
                    if length and sum(map(len, pwd)) < PWD_LENGTH_LIMIT:
                        pwd.append(bytes(buf[:length]))


def create_cursor(conn, window, screen, cursor):
    # create cursor
    csr_map = xcb.image_create_pixmap_from_bitmap_data(conn, window,
                                                       cursor["fg_bitmap"],
                                                       cursor["width"],
                                                       cursor["height"],
                                                       1, 0, 0, None)
    csr_mask = xcb.image_create_pixmap_from_bitmap_data(conn, window,
                                                        cursor["bg_bitmap"],
                                                        cursor["width"],
                                                        cursor["height"],
                                                        1, 0, 0, None)

    if cursor["color_mode"] == "named":
        csr_bg = xcb.alloc_named_color_sync(conn, screen.default_colormap,
                                            cursor["bg_color"])
        csr_fg = xcb.alloc_named_color_sync(conn, screen.default_colormap,
                                            cursor["fg_color"])
    elif cursor["color_mode"] == "rgb":
        r, g, b = cursor["bg_color"]
        csr_bg = xcb.alloc_color_sync(conn, screen.default_colormap,
                                      r, g, b)
        r, g, b = cursor["fg_color"]
        csr_fg = xcb.alloc_color_sync(conn, screen.default_colormap,
                                      r, g, b)
    else:
        panic("Invalid color mode")

    try:
        return xcb.create_cursor_sync(conn, csr_map, csr_mask, csr_fg, csr_bg,
                                      cursor["x_hot"], cursor["y_hot"])
    except xcb.XCBError:
        panic("pyxtrlock: Could not create cursor")

def lock_screen(hide_cursor: bool):
    display = X.create_window(None)
    conn = X.get_xcb_connection(display)

    if not display:
        panic("pyxtrlock: Could not connect to X server")

    screen_num = c_int()

    setup = xcb.get_setup(conn)

    iter_ = xcb.setup_roots_iterator(setup)

    while screen_num.value:
        xcb.screen_next(byref(iter_))
        screen_num.value -= 1

    screen = iter_.data.contents

    # create window
    window = xcb.generate_id(conn)

    attribs = (c_uint32 * 2)(1, xcb.EVENT_MASK_KEY_PRESS)
    xcb.create_window(conn, xcb.COPY_FROM_PARENT, window, screen.root,
                            0, 0, 1, 1, 0, xcb.WINDOW_CLASS_INPUT_ONLY,
                            xcb.VisualID(xcb.COPY_FROM_PARENT),
                            xcb.CW_OVERRIDE_REDIRECT | xcb.CW_EVENT_MASK,
                            cast(byref(attribs), POINTER(c_uint32)))

    if hide_cursor:
        cursor = create_cursor(conn, window, screen, EMPTY_CURSOR)
    else:
        cursor = 0  # keep mouse pointer as it is

    # map window
    xcb.map_window(conn, window)

    # Grab keyboard
    try:
        status = xcb.grab_keyboard_sync(conn, 0, window, xcb.CURRENT_TIME,
                                        xcb.GRAB_MODE_ASYNC, xcb.GRAB_MODE_ASYNC)

        if status != xcb.GrabSuccess:
            panic("pyxtrlock: Could not grab keyboard")
    except xcb.XCBError as err:
        panic("pyxtrlock: Could not grab keyboard " + str(err))

    # Grab pointer
    # Use the method from the original xtrlock code:
    #  "Sometimes the WM doesn't ungrab the keyboard quickly enough if
    #  launching xtrlock from a keystroke shortcut, meaning xtrlock fails
    #  to start We deal with this by waiting (up to 100 times) for 10,000
    #  microsecs and trying to grab each time. If we still fail
    #  (i.e. after 1s in total), then give up, and emit an error"
    for _ in range(100):
        try:
            status = xcb.grab_pointer_sync(conn, False, window, 0,
                                           xcb.GRAB_MODE_ASYNC,
                                           xcb.GRAB_MODE_ASYNC,
                                           xcb.WINDOW_NONE, cursor,
                                           xcb.CURRENT_TIME)

            if status == xcb.GrabSuccess:
                break
            else:
                time.sleep(0.01)
        except xcb.XCBError:
            time.sleep(0.01)
    else:
        panic("pyxtrlock: Could not grab pointing device")

    xcb.flush(conn)

    # Prepare X Input
    im = X.open_IM(display, None, None, None)
    if not im:
        panic("pyxtrlock: Could not open Input Method")

    ic = X.create_IC(im, X.N_INPUT_STYLE,
                     X.IM_PRE_EDIT_NOTHING | X.IM_STATUS_NOTHING, None)
    if not ic:
        panic("pyxtrlock: Could not open Input Context")

    X.set_ic_focus(ic)


    event_loop(display, conn, ic)

    X.close_window(display)

def main():

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-f', '--force', action='store_true',
                        help='Force locking even for root user')
    parser.add_argument('-p', '--passwd', action='store_true',
                        help='Set/change the password')
    parser.add_argument('--no-hide-cursor', action='store_true',
                        help="Don't hide the mouse pointer.")
    args = parser.parse_args()

    if args.passwd:
        pass1 = getpass.getpass('new password: ')
        pass2 = getpass.getpass('confirm new password: ')
        if pass1 != pass2:
            panic('Passwords didn\'t match')
        else:
            hash = pwd_context.encrypt(pass1)
            if not os.path.exists(os.path.dirname(PASSWD_FILE)):
                os.makedirs(os.path.dirname(PASSWD_FILE))
            with open(PASSWD_FILE, 'w', encoding='ASCII') as out:
                out.write(hash)
            exit(0)
    else:
        if getpass.getuser() == 'root' and not args.force:
            panic("pyxtrlock: refusing to run as root. Use -f to force.")
        if not os.path.exists(PASSWD_FILE):
            panic("pyxtrlock: refusing to run, no password has been set.")
        lock_screen(not args.no_hide_cursor)
