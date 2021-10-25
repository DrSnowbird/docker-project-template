import json
import logging
import re
import objectpath
import pymongo
from objectpath import Tree

from ConfigAbstractClass import ConfigAbstractClass
from ConfigInfo import ConfigInfo
from UtilityDictionary import UtilityDictionary

module_logger = logging.getLogger('ConfigFromRemote')


class MongoInfo():
    database_default = 'my_test_db'
    collection_default = 'my_collection'

    def __init__(self, user='mongoadmin', password='mongoadmin', host='127.0.0.1', port='27017', auth_source='admin',
                 database=database_default, collection=collection_default):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.auth_source = auth_source
        self.database = database
        self.collection = collection

    def get_conn_str(self):
        # mongodb://mongoadmin:mongoadmin@127.0.0.1:27017/?authSource=admin
        conn_str = "mongodb://{user}:{password}@{host}:{port}/?authSource={auth_source}".format(
            user=self.user, password=self.password, host=self.host, port=self.port,
            auth_source=self.auth_source)
        return conn_str


# -----------
# -- Tests --
# -----------
def main():
    logging.basicConfig(level='DEBUG')

    #  Singleton.getInstance()
    # ----------------------------------------------------------------------------
    # -- Setup Connection:
    # ----------------------------------------------------------------------------
    info = MongoInfo()
    mongo = MongoManager.get_instance(info)

    # -- insert dict (one document):
    mydict = {"name": "Peter", "address": "Lowstreet 27"}
    x = mongo.insert(mydict, "test_collection_123")
    print("insert mydcit: " + str(x))

    # -- insert list of dict (i.e., multi-doc): --
    mylist = [
      { "_id": 1, "name": "John", "address": "Highway 37"},
      { "_id": 2, "name": "Peter", "address": "Lowstreet 27"},
      { "_id": 3, "name": "Amy", "address": "Apple st 652"},
      { "_id": 4, "name": "Hannah", "address": "Mountain 21"},
      { "_id": 5, "name": "Michael", "address": "Valley 345"},
      { "_id": 6, "name": "Sandy", "address": "Ocean blvd 2"},
      { "_id": 7, "name": "Betty", "address": "Green Grass 1"},
      { "_id": 8, "name": "Richard", "address": "Sky st 331"},
      { "_id": 9, "name": "Susan", "address": "One way 98"},
      { "_id": 10, "name": "Vicky", "address": "Yellow Garden 2"},
      { "_id": 11, "name": "Ben", "address": "Park Lane 38"},
      { "_id": 12, "name": "William", "address": "Central st 954"},
      { "_id": 13, "name": "Chuck", "address": "Main Road 989"},
      { "_id": 14, "name": "Viola", "address": "Sideway 1633"}
    ]
    x = mongo.insert(mylist, "test_collection_list_123")
    print("insert mylist: " + str(x))

    # -- JSON test data: --
    # -- json.loads special handling with logging's escape single-quote:
    str_json='{"myprojapp":{"controller":{"disable":false,"host":"abdn-vm-166.openkbs.org","port":6100},"fdna":{"host":"abdn-vm-166.openkbs.org","port":8181},"manager":{"batch_size":10,"car_filter":{"sources":[]},"event_filters":null,"host":"abdn-vm-166.openkbs.org","port":7000,"protocol":"http"},"planner":{"training":["metrics/json/BRAWL_myproj_20170414_06_state_final.json","metrics/json/BRAWL_myproj_20170414_07_state_final.json"]},"plugin":{"configurable":{"path":"configurable_parameters.yml"},"name":"myproj"},"reasoner":{"address":"abdn-vm-166.openkbs.org","dummyKafka":0,"fdnamanager":"http://abdn-vm-166.openkbs.org:8181","manager":"http://abdn-vm-166.openkbs.org:7000/api","messageProducer":"abdn-vm-166.openkbs.org:9092","port":12781,"responderUrl":"http://abdn-vm-166.openkbs.org:5000"},"myproj":{"adapters":{"bsf":{"agents":[{"agent":"Normalizer"},{"agent":"Step_Deduplicator"},{"agent":"Predicator"},{"agent":"GapFiller"},{"agent":"ModificationJanitor"}],"config":"Caldera Tech Plus","disable":false,"file":"metrics/json/5005CASCADEreports.json","password":"cascade","time_step":60,"url":"http://myproj-dev.openkbs.org:5003","username":"cascade"},"cascade":{"config":"Caldera Tech Plus","disable":false,"password":"cascade","url":"http://myproj-dev.openkbs.org:5003","username":"cascade","verify":false},"elasticsearch":{"disable":false,"hosts":["myproj-dev.openkbs.org:9200","es01.openkbs.org:9200","es02.openkbs.org:9200","es03.openkbs.org:9200"]}},"host":"abdn-vm-166.openkbs.org","log_dir":"log","logger":{"host":"abdn-vm-166.openkbs.org","logging":{"formatters":{"json":{"format":"{\'elativeCreated\': %(relativeCreated)d, \'logger\': \'%(name)s\', \'level\': \'%(levelname)s\', \'message\': \'%(message)s\'}"}},"handlers":{"plannerWorkflowFile":{"()":"ext://__main__.rotate_if_exists_file_handler","backupCount":50,"filename":"logs/workflow.log","formatter":"json","level":"DEBUG"}},"root":{"handlers":["plannerWorkflowFile"],"level":"DEBUG"},"version":1}},"port":6101},"responder":{"host":"abdn-vm-166.openkbs.org","port":5000},"zookeeper":{"host":"abdn-vm-166.openkbs.org","port":2181}}}'
    dict_json = json.loads(str_json)

    # # -- some JSON:
    # x = '{ "name":"John", "age":30, "city":"New York"}'
    # dict_json = json.loads(x)

    x = mongo.insert(dict_json, "test_json_123")

    print("insert str_json: " + str(x))

    path="myprojapp.controller.host"
    result = mongo.query(path, "test_json_123")
    print("Query str_json: path:" + path + ", value=" + str(result))

