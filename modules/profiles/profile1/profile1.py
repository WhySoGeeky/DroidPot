

from yapsy.IPlugin import IPlugin
from django import forms
import os, shutil, ConfigParser, time,sys

sys.path.append(os.getcwd())
BASE_DIR = os.getcwd()

from multiprocessing import Process
from lib.common.commands.adb import Adb
from lib.common.constant import SCRIPTED_PROFILE_INTERACTION, RANDOM_INTERACTION
from lib.common.abstract import Profile
from lib.core.managers.session import Session
import xml.etree.ElementTree as ET
import hashlib

import logging
class profile1(IPlugin, Profile):
    """
    profile works on xiaomi red mi 4G
    """
    def __init__(self):
        self.adb = Adb()
        super(profile1, self).__init__()

    def runSimulation(self, duration,package_name, random, device_serial, session):
        from uiautomator import device as d                                 #possible bug
        #initilize status logging
        self.event_log = logging.getLogger('start_status')
        self.event_log.setLevel(logging.DEBUG)
        START_LOG = os.path.join(session.logs_dir, "interaction.log")
        ih = logging.FileHandler(START_LOG)
        ih.setLevel(logging.ERROR)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        ih.setFormatter(formatter)
        self.event_log.addHandler(ih)
        #try:

        d.screen.on()

        adb = Adb()
        start_package_command = "monkey -p %s -c android.intent.category.LAUNCHER 1"%package_name
        adb.shell(start_package_command, device_serial=device_serial)
        self.event_log.info("Started %s"%package_name)
        time.sleep(10)

        #check screen now has the same package name
        visited_screen = []
        screen_widgets = d.dump()
        root = ET.fromstring(screen_widgets)

        #DFS trigger
        self.dfs_trigger(current_screen=root, duration=duration, package_name=package_name, device_serial=device_serial, visited_screen=visited_screen)
        #except Exception as e:
            #self.event_log.info("ERROR in simulation")

    def dfs_trigger(self,current_screen, duration, package_name, device_serial, visited_screen):
        from uiautomator import device as d
        if current_screen == {}:
            #print "reach end of the world"
            d.press.back()
            self.event_log.info("back")
            return True

        for child in current_screen.iter('node'):
            node_dict = child.attrib
            m = hashlib.md5()
            m.update(node_dict.__str__())
            md5 = m.digest()

            if not visited_screen.__contains__(md5):
                visited_screen.append(md5)
                #press device to go to next screen
                if node_dict["long-clickable"] == True:
                    d(text=node_dict["text"], className=node_dict["class"]).long_click()
                    self.event_log.info("long click: %s"%node_dict)
                else:
                    d(text=node_dict["text"], className=node_dict["class"]).click()
                    self.event_log.info("short click: %s"%node_dict)

                screen_widgets = d.dump()
                subScreen = ET.fromstring(screen_widgets)
                return self.dfs_trigger(current_screen=subScreen, duration=duration, package_name=package_name, device_serial=device_serial, visited_screen=visited_screen)

        #print "child screens visited!"
        d.press.back()
        #self.event_log.info("back")
        return True




    def prepare(self, params, device_serial):
        """
        Prepare device by installing profile's apk and apk databases
        :return:
        """
        #NOTE: modified uiautomator's /usr/local/lib/python2.7/dist-packages/uiautomator/__init__.py line 470
        #to prevent library insisting on installing uiautomator without root

        #install apks for profile
        apks_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "apk")
        self.adb.wait_for_device(device_serial)
        apks = os.listdir(apks_dir)
        for apk in apks:
            apk_path = os.path.join(apks_dir, apk)
            if os.path.isfile(apk_path):
                #logs.info("Installing apk %s" %(apk_path))
                apk_realpath = os.path.realpath(apk_path)
                self.adb.push(source=apk_realpath, dest="/sdcard/tmp.apk", device_serial=device_serial)
                self.adb.shell("pm install -rt /sdcard/tmp.apk", root=True, device_serial=device_serial)
                self.adb.shell("rm -f /sdcard/tmp.apk", root=True, device_serial=device_serial)



        #copy app data to respective directory in device
        app_data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_data", "app_data.ini")
        app_data_ini = ConfigParser.ConfigParser()
        app_data_ini.read(app_data_path)

        for app_file in app_data_ini.sections():
            #logs.info("copying %s"%file)
            app_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_data", app_file)
            temp_device_path = os.path.join("data", "local", "tmp", app_file)
            self.adb.push(source=app_file_path, dest=temp_device_path, device_serial=device_serial)

            for key, value in app_data_ini.items(app_file):
                if key == "filePermission":
                    chown_command = "chown %s %s"%(value, temp_device_path)
                    self.adb.shell(root=True, command=chown_command, device_serial=device_serial)
                if key == "devicePath":
                    actual_device_path = value
                    mv_command = "mv %s %s"%(temp_device_path, actual_device_path)
                    self.adb.shell(root=True, command=mv_command, device_serial=device_serial)


        return True

    def get_view(self):
        """
        get the django configuration form.
        If you don't know what to do with this method, DON'T CHANGE ANYTHING
        :return: django configuration form
        """
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from view_profile1 import ConfigForm
        sys.path.remove(os.path.dirname(os.path.abspath(__file__)))
        return ConfigForm


if __name__ == "__main__":
    session = Session(160)
    st = profile1()
    #st.runSimulation(duration=30,package_name="com.systemsecurity6.gms", random=False, device_serial="d54d8e8f", session=session)
    st.runSimulation(duration=30,package_name="com.slideme.sam.manager", random=False, device_serial="d54d8e8f", session=session)
