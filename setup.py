#/usr/bin/env python

from distutils.core import setup

from pyful import __version__

setup(name = "Pyful",
      version = __version__,
      description = "Python file management utility",
      long_description = "Python file management utility. This application is CUI filer of the keyboard operation for Linux.",
      author = "anmitsu",
      author_email = "anmitsu.s@gmail.com",
      url = "http://github.com/anmitsu/pyful",
      license = "GPL",
      packages = ["pyful", "pyful.completion"],
      scripts = ["bin/pyful"],
      )

