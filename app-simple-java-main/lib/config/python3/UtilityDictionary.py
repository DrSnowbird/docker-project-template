import configparser
import json
import re

import yaml
import logging
from io import StringIO
from dotmap import DotMap

log = logging.getLogger('UtilityDictionary')

class UtilityDictionary:

    @staticmethod
    def load_config_string(s: str) -> (dict, bool):
        config_dict = dict()

        try:
            #config_dict = json.loads(StringIO(s))
            config_dict = json.loads(s)
            return config_dict, 'JSON'
        except Exception as ej:
            log.debug("load_config(s: str): Error trying to load the config file in JSON format")
            valid_json = False

        try:
            #config_dict = yaml.load(StringIO(s), Loader=yaml.FullLoader)
            config_dict = yaml.load(s, Loader=yaml.FullLoader)
            return config_dict, 'YAML'
        except Exception as ey:
            log.debug("load_config(s: str): Error trying to load the config file in YAML format")
            valid_yaml = False

        try:
            config_dict = configparser.ConfigParser()
            #config_dict.read_string(StringIO(s))
            config_dict.read_string(s)
            return config_dict, 'INI'
        except Exception as e:
            log.debug("load_config(s: str): Can't use ConfigParser to load Key/Value file (not standard INI file: ")

        return dict, 'unknown_format'

    @staticmethod
    def load_config_file(config_file) -> (dict, bool):
        with open(config_file, "r") as in_fh:
            # Read the file into memory as a string so that we can try
            # parsing it twice without seeking back to the beginning and
            # re-reading.
            config = in_fh.read()

        config_dict = dict()
        valid_json = True
        valid_yaml = True
        valid_ini = True
        valid_kv = True
        unknown_format = True

        try:
            config_dict = json.loads(config)
            return config_dict, valid_json
        except:
            log.debug("load_config_file(config_file): Error trying to load the config file in JSON format")
            valid_json = False

        try:
            config_dict = yaml.safe_load(config)
            return config_dict, valid_yaml
        except:
            log.debug("load_config_file(config_file): Error trying to load the config file in YAML format")
            valid_yaml = False

        try:
            config = configparser.ConfigParser()
            config.read(config_file)
            dictionary = {}
            for section in config.sections():
                dictionary[section] = {}
                for option in config.options(section):
                    dictionary[section][option] = config.get(section, option)
            return dictionary, valid_ini
        except Exception as e:
            log.debug("load_config_file(config_file): Can't use ConfigParser to load Key/Value file (not standard INI "
                      "file): " + config_file)
            log.debug(e)

        try:
            config_dict = dict()
            with open(config_file) as fp:
                for line in fp:
                    if line.startswith('#'):
                        continue
                    m = re.match("^.*=", line)
                    if m:
                        key, val = line.strip().split('=', 1)
                        config_dict[key] = val
            return config_dict, valid_kv
        except Exception as e:
            log.debug("load_config_file(config_file): Can't load simple Key=Value format: " + config_file)
            log.debug(e)

        return (dict, unknown_format)

    @staticmethod
    def try_as(loader, s, on_error) -> bool:
        try:
            loader(s)
            return True
        except on_error:
            return False

    @staticmethod
    def is_json(s) -> bool:
        return UtilityDictionary.try_as(json.loads, s, ValueError)

    @staticmethod
    def is_yaml(s) -> bool:
        return UtilityDictionary.try_as(yaml.safe_load, s, yaml.scanner.ScannerError)

    # --------------------------------------
    # -- Insert / set a new value by Path --
    # --------------------------------------
    # path: is "dot-based" syntax for multiple levels of paths
    @staticmethod
    def add_new_dict_entry(dictionary: dict, path: str, new_value: object) -> dict:
        parent = dictionary
        path_list = path.split(".")
        for p in path.split("."):
            key = path_list.pop(0)
            if p in parent:
                parent = parent[p]
            else:
                created = 0
                parent = {}
                child = {}
                child_list = reversed(path_list)
                for c in child_list:
                    if created == 0:
                        parent[c] = new_value
                        created = 1
                    else:
                        parent[c] = child
                    child = parent
                    parent = {}
                dictionary[key] = child
                break
        return dictionary

    # -------------------------------------------------
    # -- Search by path with depth (Non-recurrsive): --
    # -------------------------------------------------
    @staticmethod
    def search_by_path(d: dict, path: str) -> object:
        result = None
        if d:
            if path:
                parent = d
                path_list = path.split(".")
                child = None
                for p in path_list:
                    if p in parent.keys():
                        child = parent.get(p)
                        parent = child
                    else:
                        child = None
                        break

                result = child
            else:
                result = d
        return result

    # -------------------------------------------------
    # -- Search by path with depth (Recurrsively):   --
    # -------------------------------------------------
    @staticmethod
    def search_by_path_recurrsive(d: dict, path: str) -> object:
        result = None
        if d:
            if path:
                path_list = path.split(".")
                key = path_list[0]
                for k, v in d.items():
                    if k == key:
                        if path_list.pop(0):
                            result = UtilityDictionary.search_by_path_recurrsive(v, ".".join(path_list))
                        else:
                            result = v
                    if result:
                        return result
            else:
                result = d
        return result

    # -------------------------------------------------
    # -- Search 1st matched Key regardless of depth: --
    # -------------------------------------------------
    @staticmethod
    def search_first_match_key(d: dict, key: str) -> object:
        for k, v in d.items():
            if key == k:
                print(k, ":", v)
                return v
            else:
                return UtilityDictionary.search_first_match_key(v, key)
        return None

    @staticmethod
    def iterate_dict(d, path=''):
        for k, v in d.items():
            if isinstance(v, dict):
                if path:
                    cpath = path + "." + str(k)
                else:
                    cpath = str(k)
                UtilityDictionary.iterate_dict(v, cpath)
            else:
                print(path + "." + str(k), ":", v)


