# openkbs Confidential
# NOTICE
# This software was produced for the U. S. Government under Basic Contract No. W15P7T-13-C-A802,
# and is subject to the Rights in Noncommercial Computer Software and Noncommercial Computer
# Software and Noncommercial Computer Software Documentation Clause 252.227-7014 (FEB 2012)
# © 2020 The openkbs Corporation.
import logging
import re

import yaml
from yamlpath.exceptions import YAMLPathException

import UtilityConversion
from ConfigAbstractClass import ConfigAbstractClass
from ConfigInfo import ConfigInfo

module_logger = logging.getLogger('ConfigFromYaml')


# -----------
# -- Tests --
# -----------
def main():

    logging.basicConfig(level='DEBUG')

    #  Singleton.getInstance()

    if False:
        # -- test Save to file --
        config = ConfigFromYaml.get_instance('./simple.yaml')
        print(config.query('hash.child_attr.key'))
        # -- set new key & value
        config.set_value("hash.new_path2.key2", "new_value_2")
        print(config.query('hash.new_path2.key2'))
        config.save("simple_2.yaml")

    # ----------------------------------------------------------------------------
    # -- Setup Connection:
    # ----------------------------------------------------------------------------
    config_info = ConfigInfo(file_path='data/yaml-test-data.yaml')
    config = ConfigFromYaml.get_instance(config_info)

    # ----------------------------------------------------------------------------
    # -- Synatx-1: Use Unix File Absolute Path syntax (with leading slash '/'): --
    # -- (The following to groups will have the results)
    # ----------------------------------------------------------------------------
    print(config.query('/myprojapp/kafka/host'))
    print(config.query('/myprojapp/kafka/port'))

    print(config.query('myprojapp.kafka.host'))
    print(config.query('myprojapp.kafka.port'))

    # ----------------------------------------------------------------------------
    # -- Syntax-2: Use YAML path syntax (i.e. dot-based with no leading 'dot'): --
    # ----------------------------------------------------------------------------
    print(config.query('myprojapp.myproj.adapters.elasticsearch.hosts'))

    # ----------------------------------------------------------------------------
    # -- Query specific Array Item with subscript index:
    # -- (The following four queries will have the same results)
    # ----------------------------------------------------------------------------
    print(config.query('myprojapp.myproj.adapters.elasticsearch.hosts.[0]'))
    print(config.query('myprojapp.myproj.adapters.elasticsearch.hosts')[0])
    print(config.query('/myprojapp/myproj/adapters/elasticsearch/hosts.[0]'))
    print(config.query('/myprojapp/myproj/adapters/elasticsearch/hosts')[0])

    # --------------------------------
    # -- Query With default_value : --
    # ---------------------------------
    print(config.query_with_default('NOT.FOUND.KEY', 'DEFAULT_VALUE_1'))

    # -----------------------------
    # -- Query entire YAML tree: --
    # -----------------------------
    print(config.query(''))
    print(config.query(None))


