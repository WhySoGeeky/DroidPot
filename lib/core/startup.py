__author__ = 'RongShun'

import logging, copy, ConfigParser

from os import getuid
from lib.core.managers.plugin import MonitorsManager
from lib.common.exceptions import InitilizeError
from lib.common.commands.adb import Adb
from lib.common.device import Device
from lib.common.constant import BASE_PATH
from lib.common.color import red, yellow, cyan, blue


log = logging.getLogger()
dev = Device()

def check_root():
    """
    check if program is started with root privilege.
    """
    if not getuid() == 0:
        log.critical("droidpot required to be run in root")

        raise InitilizeError

def check_modules():
    """
    initilize and check all modules
    """
    MonitorsManager().count_modules()

def init_logging():
    """
    initilize logging
    :return:
    """
    formatter = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")
    console_log = ConsoleHandler()
    console_log.setFormatter(formatter)
    log.addHandler(console_log)
    log.setLevel("INFO")
    log.propagate = False


def check_ini_files():
    """
    Check all ini files are correctly written
    """

    #check device.ini first
    device_parser = ConfigParser.ConfigParser()
    device_parser.read("devices.ini")

    for section_name in device_parser.sections():
        for name, value in device_parser.items(section_name):
            if not value:
                log.critical("%s of %s in devices.ini is not configured properly."%(name,section_name))
                raise InitilizeError


def check_device_compatibility():
    """
    checks for connected device compatibility with the framework. Quit if connected device is not found or compatible
    """
    '''
    DEVICE_CONFIG = "devices.ini"

    config = ConfigParser.ConfigParser()
    config.read(DEVICE_CONFIG)
    serial_numbers = config.sections()
    '''

    serial_numbers = dev.list()

    adb = Adb()
    connected_devices = adb.devices()

    if len(connected_devices) >= 1:
        print "Total of %d devices connected"%len(connected_devices)
    else:
        log.critical("Please connect device before starting droidpot")
        exit(0)

    for device in connected_devices:
        isCompatible = False
        for serial_number in serial_numbers:
            if device == serial_number:
                print "device %s is compatible"%serial_number
                isCompatible = True
                break

        if not isCompatible:
            log.critical("Found device that is not compatible with droidpot. Please use only compatible devices for malware analysis.")
            exit(1)



class ConsoleHandler(logging.StreamHandler):
    """
    Console logging color handler
    """
    def emit(self, record):
        colored = copy.copy(record)

        if record.levelname == "WARNING":
            colored.msg = yellow(record.msg)
        elif record.levelname == "ERROR" or record.levelname == "CRITICAL":
            colored.msg = red(record.msg)
        else:
            if "Preparing device" in record.msg:
                colored.msg = cyan(record.msg)
            elif "loaded" in record.msg:
                colored.msg = yellow(record.msg)
            else:
                colored.msg = record.msg

        logging.StreamHandler.emit(self, colored)



