

from yapsy.IPlugin import IPlugin
import os, ConfigParser, time,sys, hashlib

sys.path.append(os.getcwd())
BASE_DIR = os.getcwd()

from lib.common.commands.adb import Adb
from lib.common.abstract import Processing
from lib.core.managers.session import Session
from lib.common.device import Device

class system_call(IPlugin, Processing):
    def __init__(self):
        self.adb = Adb()
        super(system_call, self).__init__()

    def run(self, id):
        SYSTEM_CALL_POST = "system_call_monitor.post.cap"
        

        session = Session(id)
        logs_dir = session.logs_dir



