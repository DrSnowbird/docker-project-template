import json
import logging
import re
import sys

import objectpath
import requests

from ConfigAbstractClass import ConfigAbstractClass
from ConfigInfo import ConfigInfo
from UtilityDictionary import UtilityDictionary

module_logger = logging.getLogger('ConfigFromJsonRemote')


# -----------
# -- Tests --
# -----------
def main():

    logging.basicConfig(level='DEBUG')

    #  Singleton.getInstance()
    # --------------------
    # -- Setup Connection:
    # --------------------
    config_info = ConfigInfo(remote_url='http://abdn-vm-155.openkbs.org:3000/',
                             config_object_uid='myproj_config_LOCAL_abdn-vm-166.openkbs.org')
    config = ConfigFromJsonRemote.get_instance(config_info)

    # ------------------------------------------------------
    # -- These two groups below should have the same results
    # -- Syntax:
    #    Unix file path syntax or objectpath syntax
    #    Partial or full path segments provided: --
    # ------------------------------------------------------
    print(config.query('$..kafka.host'))
    print(config.query('kafka.host'))
    print(config.query('kafka/host'))
    print(config.query('$..myprojapp.kafka.host'))
    print(config.query('/myprojapp/kafka/host'))

    print(config.query('$..kafka.port'))
    print(config.query('kafka.port'))
    print(config.query('kafka/port'))
    print(config.query('myprojapp.kafka.port'))
    print(config.query('/myprojapp/kafka/port'))

    # --------------------------------
    # -- Query With default_value : --
    # --------------------------------
    print(config.query_with_default('NOT.FOUND.KEY', 'DEFAULT_VALUE_1'))

    # --------------------------------------------------
    # -- Query specific Array Item with subscript index:
    # --------------------------------------------------
    print(config.query('$..elasticsearch.hosts'))
    # -- (The following eight queries will have the same results) either partial or full paths: --
    print(config.query('$..elasticsearch.hosts[0]'))
    print(config.query('$..elasticsearch.hosts')[0])
    print(config.query('adapters.elasticsearch.hosts[0]'))
    print(config.query('adapters.elasticsearch.hosts')[0])
    print(config.query('myprojapp.myproj.adapters.elasticsearch.hosts[0]'))
    print(config.query('myprojapp.myproj.adapters.elasticsearch.hosts')[0])
    print(config.query('/myprojapp/myproj/adapters/elasticsearch/hosts[0]'))
    print(config.query('/myprojapp/myproj/adapters/elasticsearch/hosts')[0])

    # -----------------------------
    # -- Query entire tree: --
    # -----------------------------
    print(config.query(''))
    print(config.query(None))

    # ------------------------------
    # -- Insert (new path:value): --
    # ------------------------------
    config.set_value("aaa.bbb.ccc", "abc_value_new")
    print(config.query('aaa.bbb.ccc'))


# ---------------------------
# -- Class: ConfigFromYaml --
# -- ref: http://objectpath.org/reference.html
# ---------------------------
class ConfigFromJsonRemote(ConfigAbstractClass):
    __instance = None
    jsonData = None;
    treeObject = None;

    @staticmethod
    def get_instance(args: ConfigInfo):
        """ Static access method. """
        if ConfigFromJsonRemote.__instance is None:
            ConfigFromJsonRemote.__instance = ConfigFromJsonRemote(args)
        return ConfigFromJsonRemote.__instance

    def __init__(self, args: ConfigInfo):

        """ Virtually private constructor. """
        if ConfigFromJsonRemote.__instance is None:
            ConfigFromJsonRemote.__instance = self
        else:
            return

        self.log = logging.getLogger('ConfigFromRemote')
        self.log.info('creating an instance of ConfigFromRemote')

        self.config_info = args
        self.log.info("ConfigFromRemote.__init__(): open JSON Remote: url={0}, object_UID={1}:".format(
            self.config_info.remote_url, self.config_info.config_object_uid))

        # # Initializer / Instance Attributes
        self.remote_url = re.sub("/$", "", self.config_info.remote_url).strip()
        self.json_object_UID = re.sub("/$", "", self.config_info.config_object_uid).strip()

        try:
            # url = 'http://abdn-vm-166.openkbs.org:3000/myproj_config_LOCAL_abdn-vm-166.openkbs.org'
            url = self.remote_url + '/' + self.json_object_UID
            self.log.info("ConfJsonRemote: CONNECT: " + url)
            response = requests.get(url)
            self.log.debug(json.dumps(response.json(), indent=4, sort_keys=True))
            self.jsonData = response.json()
            # -- Using "objectpath" to query the JSON Tree.
            self.treeObject = objectpath.Tree(self.jsonData)
            self.log.debug(response.json())
            self.connected = True
        except requests.exceptions.Timeout:
            # Maybe set up for a retry, or continue in a retry loop
            self.log.critical("*** ConfigFromRemote: FAIL: Timeout in trying to connect!")
            pass
        except requests.exceptions.TooManyRedirects:
            # Tell the user their URL was bad and try a different one
            self.log.critical("*** ConfigFromRemote: FAIL: TooManyRedirects!")
            pass
        except requests.exceptions.RequestException as e:
            # catastrophic error. Abort!
            self.log.critical("*** ConfigFromRemote: FAIL: failed to establish connection!")
            self.log.critical(e)
            # ref: https://docs.python.org/3/library/exceptions.html
            self.connected = False

    def is_connected(self) -> bool:
        return self.connected

    def getData(self) -> dict:
        return self.jsonData

    # -------------------
    # -- Query by Path --
    # -------------------
    def query(self, path) -> object:
        if path:
            self.log.debug('query(): path='+ path)

            m = re.match("^\/.*", path)
            if m:
                # -- Synatx: Unix file path: "/abc/def/ghi" : --
                tmp = path
                # -- Unix file path syntax: /abc/def for query
                tmp = re.sub("^\/", "", tmp)
                tmp = re.sub("\/", ".", tmp)
                path = str("$..") + tmp
            else:
                m2 = re.match("\$", path)
                if not m2:
                    # -- Syntax: 'abc.def.ghi' or 'abd/def/ghi' : --
                    tmp2 = path
                    path = str("$..") + re.sub("\/", ".", tmp2)
            try:
                if self.treeObject.execute(path):
                    return tuple(self.treeObject.execute(path))[0]
                else:
                    return None
            except Exception as e:
                return None
        else:
            return self.jsonData

    # --------------------------------------
    # -- Query with default_value by Path --
    # --------------------------------------
    def query_with_default(self, path, default_value) -> object:
        result = self.query(path)
        if result is None:
            return default_value
        else:
            return result

    # --------------------------------------
    # -- Insert / set a new value by Path --
    # --------------------------------------
    def set_value(self, path: str, new_value)->dict:
        self.jsonData = UtilityDictionary.add_new_dict_entry(self.jsonData, path, new_value)
        self.treeObject = objectpath.Tree(self.jsonData)
        return self.jsonData


# -----------
# -- main --
# -----------
if __name__ == "__main__":
    # execute only if run as a script
    main()
