import os, sys,ast
from lib.common.commands.adb import Adb
from lib.common.abstract import Monitor

from yapsy.IPlugin import IPlugin

adb = Adb()
class system_properties(Monitor, IPlugin):
    def __init__(self):
        super(system_properties, self).__init__()
        self.compatible_device = []


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
        for param_name, status in params.iteritems():
            if status == "on":
                getprop_command = "getprop"
                result = adb.shell(command=getprop_command, device_serial=device_serial, root=True)
                return result.std_output
            else:
                return ""




    def postSession(self, params, module, session, device_serial):
        """
        This method handles the manipulation or extraction of information from the device after the monitoring session has ended
        :param params: session's configuration created from web interface
        :param module:
        :param session: session object
        :param device_serial: device's serial from [adb devices] command
        :return:
        """
        for param_name, status in params.iteritems():
            if status == "on":
                getprop_command = "getprop"
                result = adb.shell(command=getprop_command, device_serial=device_serial, root=True)
                return result.std_output
            else:
                return ""



    def get_view(self):
        """
        get the django configuration form.
        If you don't know what to do with this method, DON'T CHANGE ANYTHING
        :return: django configuration form
        """
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from view_system_properties import ConfigForm
        sys.path.remove(os.path.dirname(os.path.abspath(__file__)))
        return ConfigForm




