# openkbs Confidential
# NOTICE
# This software was produced for the U. S. Government under Basic Contract No. W15P7T-13-C-A802,
# and is subject to the Rights in Noncommercial Computer Software and Noncommercial Computer
# Software and Noncommercial Computer Software Documentation Clause 252.227-7014 (FEB 2012)
# © 2020 The openkbs Corporation.
import logging
import re

import yaml
from yamlpath import Processor
from yamlpath import YAMLPath
from yamlpath.exceptions import YAMLPathException
from yamlpath.eyaml.exceptions import EYAMLCommandException
from yamlpath.func import get_yaml_data, get_yaml_editor
from yamlpath.wrappers import ConsolePrinter

from ConfigAbstractClass import ConfigAbstractClass
from ConfigInfo import ConfigInfo


class DebugObj:
    # Positional Parameters:
    #     1. args (object) An object representing log level settings with these
    #        properties:
    #         - debug (Boolean) true = write debugging informational messages
    #         - verbose (Boolean) true = write verbose informational messages
    #         - quiet (Boolean) true = write only error messages
    def __init__(self):
        self.debug = True
        self.verbose = False
        self.quiet = True

    def set_debug(self, value=True):
        self.debug = value

    def set_verbose(self, value=False):
        self.verbose = value

    def set_quiet(self, value=True):
        self.quiet = value


# -----------
# -- Tests --
# -----------
def main():

    logging.basicConfig(level='DEBUG')

    #  Singleton.getInstance()

    if False:
        # -- test Save to file --
        config = ConfigFromYamlPath.get_instance('./simple.yaml')
        print(config.query('hash.child_attr.key'))
        config.set_value("hash.new_path", "new_value_1")
        print(config.query('hash.new_path'))
        config.save("simple_1.yaml")

    # ----------------------------------------------------------------------------
    # -- Setup Connection:
    # ----------------------------------------------------------------------------
    config_info = ConfigInfo(file_path='data/yaml-test-data.yaml')
    config = ConfigFromYamlPath.get_instance(config_info)

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


# -------------------------------
# -- Class: ConfigFromYamlPath
# -- Ref: https://github.com/wwkimball/yamlpath
# -------------------------------
# To Read YAML and then query using yamlpath libary to do path-based query
#
class ConfigFromYamlPath(ConfigAbstractClass):
    # global config

    __instance = None

    @staticmethod
    def get_instance(args: ConfigInfo):
        if ConfigFromYamlPath.__instance == None:
            ConfigFromYamlPath.__instance = ConfigFromYamlPath(args)
        return ConfigFromYamlPath.__instance

    # ---------------------------------
    # Initializer / Instance Attributes
    # ---------------------------------
    def __init__(self, args: ConfigInfo):
        """ Virtually private constructor. """
        if ConfigFromYamlPath.__instance is None:
            ConfigFromYamlPath.__instance = self
        else:
            return

        self.log = logging.getLogger('ConfigFromYamlPath')
        self.log.info('creating an instance of ConfigFromYamlPath')

        self.config_info = args
        self.log.info("ConfigFromYamlPath.__init__(): open YAML file={0}:".format(self.config_info.file_path))

        # Initializer / Instance Attributes
        self.config_file = self.config_info.file_path.strip()

        try:
            args = DebugObj()
            self.log = ConsolePrinter(args)

            # Prep the YAML parser and round-trip editor (tweak to your needs)
            self.yaml = get_yaml_editor()

            # At this point, you'd load or parse your YAML file, stream, or string.  When
            # loading from file, I typically follow this pattern:
            self.yaml_data = get_yaml_data(self.yaml, self.log, self.config_file)
            if self.yaml_data is None:
                self.connected = False
                self.log.error('There was an issue loading the file:', self.config_file)
            else:
                # Pass the log writer and parsed YAML data to the YAMLPath processor
                self.config = Processor(self.log, self.yaml_data)
                self.connected = True
        except Exception as e:
            # ref: https://docs.python.org/3/library/exceptions.html
            self.log.error("ConfigFromYamlPath.__init()__: *** ERROR ****: --- Can't open YAML file: " + self.config_file)
            self.connected = False

        # At this point, the processor is ready to handle YAMLPaths
        # self.setupYamlPath(self, None, yaml_file)

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
                # yaml.dump(self.config.data, f)
                yaml.dump(self.config.data, f, default_flow_style=False)
        except YAMLPathException as e:
            self.log.error("ConfigFromYamlPath().save(): *** ERROR ***: Can't write to file: " + output_yaml_path)

    # ---------------------
    # -- Changing Values --
    # ---------------------
    # At its simplest, you only need to supply the the YAML Path to one or more nodes to update, and
    # the value to apply to them.
    # Catching "yamlpath.exceptions.YAMLPathException" is optional
    # but usually preferred over allowing Python to dump the call stack in front of your users.
    # When using EYAML, the same applies to "yamlpath.eyaml.exceptions.EYAMLCommandException".
    #
    def set_value(self, yaml_path, new_value):
        if self.connected:
            try:
                self.config.set_value(yaml_path, new_value)
                # self.log.debug("ConfigFromYamlPath().set_value(): " + self.yaml_data)
            except YAMLPathException as ex:
                self.log.critical(ex, 119)
            except EYAMLCommandException as ex:
                self.log.critical(ex, 120)
        else:
            self.log('WARN: ConfigFromYamlPath: -- not setup ready!')

    # -------------------------
    # -- Query by YAML Path: --
    # -------------------------
    # yamlpath:
    #    ref: https://pypi.org/project/yamlpath/#get-a-yaml-value
    #    ref: https://pypi.org/project/yamlpath/
    # e.g.:
    #  Exact match: hash[name=admin]
    #  Starts With match: hash[name^adm]
    #  Ends With match: hash[name$min]
    #  Contains match: hash[name%dmi]
    #  Less Than match: hash[access_level<500]
    #  Greater Than match: hash[access_level>0]
    #  Less Than or Equal match: hash[access_level<=100]
    #  Greater Than or Equal match: hash[access_level>=0]
    #  Regular Expression matches: hash[access_level=~/^\D+$/] (the / Regular Expression delimiter
    #  can be substituted for any character you need, except white-space; note that / does not interfere
    #  with forward-slash notation and it does not need to be escaped because the entire search expression
    #  is contained within a [] pair)

    def query(self, yaml_path, getList=False) -> object:
        if not (yaml_path):
            return self.yaml_data

        values = None

        # -- Auto-converted from '/' to '.' as YamlPath specification to represent the path
        yaml_path = re.sub("^\/", "", yaml_path)
        yaml_path = re.sub("\/", ".", yaml_path)
        self.log.debug("ConfigFromYamlPath().query(): ".format(yaml_path))

        if self.connected:
            # if yaml_path is '' or yaml_path is None:
            #     return self.config
            # else:
            # yaml_path = YAMLPath("see.documentation.above.for.many.samples")
            try:
                for node_value in self.config.get_nodes(YAMLPath(yaml_path)):
                    self.log.debug("ConfigFromYamlPath().query(): Got {} from '{}'.".format(node_value, yaml_path))
                    if getList:
                        # for multiple results, aggregate them to set as collection:
                        # Do something with each node_coordinate.node (the actual data)
                        values = set()
                        values.append(node_value.node)
                    else:
                        values = node_value.node
                        break
            except YAMLPathException as ex:
                # If merely retrieving data, this exception may be deemed non-critical
                # unless your later code absolutely depends upon a result.
                self.log.error(ex)
                values = None

        return values

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
