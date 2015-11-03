__author__ = 'RongShun'

import os, sys, time, shutil,json
from os.path import join, abspath

#loggings
import logging
#logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

#BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), "..", "..", ".."))
sys.path.append(os.getcwd())
BASE_DIR = os.getcwd()

from lib.core.managers.plugin import MonitorsManager, ProfilesManager
from lib.common.commands.adb import Adb
from lib.common.commands.fastboot import Fastboot
from lib.common.commands.command import Command
from lib.common.exceptions import SessionDirError
from lib.common.device import Device
from lib.core.partitions import Partition
import lib.common.config as config
from multiprocessing import Process
import time, logging, urllib2,datetime

SESSION_DIR = os.path.join(BASE_DIR, "sessions")

DAEMON = 0
PARTITIONS = 1
LOGS = 2
REPORT = 3
APK = 4
PROFILE = 5
directories = ["daemon", "partitions", "logs", "report", "apk", "profile"]

def get_current_device_serial():
    """
    Import method to get the current configuration device from django web
    Use for modules to get the selected device to be configured in web interface
    :return: String
    """
    device_path = os.path.join(BASE_DIR,"web", "device")
    with open(device_path) as f:
        device = f.readline()
        return device


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Session(object):
    """
    session object to get the path easily
    """
    def __init__(self, id):
        self.id = id

        self.base_dir = abspath(join(BASE_DIR, "sessions", self.id.__str__()))
        self.daemon_dir = abspath(join(self.base_dir, directories[DAEMON]))
        self.partition_dir = abspath(join(self.base_dir, directories[PARTITIONS]))
        self.logs_dir = abspath(join(self.base_dir, directories[LOGS]))
        self.report_dir = abspath(join(self.base_dir, directories[REPORT]))
        self.apk_dir = abspath(join(self.base_dir, directories[APK]))
        self.profile_dir = abspath(join(self.base_dir, directories[PROFILE]))

        self.bootimg_dir = abspath(join(self.partition_dir, "boot.img"))
        self.new_bootimg_dir = abspath(join(self.partition_dir, "new_boot.img"))
        self.extracted_boot_dir = abspath(join(self.partition_dir, "boot-extract"))
        self.ramdisk_dir = abspath(join(self.extracted_boot_dir, "ramdisk"))

        self.session_ini = abspath(join(self.base_dir, "session.ini"))

class Tool(object):
    """
    tool object to get tool path easily
    """
    def __init__(self):
        self.base_dir = abspath(join(BASE_DIR, "tools"))
        self.mkboot = abspath(join(self.base_dir, "mkbootimg", "mkboot"))
        self.twrp = abspath(join(self.base_dir, "twrp", "twrp_recovery.img"))

def run_simulation(simulation_option, modules, duration, device_serial, package_name, session):
    print "New thread for profile interaction"
    profileManager = ProfilesManager()
    analysis_time_left = duration * 60
    profileManager.run_simulation(simulation_option, modules, duration, device_serial, package_name, session)
    while analysis_time_left > 0:
        pass

    #after simulation ended, send a end session get request to django server
    urllib2.urlopen("http://localhost:8000/end_session/%s"%session.id)

