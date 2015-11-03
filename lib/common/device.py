__author__ = 'RongShun'

import os, ConfigParser

DEVICES_INI = "devices.ini"

class Device(object):
    def __init__(self):
        pass

    def _read_ini(self,):
        """
        Private function to read devices.ini file
        :return: ConfigParser object
        """

        DEVICE_CONFIG = "devices.ini"

        config = ConfigParser.ConfigParser()
        config.read(DEVICE_CONFIG)
        return config

    def model(self,device_serial):
        """
        get model name for the device serial number
        :param device_serial: device serial number
        :return: device model name, if empty return empty string
        """
        config = self._read_ini()

        if config.has_section(device_serial):
            return config.get(device_serial, "model")
        else:
            return ""

    def manufacturer(self,device_serial):
        """
        get manufacturer name for the device
        :param device_serial: device serial number
        :return: device manufacturer name, if empty return empty string
        """
        config = self._read_ini()

        if config.has_section(device_serial):
            return config.get(device_serial, "manufacturer")
        else:
            return ""

    def path_name(self,device_serial):
        """
        get the directory location that stores all critical device related files, such as manufactorer root/unroot file
        :param device_serial: device serial number
        :return: location of critical device related folder
        """
        config = self._read_ini()

        if config.has_section(device_serial):
            return config.get(device_serial, "path_name")
        else:
            return ""

    def vendor_id(self,device_serial):
        """
        get the vendor id of the device
        :param device_serial: device serial number
        :return: vendor id
        """
        config = self._read_ini()

        if config.has_section(device_serial):
            return config.get(device_serial, "vendor_id")
        else:
            return ""

    def daemon_path(self,device_serial):
        """
        get the daemon location to store module's daemons
        :param device_serial: device serial number
        :return: daemon path
        """
        config = self._read_ini()

        if config.has_section(device_serial):
            return config.get(device_serial, "daemon_path").replace("\"","")
        else:
            return ""

    def backup_path(self, device_serial):
        """
        get the directory on the device to store partition backups
        :param device_serial: device serial number
        :return: partition backup directory on device
        """
        config = self._read_ini()

        if config.has_section(device_serial):
            return config.get(device_serial, "backup_path").replace("\"","")
        else:
            return ""

    def list(self,):
        """
        list all the devices in the ini file
        :return: all devices serials object
        """
        config = self._read_ini()

        return config.sections()

    def options(self, device_serial):
        """
        get all options for the device
        :return:
        """
        config = self._read_ini()
        return config.options(device_serial)




