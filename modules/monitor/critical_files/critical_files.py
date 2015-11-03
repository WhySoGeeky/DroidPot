from operator import attrgetter
import os, sys,ast
from lib.common.commands.adb import Adb
from lib.common.abstract import Monitor
from os.path import join, isfile
from os import listdir

from re import search,findall
import re

from yapsy.IPlugin import IPlugin

adb = Adb()
class critical_files(Monitor, IPlugin):
    def __init__(self):
        super(critical_files, self).__init__()
        self.compatible_device = []
        self.pre_md5 = "system_pre_md5_.txt"
        self.post_md5 = "system_post_md5_.txt"


    def prepare(self, params, session, device_serial):
        pass

    def preSession(self, params, module, session, device_serial):
        """
        Get the checksum of monitored files
        :param params:
        :param module:
        :param session:
        :param device_serial:
        :return:
        """
        MD5_LEN = 32
        log_dir = session.logs_dir

        md5_list = {}
        for param_name, init_file in params.iteritems():
            for each_file in init_file:
                get_md5_command = "md5 %s"%each_file
                result = adb.shell(get_md5_command, root=True, device_serial=device_serial)
                if result.std_output:
                    md5_list[each_file] = result.std_output[:MD5_LEN]

        print md5_list

        return md5_list




    def postSession(self, params, module, session, device_serial):
        MD5_LEN = 32
        log_dir = session.logs_dir

        md5_list = {}
        for param_name, init_file in params.iteritems():
            for each_file in init_file:
                get_md5_command = "md5 %s"%each_file
                result = adb.shell(get_md5_command, root=True, device_serial=device_serial)
                if result.std_output:
                    md5_list[each_file] = result.std_output[:MD5_LEN]

        print md5_list

        return md5_list



    def get_view(self):
        """
        get the django configuration form
        :return: django configuration form
        """
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from view_critical_files import ConfigForm
        sys.path.remove(os.path.dirname(os.path.abspath(__file__)))
        return ConfigForm




