from operator import attrgetter

__author__ = 'RongShun'


import os, sys

from lib.common.commands.adb import Adb
from lib.common.abstract import Monitor
from django import forms
from django.db import models
from django.forms import ModelForm
from os.path import join, isfile
from os import listdir


import logging
#logging.basicConfig(level=logging.DEBUG)
logs = logging.getLogger("yapsy")
from yapsy.IPlugin import IPlugin

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
        pass

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

    def baseline(self,):
        pass

    def getView(self):
        """
        get the django configuration form
        :return: django configuration form
        """
        return ConfigForm




class ConfigForm(forms.Form):
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

