import json
import logging
import re
import sys

import objectpath
import requests


from ConfigAbstractClass import ConfigAbstractClass
from ConfigInfo import ConfigInfo
from UtilityDictionary import UtilityDictionary

module_logger = logging.getLogger('ConfigFromRemote')


# -----------
# -- Tests --
# -----------
def main():

    logging.basicConfig(level='DEBUG')

    #  Singleton.getInstance()

    # ----------------------------------------------------------------------------
    # -- Setup Connection:
    # ----------------------------------------------------------------------------
    config_info = ConfigInfo(file_path='data/json-test-data.json')
    config = ConfigFromJson.get_instance(config_info)

    # --------------------------------------------------------------------------------------------------------------
    # -- These two groups below should have the same results
    # -- Syntax:
    #    Unix file path syntax or objectpath syntax
    #    Partial or full path segments provided: --
    # --------------------------------------------------------------------------------------------------------------
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

    # --------------------------------------------------------------------------------------------------------------
    # -- Query specific Array Item with subscript index:
    # --------------------------------------------------------------------------------------------------------------
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
    # -- More test: bsf_state.py: --
    # ------------------------------
    print(config.query('myproj/adapters/bsf/agents'))

    # ------------------------------
    # -- Insert (new path:value): --
    # ------------------------------
    config.set_value("aaa.bbb.ccc", "abc_value_new")
    print(config.query('aaa.bbb.ccc'))

# ---------------------------
# -- Class: ConfigFromYaml --
# -- ref: http://objectpath.org/reference.html
# ---------------------------
class ConfigFromJson(ConfigAbstractClass):
    __instance = None
    jsonData = None;
    treeObject = None;

    @staticmethod
    def get_instance(args: ConfigInfo):
        """ Static access method. """
        if ConfigFromJson.__instance is None:
            ConfigFromJson.__instance = ConfigFromJson(args)
        return ConfigFromJson.__instance

    def __init__(self, args: ConfigInfo):

        """ Virtually private constructor. """
        if ConfigFromJson.__instance is None:
            ConfigFromJson.__instance = self
        else:
            return

        self.log = logging.getLogger('ConfigFromJson')
        self.log.info('creating an instance of ConfigFromJson')

        self.config_info = args
        self.log.info("ConfigFromJson.__init__(): open JSON file={0}:".format(self.config_info.file_path))

        # Initializer / Instance Attributes
        self.config_file = self.config_info.file_path.strip()

        try:
            with open(self.config_file, 'r') as f:
                self.jsonData = json.load(f)
            self.log.debug(json.dumps(self.jsonData, indent=4, sort_keys=True))
            # -- Using "objectpath" to query the JSON Tree.
            self.treeObject = objectpath.Tree(self.jsonData)
            self.connected = True
        except requests.exceptions.Timeout:
            # Maybe set up for a retry, or continue in a retry loop
            pass
        except requests.exceptions.TooManyRedirects:
            # Tell the user their URL was bad and try a different one
            pass
        except requests.exceptions.RequestException as e:
            # catastrophic error. Abort!
            self.log.error(e)
            self.log.error("ConfigFromJson.__init()__: *** ERROR ****: --- Can't open YAML file: " + self.config_file)
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
            self.log.debug('query(): path=' + path)
            m = re.match("^\/.*", path)
            if m:
                tmp = path
                # -- Unix file path syntax: /abc/def for query
                tmp = re.sub("^\/", "", tmp)
                tmp = re.sub("\/", ".", tmp)
                path = str("$..") + tmp
            else:
                m2 = re.match("\$", path)
                if not m2:
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



    # def search_by_path(self, d: dict, path:str) -> object:
    #     if self.config_dict:
    #         parent = self.config_dict
    #         path_list = path.split().sort(reverse=True)
    #         for p in path.split("."):
    #             if p in parent:
    #                 parent = parent[p]
    #             else:
    #                 result = None
    #                 break
    #         return result
    #
    # def search_by_path(d: dict, path: str) -> object:
    #     result = None
    #     if path:
    #         parent = d
    #         path_list = path.split(".")
    #         child = None
    #         for p in path_list:
    #             if p in parent.keys():
    #                 child = parent.get(p)
    #                 parent = child
    #             else:
    #                 child = None
    #                 break
    #
    #         result = child
    #     else:
    #         result = d
    #     return result

# -----------
# -- main --
# -----------
if __name__ == "__main__":
    # execute only if run as a script
    main()