class SessionManager(object):
    def __init__(self):
        self.monitorManager = MonitorsManager()
        self.profileManager = ProfilesManager()
        self.adb = Adb()
        self.fastboot = Fastboot()
        self.partition = Partition()

        self.tool = Tool()
        self.session = object
        self.config_ini = config.Session()
        self.device_backup_path = ""
        self.device = Device()


    def create_session_dir(self, session_id, device_serial):
        """
        Create new session directory with given session ID
        :param session_id: session id
        :return: nil
        """
        try:
            id_path = os.path.join(SESSION_DIR, session_id.__str__())

            is_session_dir_exist = os.path.isdir(id_path)

            if is_session_dir_exist:
                raise SessionDirError

            for directory in directories:
                new_session_path = os.path.join(id_path, directory)
                os.makedirs(new_session_path)

            self.config_ini.create(id_path, device_serial)

        except Exception as e:
            log.error("Unable to create session directory")
            self.create_session_dir(session_id, device_serial)

    def save_result(self, session_id,name, result, ext=""):
        """
        save processing result into session directory
        :param session_id:
        :param name:
        :param result:
        :return:
        """
        try:
            session = Session(session_id)
            file = open(os.path.join(session.report_dir, name+ext), 'w')
            file.write(result)
            file.close()

            return True
        except Exception as e:
            return False

    def get_results(self, session_id):
        """
        Get all json results from session's report directory
        :param session_id:
        :return:
        """
        reports = {} #key: file name, value: json content
        current_session = Session(session_id)
        for file in os.listdir(current_session.report_dir):
            if file.endswith(".json"):
                with open(os.path.join(current_session.report_dir, file)) as data_file:
                    reports[file.split(".")[0].replace("_"," ")] = json.load(data_file)

        return reports



    def end(self, session_id, device_backup_path, modules_config, device_serial):
        """
        End sandbox analysis
        :param session_id:
        :return:
        """
        self.session = Session(session_id)

        log_name = "end_status_%s"%session_id
        end_logger = logging.getLogger(log_name)
        end_logger.setLevel(logging.INFO)
        START_LOG = os.path.join(self.session.logs_dir, "end_status.log")
        fh = logging.FileHandler(START_LOG)
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        fh.setFormatter(formatter)
        end_logger.addHandler(fh)

        #get post-session monitor required data from device
        end_logger.info("Post-session information gathering")
        if modules_config:
            for module, params in modules_config.iteritems():
                if params["module_type"] == "monitor":
                    end_result = self.monitorManager.postSession(module,params,self.session, device_serial=device_serial)
                    log_file = os.path.join(self.session.logs_dir, module.replace(" ","_")+ ".post" +".cap")
                    file_handler = open(log_file, "w+")
                    file_handler.write(end_result.__str__())
                    file_handler.close()


        #restore partitions
        end_logger.info("Restoring boot partition")
        self.restore_boot_partition(self.session, device_serial)
        end_logger.info("Restoring other partitions")
        self.partition.restore(twrp_path=self.tool.twrp, backup_src=self.session.partition_dir, backup_dest=device_backup_path, device_serial=device_serial)

        return True

    def start_logger(self, session_id):
        #initilize status logging
        log_name = "start_status_%s"%session_id
        self.start_logger = logging.getLogger(log_name)
        self.start_logger.setLevel(logging.INFO)
        self.START_LOG = os.path.join(self.session.logs_dir, "status.log")
        fh = logging.FileHandler(self.START_LOG)
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        fh.setFormatter(formatter)
        self.start_logger.addHandler(fh)


    def start(self, modules_config, session_id, apk_paths, duration, device_serial):
        """
        Begin sandbox analysis.
        :param modules_config: parameters selected from configuration page
        :type modules_config: dictionary. configuration of modules from django session database
        :return: if analysis is successful or not
        """

        #create session directory
        self.create_session_dir(session_id, device_serial)
        #session object
        self.session = Session(session_id)

        self.start_logger(session_id)

        #checking device temp folders are ready
        self.start_logger.info("Initilizing device %s",device_serial)
        self.start_logger.info("Checking device temp folders are ready")
        self.check_device_tmp_folders(device_serial)

        #create symbolic link for apks
        self.start_logger.info("Creating symbolic links for APKs")
        self.create_apk_symbolic_links(apk_paths)
        #backup device partitions
        self.start_logger.info("Backing up partitions")
        device_backup_path = self.backup_device_partitions(device_serial)

        #prepare device for session (haven't copy to device yet)
        self.start_logger.info("Preparing device partitions")
        is_partition_init = self.prepare_device_for_session(device_serial, modules_config)

        #install user profile
        self.start_logger.info("Installing user profile")
        self.install_user_profile(device_serial, modules_config)

        #copy daemons to device
        self.start_logger.info("Copying daemons onto device")
        self.copy_daemons_to_device(device_serial, modules_config)

        #push modified partition to device
        self.start_logger.info("Pushing modified partitions to device")
        self.push_modified_partition_to_device(device_serial, is_partition_init)

        #get baseline of the device (pre session)
        #depending on the monitor modules requirements
        self.start_logger.info("Pre-session initilizations")
        self.device_presession(device_serial, modules_config)

        #lastly, install the suspicious apk
        self.start_logger.info("Installing APK on device")
        package_name = self.install_apk(device_serial)
        while not package_name:
            package_name = self.install_apk(device_serial)

        #whitelist package name for monitoring
        self.whitelist_package_name(package_name, device_serial)

        #run profile simulation script
        self.start_logger.info("package name is %s"%package_name)
        self.start_logger.info("Running profile simulation")

        now = datetime.datetime.now()
        end_time = now + datetime.timedelta(minutes=duration)
        end_time_str = end_time.strftime("%H:%M:%S %d-%m-%Y")
        self.run_profile_simulation(duration, modules_config, device_serial, package_name, self.session)
        self.start_logger.info("Session end time:  %s"%end_time_str)

        return (device_backup_path,self.START_LOG, end_time)

    def whitelist_package_name(self,package_name, device_serial):
        tmp_path = self.device.daemon_path(device_serial)
        whitelist_path = os.path.join(tmp_path, "whitelist.txt")
        add_whitelist_command = "echo \"%s\" > %s"%(package_name, whitelist_path)
        result = self.adb.shell(add_whitelist_command, root=True, device_serial=device_serial)



    def check_device_tmp_folders(self,device_serial):
        '''
        Check android device for the temp folders declared in devices.ini
        :param device_serial: device serial no.
        :return: boolean result
        '''
        try:
            device_backup_path = self.device.backup_path(device_serial)
            device_daemon_path = self.device.daemon_path(device_serial)

            paths = [device_backup_path, device_daemon_path]
            for path in paths:
                check_path_command = "ls %s"%path
                result = self.adb.shell(check_path_command, device_serial=device_serial, root=True)
                if not result.std_output:
                    log.error("device %s is not ready for DroidPot! Ensure all tmp folders declared in devices.ini are present on the device")
                    return False

            return True
        except Exception as e:
            log.error("device %s is not ready for DroidPot! Ensure all tmp folders declared in devices.ini are present on the device")
            return False


    def run_profile_simulation(self, duration, modules_config,device_serial, package_name, session):
        #try:
        log.info("Running user simulation")
        if modules_config:
            for modules, params in modules_config.iteritems():
                try:
                    if params["module_type"] == "profile":
                        simulation_option = params["simulation_option"]
                        p = Process(target=run_simulation,
                                    args=(simulation_option, modules, duration, device_serial, package_name, session))
                        p.start()
                        break #break in case there's more than 1 profile selected
                except KeyError as e:
                    pass
        #except Exception as e:
            #log.error("Unable to run profile simulation")
            #time.sleep(10)
            #self.run_profile_simulation(duration, modules_config,device_serial, package_name, session)

    def install_apk(self, device_serial):
        try:
            log.info("Installing sample apk")
            self.adb.wait_for_device(device_serial)
            apks = os.listdir(self.session.apk_dir)
            for apk in apks:
                apk_path = os.path.join(self.session.apk_dir, apk)
                if os.path.isfile(apk_path):
                    log.info("Installing apk %s" % (apk_path))

                    get_current_packages_command = "pm list packages"
                    result = self.adb.shell(get_current_packages_command, root=True, device_serial=device_serial)
                    packages = result.std_output

                    apk_realpath = os.path.realpath(apk_path)
                    self.adb.push(source=apk_realpath, dest="/sdcard/tmp.apk", device_serial=device_serial)
                    time.sleep(2)
                    self.adb.shell("pm install -rt /sdcard/tmp.apk", root=True, device_serial=device_serial)
                    time.sleep(2)
                    self.adb.shell("rm -f /sdcard/tmp.apk", root=True, device_serial=device_serial)
                    #os.remove(apk_path)

                    result = self.adb.shell(get_current_packages_command, root=True, device_serial=device_serial)
                    packages_after = result.std_output
                    sample_package_name = ""
                    for package in packages_after:
                        if not packages.__contains__(package):
                            sample_package_name = package.replace("package:","")

                    return  sample_package_name
                    #break

                    # Note: ONLY 1 APK TO BE ANALYSIS AT A TIME. AFTER ANALYSIS SESSION, INSTALL THE NEXT APK
        except Exception as e:
            log.error("Unable to install APK onto device")
            print e
            time.sleep(10)
            return ""

    def device_presession(self, device_serial, modules_config):
        try:
            log.info("Getting device baseline")
            self.adb.wait_for_device(device_serial)
            time.sleep(10)
            if modules_config:
                for module, params in modules_config.iteritems():
                    if params["module_type"] == "monitor":
                        baseline = self.monitorManager.preSession(module, params, self.session, device_serial)

                        print "baseline file result is "
                        print baseline

                        # store baseline information into an analysis file
                        log_file = os.path.join(self.session.logs_dir, module.replace(" ", "_") + ".pre" + ".cap")

                        file_handler = open(log_file, "w+")
                        file_handler.write(baseline.__str__())
                        file_handler.close()
        except Exception as e:
            log.error("Unable to get baseline of device")
            time.sleep(10)
            self.device_presession(device_serial, modules_config)

    def push_modified_partition_to_device(self, device_serial, is_partition_init):
        try:
            log.info("Modifying device's partitions")
            if is_partition_init:
                self.push_boot_partition(self.session, device_serial=device_serial)
        except Exception as e:
            log.error("Unable to push modified partition to device")
            time.sleep(10)
            self.push_modified_partition_to_device(device_serial, is_partition_init)

    def copy_daemons_to_device(self, device_serial, modules_config):
        try:
            log.info("Transferring daemons to device")
            if modules_config:
                for module, params in modules_config.iteritems():
                    # copy each module's daemons individually into device

                    if params["module_type"] == "monitor":
                        daemon = self.monitorManager.daemons(module, params)
                        if daemon:
                            self.copy_daemons(daemon, self.session)
                            # check device ini for temp path preference
                            dev_daemon_path = self.device.daemon_path(device_serial)
                            self.push_daemons(self.session, dev_daemon_path, device_serial=device_serial)

        except Exception as e:
            log.error("Unable to install process monitors on device")
            time.sleep(10)
            self.copy_daemons_to_device(device_serial, modules_config)

    def install_user_profile(self, device_serial, modules_config):
        try:
            log.info("Installing profile on device")
            self.adb.wait_for_device(device_serial)
            if modules_config:
                for module, params in modules_config.iteritems():
                    if params["module_type"] == "profile":
                        self.profileManager.setup_device(module, params, device_serial)
                        break
        except Exception as e:
            log.error("Unable to install user profile onto device")
            time.sleep(10)
            self.install_user_profile(device_serial, modules_config)

    def prepare_device_for_session(self, device_serial, modules_config):
        try:
            is_partition_init = self.monitorManager.prepare(modules_config, self.session, device_serial)
        except Exception as e:
            log.error("Unable to prepare partitions for session")
            time.sleep(10)
            return self.prepare_device_for_session(device_serial, modules_config)

        return is_partition_init

    def backup_device_partitions(self, device_serial):
        try:
            log.info("Backing up device partitions")
            self.start_logger.info("Performing TWRP backup")
            device_backup_path = self.partition.backup(twrp_path=self.tool.twrp, backup_dest=self.session.partition_dir,
                                                       device_serial=device_serial)

            if device_backup_path:
                log.debug("Backup completed, extracting boot partition for modification")

                time.sleep(3)
                self.device_backup_path = device_backup_path
                is_boot_extracted = self.get_and_extract_boot_partition(self.session, device_serial=device_serial)
                while (not is_boot_extracted):
                    time.sleep(3)
                    is_boot_extracted = self.get_and_extract_boot_partition(self.session, device_serial=device_serial)
        except Exception as e:
            log.error("Unable to perform backup")
            time.sleep(2)
            return self.backup_device_partitions(device_serial)

        return device_backup_path

    def create_apk_symbolic_links(self, apk_paths):
        try:
            log.info("Creating symbolic links for APKs")
            for apk_name, apk_realpath in apk_paths.iteritems():
                os.symlink(apk_realpath, os.path.join(self.session.apk_dir, apk_name))
        except Exception as e:
            log.error("Unable to create symbolic link for apks")
            time.sleep(10)
            self.create_apk_symbolic_links(apk_paths)

    def get_baseline(self,device_serial):
        """
        Get the device baseline processes
        """
        process_names = []

        list_proc_command = "ls /proc/"
        output = self.adb.shell(list_proc_command,root=True,needOutput=True,device_serial=device_serial)
        processes = output.std_output

        commands = ""
        for proc in processes:
            get_proc_name_command = "cat /proc/%s/status" %(proc)

            commands += get_proc_name_command + " && "

        proc_name = self.adb.shell(commands,root=True, needOutput=True, device_serial=device_serial).std_output
        if proc_name:
            process_names.append(proc_name)

        return process_names



    """
    DAEMON HANDLER
    handles the copying daemons into session directory and pushing daemons to android device
    """
    def copy_daemons(self, daemons, session):
        daemon_dir = session.daemon_dir

        for module_name, daemons_path in daemons.iteritems():
            log.debug("found %s in module %s"% (daemons_path,module_name))

            for d_path in daemons_path:
                shutil.copy(d_path, daemon_dir)
        return True

    def push_daemons(self, session, dir, device_serial):
        daemon_dir = session.daemon_dir

        for daemon in os.listdir(daemon_dir):
            log.info("[*] Pushing %s to device" % daemon)
            log.debug("pushing %s to device %s directory"%(daemon,dir))
            source = os.path.join(daemon_dir, daemon)

            self.adb.push(source=source, dest=dir, device_serial=device_serial)

            log.info("[*] Changing permission of daemons")
            device_daemon_path = os.path.join(dir, daemon)
            chmod_command = "chmod 777 %s"%device_daemon_path
            chown_command = "chown root:root %s"%device_daemon_path
            self.adb.shell(chown_command, root=True, device_serial=device_serial)
            self.adb.shell(chmod_command, root=True, device_serial=device_serial)

        return True


    """
    PARTITION HANDLER
    handles the partition extraction and reflashing of android device
    """
    def get_and_extract_boot_partition(self, session,device_serial):
        self.start_logger.info("Extracting boot partition for modification")
        EXTRACTED_BOOT_LOC = "/sdcard/boot.img"

        #retrieve boot partition location
        retry = True
        while retry:
            log.warn("[*] Retrieving boot partition location...")
            command = "ls -al /dev/block/platform/msm_sdcc.1/by-name | grep ' boot'"
            result = self.adb.shell(command=command, device_serial=device_serial)

            boot_image_loc = ""

            for output in result.std_output:
                log.debug("result line: %s"%output)
                try:
                    output_split = output.split('-> ')
                    boot_image_loc = output_split[1]
                    boot_image_loc.replace('\r', '')
                    retry = False
                except IndexError:
                    log.debug("Cannot get boot partition location. Retrying.")
                    time.sleep(3)
                    pass


        time.sleep(5)

        #copy image locally
        log.info("[*] dd image on device...")
        command = "dd if=" + boot_image_loc +" of=" + EXTRACTED_BOOT_LOC
        result = self.adb.shell(root=True, command=command, device_serial=device_serial)

        if not result.isSuccess:
            raise OSError

        time.sleep(5)

        #pulling boot.img from device
        log.info("[*] Pulling boot.img from device...")
        self.adb.pull(source=EXTRACTED_BOOT_LOC, dest=session.partition_dir, device_serial=device_serial)

        time.sleep(5)

        #decompress boot.img
        log.info("[*] Decompressing boot.img with mkboot tool...")
        params =  " ".join([session.bootimg_dir, session.extracted_boot_dir])

        log.debug("parameters are %s" %params)
        cmd = Command()
        cmd.setCommand(self.tool.mkboot)
        cmd.setParameters(params)
        logging.debug(params)
        cmd.execute()

        time.sleep(5)

        if(not os.path.exists(session.extracted_boot_dir)):
            self.start_logger.info("Extracting boot partition failed")
            return False
        else:
            return True

    def push_boot_partition(self, session,device_serial):
        #create new boot.img
        logging.debug("creating new boot partition")
        params = " ".join([session.extracted_boot_dir, session.new_bootimg_dir])
        cmd = Command()
        cmd.setCommand(self.tool.mkboot)
        cmd.setParameters(params)
        logging.debug(params)
        cmd.execute()

        time.sleep(5)

        #push new partition to device
        self.adb.reboot_bootloader(device_serial)
        time.sleep(5)

        fastboot_devices = self.fastboot.devices()
        for i in range(0,5):
            if len(fastboot_devices) > 0:
                log.info("[*] Device found in bootloader mode")
                break
            else:
                log.info("[!] Could not detect device in bootloader mode. Retrying...")
                time.sleep(10)
                fastboot_devices = self.fastboot.devices()

            if i == 4:
                log.warning("[!] Could not detect device in bootloader mode. TIME OUT")
                return False

        #flash boot partition with fastboot
        #must be in sudo
        log.info("[*] Flashing partition with new image")

        self.fastboot.flash(partition="boot", image_path=session.new_bootimg_dir,device_serial=device_serial)

        time.sleep(5)
        self.fastboot.reboot(device_serial)

    def restore_boot_partition(self, session,device_serial):
        log.info("[*] Restoring boot partition...")
        self.adb.wait_for_device(device_serial)
        self.adb.reboot_bootloader(device_serial)

        while True:
            devices = self.fastboot.devices()
            if devices:
                break

        self.fastboot.flash("boot", session.bootimg_dir, device_serial=device_serial)
        self.fastboot.reboot(device_serial)


if __name__ == '__main__':
    sm = SessionManager()

    modules = {"Syscall Monitor": {"proc_name":"camera"}}
    print sm.get_baseline(device_serial="d54d8e8f")