def main():
    D1 = {1: {2: {3: 4, 5: 6}, 3: {4: 5, 6: 7}}, 2: {3: {4: 5}, 4: {6: 7}}}
    UtilityDictionary.iterate_dict(D1)

    # ------------------------------
    # -- Insert (new path:value): --
    # ------------------------------
    my_dict = {'key1': 'value1'}
    my_dict = UtilityDictionary.add_new_dict_entry(my_dict, "aaa.bbb.ccc", "abc_value_new")

    # print("search_first_match_key: " + search_first_match_key(my_dict, 'ccc'))

    print("search_by_path: " + UtilityDictionary.search_by_path(my_dict, 'aaa.bbb.ccc'))
    print("search_by_path_recurrsive: " + UtilityDictionary.search_by_path_recurrsive(my_dict, 'aaa.bbb.ccc'))

    print('\n== d2=DotMap(D1) ==')
    d2= DotMap(D1)
    UtilityDictionary.iterate_dict(d2)

    print('\n== DotMap: creating new children ==')
    m = DotMap()
    m.people.john.age = 32
    m.people.john.job = 'programmer'
    m.people.mary.age = 24
    m.people.mary.job = 'designer'
    m.people.dave.age = 55
    m.people.dave.job = 'manager'
    m['key1']['key2'] = 'value12'
    for k, v in m.people.items():
        print(k, v)
    UtilityDictionary.iterate_dict(m)

    # init from DotMap
    print('\n== init from DotMap ==')
    e = DotMap(m)
    print(e)
    print("===== print children() =====")
    for k, v in e.people.items():
        print(k, v)

    print("===== toDict() =====")
    print(e.toDict())

    print("===== pprint(pformat='json' =====")
    e.pprint(pformat='json')

    print("===== Add to existing DotMap =====")
    e2 = DotMap()
    e2.student.mary.age = 25
    e2.student.mary.job = 'manager'
    e2.update(e)
    print(e2.toDict())
    e2.pprint(pformat='json')

    print("===== Add new dict to existing DotMap =====")
    d3 = "{'key2': 'value2'}"
    m3 = DotMap(d3)
    e2.update(m3)
    e2.pprint(pformat='json')

    print("===== Load config JSON File =====")
    (jconfig, is_json) = UtilityDictionary.load_config_file(config_file='data/json-test-data.json')
    jdict= DotMap(jconfig)
    jdict.pprint(pformat='json')
    jstring=json.dumps(jdict.toDict())
    print('j-string=\n' + jstring)

    # ================================================

    print("===== Load config YAML File =====")
    (yconfig, is_yaml) = UtilityDictionary.load_config_file(config_file='data/yaml-test-data.yaml')
    ydict= DotMap(yconfig)
    ydict.pprint(pformat='json')
    ystring = yaml.dump(ydict.toDict())
    print('y-string=\n' + ystring)

    print("===== Load config INI File =====")
    (iconfig, is_ini) = UtilityDictionary.load_config_file(config_file='data/test-data-key-value.ini')
    idict= DotMap(iconfig)
    idict.pprint(pformat='json')
    istring=json.dumps(idict.toDict())
    print('i-string=\n' + istring)

    print("===== Load config Key=Value File =====")
    (kvconfig, is_ini) = UtilityDictionary.load_config_file(config_file='data/yaml-test-data-prettified-flatten.txt')
    kvdict= DotMap(kvconfig)
    kvdict.pprint(pformat='json')
    kvstring=json.dumps(kvdict.toDict())
    print('kv-string=\n' + kvstring)

    # ================================================

    print("===== Load config JSON String/Stream =====")
    (jsconfig, is_json) = UtilityDictionary.load_config_string(jstring)
    jsdict= DotMap(jsconfig)
    jsdict.pprint(pformat='json')

    print("===== Load config YAML String/Stream =====")
    (ysconfig, is_json) = UtilityDictionary.load_config_string(ystring)
    ysdict= DotMap(ysconfig)
    ysdict.pprint(pformat='json')
    ysstring = yaml.dump(ysdict.toDict())
    print('ys-string=\n' + ysstring)

    print("===== Load config INI String/Stream =====")
    (isconfig, is_ini) = UtilityDictionary.load_config_string(istring)
    isdict= DotMap(isconfig)
    isdict.pprint(pformat='json')

    print("===== Load config Key=Value String/Stream =====")
    (kvsconfig, is_ini) = UtilityDictionary.load_config_string(kvstring)
    kvsdict= DotMap(kvsconfig)
    kvsdict.pprint(pformat='json')

# -----------
# -- main --
# -----------
if __name__ == "__main__":
    # execute only if run as a script
    main()
