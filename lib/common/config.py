import os
from ConfigParser import ConfigParser

CONFIGURING = "configuring"
INITILIZING = "initilizing"
RUNNING = "running"
COMPLETE = "complete"

class Session(object):
    def __init__(self,):
        self.ini_path = str

    def create(self, session_dir, device_serial):
        self.ini_path = os.path.join(session_dir, "session.ini")

        ini_file = open(self.ini_path, 'w')
        settings = ConfigParser()
        settings.add_section('General')
        settings.set(section="General", option="status", value=CONFIGURING)
        settings.set(section="General", option="device", value=device_serial)
        settings.write(ini_file)
        ini_file.close()



    def status(self, session_dir=""):

        if session_dir:
            config = _read_config(os.path.join(session_dir, 'session.ini'))
        else:
            config = _read_config(self.ini_path)

        status = config.get("General", "status")
        return status

    def get_device_serial(self, session_dir=""):
        if session_dir:
            config = _read_config(os.path.join(session_dir, 'session.ini'))
        else:
            config = _read_config(self.ini_path)

        device_serial = config.get("General", "device")
        return device_serial


def _read_config(config_path):
    config = ConfigParser()
    config.read(config_path)

    return config

