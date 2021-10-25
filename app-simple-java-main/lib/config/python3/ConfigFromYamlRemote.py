import logging
import re

import requests
import yaml
from yamlpath.exceptions import YAMLPathException

import UtilityConversion

# create logger
from ConfigAbstractClass import ConfigAbstractClass
from ConfigInfo import ConfigInfo

module_logger = logging.getLogger('ConfigFromYamlRemote')


# -----------
# -- Tests --
# -----------
def main():

    logging.basicConfig(level='DEBUG')

    # logging.basicConfig(level=logging.DEBUG, format='%(relativeCreated)6d %(threadName)s %(message)s')

    # -- Tests --
    #  Singleton.getInstance()
    # yaml_url = 'http://abdn-vm-166:18080/jetty_base/yaml'
    # yaml_object_UID = 'myproj_config_LOCAL_abdn-vm-166.openkbs.org.yaml'
    # http://abdn-vm-166:18080/jetty_base/yaml/myproj_config_LOCAL_abdn-vm-166.openkbs.org.yaml

    # --------------------
    # -- Setup Connection:
    # --------------------
    config_info = ConfigInfo(remote_url='http://abdn-vm-166:18080/jetty_base/yaml',
                             config_object_uid='myproj_config_LOCAL_abdn-vm-166.openkbs.org.yaml')
    config = ConfigFromYamlRemote.get_instance(config_info)

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

    # ----------------------------------------------------------
    # -- Query specific Array Item with subscript index:
    # -- (The following four queries will have the same results)
    # ----------------------------------------------------------
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
class ConfigFromYamlRemote(ConfigAbstractClass):
    # global config
    __instance = None

    @staticmethod
    # The YAML file will be available at e.g., http://abdn-vm-166:18080/jetty_base/yaml/myproj_config_LOCAL_abdn-vm-166.openkbs.org.yaml
    # yaml_url: The base URL of the Remote YAML Server, e.g.
    #     http://abdn-vm-166:18080/jetty_base/yaml/
    # yaml_object_UID: The specific YAML file (including .yaml file extension - optional to provide .yaml part), e.g.
    #    myproj_config_LOCAL_abdn-vm-166.openkbs.org.yaml
    #
    def get_instance(args: ConfigInfo):
        if ConfigFromYamlRemote.__instance is None:
            ConfigFromYamlRemote.__instance = ConfigFromYamlRemote(args)
        return ConfigFromYamlRemote.__instance

    # Initializer / Instance Attributes
    def __init__(self, args: ConfigInfo):

        """ Virtually private constructor. """
        if ConfigFromYamlRemote.__instance is None:
            ConfigFromYamlRemote.__instance = self
        else:
            return

        self.log = logging.getLogger('ConfigFromYamlRemote')
        self.log.info('creating an instance of ConfigFromYamlRemote')


        self.config_info = args
        self.log.info("ConfigFromYaml.__init__(): open YAML Remote url={0}, object_UID={1}:".format(
            self.config_info.remote_url, self.config_info.config_object_uid))

        self.yaml_url = self.config_info.remote_url
        self.yaml_object_UID = self.config_info.config_object_uid
        try:
            url = re.sub("^/|/$", "", self.yaml_url) + '/' + re.sub("\.yaml$", "", self.yaml_object_UID) + '.yaml'
            self.log.info("ConfigFromYamlRemote: CONNECT: " + url)
            response = requests.get(url).text
            self.log.info(response)
            self.yaml = yaml.load(response, Loader=yaml.FullLoader)
            self.connected = True
        except requests.exceptions.Timeout:
            # Maybe set up for a retry, or continue in a retry loop
            self.log.critical("*** ConfigFromYamlRemote: FAIL: Timeout in trying to connect!")
            pass
        except requests.exceptions.TooManyRedirects:
            # Tell the user their URL was bad and try a different one
            self.log.critical("*** ConfigFromYamlRemote: FAIL: TooManyRedirects!")
            pass
        except Exception as e:
            # ref: https://docs.python.org/3/library/exceptions.html
            self.log.critical("ConfigFromYamlRemote.__init()__: *** ERROR ****: --- Can't open YAML URL: " + url)
            self.connected = False

    def is_connected(self) -> bool:
        return self.connected

    def getData(self) -> dict:
        return self.yaml

    # ------------------
    # -- Save to file --
    # ------------------
    def save(self, output_yaml_path):
        self.log.info("ConfigFromYamlRemote.save(): save to YAML file=', output_yaml_path")
        try:
            with open(output_yaml_path, 'w') as f:
                # yaml.dump(self.yaml, f)
                yaml.dump(self.config.data, f, default_flow_style=False)
        except YAMLPathException as e:
            self.log.error("ConfigFromYamlRemote.save(): *** ERROR ***: Can't write to file: " + output_yaml_path)

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
        self.log.info('ConfigFromYamlRemote.set_value(): YAML path=', yaml_path, ', new_value= ' + new_value)
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
                    self.log.error('*** ERROR: ConfigFromYaml.query(): Exception: ' + e)
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
