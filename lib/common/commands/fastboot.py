__author__ = 'RongShun'

from command import Command
from os import path, getuid
from time import sleep

import os, sys
BASE_DIR = os.path.join(os.getcwd(), "..", "..", "..")
sys.path.append(BASE_DIR)

from lib.common.exceptions import NotRootUserError

SUCCESSFUL = True
UNSUCCESSFUL = False

class Fastboot(Command):
    """
    Fastboot python wrapper
    """
    def __init__(self):
        super(Fastboot, self).__init__()
        self.setCommand("fastboot")

        #if not getuid() == 0:
         #   raise NotRootUserError

    def flash(self, partition, image_path, device_serial):
        """
        fastboot flash <partition> [<filename>]
        :param partition: partition on android device to be flashed
        :param image_path: file on local disk to be used for flashing
        :return: boolean - successful or unsuccessful
        """
        self.setDevice(device_serial)
        self.setOption("flash")

        isFilenameExist = path.exists(image_path)

        if not isFilenameExist:
            raise OSError
        else:
            parameters = " ".join((partition, image_path))
            self.setParameters(parameters)

            output = self.execute()

            sleep(2)

            if output.isSuccess:
                return SUCCESSFUL
            else:
                return UNSUCCESSFUL

    def reboot(self, device_serial):
        """
        fastboot reboot
        reboot androi device into normal boot mode
        :return: nil
        """
        self.setDevice(device_serial)
        self.setOption("reboot")
        self.execute()
        sleep(2)

    def reboot_bootloader(self, device_serial):
        """
        fastboot reboot-bootloader
        reboot android device to bootloader mode
        :return: nil
        """
        self.setDevice(device_serial)
        self.setOption("reboot-bootloader")
        self.execute()
        sleep(2)

    def devices(self):
        self.setOption("devices")
        result = self.execute()

        devices = {}

        if result.isSuccess:
            output = result.std_output

            for line in output:
                try:
                    line_split = line.split("\t")
                    devices[line_split[0]] = line_split[1]
                except IndexError as e:
                    pass


        return devices