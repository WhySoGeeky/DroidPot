import os, sys, shutil
from lib.common.commands.adb import Adb
from lib.common.abstract import Monitor

from yapsy.IPlugin import IPlugin

adb = Adb()
class system_call(Monitor, IPlugin):
    def __init__(self):
        super(system_call, self).__init__()
        self.compatible_device = []


    def prepare(self, params, session, device_serial):
        """
        This method handles the preparation of the device for monitoring. You can write any file modification here
        :param params: session's configuration created from web interface
        :param session: session object
        :param device_serial: device's serial from [adb devices] command
        :return:
        """
        cur_file = os.path.dirname(os.path.realpath("__file__"))
        print "system call directory is %s"%cur_file
        #will be map and links to /system/bin
        shutil.copy2(src=os.path.join(cur_file,"modules/monitor/system_call","daemons","bootstart.sh"), dst=os.path.join(session.ramdisk_dir, "bin"))
        shutil.copy2(src=os.path.join(cur_file,"modules/monitor/system_call","daemons","bootstart2.sh"), dst=os.path.join(session.ramdisk_dir, "bin"))

        for param_key, param_value in params.iteritems():
            if param_key == "api_monitoring" and param_value == "on":
                ramdisk_dir = session.ramdisk_dir

                init_file = open(os.path.join(ramdisk_dir, "init.rc"), 'a')

                init_file.write("\non property:dev.bootcomplete=1")
                init_file.write("\n     start bootstart")
                init_file.write("\n")


                init_file.write("\nservice bootstart /system/bin/sh /bin/bootstart.sh")
                init_file.write("\n   class late-start")
                init_file.write("\n   user root")
                init_file.write("\n   group root")
                init_file.write("\n   disable")
                init_file.write("\n   oneshot")
                init_file.write("\n")
            if param_key == "syscall_monitoring" and param_value == "on":
                ramdisk_dir = session.ramdisk_dir

                init_file = open(os.path.join(ramdisk_dir, "init.rc"), 'a')

                init_file.write("\non property:dev.bootcomplete=1")
                init_file.write("\n     start bootstart")
                init_file.write("\n")


                init_file.write("\nservice bootstart /system/bin/sh /bin/bootstart2.sh")
                init_file.write("\n   class late-start")
                init_file.write("\n   user root")
                init_file.write("\n   group root")
                init_file.write("\n   disable")
                init_file.write("\n   oneshot")
                init_file.write("\n")



    def preSession(self, params, module, session, device_serial):
        """
        This method handles the manipulation required to the device just before malicious apk is install on the device.
        :param params: session's configuration created from web interface
        :param module:
        :param session: session object
        :param device_serial: device's serial from [adb devices] command
        :return:
        """
        #clear logcat first
        clear_logcat_command = "logcat -c"
        adb.shell(clear_logcat_command, root=True, device_serial=device_serial)


    def postSession(self, params, module, session, device_serial):
        """
        This method handles the manipulation or extraction of information from the device after the monitoring session has ended
        :param params: session's configuration created from web interface
        :param module:
        :param session: session object
        :param device_serial: device's serial from [adb devices] command
        :return:
        """
        #capture api hook log from logcat -d option will give one time run of logcat
        logcat_dump_command = "logcat -d -v time -s hook-ioctl"
        result = adb.shell(logcat_dump_command, root=True, device_serial=device_serial)
        if result.std_output:
            return result.std_output
        else:
            return result.std_error


    def get_view(self):
        """
        get the django configuration form.
        If you don't know what to do with this method, DON'T CHANGE ANYTHING
        :return: django configuration form
        """
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from view_system_call import ConfigForm
        sys.path.remove(os.path.dirname(os.path.abspath(__file__)))
        return ConfigForm




