import importlib
import logging
import os
import re
import sys
import types

import requests
import json
import objectpath

sys.path.insert(0,'../../lib/config/python3')
print(sys.path)

# -----------
# -- Tests --
# -----------
from ConfigAbstractClass import ConfigAbstractClass
from ConfigFromRemote import ConfigFromRemote
from ConfigInfo import ConfigInfo, ConfigInfoList
from ConfigManager import ConfigManager

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

def main_facade():
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

# -----------
# -- main --
# -----------
if __name__ == "__main__":
    # execute only if run as a script
    main()
