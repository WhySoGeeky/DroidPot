

from yapsy.IPlugin import IPlugin
import os, ConfigParser, time,sys, hashlib, ast

sys.path.append(os.getcwd())
BASE_DIR = os.getcwd()

from lib.common.commands.adb import Adb
from lib.common.abstract import Processing
from lib.core.managers.session import Session
from lib.common.device import Device

class critical_variable(IPlugin, Processing):
    def __init__(self):
        self.adb = Adb()
        super(critical_variable, self).__init__()

    def run(self, id):
        CRITICAL_VARIABLE_PRE = "critical_variable_monitor.pre.cap"
        CRITICAL_VARIABLE_POST = "critical_variable_monitor.post.cap"
        PROPERTY_INDEX = 0
        PROPERTY_VALUE_INDEX = 1

        pre_dict = {}
        post_dict = {}

        result = {}

        session = Session(id)
        logs_dir = session.logs_dir

        try:
            system_prop_pre_log = open(os.path.join(logs_dir, CRITICAL_VARIABLE_PRE), 'r')
            system_prop_post_log = open(os.path.join(logs_dir, CRITICAL_VARIABLE_POST), 'r')
            pre_content = system_prop_pre_log.readlines()
            post_content = system_prop_post_log.readlines()

            pre_dict = ast.literal_eval(pre_content[0])
            post_dict = ast.literal_eval(post_content[0])

            for variable, value in post_dict.iteritems():
                if pre_dict.has_key(variable):
                    if pre_dict[variable] != value:
                        result[variable] = "%s  ===>   %s"%(pre_dict[variable][0],value[0])


            return result
        except Exception as e:
            return {}




