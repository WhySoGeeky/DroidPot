

from yapsy.IPlugin import IPlugin
import os, ConfigParser, time,sys, hashlib

sys.path.append(os.getcwd())
BASE_DIR = os.getcwd()

from lib.common.commands.adb import Adb
from lib.common.abstract import Processing
from lib.core.managers.session import Session
from lib.common.device import Device

SESSION_ID = "id"
START_TIME = "start_time"
END_TIME = "end_time"
SAMPLE_HASH = "sample_hash"
SAMPLE_SIZE = "sample_size"
PACKAGE_NAME = "package_name"
DEVICE_NAME = "device_name"
DEVICE_SERIAL = "device_serial"

MD5 = "md5"
SHA1 = "sha1"
SHA256 = "sha256"

general_info = {
    SESSION_ID: "",
    START_TIME :"",
    END_TIME :"",
    SAMPLE_HASH: {
        MD5:"",
        SHA1:"",
        SHA256:""
    },
    SAMPLE_SIZE:"",
    PACKAGE_NAME:"",
    DEVICE_NAME: "",
    DEVICE_SERIAL: ""
}

class general_information(IPlugin, Processing):
    def __init__(self):
        self.adb = Adb()
        super(general_information, self).__init__()

    def run(self, id):
        """
        Gather sample general information
        1. file hash
        2. file size
        3. file name
        4. package name
        5. device name
        6. device serial
        :return:
        """
        STATUS_FILE = "status.log"
        package_name = ""
        sample_md5 = ""
        sample_sha1 = ""
        sample_sha256 = ""
        sample_size = ""
        device_serial = ""
        start_time = ""
        end_time = ""
        device_name = ""

        session = Session(id)
        logs_dir = session.logs_dir
        status_log = open(os.path.join(logs_dir, STATUS_FILE), 'r')
        status_log_lines = status_log.readlines()

        #get start time and end time from status log
        first_line = status_log_lines[0]
        last_line = status_log_lines[len(status_log_lines) - 1]
        start_time = first_line.split(" - ")[0]
        end_time = last_line.split(" - ")[0]

        #get package name from status log
        for line in status_log_lines:
            description = "package name is "
            if description in line:
                package_name = line.split(" - ")[1][len(description):]

        #get device serial
        ini_description = "Initilizing device "
        device_serial = first_line.split(" - ")[1][len(ini_description):].replace("\n", "")

        #get device model name
        device_name = Device().model(device_serial)

        #get sample real file and calculate hash
        for file in os.listdir(session.apk_dir):
            if file.endswith(".apk"):
                sample_real_path = os.path.realpath(os.path.join(session.apk_dir, file))

                sample_md5 = hashlib.md5(sample_real_path).hexdigest()
                sample_sha1 = hashlib.sha1(sample_real_path).hexdigest()
                sample_sha256 = hashlib.sha256(sample_real_path).hexdigest()

                #get sample size
                statinfo = os.stat(sample_real_path)
                sample_size = statinfo.st_size


        general_info[DEVICE_SERIAL] = device_serial.replace("\n","")
        general_info[DEVICE_NAME] = device_name
        general_info[SAMPLE_SIZE] = sample_size
        general_info[SAMPLE_HASH][MD5] = sample_md5
        general_info[SAMPLE_HASH][SHA1] = sample_sha1
        general_info[SAMPLE_HASH][SHA256] = sample_sha256
        general_info[SESSION_ID] = id
        general_info[START_TIME] = start_time
        general_info[END_TIME] = end_time
        general_info[PACKAGE_NAME] = package_name.replace("\n", "")

        return general_info



if __name__ == '__main__':
    gi =general_information()
    print gi.run(id="202")










