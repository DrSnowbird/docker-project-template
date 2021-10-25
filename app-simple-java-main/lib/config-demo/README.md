# myproj Python3 Configuration Client Libraries

# Facade Design Pattern and Abstract Base Class Pattern:
The libraries implement Python3 ABC Abstract Base Class pattern and Architecture Pattern - Facade
similar to myproj Java Configuration Client Libraries.ABC

All three types of Classes familes, namely, "Environment Var, JSON, and YAML including Remote Server" are children of the parent class, namely, ConfigAbstractClass which has to mandatory methods, so that myprojConfigManager can use the same interfaces (methods) to access any of these three families of Configuration classes without having to use different meothds to access any of these Configuration classes.
  ```
    @abstractmethod
    def query(self, path) -> object:

    @abstractmethod
    def query_with_default(self, path, default_value) -> object:

    @abstractmethod
    def is_connected(self) -> bool:
  ```
# myprojConfigManager.py - the Facade Controller
* This is the Recommended to use this instead of individual Config classes to access specific config resource(s). Here is the example in how to access ENV, JSON file (local), and Remote JSON Server, and Remote YAML server with specific order.
* "ConfigInfo class" is the common provision information for all the Config Classes in the Python3 library.
  * It has the collection of common attributes used by all sorts of configuration sources (files, remote, etc) and not all attributes will be used by all Config Classes: "(config_type='', file_path='', remote_url='', config_object_uid='', remote_host='', remote_port='', priority=0)"
  * To control how the order of config values from multiple sources, the "priroty=<number>", is used to set the priority. The "priority" is used to determine which has the highest priority in overwriting others
* Example of Usage of myprojConfigManager as Facacde Controller
```
# -- ENV --
config_env = ConfigInfo(config_type='ConfigFromEnv', priority=9)

# -- JSON (local file) --
config_yaml_remote = ConfigInfo(config_type='ConfigFromYamlRemote',
    remote_url='http://abdn-vm-166:18080/jetty_base/yaml',
    config_object_uid='myproj_config_LOCAL_abdn-vm-166.openkbs.org.yaml', 
    priority=7)
    
# -- JSON (Remote file) --
config_json_remote = ConfigInfo(config_type='ConfigFromJsonRemote',
    remote_url='http://abdn-vm-155.openkbs.org:3000/',
    config_object_uid='myproj_config_LOCAL_abdn-vm-166.openkbs.org',
    priority=5)
    
# -- YAML (local file) --
config_yaml = ConfigInfo(config_type='ConfigFromYaml', file_path='data/yaml-test-data.yaml', priority=3)

# -- YAML (Remote file) --
config_json = ConfigInfo(config_type='ConfigFromJson', file_path='data/json-test-data.json', priority=1)

# -- Register the above Config sources as a list for Facade Controller to manage: --
# -- (To test all the above, uncomment the comment symbols below.) --
conf_list = ConfigInfoList()
# conf_list.append(config_env)
conf_list.append(config_json)
conf_list.append(config_yaml)
# conf_list.append(config_json_remote)
# conf_list.append(config_yaml_remote)

# -- Facade manager control how to prioritize and access / evaluate the final value for a query: --
manager = myprojConfigManager.get_instance(conf_list)

# -- Demo: read both JSON (priority=1) and YAML files and YAML files (priority=3) --
# -- Priority: YAML's value '10.128.9.166 will 'overwirte' JSON's value 'abdn-vm-166.openkbs.org' 
# -- Results: 
#      Key/value: /myprojapp/kafka/host=10.128.9.166                                      
path = "/myprojapp/kafka/host"
value = manager.query(path)
print("Key/value: {0}={1}".format(path, value))
```
# JSON family of Configuration Classes:
There are three classes and all are children of "ConfigAbstractClass" to provide common methods. 
* All have the test code for demonstrating query syntax in "main()". 
* Please use the examples to learn how to use the simple "path-based (e.g., /myprojapp/kafka/host)" query. The path-based query is more flexible than using Python native dictionary-based '[key1][key2]...' which is not easy to maintain especially when the JSON or YAML schema changes. 
* For path-based query, it is as simple change the string of "query path, e.g., /myprojapp/kafka/host" and no need to change the code of myproj APPs' Python code except the path string - less likely to break the code. It is further possible to define a alias mapping in, say, "bsfstate-alias-config.txt", so that "bsfstate.py" use "KFAKA_HOST" as alias key to get the alias mapping to actual "path". When schema changes, only change such "alias mapping file" and no myproj APP (e.g., bsfstate.py) code change at all!
``` (file: bsfstate-alias-config.txt)
# The real Paths (values) are schema-dependent but alias (keys) are bit and will be used by the APP's code 
# Using this alias, the APP code is immuned from the physical schema changes and 
# just need to re-code the mapping values below:
#      syntax: <alias_in_APP> = <actual JSON/YAML Path>
KFAKA_HOST=/myprojapp/kafka/host
KFAKA_PORT=/myprojapp/kafka/port
ELASTICSEARCH_HOSTS=/myprojapp/myproj/adapters/elasticsearch/hosts
```

  * ConfigFromJson (simple path-based query:
    * Configuration from JSON file - using the more capable objectpath PyPI modules to provide simple path-based query.
  * ConfigFromJsonPath (capable of powerful objectpath query):
    * Configuration from JSON file - using the more capable objectpath PyPI modules to provide simple path-based query.
  * ConfigFromYamlRemote:
    * Configuration from remote JSON Coonfiguration Server, e.g. 
      * http://abdn-vm-155.openkbs.org:3000/ 
    * The Configuration Object example:   
        * http://abdn-vm-155.openkbs.org:3000/myproj_config_LOCAL_abdn-vm-166.openkbs.org

# YAML family of Configuration classes:
There are three classes and all are children of "ConfigAbstractClass" to provide common methods:
  * ConfigFromYaml:
    * Configuration from YAML file
  * ConfigFromYamlPath:
    * Configuration from YAML file using the more capable yamlpath PyPI modules for advanced query needs.
  * ConfigFromYamlRemote:
    * Configuration from remote YAML Coonfiguration Server, e.g.
        * http://abdn-vm-166:18080/jetty_base/yaml/ 
    * The Configuration Object example:   
        * http://abdn-vm-166:18080/jetty_base/yaml/myproj_config_LOCAL_abdn-vm-166.openkbs.org.yaml

# ENV Environment VAR based Configuration
There is only one ENV class to wrap around OS call to get enviornment varaible's value. However, the class also implements the abstract class, namely, ConfigAbstractClass so that the ENV configuration class will be part of Facade Design Pattern family to provide seamless common access from myprojConfigManager.
