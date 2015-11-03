import os, sys
from lib.common.commands.adb import Adb
from lib.common.abstract import Monitor

from yapsy.IPlugin import IPlugin

adb = Adb()
class template(Monitor, IPlugin):
    def __init__(self):
        super(template, self).__init__()

    def prepare(self, params, session, device_serial):
        """
        This method handles the preparation of the device for monitoring. You can write any file modification here
        :param params: session's configuration created from web interface
        :param session: session object
        :param device_serial: device's serial from [adb devices] command
        :return:
        """
        pass

    def preSession(self, params, module, session, device_serial):
        """
        This method handles the manipulation required to the device just before malicious apk is install on the device.
        :param params: session's configuration created from web interface
        :param module:
        :param session: session object
        :param device_serial: device's serial from [adb devices] command
        :return:
        """
        pass




    def postSession(self, params, module, session, device_serial):
        """
        This method handles the manipulation or extraction of information from the device after the monitoring session has ended
        :param params: session's configuration created from web interface
        :param module:
        :param session: session object
        :param device_serial: device's serial from [adb devices] command
        :return:
        """
        pass



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




