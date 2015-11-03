__author__ = 'RongShun'

from os import path
from command import Command
from time import sleep


SUCCESSFUL = True
UNSUCCESSFUL = False

class Adb(Command):
    """
    ADB python wrapper
    """
    def __init__(self):
        super(Adb, self).__init__()
        self.setCommand("adb")

    def push(self, source, dest, device_serial):
        self.setDevice(device_serial)
        self.setOption("push")

        isSrcPathExist = path.isfile(source)
        #unable to check destination path valid or not because it is in the phone
        if(not isSrcPathExist):
            raise OSError
        else:
            parameters = source + " " + dest
            self.setParameters(parameters)

        output = self.execute()

        if output.std_error.__contains__("protocol failure"):
            sleep(2)
            return self.push(source,dest, device_serial)

        if output.isSuccess:
            return SUCCESSFUL
        else:
            return UNSUCCESSFUL

    def pull(self, source, dest, device_serial):
        """
        adb pull <source> <dest>
        :param source: source file path
        :param dest: destination file path on mobile device
        :return: boolean - if operation is successful
        """
        self.setDevice(device_serial)
        self.setOption("pull")

        isDestPathExist = path.dirname(dest)
        #unable to check destination path valid or not because it is in the phone

        if(not isDestPathExist):
            raise OSError
        else:
            parameters = source + " " + dest
            self.setParameters(parameters)

        output = self.execute()

        if output.isSuccess:
            return SUCCESSFUL
        else:
            return UNSUCCESSFUL

    def shell(self, command, device_serial, root=False, needOutput=True):
        """
        adb shell <parameters>
        :param command: commands to be run on the mobile device via adb shell
        :type command: str
        :param needOutput: if output is needed to be returned
        :type needOutput: bool
        :param root: if root privilege [ON THE MOBILE DEVICE] is required to run the command
        :type root: bool
        :return: output from command execution
        :rtype: object result
        """
        self.setDevice(device_serial)
        self.setOption("shell")

        if(not str(command)):
            raise ValueError

        if root is True:
            command = "su -c \"" + command + "\""

        self.setParameters(command)
        result = self.execute()

        sleep(2)
        if result.std_error.__contains__("error"):
            return self.shell(command, root, needOutput)


        return result

    def devices(self):
        """
        adb devices
        get the android devices currently connected to the host machine
        :return: dictionary of android devices
        """
        DESCRIPTION = 0
        DEVICE_ID = 0
        DEVICE_STATUS = 1

        self.setOption("devices")

        output = self.execute()
        output = output.std_output
        try:
            output.pop(DESCRIPTION)
        except IndexError as i:
            pass

        devices = {}
        #return False if no devices found
        if output:
            for line in output:
                try:
                    line_split = line.split("\t")
                    devices[line_split[DEVICE_ID]] = line_split[DEVICE_STATUS]
                except IndexError:
                    pass

        return devices

    def start_server(self):
        """
        adb start-server
        :return: nil
        """
        self.setOption("start-server")
        self.execute()

    def reboot(self, device_serial):
        """
        adb reboot
        restart android device normally
        :return: nil
        """
        self.setOption("reboot")
        self.execute()

    def reboot_bootloader(self, device_serial):
        """
        adb reboot-bootloader
        restart android device to bootloader mode
        :return: nil
        """
        self.setOption("reboot-bootloader")
        self.execute()
        sleep(2)

    def install(self, file, device_serial):
        """
        adb install <file>
        :param file: apk to be installed
        :return:
        """
        self.setDevice(device_serial)
        self.setOption("install")
        parameters = "-r %s"%(file)
        self.setParameters(parameters)
        result = self.execute()
        while result.std_error == "protocol failure":
            sleep(5)
            result = self.execute()

        sleep(1)

    def reboot_recovery(self, device_serial):
        """
        adb reboot recovery
        reboot device into recovery mode
        :return:
        """
        self.setDevice(device_serial)
        self.setOption("reboot recovery")
        self.execute()
        sleep(2)

        return self.__wait_for_recovery_mode(device_serial)


    def __wait_for_recovery_mode(self,device_serial, retries=3):
        if retries == 0:
            return False

        RECOVERY = "recovery"
        devices = self.devices()
        for device_id, device_status in devices.iteritems():
            if device_status == RECOVERY and device_id == device_serial:
                sleep(2)
                return True

        sleep(10)
        return self.__wait_for_recovery_mode(device_serial, retries-1)

    def wait_for_device(self, device_serial):
        """
        adb wait-for-device
        :return:
        """
        #self.setOption("wait-for-device")
        #self.execute()
        #sleep(2)
        while True:
            devices = self.devices()
            for device, status in devices.iteritems():
                if device == device_serial:
                    sleep(5)
                    return
            sleep(2)

    def kill_server(self):
        """
        adb kill_server
        terminate adb server
        :return: nil
        """
        self.setOption("kill-server")
        self.execute()
        sleep(2)


