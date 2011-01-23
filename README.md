Pyful - python file management utility
======================================

Pyful is the filer on console of the keyboard operation main with the
interface of curses for Linux. This application operates at the terminal
emulator such as xterm.

Features
--------

* Flexible and powerful custamizing by Python;
* File view of multi screen;
* Interactive command line;
* Command line completion function like zsh;
* High-level file management.

Installation
------------

Pyful is installed in **/usr/local** by executing the following
command as a super user:

     $ python setup.py install

The application can execute by the following command
if the installation is normally completed:

     $ pyful

If the installation on the system is unnecessary,
the application is started by only executing the following command:

     $ python ./bin/pyful

Dependencies
------------

The operation of Pyful is confirmed by Python2.6 and Python3.1 on
Ubuntu 10.04.

To display multi byte character including Japanese,
**libncursesw** library might become necessary.

In addition, Pyful operates in the assumption that encoding is **utf-8**.
Therefore, normal operation cannot be expected in the environment that
uses encoding that is not **utf-8**.

Configuration
-------------

Pyful configuration has edit of **~/.pyful/rc.py**.
Please copy rc.py because it doesn't exist in default
and configure this file.

