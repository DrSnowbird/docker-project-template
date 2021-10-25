import importlib
import logging
import os
import re
import sys
import types

import requests
import json
import objectpath

# -----------
# -- Tests --
# -----------
import ConfigAbstractClass
import ConfigFromJson
from ConfigInfo import ConfigInfo, ConfigInfoList


def main():
    # logging.basicConfig(filename='example.log', filemode='w', level=logging.DEBUG)
    logging.basicConfig(level='DEBUG')

    # ------------------------------------------------------------------------------------------------------------
    # -- "priority" is used to determine which has the highest priority in overwriting other config sources:    --
    # -- priority=9 (if the rest is 1, 3, 5, 7, then this has the final control of the key's value if not None) --
    # ------------------------------------------------------------------------------------------------------------

    # ----------------
    # -- priority=9 --
    # ----------------
    config_env = ConfigInfo(config_type='ConfigFromEnv', priority=9)

    # ----------------
    # -- priority=7 --
    # ----------------
    config_yaml_remote = ConfigInfo(config_type='ConfigFromYamlRemote',
                                    remote_url='http://abdn-vm-166:18080/jetty_base/yaml',
                                    config_object_uid='myproj_config_LOCAL_abdn-vm-166.openkbs.org.yaml',
                                    priority=7)
    # ----------------
    # -- priority=5 --
    # ----------------
    config_json_remote = ConfigInfo(config_type='ConfigFromRemote',
                                    remote_url='http://abdn-vm-155.openkbs.org:3000/',
                                    config_object_uid='myproj_config_LOCAL_abdn-vm-166.openkbs.org',
                                    priority=5)
    # ----------------
    # -- priority=3 --
    # ----------------
    config_yaml = ConfigInfo(config_type='ConfigFromYaml', file_path='data/yaml-test-data.yaml', priority=3)

    # ----------------
    # -- priority=1 (the lowest compared to the above sources).
    # ----------------
    config_json = ConfigInfo(config_type='ConfigFromJson', file_path='data/json-test-data.json', priority=1)

    # ---------------------------------------------------------------------------------------------
    # -- Now, register all the above Config sources into a list for Facade Controller to manage: --
    # -- To test all the above, uncomment the comment symbols below.                             --
    # ---------------------------------------------------------------------------------------------
    conf_list = ConfigInfoList()
    conf_list.append(config_env)
    conf_list.append(config_json)
    conf_list.append(config_yaml)
    conf_list.append(config_json_remote)
    conf_list.append(config_yaml_remote)

    # -----------------------------------------------------------------------------------------------------
    # -- Now, register all the above Config sources list into Facade Controller:                         --
    # -- Facade manager now control how to prioritize and access / evaluate the final value for a query: --
    # -----------------------------------------------------------------------------------------------------
    manager = ConfigManager.get_instance(conf_list)

    # ------------------------------------------------------------------------------------------------------------
    # -- Demo: read both JSON (priority=1) and YAML files and YAML files (priority=3) -- see above code lines:  --
    # -- Priority: YAML's value '10.128.9.166' will overwirte JSON's value 'abdn-vm-166.openkbs.org'              --
    # -- Results: Key/value: /myprojapp/kafka/host=10.128.9.166                                                 --
    # ------------------------------------------------------------------------------------------------------------
    path = "/myprojapp/kafka/host"
    value = manager.query(path)
    print("Key/value: {0}={1}".format(path, value))


# ---------------------------
# -- Class: ConfigManaer
# -- Role : Facade Controller
# ---------------------------
class ConfigManager:
    # Class Attribute
    JSON_CONFIG_SERVER_URL_DEFAULT = 'http://abdn-vm-155.openkbs.org:3000/'
    JSON_CONFIG_OBJECT_UID_DEFAULT = 'myproj_config_LOCAL_abdn-vm-166.openkbs.org'

    __instance = None

    @staticmethod
    def get_instance(args: ConfigInfoList):
        """ Static access method. """
        if ConfigManager.__instance is None:
            ConfigManager.__instance = ConfigManager(args)
        return ConfigManager.__instance

    # Initializer / Instance Attributes
    def __init__(self, args: ConfigInfoList):

        """ Virtually private constructor. """
        if ConfigManager.__instance is None:
            ConfigManager.__instance = self
        else:
            return
        # -- List of ConfigAbstractClass w/ Children: ConfigFrom Env, Json, Yaml, etc.: --
        self.conf_instances = list()

        self.log = logging.getLogger('ConfigManager')
        self.log.info('creating an instance of ConfigManager')
        self.log.info("ConfigManager.__init__(): args of ConfigInfo=" + args.to_str())

        self.config_list = args

        self.config_list.config_items.sort(key=lambda x: x.priority)

        self.log.debug("type: " + type(args).__name__)
        for info in self.config_list.config_items:
            self.log.info("ConfigManager.__init__: --- creating singleton instance: \n" + info.to_str())
            try:
                config_instance = self.class_for_name(info.config_type, info.config_type).get_instance(info)
                self.conf_instances.append(config_instance)
                self.log.debug("My config_instance type: " + str(type(config_instance)))
            except Exception as e:
                self.log.error("ConfigManager: *** EXCEPTION: " + str(e))
                self.log.error('*** ERROR: failed to create Class for type:' + info.config_type)

    # -- Use: loaded_class = class_for_name('foo.bar', 'Baz')
    def class_for_name(self, module_name, class_name):
        # load the module, will raise ImportError if module cannot be loaded
        m = importlib.import_module(module_name)
        # get the class, will raise AttributeError if class cannot be found
        c = getattr(m, class_name)
        return c

    def setupConfigClasses(self):
        self.class_dict = dict()
        class_list = ['ConfigFromEnv', 'ConfigFromJson', 'ConfigFromRemote', 'ConfigFromYaml', 'ConfigFromYamlPath',
                      'ConfigFromYamlRemote']

    def is_connected(self) -> bool:
        return self.connected

    # -------------------
    # -- Query by Path --
    # -------------------
    def query(self, path) -> object:
        if path:
            final_value = None
            for c in self.conf_instances:
                tmp_value = c.query(path)
                if tmp_value:
                    final_value = tmp_value
            return final_value
        else:
            return None

    # --------------------------------------
    # -- Query with default_value by Path --
    # --------------------------------------
    def query_with_default(self, path, default_value) -> object:
        result = self.query(path)
        if result is None:
            return default_value
        else:
            return result


# -----------
# -- main --
# -----------
if __name__ == "__main__":
    # execute only if run as a script
    main()
