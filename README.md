pyful - Python file management utility
======================================

pyful is CUI filer of the keyboard operation for Linux.
This application operates at the terminal emulator such as xterm.

For more information, see <https://github.com/anmitsu/pyful/wiki>

Features
--------

* Flexible and powerful customizing by Python;
* File view of multi screen;
* Interactive command line;
* Command line completion function like zsh;
* High-level file management.

Installation
------------

pyful is installed in **/usr/local** by executing the following
command as a super user:

     $ python setup.py install

The application can execute by the following command
if the installation is normally completed:

     $ pyful

If the installation on the system is unnecessary,
the application is started by only executing the following command:

     $ ./bin/pyful

Dependencies
------------

The operation of pyful is confirmed by Python2.6 and Python3.1 on
Ubuntu 10.04.

To display multi byte character including Japanese,
**libncursesw** library might become necessary.

In addition, pyful operates in the assumption that encoding is **utf-8**.
Therefore, normal operation cannot be expected in the environment that
uses encoding that is not **utf-8**.

Configuration
-------------

pyful configuration has edit of **~/.pyful/rc.py** .

For edit of rc.py, see <https://github.com/anmitsu/pyful/wiki/Configuration>
