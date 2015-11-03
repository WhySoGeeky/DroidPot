

from yapsy.IPlugin import IPlugin
import os, ConfigParser, time,sys, hashlib

sys.path.append(os.getcwd())
BASE_DIR = os.getcwd()

from lib.common.commands.adb import Adb
from lib.common.abstract import Processing
from lib.core.managers.session import Session
from lib.common.device import Device

class template(IPlugin, Processing):
    def __init__(self):
        self.adb = Adb()
        super(template, self).__init__()

    def run(self, id):
        pass



