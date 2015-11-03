

from yapsy.IPlugin import IPlugin
import os, ConfigParser, time,sys
sys.path.append(os.getcwd())
BASE_DIR = os.getcwd()
from lib.common.commands.adb import Adb
from lib.common.abstract import Profile

class template(Profile,IPlugin):
    def __init__(self):
        self.adb = Adb()
        super(template, self).__init__()

    def runSimulation(self,duration,package_name, random, device_serial, session):
        """
        run interaction with device
        :return:
        """
        pass

    def prepare(self, params, device_serial):
        """
        Prepare device by installing profile's apk and apk databases
        :return:
        """
        return True

    def get_view(self):
        """
        get the django configuration form.
        If you don't know what to do with this method, DON'T CHANGE ANYTHING
        :return: django configuration form
        """
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from view_template import ConfigForm
        sys.path.remove(os.path.dirname(os.path.abspath(__file__)))
        return ConfigForm



