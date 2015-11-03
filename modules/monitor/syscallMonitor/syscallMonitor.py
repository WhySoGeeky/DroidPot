from operator import attrgetter

__author__ = 'RongShun'


import os, sys
#BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), "..", "..", ".."))
#sys.path.append(BASE_DIR)

from lib.common.commands.adb import Adb
from lib.common.abstract import Monitor
from django import forms
from django.db import models
from django.forms import ModelForm
from os.path import join, isfile
from os import listdir

from re import search,findall
import re


import logging
#logging.basicConfig(level=logging.DEBUG)
logs = logging.getLogger("yapsy")
from yapsy.IPlugin import IPlugin

'''
class syscallMonitor(IPlugin):
    def getCompatibleDevices(self):
        """
        get the compatible list of devices that works with this module
        :return: list of compatible device
        """
        print "specific function to be called by plugin manager"

    def activate(self):
        print "called when plugin is activated"
        self.is_activated = True

    def deactivate(self):
        print "called when plugin is deactivated"
        self.is_activated = False
'''

class SyscallMonitor(Monitor, IPlugin):
    def __init__(self):
        super(SyscallMonitor, self).__init__()
        self.compatible_device = []

    def init_partition(self, params, session):
        """
        Configuration required to be place in ramdisk
        :param params: configuration chosen by user
        :param session: current session object
        :return: is successful or not
        """
        ramdisk_dir = session.ramdisk_dir

        init_file = open(join(ramdisk_dir, "init.rc"), 'a')
        init_file.write("#this is another test message")
        logs.info("[*] init.rc file appended")

        '''
        for specific proc name that you wan to monitor. grep the pid from proc name then strace that pid
        it will be placed inside the init.rc
        '''

        return True

    def daemons(self, compile=False):
        """
        get the daemons path in module
        :param session: session object
        :param compile: if daemon requires cross compilation from source
        :return:
        """
        daemons = []
        daemon_dir = join(os.path.dirname(os.path.realpath(__file__)), "daemons")

        for file_name in listdir(daemon_dir):
            dir_file_path = join(daemon_dir, file_name)
            if isfile(dir_file_path):
                daemons.append(dir_file_path)

        return daemons

    def getView(self):
        """
        get the django configuration form
        :return: django configuration form
        """
        return ConfigForm




class ConfigForm(forms.Form):
    '''
    adb = adb()
    parameter = "ps"
    processes = adb.shell(parameter).std_output

    processes_choice = []
    pids = []
    process_names = []

    for process in processes:
        match = search(r"\d{1,}", process)

        if match:
            pids.append(match.group())


    regex = re.compile("\S{1,}$")
    for process in processes:
        process = process.rstrip("\r")
        match = regex.findall(process)
        #print match
        if match:
            process_names.append(match)

    #relation_tuple = (process_pid, process)
    relation_tuple = ("weee", "wwwssss")

    #processes_choice = (("1", "wwwssss"), ("2", "22222"))
    '''
    user_space_services_choice = (
        ('netd', 'netd'),
        ('mediaserver', 'mediaserver'),
        ('dbus-daemon', 'dbus-daemon'),
        ('installd', 'installd'),
        ('drmserver', 'drmserver'),
        ('serviceman-ager', 'serviceman-ager'),
        ('surface-flinger', 'surface-flinger'),
        ('ueventd', 'ueventd')
    )

    processes_field = forms.MultipleChoiceField(widget=forms.SelectMultiple, choices=user_space_services_choice, required=True)
    PID = forms.CharField(max_length=1000, help_text="PID of process to be monitored.")




if __name__ == "__main__":
    mm = SyscallMonitor()


