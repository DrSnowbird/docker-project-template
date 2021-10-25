class ConfigInfo:

    def __init__(self, config_type='', file_path='', remote_url='', config_object_uid='', remote_host='', remote_port='',
                 priority=0):
        # -- config object type: --
        # ConfigFromEnv,
        # ConfigFromJson,
        # ConfigFromRemote,
        # ConfigFromYaml,
        # ConfigFromYamlPath,
        # ConfigFromYamlRemote
        self.__config_type = config_type
        # -- config from File (YAML or JSON): --
        self.__file_path = file_path
        # -- Config from remote Config Server with URL (base URL): --
        self.__remote_url = remote_url
        # -- Config from remote Config Server - config object (YAML or JSON) UID or Unique Config Object Name: --
        self.__config_object_uid = config_object_uid
        # -- Priority of Configuration, higher number higher priority to overwrite any other lower priority config items.
        self.__priority = priority
        # -- Remote host: --
        self.__remote_host = remote_host
        # -- Remote port: --
        self.__remote_port = remote_port

    def __repr__(self):
        return str(self.__dict__)

    # -- config_type --
    @property
    def config_type(self):
        return self.__config_type

    @config_type.setter
    def config_type(self, config_type):
        self.__config_type = config_type

    # -- file_path --
    @property
    def file_path(self):
        return self.__file_path

    @file_path.setter
    def file_path(self, file_path):
        self.__file_path = file_path

    # -- __remote_url --
    @property
    def remote_url(self):
        return self.__remote_url

    @remote_url.setter
    def remote_url(self, remote_url):
        self.__remote_url = remote_url

    # -- __config_object_uid --
    @property
    def config_object_uid(self):
        return self.__config_object_uid

    @config_object_uid.setter
    def config_object_uid(self, config_object_uid):
        self.__config_object_uid = config_object_uid

    # -- __remote_host --
    @property
    def remote_host(self):
        return self.__remote_host

    @remote_host.setter
    def remote_host(self, remote_host):
        self.__remote_host = remote_host

    # -- __remote_port --
    @property
    def remote_port(self):
        return self.__remote_port

    @remote_port.setter
    def remote_port(self, remote_port):
        self.__remote_port = remote_port

    # -- __priority --
    @property
    def priority(self):
        return self.__priority

    @priority.setter
    def priority(self, priority):
        self.__priority = priority

    def to_str(self) -> str:
        s = "(config_type=" + self.__config_type
        s += ", file_path=" + self.__file_path
        s += ", remote_url=" + self.__remote_url
        s += ", config_object_uid=" + self.__config_object_uid
        s += ", remote_host=" + self.__remote_host
        s += ", remote_port=" + self.__remote_port
        s += ", priority=" + str(self.__priority) + ')'
        return s


class ConfigInfoList():

    def __init__(self):
        self.config_items = list()

    def append(self, config_info: ConfigInfo):
        self.config_items.append(config_info)

    def to_str(self) -> str:
        s = str('[')
        for i in self.config_items:
            s += i.to_str() + ','

        s = s + ']'
        return s

    #
    # def __repr__(self):
    #     return str(self.config_items)


    # # -- JSON Config Sources: --
    # # e.g.
    # #    export JSON_CONFIG_FILE_PATH = 'data/json-test-data.json'
    # #    export JSON_CONFIG_SERVER_URL = 'http://abdn-vm-155.openkbs.org:3000/'
    # #    export JSON_CONFIG_OBJECT_UID= 'myproj_config_LOCAL_abdn-vm-166.openkbs.org'
    # #
    # json_config_file_path = os.getenv('JSON_CONFIG_FILE_PATH')
    # json_config_server_url = os.getenv('JSON_CONFIG_SERVER_URL')
    # json_config_object_uid = os.getenv('JSON_CONFIG_OBJECT_UID')
    #
    # # -- YAML Config Sources: --
    # # e.g.
    # #     export YAML_CONFIG_FILE_PATH = 'data/yaml-test-data.yaml'
    # #     export yaml_config_server_url = 'http://abdn-vm-166:18080/jetty_base/yaml'
    # #     export YAML_CONFIG_OBJECT_UID = 'myproj_config_LOCAL_abdn-vm-166.openkbs.org.yaml'
    # #
    # yaml_config_file_path = os.getenv('YAML_CONFIG_FILE_PATH')
    # yaml_config_server_url = os.getenv('YAMLCONFIG_SERVER_URL')
    # yaml_config_object_uid = os.getenv('YAML_CONFIG_OBJECT_UID')

