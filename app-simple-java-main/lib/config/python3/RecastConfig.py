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

    # ------------------------------------------------------------------------------------------------------------
    # -- 1.) Copy the following two statements to any Python module needs to access Config Server (JSON/YAML):  --
    # -- 2.) Then, use "Unix-path" syntax to "QUERY" the JSON/YAML Tree Path's Value.                           --
    # -- 3.) Or, you can use "Python Dictionary-style" to traverse the Tree path to access the value(s)         --
    # ------------------------------------------------------------------------------------------------------------
    config_json_remote = ConfigInfo(config_type='ConfigFromRemote',
                                    remote_url='http://abdn-vm-155.openkbs.org:3000/',
                                    config_object_uid='myproj_config_LOCAL_abdn-vm-166.openkbs.org',
                                    priority=5)
    myproj_config = myprojConfig.get_instance(config_json_remote, "")

    # -----------------------------------------
    # -- Examples: QUERY in Unix-path syntax --
    # -----------------------------------------
    path = "/myprojapp/kafka/host"
    value = myproj_config.query(path)
    print("Key/value: {0}={1}".format(path, value))

    # ------------------------------------------------------
    # -- Examples: QUERY with DEFAULT in Unix-path syntax --
    # ------------------------------------------------------
    new_path="/undefined/remote_url"
    new_value = myproj_config.query_with_default(new_path, "http://some_remote_url:30000/")
    print("Key/value: {0}={1}".format(new_path, new_value))

    # ------------------------------------------------------------------
    # -- Direct Access dict object instead of myprojConfig wrapper:   --
    # -- Use 'dict' syntax to access the tree path value              --
    # ------------------------------------------------------------------
    config = myproj_config.get_config()
    value = config['myprojapp']['kafka']['port']
    print("Key/value: {0}={1}".format(path, value))


# -------------------------------------------------------------------------------------------------------
# -- Facade Manager to load different Config object types using ConfigInfoList (array of ConfigInfo)   --
# -- And, use 'priority' to order the search precedence among the list of Config Objects               --
# -- Since the 'dict' (braket-style) syntax can not be used since multiple underlying objects used     --
# -- Only the 'query' function with "Unix-path" syntax for accessing tree path is allowed.             --
# -------------------------------------------------------------------------------------------------------
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
    # -- Facade myproj_config now control how to prioritize and access / evaluate the final value for a query: --
    # -----------------------------------------------------------------------------------------------------
    myproj_config = myprojConfig.get_instance(conf_list)

    # ------------------------------------------------------------------------------------------------------------
    # -- Demo: read both JSON (priority=1) and YAML files and YAML files (priority=3) -- see above code lines:  --
    # -- Priority: YAML's value '10.128.9.166' will overwirte JSON's value 'abdn-vm-166.openkbs.org'              --
    # -- Results: Key/value: /myprojapp/kafka/host=10.128.9.166                                                 --
    # ------------------------------------------------------------------------------------------------------------
    path = "/myprojapp/kafka/host"
    value = myproj_config.query(path)
    print("Key/value: {0}={1}".format(path, value))

    return myproj_config


