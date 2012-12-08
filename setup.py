#/usr/bin/env python

from distutils.core import setup

import pyful

setup(name = "pyful",
      version = pyful.__version__,
      description = "Python file management utility",
      long_description = pyful.__doc__,
      author = "anmitsu",
      author_email = "anmitsu.s@gmail.com",
      url = "https://github.com/anmitsu/pyful",
      download_url = "https://github.com/anmitsu/pyful/archive/master.zip",
      license = "GPL",
      packages = ["pyful", "pyful.completion", "pyful.widget"],
      scripts = ["bin/pyful"],
      keywords = "filer curses linux",
      classifiers = ["Environment :: Console :: Curses",
                     "License :: OSI Approved :: GNU General Public License (GPL)",
                     "Operating System :: POSIX :: Linux",
                     "Programming Language :: Python",
                     "Topic :: Desktop Environment :: File Managers",
                     "Topic :: System :: Shells",
                     "Topic :: Utilities"],
      )

