__author__ = 'RongShun'

import logging, json,os, ast
#logging.basicConfig(level=logging.INFO)
#logs = logging.getLogger("yapsy")
from yapsy.PluginManager import PluginManager
from lib.common.constant import MONITOR_MODULE_DIR, PROFILE_MODULE_DIR, SCRIPTED_PROFILE_INTERACTION, RANDOM_INTERACTION, PROCESSING_MODULE_DIR

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class ProcessingManager(object):
    def __init__(self):
        self.plugin_location = [PROCESSING_MODULE_DIR]
        self.pluginManager = PluginManager(plugin_info_ext="plugin")
        self.pluginManager.setPluginPlaces(self.plugin_location)
        self.pluginManager.collectPlugins()

    def modules_info(self):
        """
        Get information with regards to each modules loaded. It includes author,category, copyright, description,
        details, name, version and website.
        :return: information of all modules loaded
        """
        modules_info = {}
        for pluginInfo in self.pluginManager.getAllPlugins():
            modules_info[pluginInfo.name] = pluginInfo

        return modules_info

    def run(self,session_id):
        results = {}
        for plugInfo in self.pluginManager.getAllPlugins():
            result = plugInfo.plugin_object.run(session_id)
            #format int json
            result_json = json.dumps(result, sort_keys=True, indent=4)
            #save into session
            module_name = plugInfo.name

            results[module_name] = result_json

        return results


    def general_information(self, session_id):
        """
        Get general information of the session
        :param session_id:
        :return: dict
        """
        plugin = self.pluginManager.getPluginByName(name="general_information")
        result = plugin.plugin_object.run(session_id)

        return result




class ProfilesManager(object):

    def __init__(self):
        self.plugin_location = [PROFILE_MODULE_DIR]
        self.pluginManager = PluginManager(plugin_info_ext="plugin")

        self.pluginManager.setPluginPlaces(self.plugin_location)
        self.pluginManager.collectPlugins()

    def modules_info(self):
        """
        Get information with regards to each modules loaded. It includes author, category, copyright, description,
        details, name, version and website.
        :return: information of all modules loaded
        """
        modules_info = {}
        for pluginInfo in self.pluginManager.getAllPlugins():
            modules_info[pluginInfo.name] = pluginInfo

        return modules_info

    def configForms(self, device_serial, module_name=""):
        """
        Get the configuration views of each modules to be displayed on web interface
        :return: dictionary of pluginInfo as key and form as value
        """
        if module_name:
            plugin = self.pluginManager.getPluginByName(name=module_name)
            configForms = plugin.plugin_object.get_view()
        else:
            configForms = {}
            for pluginInfo in self.pluginManager.getAllPlugins():
                form = pluginInfo.plugin_object.get_view()
                configForms[pluginInfo] = form

        return configForms

    def run_simulation(self,option, profile_name, duration, device_serial, package_name, session):
        """
        Run profile simulation script
        :return:
        """
        plugin = self.pluginManager.getPluginByName(name=profile_name)
        if option == RANDOM_INTERACTION:
            plugin.plugin_object.runSimulation(duration,package_name, random=True, device_serial=device_serial, session=session)
        elif option == SCRIPTED_PROFILE_INTERACTION:
            plugin.plugin_object.runSimulation(duration,package_name, random=False, device_serial=device_serial, session=session)



    def setup_device(self,module, params, device_serial):
        """
        install profile apk and profile app data onto device
        :return:
        """
        pluginInfo = self.pluginManager.getPluginByName(name=module)
        if pluginInfo.name == module:
            pluginInfo.plugin_object.prepare(params, device_serial)

        return True


class MonitorsManager(object):

    def __init__(self):
        self.plugin_location = [MONITOR_MODULE_DIR]
        self.pluginManager = PluginManager(plugin_info_ext="plugin")

        self.pluginManager.setPluginPlaces(self.plugin_location)
        self.pluginManager.collectPlugins()


    def configForms(self, device_serial, module_name=""):
        """
        Get the configuration views of each modules to be displayed on web interface
        :return: dictionary of pluginInfo as key and form as value
        """
        if module_name:
            plugin = self.pluginManager.getPluginByName(name=module_name)
            configForms = plugin.plugin_object.get_view()
        else:
            configForms = {}
            for pluginInfo in self.pluginManager.getAllPlugins():
                form = pluginInfo.plugin_object.get_view()
                configForms[pluginInfo] = form


        return configForms

    def prepare(self, modules, session, device_serial):
        """
        Initilizing the partition on android device according to the required settings of monitoring modules
        :param modules: module's configuration setting from user
        :param session: current session object
        :return: is successful
        """

        for module_name, params in modules.iteritems():
            #logs.debug("module name: %s" % module_name)
            #logs.debug("module parameters: %s" % modules[module_name].__str__())
            print module_name
            if params["module_type"] == "monitor":
                plugin = self.pluginManager.getPluginByName(name=module_name)
                plugin.plugin_object.prepare(params=modules[module_name], session=session, device_serial=device_serial)

        return True

    def count_modules(self):
        count = 0
        for pluginInfo in self.pluginManager.getAllPlugins():
            #logs.info("Module %s loaded"% pluginInfo.name)
            count +=1

        return count

    def modules_info(self, module_name=""):
        """
        Get information with regards to each modules loaded. It includes author, category, copyright, description,
        details, name, version and website.
        :return: information of all modules loaded
        """
        modules_info = {}
        if module_name:
            plugin = self.pluginManager.getPluginByName(name=module_name)
            modules_info[plugin.name]= plugin
        else:
            for pluginInfo in self.pluginManager.getAllPlugins():
                modules_info[pluginInfo.name] = pluginInfo

        return modules_info

    def preSession(self, module, params, session, device_serial):
        """
        Get the baseline of device that is required by the specific monitoring module
        :param module:
        :param params:
        :return:
        """
        plugin = self.pluginManager.getPluginByName(name=module)
        params.pop("module_type")
        return plugin.plugin_object.preSession(params=params, module=module, session=session, device_serial=device_serial)

    def postSession(self, module, params, session, device_serial):
        """
        Get the post device monitor session's information that is required by the specific monitoring module
        :param module:
        :param params:
        :return:
        """
        plugin = self.pluginManager.getPluginByName(name=module)
        params.pop("module_type")
        return plugin.plugin_object.postSession(params=params, module=module, session=session, device_serial=device_serial)



    def daemons(self, module, params):
        """
        Get the daemon's path of module
        :return: dictionary with key as daemon name and daemon's path as value.
        """
        daemons = {}
        for pluginInfo in self.pluginManager.getAllPlugins():
            if pluginInfo.name == module:

                daemons_path = pluginInfo.plugin_object.daemons(module,False)
                daemons[pluginInfo.name] = daemons_path
            # module name : daemons path
        #logs.debug(daemons)
        return daemons

    '''
    def run(self):
        global pluginManager

        pluginManager.setPluginPlaces(self.pluginLocation)
        pluginManager.collectPlugins()

        for pluginInfo in pluginManager.getAllPlugins():
            self.__registerModules(pluginInfo.name)
            pluginManager.activatePluginByName(pluginInfo.name)
            print pluginInfo.is_activated
            #to do something
            #pluginInfo.plugin_object.[method name]

        global monitorModName
        print monitorModName

    def __registerModules(self, moduleName):
        print moduleName
        global monitorModName
        monitorModName.append(moduleName)

        '''

'''
if __name__ == "__main__":
    mm = MonitorsManager()
'''

