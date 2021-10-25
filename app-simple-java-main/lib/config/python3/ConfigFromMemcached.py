import json
import logging

import requests

from pymemcache.client.base import Client

from ConfigInfo import ConfigInfo

module_logger = logging.getLogger('ConfigFromMemcachedRemote')


# -----------
# -- Tests --
# -----------
def main():
    logging.basicConfig(level='DEBUG')

    #  Singleton.getInstance()
    # ----------------------------------------------------------------------------
    # -- Setup Connection:
    # ----------------------------------------------------------------------------
    config_info = ConfigInfo(remote_host='abdn-vm-166.openkbs.org', remote_port='11211')
    config = ConfigFromMemcached.get_instance(config_info)

    # client = Client(('10.128.9.166', 11211), serializer=json_serializer,
    #                 deserializer=json_deserializer)
    config.set('key', {'a': 'b', 'c': 'd'})
    result = config.get('key')

    print('result=' + str(result))

    # Once the client is instantiated, you can access the cache:
    # client.set('some_key', 'some value', expire=30000, noreply=False)
    config.set('some_key', 'some_value')
    # Retrieve previously set data again:
    result = config.get('some_key')
    print('result=' + result)

    # --------------------------------------------------------------------------------------------------------------
    # -- These two groups below should have the same results
    # -- Syntax:
    #    Unix file path syntax or objectpath syntax
    #    Partial or full path segments provided: --
    # --------------------------------------------------------------------------------------------------------------
    #print(config.query('myprojapp.kafka.host'))

    # --------------------------------
    # -- Query With default_value : --
    # --------------------------------
    #print(config.query_with_default('NOT.FOUND.KEY', 'DEFAULT_VALUE_1'))

    # --------------------------------------------------------------------------------------------------------------
    # -- Query specific Array Item with subscript index:
    # --------------------------------------------------------------------------------------------------------------
    #print(config.query('/myprojapp/myproj/adapters/elasticsearch/hosts[0]'))


def json_serializer(key, value):
    if type(value) == str:
        return value, 1
    return json.dumps(value), 2


def json_deserializer(key, value, flags):
    if flags == 1:
        return value.decode('utf-8')
    if flags == 2:
        return json.loads(value.decode('utf-8'))
    raise Exception("Unknown serialization format")


# ---------------------------
# -- Class: ConfigFromYaml --
# ---------------------------
class ConfigFromMemcached():
    __instance = None

    @staticmethod
    def get_instance(args: ConfigInfo):
        """ Static access method. """
        if ConfigFromMemcached.__instance is None:
            ConfigFromMemcached.__instance = ConfigFromMemcached(args)
        return ConfigFromMemcached.__instance

    def __init__(self, args: ConfigInfo):

        """ Virtually private constructor. """
        if ConfigFromMemcached.__instance is None:
            ConfigFromMemcached.__instance = self
        else:
            return

        self.log = logging.getLogger('ConfigFromMemcached')
        self.log.info('creating an instance of ConfigFromMemcached')

        # -- Prepare initial setup: --
        # ... code here ...
        self.config_info = args
        self.log.info("ConfigFromMemcached.__init__(): open Memcached: host={0}, port={1}:".format(
            self.config_info.remote_host, self.config_info.remote_port))
        try:
            # ref: https://pymemcache.readthedocs.io/en/latest/getting_started.html
            self.client = Client((self.config_info.remote_host, int(self.config_info.remote_port)),
                            serializer=json_serializer, deserializer=json_deserializer)
            self.connected = True

            # # Once the client is instantiated, you can access the cache:
            # # client.set('some_key', 'some value', expire=30000, noreply=False)
            # self.client.set('some_key', 'some_value')
            # # Retrieve previously set data again:
            # result = self.client.get('some_key')

            # ... normal processing code here ...
            # self.log.debug("-- Some debug print out here ... some_key:" + result)  # .decode('utf-8'))

        except requests.exceptions.Timeout:
            # Maybe set up for a retry, or continue in a retry loop
            pass
        except requests.exceptions.TooManyRedirects:
            # Tell the user their URL was bad and try a different one
            pass
        except requests.exceptions.RequestException as e:
            # ... exception handling processing code here ...
            self.log.error("*** ERROR: " + str(e))
            self.connected = False

    def set(self, key, value, expire=0, noreply=False, flags=None) -> bool:
        if not self.config_info:
            return False
        try:
            result = self.client.set(key, value, noreply=False)
            return result
        except Exception as e:
            self.log.error("set(): *** ERROR: key=" + key + "; Exception:"+ str(e))

    def get(self, key) -> object:
        if not self.config_info:
            return None
        try:
            result = self.client.get(key)
            return result
        except Exception as e:
            self.log.error("get(): *** ERROR: key=" + key + "; Exception:"+ str(e))
            return None


    def is_connected(self) -> bool:
        return self.connected

    # -------------------
    # -- Query by Path --
    # -------------------
    def query(self, key) -> object:
        if not key:
            return None

        self.log.debug('query(): path='+ key)
        return self.get(key)


# -----------
# -- main --
# -----------
if __name__ == "__main__":
    # execute only if run as a script
    main()
