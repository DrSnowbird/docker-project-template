import configparser
import logging
import re

import requests

from ConfigAbstractClass import ConfigAbstractClass
from ConfigInfo import ConfigInfo

module_logger = logging.getLogger('ConfigFromKeyValueFile')


# ----------------------------------------------------------------------------------
# -- Usage:
# --     This assume the config file is using "standard INI property defintion, i.e.,
# --     All Key=Value line should be under specific "Section" including "DEFAULT"
# -- Query:
# --     <Section>__<some_key_name>
# -- Example:
#        To query 'User' under Section "bitbucket.org" -- the "#" symbol to indicate the Section name.
#        You can change this special '#' to, say, '%' or '__' (double understand) or anything special character
#        using the method, setSectionDelimiter='#' (default is '#')
#           'bitbucket.org#User'
#        However, if you don't provide the above "Section#" name, the "query(...)" will search and find
#          'Default' and then search all 'Section's to find any matched 'key' and then then get its value as result.
#          the first matched 'User' row to get its value as results. -- So, you need to be aware this default behavior!
# -- Extension:
#        This class actually supports Non-standard INI property Key=Value file format automatically detection.
#        To query, you just use the "key" since there is no 'Section' name for this kind of Non-Standard Key=Value file
#            config.query('myprojapp.myproj.adapters.elasticsearch.hosts')
#        Or, you can just add a "Section" title, '[DEFAULT]' at the first line and don't leave any blank lines
#        in-between all the key=value rows.
#
# --   Example:
#         [DEFAULT]
#         ServerAliveInterval = 45
#         Compression = yes
#         CompressionLevel = 9
#         ForwardX11 = yes
#         key1 = value1
#
#         [bitbucket.org]
#         User = hg
#
#         [topsecret.server.com]
#         Port = 50022
#         ForwardX11 = no
# ----------------------------------------------------------------------------------

def lprint(args):
    module_logger.debug(args)


# -- Tests --
# -----------
def main():
    logging.basicConfig(level='DEBUG')

    # ----------------------------------------------------------------------------
    # -- Setup Connection:
    # ----------------------------------------------------------------------------
    config_info = ConfigInfo(file_path='data/yaml-test-data-prettified-flatten.txt')
    # config_info = ConfigInfo(file_path='data/test-data-key-value.ini')
    config = ConfigFromKeyValueFile.get_instance(config_info)

    # --------------------------------------------------------------------------------------------------------------
    # -- These two groups below should have the same results
    # -- Syntax:
    #    Unix file path syntax or objectpath syntax
    #    Partial or full path segments provided: --
    # --------------------------------------------------------------------------------------------------------------
    lprint(config.query('bitbucket.org#User'))
    lprint(config.query('User'))

    # --------------------------------
    # -- Query With default_value : --
    # --------------------------------
    lprint(config.query_with_default('NOT_FOUND_KEY', 'DEFAULT_VALUE_1'))

    # --------------------------------------------------------------------------------------------------------------
    # -- Query specific Array Item with subscript index:
    # --------------------------------------------------------------------------------------------------------------
    lprint(config.query('myprojapp.myproj.adapters.elasticsearch.hosts'))
    lprint(config.query('/myprojapp/myproj/adapters/elasticsearch/hosts'))

    # -- Query without 'Section#' prefix and hence, search
    lprint(config.query('key1'))

    # ------------------------------
    # -- Insert (new path:value): --
    # ------------------------------
    config.set_value("aaa.bbb.ccc", "abc_value_new")
    print(config.query('aaa.bbb.ccc'))

class SimpleKeyValueParser():
    def __init__(self, file_path) -> dict:
        self.config = {}
        with open(file_path) as fp:
            for line in fp:
                if line.startswith('#'):
                    continue
                key, val = line.strip().split('=', 1)
                self.config[key] = val

    def get_config(self) -> object:
        return self.config


