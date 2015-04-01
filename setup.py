# coding=utf-8
"""
Active8 (04-03-15)
license: GNU-GPL2
"""
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

from setuptools import setup
setup(name='sortpythonmethods',
      version='5',
      description='Sort methods, imports and classes in a python source file',
      url='https://github.com/erikdejonge/sortpythonmethod',
      author='Erik de Jonge',
      author_email='erik@a8.nl',
      license='GPL',
      packages=['sortpythonmethods'],
      zip_safe=True,
      entry_points={
          'console_scripts': [
              'sortpythonmethods=sortpythonmethods:main',
          ],
      },
      classifiers=[
          "Programming Language :: Python :: 3",
          "Development Status :: 4 - Beta ",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
          "Operating System :: POSIX",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Topic :: Software Development :: Testing",
          "Topic :: System",
      ])