# -------------------------------------------------------------
# -- Class: ConfigManaer                                     --
# -- Role : Wrapper with 'myproj' initialization parameters  --
# -------------------------------------------------------------
class myprojConfig:
    # Class Attribute
    JSON_CONFIG_SERVER_URL_DEFAULT = 'http://abdn-vm-155.openkbs.org:3000/'
    JSON_CONFIG_OBJECT_UID_DEFAULT = 'myproj_config_LOCAL_abdn-vm-166.openkbs.org'

    # -- data type hints: --
    config_info = ConfigInfo
    json_config = ConfigFromJsonRemote
    config = dict

    # -- static instance object: --
    __instance = None

    @staticmethod
    def get_instance(args: ConfigInfo=None, root_path: str = "myprojapp"):
        """ Static access method. """
        if myprojConfig.__instance is None:
            myprojConfig.__instance = myprojConfig(args, root_path)
        return myprojConfig.__instance

    # Initializer / Instance Attributes
    def __init__(self, args: ConfigInfo, root_path: str = "myprojapp"):

        self.log = logging.getLogger('myprojConfig')
        self.log.info('creating an instance of myprojConfig')
        self.root_path=root_path

        """ Virtually private constructor. """
        if myprojConfig.__instance is None:
            myprojConfig.__instance = self
        else:
            self.log.error('creating an instance of myprojConfig')
            raise Exception("Failed to get instance mostly due to connection failure!")

        # -- Initialize the config contents using remote config server object: --
        self.config = None
        self.json_config = None
        self.config_info = args
        self.config = self.load_myproj_config(self.config_info, self.root_path)

    # ----------------------------------------------
    # ---- Get the config dict object: ----
    # ----------------------------------------------
    def get_config(self) -> dict:
        return self.config.toDict()

    # ----------------------------------------------
    # ---- Get the ConfigFromJsonRemote object: ----
    # ----------------------------------------------
    def get_json_config(self) -> ConfigFromJsonRemote:
        return self.json_config


    # ----------------------------------------------
    # ---- Config Server library's load_config: ----
    # ---- (Default root_path="myprojapp" )     ----
    # ----------------------------------------------
    def load_myproj_config(self, args: ConfigInfo=None, root_path: str = "myprojapp") -> dict:

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
        cfg.json.config.server.ip = os.getenv('JSON_CONFIG_SERVER_IP', "10.128.9.166")
        cfg.json.config.server.port = os.getenv('JSON_CONFIG_SERVER_PORT', '3000')
        cfg.json.config.object.uid = os.getenv('JSON_CONFIG_OBJECT_UID', 'myproj_config_LOCAL_abdn-vm-166.openkbs.org')
        cfg.json.config.server.url = os.getenv('JSON_CONFIG_SERVER_URL', 'http://' + cfg.json.config.server.ip + ':' + cfg.json.config.server.port)

        print("===== Docker & JSON Server Info: =====")
        app_json = json.dumps(cfg.toDict())
        print(app_json)

        print("===== Remote JSON Server: =====")
        tmp_config_info=None
        if args:
            # Use the given config_info
            tmp_config_info = args
        else:
            tmp_config_info = ConfigInfo(remote_url=str(cfg.json.config.server.url),
                                 config_object_uid=str(cfg.json.config.object.uid))

        # -- Get Singleton instance: --
        self.json_config = ConfigFromJsonRemote.get_instance(tmp_config_info)
        if self.json_config:
            self.connected = True
        else:
            self.log.error("load_myproj_config(): FAIL: Can't get instance:")
            return None


        print("===== join myprojapp_dict with json and docker nodes above: =====")
        myproj_map = DotMap(self.json_config.query(root_path))
        myproj_map.update(cfg)

        # -- transfer json_config and cfg.docker & cfg.json to 'config': --
        self.config = DotMap(myproj_map)
        # app_json = json.dumps(config.toDict())
        # print(app_json)
        self.config.pprint(pformat='json')

        # -- Setup additional Responder: --
        if self.config_info:
            if 'url' not in self.config.responder:
                # "url": "http://abdn-vm-166.openkbs.org:5000/"
                responder_host = self.json_config.query_with_default("responder.host", "abdn-vm-166.openkbs.org");
                responder_port = self.json_config.query_with_default("responder.port", "5000");
                self.config.responder.url = 'http://' + responder_host + ':' + str(responder_port)

            # -- Setup additional FDNA: --
            if 'url' not in self.config.myproj.fdna:
                #  "url": "http://abdn-vm-166.openkbs.org:8181/"
                fdna_host = self.json_config.query_with_default("fdna.host", "abdn-vm-166.openkbs.org");
                fdna_port = self.json_config.query_with_default("fdna.port", "8181");
                self.config.fdna.url = 'http://' + fdna_host + ':' + str(fdna_port)

        self.config.pprint(pformat='json')
        self.log.debug("config=====>" + str(self.config.toDict()))
        return self.config

    def is_connected(self) -> bool:
        return self.json_config

    # -------------------
    # -- Query by Path --
    # -------------------
    def query(self, path) -> object:
        if self.json_config:
            return self.json_config.query(path)
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
