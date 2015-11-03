__author__ = 'droid'
"""
Trying out inspect library for plugin loading
"""

import os, sys, inspect

DIR_PATH = os.path.join(os.getcwd(), "..", "..")
sys.path.append(DIR_PATH)

import lib.common.commands.adb as adb

if __name__ == '__main__':

    #getmembers will get all the classes within the file
    for name, data in inspect.getmembers(adb, inspect.isclass):
        print '%s :' % name, repr(data)