# ---------------------------
# -- Class: ConfigFromYaml --
# -- ref: http://objectpath.org/reference.html
# ---------------------------
class ConfigFromKeyValueFile():
    __instance = None

    @staticmethod
    def get_instance(args):
        """ Static access method. """
        if ConfigFromKeyValueFile.__instance is None:
            ConfigFromKeyValueFile.__instance = ConfigFromKeyValueFile(args)
        return ConfigFromKeyValueFile.__instance

    def __init__(self, args: ConfigInfo):

        """ Virtually private constructor. """
        if ConfigFromKeyValueFile.__instance is None:
            ConfigFromKeyValueFile.__instance = self
        else:
            return

        self.log = logging.getLogger('ConfigFromKeyValueFile')
        self.log.info('creating an instance of ConfigFromKeyValueFile')

        # -- Prepare initial setup: --
        # ... code here ...
        self.connected = False
        self.config_info = args
        self.config = None
        self.sections = None
        self.section_delimiter = '#'

        try:
            self.log.debug(
                "ConfigFromKeyValue: --SUCCESS: load Key-Value file (*.ini like): " + self.config_info.file_path)
            # ... normal processing code here ...
            try:
                self.config = configparser.ConfigParser()
                self.config.read(self.config_info.file_path)
                self.sections = self.config.sections()
            except Exception as e:
                self.log.debug("__init__(): --- Exception: " + str(e))
                self.log.debug(
                    "__init__(): --- Can't use ConfigParser to load Key/Value file (not standard INI file: " + self.config_info.file_path)

            if not self.sections:
                self.config = SimpleKeyValueParser(self.config_info.file_path).get_config()
            else:
                self.log.debug("__init__(): Sections: " + str(self.sections))

            if self.config:
                self.connected = True

        except requests.exceptions.Timeout:
            # Maybe set up for a retry, or continue in a retry loop
            pass
        except requests.exceptions.TooManyRedirects:
            # Tell the user their URL was bad and try a different one
            pass
        except requests.exceptions.RequestException as e:
            # ... exception handling processing code here ...
            self.log.error("*** ERROR: " + str(e))

    def is_connected(self) -> bool:
        return self.connected

    def set_section_delimiter(self, section_delimiter='#'):
        self.section_delimiter = section_delimiter

    # -------------------
    # -- Query by Path --
    # -------------------
    def query(self, path) -> object:
        if not self.is_connected():
            return None
        if path and self.config:
            self.log.debug('query(): path=' + path)
            tmp_path = path
            # -- Unix file path syntax: /abc/def for query
            tmp_path = re.sub("^\/", "", tmp_path)
            tmp_path = re.sub("\/", ".", tmp_path)
            key_list = tmp_path.split(self.section_delimiter)
            try:
                if self.sections:
                    # -- ini standard file: ---
                    if key_list and key_list[0]:
                        section = key_list[0]
                        if section in self.sections:
                            value = self.config.get(section, key_list[1:])
                            if value:
                                return value
                            else:
                                return None
                        else:
                            # need to search all section:
                            for s in self.sections:
                                return self.config.get(s, tmp_path)
                else:
                    # -- simple key-value file: --
                    if self.config[tmp_path]:
                        return self.config[tmp_path]
                    else:
                        return None
            except Exception as e:
                self.log.debug("query(): --- Exception: " + str(e))
                self.log.info("query(): --- Exception or Not Found!: path= " + path)
                return None
        else:
            return None

    # --------------------------------------
    # -- Query with default_value by Path --
    # --------------------------------------
    def query_with_default(self, path, default_value) -> object:
        if not self.is_connected():
            return default_value
        try:
            result = self.query(path)
            if result is None:
                return default_value
            else:
                return result
        except Exception as e:
            self.log.debug("query_with_default(): --- Exception: " + str(e))
            self.log.info("query_with_default(): --- Exception or Not Found!: path= " + path)
            return default_value

    # --------------------------------------
    # -- Insert / set a new value by Path --
    # --------------------------------------
    def set_value(self, key: str, new_value: str):
        if not self.is_connected():
            return
        self.config[key] = new_value


# -----------
# -- main --
# -----------
if __name__ == "__main__":
    # execute only if run as a script
    main()
