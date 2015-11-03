__author__ = 'RongShun'

import unittest
from lib.common.commands.adb import Adb
from time import sleep
import os

SDCARD_PATH = "/sdcard/"
TEST_FILE = "testFile.txt"

class adb_testcase(unittest.TestCase):
    def setUp(self):
        self.adb_c = Adb()
        self.adb_c.start_server()

    def tearDown(self):
        #self.adb_c.kill_server()
        pass

    #@unittest.skip("skipping test device")
    def test_devices(self):
        devices = self.adb_c.devices()

        #print devices
        result = True
        if len(devices) == 0:
            result = False

        self.assertTrue(result, msg="No device detected")


    def test_push_file(self):
        path = os.path.dirname(os.path.realpath(__file__))

        src = os.path.join(path, TEST_FILE)
        dest = os.path.join(SDCARD_PATH, TEST_FILE)

        isSuccessful = self.adb_c.push(source=src, dest=dest)
        self.assertTrue(isSuccessful, msg="adb push not successful")

    def test_pull_file(self):
        path = os.path.dirname(os.path.realpath(__file__))

        src = os.path.join(SDCARD_PATH, TEST_FILE)
        dest = os.path.join(path, "extract.txt")

        isSuccessful = self.adb_c.pull(source=src, dest=dest)
        self.assertTrue(isSuccessful, msg="adb pull not successful")

        os.remove(dest)

    def test_shell_no_root(self):
        parameters = "ps"
        result = self.adb_c.shell(command=parameters)

        self.assertTrue(result.isSuccess, msg="adb shell ps not successful")
        print result.std_output

    def test_shell_with_root(self):
        parameters = "strace -p 1"
        result = self.adb_c.shell(needOutput=False, root=True, command=parameters)

        self.assertTrue(result.isSuccess, msg="adb shell with root not successful")
        self.adb_c.reboot()

        sleep(5)
        while len(self.adb_c.devices()) == 0:
            print("waiting for device to reboot...")
            sleep(10)


    @unittest.skip("skipping reboot test")
    def test_reboot_commands(self):
        """
        reboot command testcase should be the last
        :return:
        """
        self.adb_c.reboot()
        print("device rebooting... Please wait...")
        sleep(3)
        devices = self.adb_c.devices()

        foundDevice = False
        if devices:
            foundDevice = True

        self.assertFalse(foundDevice, msg="adb reboot not successful")


if __name__ == '__main__':
    unittest.main()

