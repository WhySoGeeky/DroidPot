

import os
from os.path import join, isfile
from os import listdir
import os

from abc import ABCMeta, abstractmethod
from django import forms
from lib.common.commands.adb import Adb

import logging
logging.basicConfig(level=logging.DEBUG)
logs = logging.getLogger("Monitor")

class Processing(object):
    """Base abstract class for processing module"""
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def run(self, id):
        """
        process raw data from monitoring session
        :return: dict
        """
        return dict

class Profile(object):
    """Base abstract class for profile module"""
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def get_view(self):
        """
        get the django configuration form
        :return: django configuration form
        """
        return ConfigForm

    @abstractmethod
    def runSimulation(self, duration,package_name, random, device_serial, session):
        pass

    @abstractmethod
    def prepare(self, params, device_serial):
        """
        Prepare device by installing profile's apk and apk databases
        :param params: parameters from web interface
        :param device_serial: android device's serial number
        :return:
        """
        return True

    def getCompatibleDevices(self):
        """
        get the list of compatible device for the module
        :return:
        """
        return self.compatible_device

    def setCompatibleDevices(self, new_device):
        """
        set the list of compatible device for the module
        :param new_device:
        :return:
        """
        self.compatible_device = new_device

    def activate(self):
        """
        activate the module
        :return:
        """
        logs.debug("Plugin activated")
        self.is_activated = True

    def deactivate(self):
        """
        deactivate the module
        :return:
        """
        #print "called when plugin is deactivated"
        logs.debug("Plugin deactivated.")
        self.is_activated = False


class Monitor(object):
    """Base abstract class for monitor module."""
    __metaclass__ = ABCMeta

    def __init__(self):
        super(Monitor, self).__init__()
        self.compatible_device = []

    @abstractmethod
    def prepare(self, params, session, device_serial):
        """
        initilize the device for analysis
        :param params:
        :param session:
        :return:
        """
        return bool

    @abstractmethod
    def preSession(self, params, module, session, device_serial):
        """
        things to do with the device before preparing the device for monitoring
        :return:
        """
        return bool

    @abstractmethod
    def postSession(self, params, module, session, device_serial):
        """
        things to do with the devvice after the device monitoring session is over
        :return:
        """
        return bool

    def daemons(self,module_name,compile=False):
        """
        get the daemons path in module
        :param compile: if daemon requires cross compilation from source (to be implement in the future)
        :return:
        """
        cur_dir = os.getcwd()

        daemons = []
        daemon_dir = join(cur_dir, "modules", "monitor",module_name.replace(" monitor",""), "daemons")

        for file_name in listdir(daemon_dir):
            dir_file_path = join(daemon_dir, file_name)
            if isfile(dir_file_path):
                daemons.append(dir_file_path)

        return daemons

    @abstractmethod
    def get_view(self):
        """
        get the django configuration form
        :return: django configuration form
        """
        return ConfigForm

    def getCompatibleDevices(self):
        """
        get the list of compatible device for the module
        :return:
        """
        return self.compatible_device

    def setCompatibleDevices(self, new_device):
        """
        set the list of compatible device for the module
        :param new_device:
        :return:
        """
        self.compatible_device = new_device

    def activate(self):
        """
        activate the module
        :return:
        """
        logs.debug("Plugin activated")
        self.is_activated = True

    def deactivate(self):
        """
        deactivate the module
        :return:
        """
        #print "called when plugin is deactivated"
        logs.debug("Plugin deactivated.")
        self.is_activated = False


class ConfigForm(forms.Form):
    pass


