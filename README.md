simplelock
==========
TODO: optionally hidden pointer

Minimal xorg screen locker except it doesn't touch the screen so it is
more correctly describes as a xorg input locker.

Simplelock has it's own password and does not use the system password.

It's based on ``pyxtrlock``.

It's mostly written using [XCB](http://xcb.freedesktop.org/)
instead of Xlib, although some Xlib/XCB interaction is still necessary.

Simlp lock doesn't need any special privileges.

Description
-----------

simplelock is a even simpler than it's predecessor, it's a very minimal
X display lock program. While simplelock is running, it doesn't obscure
the screen, only the mouse and keyboard are grabbed and the mouse cursor
is optionally hidden. Output displayed by X programs, and windows put
up by new X clients, continue to be visible, and any new output is
displayed normally.

In good Unix tradition, simplelock provides no visual feedback during password
entry. You simply type your password at it, followed by Enter or Newline.
Pressing Backspace or Delete erases one character of a password partially typed;
pressing Escape or Clear clears anything that has been entered.

Like simplelock will ignore further keystrokes until a timeout has
expired after too many attempts have been made in too short time.

Installation and Usage
----------------------

Clone and install simplelock:

    $ git clone git://github.com/christer/simplelock.git
    $ cd simplelock
    $ sudo python3 setup.py install

Once this is done, you should be able to simply lock your display by running

    $ simplelock

If you would like to automatically lock your screen after some idle time,
we recommend the ``xautolock`` tool. Just add something like

    xautolock -locker simplelock -time 5

to your X autostart file to lock the screen with ``pyxtrlock`` after 5
minutes idle time. ``xautolock`` has many other useful features, see
its documentation. Most distributions provide an ``xautolock`` package
with a man page. An alternative to ``xautolock`` is the use of
[autolockd](https://github.com/zombofant/autolockd) which also
monitors for lid close and suspend events.

Bugs & Limitations
------------------
Additional input devices other than the keyboard and mouse are not disabled.

Although this is not a bug, please note that simplelock does not
prevent a user from switching to a virtual terminal, so be advised to
always log out from your terminals.

The lenght of the password is limited to 100 KiB to prevent memory
exhaustion attacks. This limit can only be adapted in the source code.

Please report any new bugs you may find to our
[Github issue tracker](https://github.com/christer/simplelock/issues).

Configuration
-------------

Password is set with ``simplelock --passwd``

Requirements
------------
* Python ≥ 3.0
* libxcb
* libxcb-image
* libX11 ≥ 1.4, or libX11 ≥ 1.2 compiled with XCB backend


Authors
-------
* Christer Sjöholm <hcs at furuvik dot net>

Authors of pyxtrlock:

* Leon Weber <leon@leonweber.de>
* Sebastian Riese <s.riese@zombofant.net>

License
-------
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
