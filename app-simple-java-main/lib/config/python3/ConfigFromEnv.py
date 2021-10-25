import logging
import os
import re

from ConfigAbstractClass import ConfigAbstractClass
from ConfigInfo import ConfigInfo

module_logger = logging.getLogger('ConfigFromRemote')


# -----------
# -- Tests --
# -----------
def main():

    logging.basicConfig(level='DEBUG')

    # -- Tests --
    #  Singleton.getInstance()

    # ----------------------------------------------------------------------------
    # -- Setup Connection:
    # ----------------------------------------------------------------------------
    config_info = ConfigInfo()
    config = ConfigFromEnv.get_instance(config_info)

    print("NOT_FOUND=" + config.query_with_default('NOT_FOUND', 'NOT_FOUND_DEFAULT_VALUE'))
    print('kafka__host = ', config.query_with_default('myprojapp.kafka.host', '127.0.0.1'))
    print("kafka__port = ", config.query_with_default('kafka.port', '9092'))

    print('elasticsearch__hosts = ', config.query_with_default('elasticsearch__hosts', 'myproj-dev.openkbs.org:9200'))
    # -- call os.getenv directly: --
    print('elasticsearch__hosts = ', os.getenv('elasticsearch__hosts', 'myproj-dev.openkbs.org:9200'))


# ---------------------------
# -- Class: ConfigFromYaml --
# ---------------------------
class ConfigFromEnv(ConfigAbstractClass):
    __instance = None

    @staticmethod
    # @staticmethod
    def get_instance():
        return ConfigFromEnv.get_instance()

    @staticmethod
    def get_instance(args: ConfigInfo):
        if ConfigFromEnv.__instance is None:
            ConfigFromEnv.__instance = ConfigFromEnv(args)
        return ConfigFromEnv.__instance

    # Initializer / Instance Attributes
    def __init__(self, args: ConfigInfo):

        """ Virtually private constructor. """
        if ConfigFromEnv.__instance is None:
            ConfigFromEnv.__instance = self
        else:
            return

        self.log = logging.getLogger('ConfigFromRemote')
        self.log.info('creating an instance of ConfigFromEnv')

        self.config_info = args

        self.connected = True

    @property
    def is_connected(self) -> bool:
        return self.is_connected

    def query(self, key) -> object:
        if key is '' or key is None:
            return ''
        value = os.getenv(key)
        return value

    def query_with_default(self, key, default_value='') -> object:
        value = default_value
        if key is '' or key is None:
            return default_value
        value = os.getenv(key, default_value)
        return value

    # -- Query with common "path" expression --
    # -- Auto-convert the 'dot' to '__':
    # -- e.g.,
    def query_with_name_mapped(self, key, default_value='', sep_dot_replacement='') -> object:
        key = re.sub("\.", sep_dot_replacement, key)
        value = default_value
        if key is '' or key is None:
            return default_value
        value = os.getenv(key, default_value)
        return value


# -----------
# -- main --
# -----------
if __name__ == "__main__":
    # execute only if run as a script
    main()

# print(os.getenv('KEY_THAT_MIGHT_EXIST', default_value))
