import os, sys, ast
from lib.common.commands.adb import Adb
from lib.common.abstract import Monitor

from yapsy.IPlugin import IPlugin

adb = Adb()
class critical_variable(Monitor, IPlugin):
    def __init__(self):
        super(critical_variable, self).__init__()
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
        device_variables = {}
        for param_name, variables in params.iteritems():
            for each_variable in variables:
                get_variable_command = "echo $%s"%each_variable
                result = adb.shell(get_variable_command, device_serial=device_serial)
                device_variables[each_variable] = result.std_output

        return device_variables




    def postSession(self, params, module, session, device_serial):
        """
        This method handles the manipulation or extraction of information from the device after the monitoring session has ended
        :param params: session's configuration created from web interface
        :param module:
        :param session: session object
        :param device_serial: device's serial from [adb devices] command
        :return:
        """
        device_variables = {}
        for param_name, variables in params.iteritems():
            for each_variable in variables:
                get_variable_command = "echo $%s"%each_variable
                result = adb.shell(get_variable_command, device_serial=device_serial)
                device_variables[each_variable] = result.std_output

        return device_variables



    def get_view(self):
        """
        get the django configuration form.
        If you don't know what to do with this method, DON'T CHANGE ANYTHING
        :return: django configuration form
        """
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from view_critical_variable import ConfigForm
        sys.path.remove(os.path.dirname(os.path.abspath(__file__)))
        return ConfigForm




