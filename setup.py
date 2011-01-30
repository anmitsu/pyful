#/usr/bin/env python

import os
import sys
from distutils.core import setup

from pyfulib.version import __version__

setup(name = "pyful",
      version = __version__,
      description = "Python file management utility",
      author = "anmitsu",
      author_email = "anmitsu.s@gmail.com",
      packages = ["pyful", "pyful/completion"],
      scripts = ["bin/pyful"],
      )
