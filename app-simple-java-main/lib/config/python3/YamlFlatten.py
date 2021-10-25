# import collections
import collections.abc
import logging

import yaml

some_dict = {
    'default': {
        'heading': 'Here’s A Title',
        'learn_more': {
            'title': 'Title of Thing',
            'url': 'www.url.com',
            'description': 'description',
            'opens_new_window': 'true'
        }
    },
    'normal': {
        'heading': 'Here’s A Title',
        'learn_more': {
            'title': 'Title of Thing',
            'url': 'www.url.com',
            'description': 'description',
            'opens_new_window': 'true'
        }
    }
}

# create logger
module_logger = logging.getLogger('YamlFlatten')


# -----------
# -- Tests --
# -----------
def main():
    results = YamlFlatten.flatten(some_dict, parent_key='', sep='__')
    for item in results:
        print(item + '=' + results[item])

    YamlFlatten.save_flatten(some_dict, "data/some_dict_flatten.txt", parent_key='', sep='__', value_delimiter='=')

    ## Test YAML file
    # args: (yaml_source, yaml_flattern_file, parent_key='', sep='.', value_delimiter='=')
    YamlFlatten.convert_yaml_flatten('data/yaml-test-data-prettified.yaml', 'data/yaml-test-data-prettified-flatten.txt')
   # YamlFlatten.convert_yaml_flatten('data/simple-file.yaml', 'data/simple-file-flatten.txt')
    #YamlFlatten.convert_yaml_flatten('data/docker-compose.yaml', 'data/docker-compose-flatten.txt')

# ------------------------
# -- Class: YamlFlatten --
# ------------------------

class YamlFlatten:

    # Initializer / Instance Attributes
    def __init__(self, yaml_file):
        # create logger
        self.log = logging.getLogger('YamlFlatten')
        self.log.info('creating an instance of YamlFlatten')
        self.yaml_file = yaml_file

    def load(self, yaml_file):
        try:
            with open(self.yaml_file) as file:
                self.log.info('YamlFlatten.load(): yaml_file=' + yaml_file)
                self.yaml = yaml.load(file, Loader=yaml.FullLoader)

            sort_file = yaml.dump(self.yaml, sort_keys=True)
            print(sort_file)
            self.config = self.yaml
            self.conn_opened = 1

        except FileNotFoundError as e:
            # ref: https://docs.python.org/3/library/exceptions.html
            self.log.error("*** ERROR ****: YamlFlatten(): --- Can't open YAML file: " + yaml_file)

    # ------------------
    # -- Save to file --
    # ------------------
    def save_flatten(self, yaml_flattern_file, parent_key='', sep='.', value_delimiter='='):
        YamlFlatten.save_flatten(yaml_flattern_file, parent_key, sep, value_delimiter)

    def flatten(self, parent_key='', sep='.') -> dict:
        return YamlFlatten.flatten(self.yaml, parent_key, sep)

    ## ------------ Static methods ------------
    @staticmethod
    def convert_yaml_flatten(yaml_source, yaml_flattern_file, parent_key='', sep='.', value_delimiter='='):
        try:
            with open(yaml_source) as file:
                module_logger.info('convert_yaml_flatten(): yaml_file=' + yaml_source)
                yaml_data = yaml.load(file, Loader=yaml.FullLoader)
                sort_file = yaml.dump(yaml_data, sort_keys=True)
                results = YamlFlatten.flatten(yaml_data, parent_key, sep)
                with open(yaml_flattern_file, 'w') as f:
                    for item in results:
                        f.write(item + value_delimiter + str(results[item]) + '\n')
        except Exception as e:
            module_logger.error("convert_yaml_flatten(): *** ERROR ***:" + str(e))
            module_logger.error("convert_yaml_flatten(): *** ERROR ***: Can't write to file: ", yaml_flattern_file)

    @staticmethod
    def save_flatten(dictionary, yaml_flattern_file, parent_key='', sep='.', value_delimiter='='):
        results = YamlFlatten.flatten(dictionary, parent_key, sep)
        try:
            with open(yaml_flattern_file, 'w') as f:
                for item in results:
                    f.write(item + value_delimiter + str(results[item]) + '\n')
        except Exception as e:
            module_logger.error("ConfigFromYaml().save(): *** ERROR ***: Can't write to file: ", yaml_flattern_file)

    @staticmethod
    def flatten(dictionary, parent_key='', sep='.') -> dict:
        items = []
        for k, v in dictionary.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, collections.abc.MutableMapping):
                items.extend(YamlFlatten.flatten(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)


# -----------
# -- main --
# -----------
if __name__ == "__main__":
    # execute only if run as a script
    main()
