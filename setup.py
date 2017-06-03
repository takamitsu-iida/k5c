#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cx_Freeze 用セットアップファイル

setup.py build
setup.py bdist_msi
"""

import glob
import os
import sys

from cx_Freeze import setup, Executable

def here(path=''):
  """相対パスを絶対パスに変換して返却します"""
  return os.path.abspath(os.path.join(os.path.dirname(__file__), path))


copyDependentFiles = True
silent = True
packages = ['k5c']
includes = ['bin/fwcommon']
excludes = []
include_files = []


options = {
  'build_exe': {
    'includes': includes,
    'excludes': excludes,
    'packages': packages,
    'include_files': include_files,
    'path': sys.path + [here("./lib"), here("./lib/site-packages")]
  }
}


executables = []
pyfiles = [os.path.basename(r) for r in glob.glob('bin/*.py')]
for item in pyfiles:
  p = os.path.join('bin', item)
  exe = Executable(script=p, base=None)
  executables.append(exe)

setup(name='k5c', version='0.1', description='k5 network operation tools.', options=options, executables=executables)
