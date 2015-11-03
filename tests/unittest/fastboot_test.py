__author__ = 'RongShun'


import unittest, os, sys, time

DIR_PATH = os.path.join(os.getcwd(), "..", "..")
sys.path.append(DIR_PATH)

from lib.common.commands.fastboot import Fastboot
from lib.common.commands.adb import Adb


class fastboot_testCase(unittest.TestCase):
    def setUp(self):
        self.fastboot = Fastboot()
        self.adb = Adb()
        self.adb.reboot_bootloader()

    def tearDown(self):
        self.fastboot.reboot()

        while len(self.adb.devices()) == 0:
            time.sleep(5)

    @unittest.skip("skip reboot test")
    def test_reboot(self):
        self.fastboot.reboot()
        result = True

        print "[!] waiting for phone to reboot..."
        for i in range(0,5):
            if len(self.adb.devices()) == 0:
                time.sleep(10)
                result = False
            else:
                result = True
                break

            if i == 4:
                print "[!] Reboot time out"

        self.assertTrue(result, msg="fastboot reboot failed")

    @unittest.skip("skip reboot bootloader test")
    def test_reboot_bootloader(self):
        result = False
        self.fastboot.reboot_bootloader()

        devices = self.fastboot.devices()

        print "[!] waiting for phone to enter bootloader mode..."
        for i in range(0,5):
            devices = self.fastboot.devices()

            if len(devices) != 0:
                result = True
                break
            else:
                time.sleep(10)

            if i == 4:
                print "[!] Reboot time out"


        self.assertTrue(result, msg="fastboot reboot-bootloader failed")

    def test_devices(self):
        result = False
        self.fastboot.reboot_bootloader()

        time.sleep(5)
        devices = self.fastboot.devices()

        if len(devices) > 0:
            result = True

        self.assertTrue(result, msg="fastboot devices did not detect any devices")

if __name__ == '__main__':
    unittest.main()

