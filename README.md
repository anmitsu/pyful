pyful - Python File Management Utility
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

pyful is installed by executing the following command:

    $ git clone git://github.com/anmitsu/pyful
    $ cd pyful
    $ sudo python setup.py install -f
    $ pyful

Configuration
-------------

pyful configuration has edit of `~/.pyful/rc.py`.

Configuration file is created to `~/.pyful/rc.py` by following command with `--create-config` option.

    $ pyful --create-config

For edit of rc.py, see <https://github.com/anmitsu/pyful/wiki>

Dependencies
------------

The operation of pyful is confirmed by Python2.7 and Python3.2 on
Ubuntu 11.10.

To display multi byte character including Japanese,
**libncursesw** library might become necessary.

In addition, pyful operates in the assumption that encoding is **utf-8**.
Therefore, normal operation cannot be expected in the environment that
uses encoding that is not **utf-8**.