# ---------------------------
# -- Class: ConfigFromYaml --
# ---------------------------
class ConfigFromYaml(ConfigAbstractClass):
    # global config

    __instance = None

    @staticmethod
    def get_instance(args: ConfigInfo):
        if ConfigFromYaml.__instance is None:
            ConfigFromYaml.__instance = ConfigFromYaml(args)
        return ConfigFromYaml.__instance

    # Initializer / Instance Attributes
    def __init__(self, args: ConfigInfo):

        """ Virtually private constructor. """
        if ConfigFromYaml.__instance is None:
            ConfigFromYaml.__instance = self
        else:
            return

        self.log = logging.getLogger('ConfigFromYaml')
        self.log.info('creating an instance of ConfigFromYaml')

        self.config_info = args
        self.log.info("ConfigFromYaml.__init__(): open YAML file={0}:".format(self.config_info.file_path))

        # Initializer / Instance Attributes
        self.config_file = self.config_info.file_path.strip()

        self.config = None
        self.log.info("ConfigFromYam.__initi__(): open YAML file:" + self.config_file)
        # try:
        # self.yamlStream = open(yaml_file_path, "rw")
        # doc = yaml.load(self.yamlStream, Loader=yaml.FullLoader)
        try:
            with open(self.config_file) as file:
                self.yaml = yaml.load(file, Loader=yaml.FullLoader)
            sort_file = yaml.dump(self.yaml, sort_keys=True)
            self.log.debug(sort_file)
            self.connected = True
        except Exception as e:
            # ref: https://docs.python.org/3/library/exceptions.html
            self.log.error("ConfigFromYamlRemote.__init()__: *** ERROR ****: --- Can't open YAML file: " + self.config_file)
            self.connected = False

    def is_connected(self) -> bool:
        return self.connected

    def getData(self) -> dict:
        return self.yaml

    # ------------------
    # -- Save to file --
    # ------------------
    def save(self, output_yaml_path):
        try:
            with open(output_yaml_path, 'w') as f:
                yaml.dump(self.yaml, f)
                # yaml.dump(self.config.data, f, default_flow_style=False)
        except YAMLPathException as e:
            self.log.error("ConfigFromYaml().save(): *** ERROR ***: Can't write to file: ", output_yaml_path)

    # ----------------------
    # -- create new nodes --
    # ----------------------
    @staticmethod
    def set_value_new(keys_remained, new_value) -> dict:
        mom_dict = dict()
        child_dict = dict()
        count = len(keys_remained)
        for k in reversed(keys_remained):
            if count >= len(keys_remained):
                child_dict[k] = new_value
            else:
                mom_dict = dict()
                mom_dict[k] = child_dict.copy()
                child_dict = mom_dict
            count -= 1

        return child_dict

    # ---------------------
    # -- Change Values   --
    # ---------------------
    # At its simplest, you only need to supply the the YAML Path to one or more nodes to update, and
    # the value to apply to them.
    # Catching "yamlpath.exceptions.YAMLPathException" is optional
    # but usually preferred over allowing Python to dump the call stack in front of your users.
    # When using EYAML, the same applies to "yamlpath.eyaml.exceptions.EYAMLCommandException".
    #
    def set_value(self, yaml_path, new_value):
        if self.connected:
            if not (yaml_path is '' or yaml_path is None):
                if new_value is None:
                    new_value = "~"
                    # new_value = "''"

                # -- Auto-converted from '/' to '.' as YamlPath specification to represent the path
                yaml_path = re.sub("^\/", "", yaml_path)
                yaml_path = re.sub("\/", ".", yaml_path)
                key_list = yaml_path.split(".")

                _yaml = self.yaml
                count = 0
                keys_remained = key_list.copy()
                for k in key_list:
                    if not k in _yaml:
                        keys_remained.remove(k)
                        _dict_new = self.set_value_new(keys_remained, new_value)
                        _yaml[k] = _dict_new
                        break

                    _yaml = _yaml[k]
                    count += 1
                    keys_remained.remove(k)
                    if count >= len(key_list):
                        _yaml = new_value
                        break

    # -------------------
    # -- Query by Path --
    # -------------------
    # yamlpath:
    #   ref: https://pypi.org/project/yamlpath/#get-a-yaml-value
    def query(self, yaml_path) -> dict:
        if not (yaml_path):
            return self.yaml

        value = None
        if self.connected:
            if yaml_path is '' or yaml_path is None:
                return self.yaml
            else:
                # -- Auto-converted from '/' to '.' as YamlPath specification to represent the path
                yaml_path = re.sub("^\/", "", yaml_path)
                yaml_path = re.sub("\/", ".", yaml_path)
                key_list = yaml_path.split(".")

                _yaml = self.yaml
                count = 0
                try:
                    for k in key_list:
                        if not k in _yaml:
                            m = re.match("^\[(\d+)\]$", k)
                            if m:
                                index = int(m.groups()[0])
                                _yaml = _yaml[index]
                            else:
                                if UtilityConversion.isInt(k):
                                    index = int(k)
                                    _yaml = _yaml[index]
                                else:
                                    # -- not found --
                                    value = None
                                    break
                        else:
                            _yaml = _yaml[k]

                        count += 1
                        if count >= len(key_list):
                            value = _yaml
                            break
                except Exception as e:
                    self.log.error('*** ERROR: ConfigFromYaml.query(): Exception: ', e)
                    value = None

        return value

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