# ---------------------------
# -- Class: MongoManager --
# ---------------------------
class MongoManager(ConfigAbstractClass):
    treeObject: Tree
    jsonData: dict

    __instance = None

    @staticmethod
    def get_instance(args: MongoInfo, singleton: bool = True):
        """ Static access method. """
        if singleton:
            if MongoManager.__instance is None:
                MongoManager.__instance = MongoManager(args)
            return MongoManager.__instance
        else:
            return MongoManager(args)

    def __init__(self, info: MongoInfo):
        self.jsonData = {}
        self.treeObject = {}
        """ Virtually private constructor. """
        if MongoManager.__instance is None:
            MongoManager.__instance = self
        else:
            return

        self.log = logging.getLogger('ConfigFromMongo')
        self.log.info('creating an instance of ConfigFromMongo')

        self.info = info
        try:
            if self.info:
                self.client = pymongo.MongoClient(self.info.get_conn_str())
                if self.info.database:
                    self.database = self.client[self.info.database]
                    self.connected = True
                else:
                    self.connected = False
            else:
                self.connected = False
        except Exception as e:
            self.connected = False
            self.log.error("*** ERROR: " + str(e))

    def is_connected(self) -> bool:
        return self.connected

    def get_database(self):
        if not self.connected:
            return None
        return self.database

    def collection_list(self) -> object:
        if self.connected:
            collist = self.database.list_collection_names()
            return collist
        else:
            return None

    def database_list(self) -> object:
        if self.connected:
            dblist = self.client.list_database_names()
            return dblist
        else:
            return None

    def check_db_exist(self, database_name) -> bool:
        if self.connected:
            dblist = self.client.list_database_names()
            if database_name in dblist:
                self.log.info("check_db_exist(): database exists: " + database_name)
                return True
            else:
                return False
        else:
            return False

    def check_collection_exist(self, collection_name) -> bool:
        if self.connected:
            collist = self.database.list_collection_names()
            if collection_name in collist:
                self.log.info("check_collection_exist(): database exists: " + collection_name)
            else:
                return False
        else:
            return False

    # ----------------------------------------
    # -- Insert data string in JSON  --
    # ----------------------------------------
    def insert_json(self, json_str: str, collection: str = MongoInfo.collection_default) -> object:
        if not self.connected:
            return None
        if self.connected and dict and collection:
            self.jsonData = json.loads(json_str)
            self.log.debug(json.dumps(json_str, indent=4, sort_keys=True))
            # -- Using "objectpath" to query the JSON Tree.
            self.treeObject = objectpath.Tree(self.jsonData)
            return self.insert (json_str, collection)
        else:
            self.log.error("insert(): *** ERROR: missing arguments or database not connected or setup!")
            return None

    # -----------
    # Return Object could be either "dict" object of "array of dict objects":
    # So, the client code needs to detect the results:
    def collection_to_json(self, filter: object = {}, collection: str = MongoInfo.collection_default) -> object:
        if not self.connected:
            return None
        # -- Example --
        # myquery = { "address": { "$gt": "S" } }
        # mydoc = mycol.find(myquery)
        # for x in mydoc:
        #   print(x)
        if self.treeObject:
            return self.treeObject

        my_coll = self.database[collection]
        total_count = 0
        my_docs = None
        if filter and isinstance(filter, dict):
            my_docs = my_coll.find(filter, { "_id": 0} )
            total_count = my_coll.count_documents(filter)
        else:
            self.log.info("collection_to_json():INFO: input args, filter is not dict (dictionary) type!")
            my_docs = my_coll.find({}, { "_id": 0} )
            total_count = my_coll.count_documents({})
            results = []
            # Start from one as type_documents_count also starts from 1.
            for x in my_coll.find():
                print(x)
                results.append(x)

            if results and len(results) == 1:
                return results[0]
            else:
                return results

            # for i, document in enumerate(my_docs, 1):
            #     self.log.debug(json.dumps(document, indent=4, sort_keys=True))
            #     # json.dumps(document, default=str)
            #     # -- Using "objectpath" to query the JSON Tree.
            #     jsonData = document
            #     return jsonData;
            #     # self.treeObject = objectpath.Tree(document)
            #     # self.connected = True
            #     # return self.treeObject

            return None

    # -----------------------------------------------------------
    # -- Insert data (dict, JSON, YAML) object: list or dict:  --
    # -----------------------------------------------------------
    def insert(self, data, collection: str = MongoInfo.collection_default) -> object:
        if not self.connected:
            return None
        if self.connected and dict and collection:
            self.log.debug("data type=" + str(type(data)))
            try:
                if isinstance(data, dict):
                    my_coll = self.database[collection]
                    x = my_coll.insert_one(data)
                    self.log.debug("insert(): --- SUCCESS: insert_one: " + str(data))
                    return x
                elif isinstance(data, list):
                    # -- multi-records insert
                    my_coll = self.database[collection]
                    x = my_coll.insert_many(data)
                    self.log.debug("insert(): --- SUCCESS: insert_many: " + str(data))
                    return x
                elif isinstance(data, str):
                    # JSON maybe?
                    self.jsonData, config_format = UtilityDictionary.load_config_string(data)
                    # -- Using "objectpath" to query the JSON Tree.
                    self.treeObject = objectpath.Tree(self.jsonData)
                    self.connected = True
                    my_coll = self.database[collection]
                    x = my_coll.insert_one(data)
                    self.log.debug("insert(): --- SUCCESS: insert_one: " + str(data))
                    return x
            except Exception as e:
                self.log.error("insert(): *** ERROR: database exception: " + str(e))
                return None
        else:
            self.log.error("insert(): *** ERROR: missing arguments or database not connected or setup!")
            return None

    # -------------------
    # -- Query:        --
    # -------------------
    def query(self, query_str: str, collection: str = MongoInfo.collection_default) -> object:
        if not self.connected:
            return None
        # myquery = { "address": { "$gt": "S" } }
        # mydoc = mycol.find(myquery)
        # for x in mydoc:
        #   print(x)
        my_coll = self.database[collection]
        if query_str:
            self.log.debug('query(): query_str=' + query_str)
            m = re.match("^\{.*", query_str.strip())
            if m:
                # -- assuming Mongo qquery string: --
                tmp = query_str
                mydoc = my_coll.find(query_str)
                return mydoc
            else:
                m2 = re.match("\$", query_str)
                if not m2:
                    tmp2 = query_str
                    query_str = str("$..") + re.sub("\/", ".", tmp2)
                my_dict = self.collection_to_json(collection=collection)
                result = self.query_json(my_dict, query_str)
                return result;
        else:
            return None

    # --------------------------------------
    # -- Query with default_value by Path --
    # --------------------------------------
    def query_with_default(self, path, default_value) -> object:
        if not self.connected:
            return None
        result = self.query(path)
        if result is None:
            return default_value
        else:
            return result

    def query_json(self, json_dict, path: str) -> object:
        if isinstance(json_dict, list):
            return self.query_json_multi_dict(json_dict, path)
        elif isinstance(json_dict, dict):
            return self.query_json_single_dict(json_dict, path)
        else:
            self.log.error("query_json():ERROR: input json_dicts is neither dict or list of dict type! Abort!")
            return None

    def query_json_multi_dict(self, json_dicts: [], path: str) -> object:
        results=[]
        for d in json_dicts:
            result = self.query_json(d, path)
            if result:
                results.append(result)
        return results

    # -------------------
    # -- Query by Path --
    # -------------------
    def query_json_single_dict(self, json_dict: dict, path: str) -> object:
        if not dict:
            return None
        if path:
            self.log.debug('query_json(): path=' + path)
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
                treeObject = objectpath.Tree(json_dict)
                if treeObject.execute(path):
                    return tuple(treeObject.execute(path))[0]
                else:
                    return None
            except Exception as e:
                self.log.error("query_json(): *** ERROR: " + e)
                return None
        else:
            return self.jsonData

    # --------------------------------------
    # -- Query with default_value by Path --
    # --------------------------------------
    def query_json_with_default(self, json_dict: object, path, default_value) -> object:
        result = self.query_json(json_dict, path)
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
