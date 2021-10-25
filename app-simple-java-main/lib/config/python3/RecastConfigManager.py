import importlib
import logging
import os
import sys

import json

#sys.path.append('./lib/config/python3')

from ConfigFromJsonRemote import ConfigFromJsonRemote
from ConfigInfo import ConfigInfo, ConfigInfoList

from dotmap import DotMap

def main():
    # logging.basicConfig(filename='example.log', filemode='w', level=logging.DEBUG)
    logging.basicConfig(level='DEBUG')
    load_myproj_config()


# ----------------------------------------------
# ---- Config Server library's load_config: ----
# ----------------------------------------------
def load_myproj_config(config_server_host:str="127.0.0.1", config_server_port:str="3000") -> dict:

    cfg = DotMap()

    # ---------------------------------------------
    # ---- Docker:Host ----
    # ---------------------------------------------
    # DOCKER_HOST_IP=10.128.9.166
    # DOCKER_HOST_NAME=abdn-vm-166.openkbs.org
    cfg.docker.host.ip = os.getenv('DOCKER_HOST_IP', '127.0.0.1')
    cfg.docker.host.name = os.getenv('DOCKER_HOST_NAME', 'localhost')

    # ---------------------------------------------
    # ---- App:ConfigServer ----
    # ---------------------------------------------
    # JSON_CONFIG_SERVER_IP=10.128.9.166
    # JSON_CONFIG_SERVER_PORT=3000
    # JSON_CONFIG_SERVER_URL=http://abdn-vm-155.openkbs.org:3000/
    # JSON_CONFIG_OBJECT_UID=myproj_config_LOCAL_abdn-vm-166.openkbs.org
    cfg.json.config.server.ip = os.getenv('JSON_CONFIG_SERVER_IP', '10.128.9.155')
    cfg.json.config.server.port = os.getenv('JSON_CONFIG_SERVER_PORT', '3000')
    cfg.json.config.object.uid = os.getenv('JSON_CONFIG_OBJECT_UID', 'myproj_config_LOCAL_abdn-vm-166.openkbs.org')
    cfg.json.config.server.url = 'http://' + cfg.json.config.server.ip + ':' + cfg.json.config.server.port

    print("===== Docker & JSON Server Info: =====")
    app_json = json.dumps(cfg.toDict())
    print(app_json)

    print("===== Remote JSON Server: =====")
    config_info = ConfigInfo(remote_url=str(cfg.json.config.server.url),
                             config_object_uid=str(cfg.json.config.object.uid))
    json_config = ConfigFromJsonRemote.get_instance(config_info)

    print("===== join myprojapp_dict with json and docker nodes above: =====")
    myproj_map = DotMap(json_config.query("myprojapp"))
    myproj_map.update(cfg)

    # -- transfer json_config and cfg.docker & cfg.json to 'config': --
    config = DotMap(myproj_map)
    # app_json = json.dumps(config.toDict())
    # print(app_json)
    config.pprint(pformat='json')

    if 'url' not in config.responder:
        # "url": "http://abdn-vm-166.openkbs.org:5000/"
        config.responder.url = 'http://' + config.responder.host + ':' + str(config.responder.port)

    if 'url' not in config.myproj.fdna:
        #  "url": "http://abdn-vm-166.openkbs.org:8181/"
        config.fdna.url = 'http://' + config.responder.host + ':' + str(config.responder.port)

    config.pprint(pformat='json')
    print("config=====>" + str(config.toDict()))
    return config


def load_myproj_config_manager() -> object:
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
    #conf_list.append(config_yaml)
    conf_list.append(config_json)
    #conf_list.append(config_yaml_remote)
    conf_list.append(config_json_remote)

    # -----------------------------------------------------------------------------------------------------
    # -- Now, register all the above Config sources list into Facade Controller:                         --
    # -- Facade manager now control how to prioritize and access / evaluate the final value for a query: --
    # -----------------------------------------------------------------------------------------------------
    manager = myprojConfigManager.get_instance(conf_list)

    # ------------------------------------------------------------------------------------------------------------
    # -- Demo: read both JSON (priority=1) and YAML files and YAML files (priority=3) -- see above code lines:  --
    # -- Priority: YAML's value '10.128.9.166' will overwirte JSON's value 'abdn-vm-166.openkbs.org'              --
    # -- Results: Key/value: /myprojapp/kafka/host=10.128.9.166                                                 --
    # ------------------------------------------------------------------------------------------------------------
    path = "/myprojapp/kafka/host"
    value = manager.query(path)
    print("Key/value: {0}={1}".format(path, value))

    return manager


# ---------------------------
# -- Class: ConfigManaer
# -- Role : Facade Controller
# ---------------------------
class myprojConfigManager:
    # Class Attribute
    JSON_CONFIG_SERVER_URL_DEFAULT = 'http://abdn-vm-155.openkbs.org:3000/'
    JSON_CONFIG_OBJECT_UID_DEFAULT = 'myproj_config_LOCAL_abdn-vm-166.openkbs.org'

    __instance = None

    @staticmethod
    def get_instance(args: ConfigInfoList):
        """ Static access method. """
        if myprojConfigManager.__instance is None:
            myprojConfigManager.__instance = myprojConfigManager(args)
        return myprojConfigManager.__instance

    # Initializer / Instance Attributes
    def __init__(self, args: ConfigInfoList):

        """ Virtually private constructor. """
        if myprojConfigManager.__instance is None:
            myprojConfigManager.__instance = self
        else:
            return
        # -- List of ConfigAbstractClass w/ Children: ConfigFrom Env, Json, Yaml, etc.: --
        self.conf_instances = list()

        self.log = logging.getLogger('myprojConfigManager')
        self.log.info('creating an instance of myprojConfigManager')
        self.log.info("myprojConfigManager.__init__(): args of ConfigInfo=" + args.to_str())

        self.config_list = args

        self.config_list.config_items.sort(key=lambda x: x.priority)

        self.log.debug("type: " + type(args).__name__)
        for info in self.config_list.config_items:
            self.log.info("myprojConfigManager.__init__: --- creating singleton instance: \n" + info.to_str())
            try:
                config_instance = self.class_for_name(info.config_type, info.config_type).get_instance(info)
                self.conf_instances.append(config_instance)
                self.log.debug("My config_instance type: " + str(type(config_instance)))
            except Exception as e:
                self.log.error("myprojConfigManager: *** EXCEPTION: " + str(e))
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
