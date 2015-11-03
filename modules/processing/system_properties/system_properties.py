

from yapsy.IPlugin import IPlugin
import os, ConfigParser, time,sys, hashlib, ast

sys.path.append(os.getcwd())
BASE_DIR = os.getcwd()

from lib.common.commands.adb import Adb
from lib.common.abstract import Processing
from lib.core.managers.session import Session
from lib.common.device import Device

class system_properties(IPlugin, Processing):
    def __init__(self):
        self.adb = Adb()
        super(system_properties, self).__init__()

    def run(self, id):
        """
        compare system properties before session and after session
        :param id:
        :return: difference in dict {system_prop_name: [pre_value,post_value]}
        """

        SYSTEM_PROPERTIES_PRE = "system_properties_monitor.pre.cap"
        SYSTEM_PROPERTIES_POST = "system_properties_monitor.post.cap"
        PROPERTY_INDEX = 0
        PROPERTY_VALUE_INDEX = 1

        post_dict = {}
        pre_dict = {}

        result = {}

        session = Session(id)
        logs_dir = session.logs_dir

        try:
            system_prop_pre_log = open(os.path.join(logs_dir, SYSTEM_PROPERTIES_PRE), 'r')
            system_prop_post_log = open(os.path.join(logs_dir, SYSTEM_PROPERTIES_POST), 'r')
            pre_content = system_prop_pre_log.readlines()
            post_content = system_prop_post_log.readlines()

            pre_list = ast.literal_eval(pre_content[0])
            post_list = ast.literal_eval(post_content[0])

            #convert into proper dict
            for each_entry in post_list:
                splitted_entry = each_entry.replace("[","").replace("]","").split(": ")
                post_dict[splitted_entry[PROPERTY_INDEX]] = splitted_entry[PROPERTY_VALUE_INDEX]

            for each_entry in pre_list:
                splitted_entry = each_entry.replace("[","").replace("]","").split(": ")
                post_dict[splitted_entry[PROPERTY_INDEX]] = splitted_entry[PROPERTY_VALUE_INDEX]

            #compare
            for prop_key, prop_value in post_list.iteritems():
                if pre_dict.has_key(prop_key):
                    if prop_value != pre_dict[prop_key]:
                        result[prop_key] = "%s ===> %s"%(pre_dict[prop_key][0], prop_value[0])
                else:
                    pass

            return result


        except Exception as e:
            return {}




