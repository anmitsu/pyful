#/usr/bin/env python

from distutils.core import setup

import pyful

setup(name = "Pyful",
      version = pyful.__version__,
      description = "Python file management utility",
      long_description = pyful.__doc__,
      author = "anmitsu",
      author_email = "anmitsu.s@gmail.com",
      url = "http://github.com/anmitsu/pyful",
      license = "GPL",
      packages = ["pyful", "pyful.completion"],
      scripts = ["bin/pyful"],
      keywords = "filer curses linux"
      )

