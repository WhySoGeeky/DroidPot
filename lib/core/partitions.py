__author__ = 'RongShun'

import sys, os,re, time, hashlib, logging, subprocess, glob

#logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__file__)

sys.path.append(os.getcwd())
BASE_DIR = os.getcwd()

from lib.common.commands.adb import Adb
from lib.common.commands.fastboot import Fastboot
from lib.common.exceptions import BackupError
from lib.common.device import Device
from lib.common.exceptions import PartitionError


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

'''
TRWP switches
-S = System
-D = Data
-C = Cache
-R = Recovery
-1 = special partition 1
-2 = special partition 2
-3 = special partition 3
-B = Boot
-A = Android secure
-E = SD-Ext
-O = use compression
-M = do not create MD5
'''

class Partition(object):
    __metaclass__ = Singleton

    def __init__(self):
        self.adb = Adb()
        self.fastboot = Fastboot()
        self.device = Device()

        #constant variables
        self.RECOVERY = "recovery"
        self.TWRP_SWITCH = "BDO" #BSDCO


    def restore(self, twrp_path, backup_src, backup_dest, device_serial):
        try:
            log.info("Restoring android device partitions")
            RECOVERY = self.RECOVERY
            ORIGINAL_RECOVERY_PATH = os.path.join(backup_src, "original_recovery")

            log.info("Waiting for device in adb mode")
            self.adb.wait_for_device(device_serial)

            self.adb.reboot_bootloader(device_serial)
            self.fastboot.flash(partition=RECOVERY, image_path=twrp_path, device_serial=device_serial)
            self.fastboot.reboot(device_serial)
            self.adb.wait_for_device(device_serial)
            self.adb.reboot_recovery(device_serial)
            #self.adb.shell("mkdir -p %s"%(backup_dest))

            backup_file_paths = glob.glob(os.path.join(backup_src, "*.win*"))
            self.adb.reboot_recovery(device_serial) #needed, if not will have bug in adb push
            for backup_file_path in backup_file_paths:
                backup_file_split = backup_file_path.split("/")
                backup_file_name = backup_file_split[len(backup_file_split) - 1]
                #self.__copy_backup(source_filepath=backup_file_path, dest_filepath=os.path.join(backup_dest, backup_file_name), direction="push", twrp=True, device_serial=device_serial, check_hash=True)


            backup_dest_split = backup_dest.split("/")
            backup_folder_name = backup_dest_split[-2]

            self.adb.shell("twrp restore %s %s"%(backup_folder_name, self.TWRP_SWITCH),device_serial)
            self.adb.shell("rm -rf %s"%(backup_dest), device_serial)
            self.adb.reboot(device_serial)
            self.adb.wait_for_device(device_serial)
            self.adb.reboot_bootloader(device_serial)
            self.fastboot.flash(RECOVERY, ORIGINAL_RECOVERY_PATH, device_serial)
            self.fastboot.reboot(device_serial)
            self.adb.wait_for_device(device_serial)
            log.info("Restore device successfully")
            return True
        except Exception as e:
            log.error("unable to restore device partitions")
            self.restore(self, twrp_path, backup_src, backup_dest, device_serial)


    def backup(self, twrp_path, backup_dest, device_serial):
        try:
            log.info("Backing up android device partitions")
            RECOVERY = self.RECOVERY

            RECOVERY_PATH = self.device.backup_path(device_serial)

            RECOVERY_TEMP_DEV_LOC = os.path.join(RECOVERY_PATH, RECOVERY)
            ORIGINAL_RECOVERY_PATH = os.path.join(backup_dest, "original_recovery")

            mount_point = self.__get_mount_point(device_serial=device_serial)
            partitions = self.__get_partitions(mount_point, device_serial=device_serial)

            if partitions.has_key(RECOVERY):
                recovery_device = partitions[RECOVERY]
            else:
                raise BackupError

            log.info("Waiting for device in adb mode")
            self.adb.wait_for_device(device_serial)

            self.__dd_backup_partition(partition_name=RECOVERY, device=recovery_device, dest=RECOVERY_TEMP_DEV_LOC, device_serial=device_serial)
            self.__copy_backup(source_filepath=RECOVERY_TEMP_DEV_LOC, dest_filepath=ORIGINAL_RECOVERY_PATH, direction="pull", device_serial=device_serial, check_hash=True)
            self.adb.shell("rm -f %s"%(RECOVERY_TEMP_DEV_LOC), device_serial=device_serial)
            self.adb.reboot_bootloader(device_serial)
            self.fastboot.flash(partition=RECOVERY, image_path=twrp_path, device_serial=device_serial)
            self.fastboot.reboot(device_serial)
            self.adb.wait_for_device(device_serial)
            self.adb.reboot_recovery(device_serial)
            backup_path = self.__twrp_backup_partitions(switches=self.TWRP_SWITCH, device_serial=device_serial)

            backup_files = self.adb.shell("ls %s"%(backup_path),device_serial=device_serial)
            self.adb.reboot_recovery(device_serial) #needed, if not there's a bug in adb pull
            for file in backup_files.std_output:
                source_filepath = os.path.join(backup_path, file)
                dest_filepath = os.path.join(backup_dest, file)
                #self.__copy_backup(source_filepath, dest_filepath, direction="pull", twrp=True, check_hash=False, device_serial=device_serial)
                time.sleep(2)
                #self.adb.shell("rm -f %s"%(source_filepath))

            self.adb.reboot_bootloader(device_serial)
            self.fastboot.flash(partition=RECOVERY, image_path=ORIGINAL_RECOVERY_PATH, device_serial=device_serial)
            self.fastboot.reboot(device_serial)
            self.adb.wait_for_device(device_serial)
            #self.adb.shell("rm -rf %s"%(backup_path))

            log.info("Backup device successfully")
            return backup_path
        except Exception as e:
            log.error("Unable to perform partition backup")
            #self.backup(twrp_path,backup_dest, device_serial)



    def __copy_backup(self, source_filepath, dest_filepath, check_hash, direction,tries=30, twrp=False, device_serial=""):
        """
        Recursive function to backup file from device to host machine with limited retries
        :param source_filepath: source file path on device
        :param dest_filepath: destination file path on host machine
        :param tries: number of retries (default:3)
        :return: bool
        """
        try:
            if tries == 0:
                log.critical("Reach max retries")
                raise PartitionError

            if direction =="pull":
                self.adb.pull(source=source_filepath, dest=dest_filepath, device_serial=device_serial)
                time.sleep(2)
                if check_hash:
                    has_file_integrity = self.__compare_md5(source_filepath, dest_filepath, twrp, device_serial)
            elif direction == "push":
                self.adb.push(source=source_filepath, dest=dest_filepath, device_serial=device_serial)
                time.sleep(2)
                if check_hash:
                    has_file_integrity = self.__compare_md5(dest_filepath, source_filepath, twrp, device_serial)
            else:
                raise BackupError
            if check_hash:
                if not has_file_integrity :
                    log.critical("Hash of %s of copied file is different from file on device."%(source_filepath))
                    log.critical("Retrying after 10 seconds...")
                    time.sleep(10)
                    return self.__copy_backup(source_filepath, dest_filepath,check_hash,direction, tries-1, twrp, device_serial)
        except Exception as e:
            log.error("Unable to copy backup files from device to host machine")
            self.__copy_backup(source_filepath, dest_filepath, check_hash, direction,tries-1, twrp, device_serial)




    def __compare_md5(self, device_path, host_path, twrp, device_serial):
        """
        Compare the md5 of original file on device and copied file to host machine
        :param device_path:  file path on device
        :param host_path:  file path on host machine
        :return: bool
        """
        try:
            if not twrp:
                result = self.adb.shell("md5 " + device_path, device_serial)
            else:
                result = self.adb.shell("md5sum " + device_path, device_serial)

            stdout = result.std_output
            try:
                device_md5 = stdout[0].split(" ")[0]
            except IndexError:
                device_md5 = ""

            host_md5 = hashlib.md5(open(host_path).read()).hexdigest()
            log.debug("device: %s    host: %s"%(device_md5, host_md5))
            if device_md5 == host_md5:
                return True
            else:
                return False
        except Exception as e:
            log.error("Unable to compare md5")
            raise PartitionError

    def __twrp_backup_partitions(self, switches, foldername="", device_serial=""):
        try:
            command = "twrp backup %s %s"%(switches, foldername)
            result = self.adb.shell(command, device_serial=device_serial)

            backup_path = ""
            log.debug(result.std_output)
            for line in result.std_output:
                match = re.search(r'Backup Folder: .*', line)
                if match:
                    log.debug(match.group())
                    match_split = match.group().split(":")
                    backup_path = match_split[1].replace(" ", "")

            return backup_path
        except Exception as e:
            log.error("unable to perform twrp partition backup")
            self.__twrp_backup_partitions(self, switches, foldername, device_serial)




    def __get_mount_point(self,device_serial):
        """
        Get the mount point of device partition
        :return:
        """
        try:
            self.adb.wait_for_device(device_serial)
            FIRST_LINE = 0

            parameter = "mount | grep -E /dev/block/platform/.+/by-name/system"
            result = self.adb.shell(root=True, command=parameter, device_serial=device_serial)
            if result.std_error:
                raise Exception
            #remove /system from command outline
            mount_point = result.std_output[FIRST_LINE].split()[FIRST_LINE][:-6]

            return mount_point
        except Exception as e:
            log.error("cannot get device mount points")
            time.sleep(5)
            return self.__get_mount_point(device_serial)

    def __get_partitions(self, device, device_serial):
        """
        Get android device partitions
        :param device: mount path
        :return: list of dict of partition name as key and partition location as value
        """
        try:
            self.adb.wait_for_device(device_serial)
            parameter = "ls -al " + device
            result = self.adb.shell(root=True, command=parameter, device_serial=device_serial)

            if result.std_error:
                raise Exception

            partitions = {}
            for line in result.std_output:
                match = re.search(r'\w* -> .*', line)
                if match:
                    match_split = match.group().split(" -> ")
                    partitions[match_split[0]] = match_split[1]

            return partitions
        except Exception as e:
            log.error("Unable to get device partitions")
            time.sleep(5)
            return self.__get_partitions(device, device_serial)

    def __dd_backup_partition(self, partition_name, device, dest, device_serial):
        """
        backup given partition to desired destination
        :param partition_name: name of partition
        :param device: dev path of partition
        :return:
        """
        try:
            command = "dd if=%s of=%s"%(device, dest)
            result = self.adb.shell(root=True, command=command, device_serial=device_serial)

            if result.std_output:
                log.debug(result.std_output)
                return True
            else:
                log.debug(result.std_error)
                return False
        except Exception as e:
            log.error("Unable to backup partition to destination")
            raise PartitionError




if __name__ == "__main__":
    bk = Partition()
    device_backup_path = bk.backup(twrp_path="/home/droid/Desktop/twrp_recovery.img", backup_dest="/home/droid/test/", device_serial="d54d8e8f")
    time.sleep(60)
    bk.restore(twrp_path="/home/droid/Desktop/twrp_recovery.img", backup_src="/home/droid/test/", backup_dest="/external_sd/TWRP/BACKUPS/d54d8e8f/2015-07-15--09-18-35/", device_serial="d54d8e8f")







