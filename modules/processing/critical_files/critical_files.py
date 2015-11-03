

from yapsy.IPlugin import IPlugin
import os, ConfigParser, time,sys, hashlib, ast

sys.path.append(os.getcwd())
BASE_DIR = os.getcwd()

from lib.common.commands.adb import Adb
from lib.common.abstract import Processing
from lib.core.managers.session import Session
from lib.common.device import Device

class critical_files(IPlugin, Processing):
    def __init__(self):
        self.adb = Adb()
        super(critical_files, self).__init__()

    def run(self, id):

        SYSTEM_PROPERTIES_PRE = "critical_files_monitor.pre.cap"
        SYSTEM_PROPERTIES_POST = "critical_files_monitor.post.cap"
        PROPERTY_INDEX = 0
        PROPERTY_VALUE_INDEX = 1

        post_dict = {}
        pre_dict = {}

        result = {}

        session = Session(id)
        logs_dir = session.logs_dir


        system_prop_pre_log = open(os.path.join(logs_dir, SYSTEM_PROPERTIES_PRE), 'r')
        system_prop_post_log = open(os.path.join(logs_dir, SYSTEM_PROPERTIES_POST), 'r')
        pre_content = system_prop_pre_log.readlines()
        post_content = system_prop_post_log.readlines()

        pre_dict = ast.literal_eval(pre_content[0])
        post_dict = ast.literal_eval(post_content[0])


        #compare
        for prop_key, prop_value in post_dict.iteritems():
            if pre_dict.has_key(prop_key):
                if prop_value != pre_dict[prop_key]:
                    result[prop_key] = "%s ===> %s"%(pre_dict[prop_key][0].split(" ")[0], prop_value[0].split(" ")[0])
            else:
                pass

        return result







