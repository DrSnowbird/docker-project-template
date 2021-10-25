package config;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.Writer;
import java.util.Properties;

import org.apache.log4j.BasicConfigurator;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * The myprojer (Jena Reasoner) application-specific configuration
 */
public class ConfigReasoner {

	protected static final Logger log = LoggerFactory.getLogger(ConfigReasoner.class);

	// ---------------------------------------------
	// -- The Singleton JsonQueryRemote instance: --
	// ---------------------------------------------
	protected static ConfigInterface configFromJson = ConfigFromJson.getConfigFromJson(false);
	protected static ConfigInterface configFromFile = ConfigFromPropertiesFile.getConfigFromPropertiesFile(false);
	protected static ConfigInterface configFromEnv = ConfigFromEnv.getConfigFromEnv();

	// -------------------------------------------------------------------------
	// ---- Private/Protected: ----
	// -------------------------------------------------------------------------

	// ---- The final config properties for myprojer to use
	protected Properties config = new Properties();

	// ---- The default config Key/Value properties for myprojer to use
	protected static String[] propertyKeys = new String[] { "address", "port", "responderUrl", "manager", "fdnamanager",
			"messageProducer", "dummyKafka" };
	
	protected static String[] propertyValues = new String[] { "0.0.0.0", "12781", "http://0.0.0.0:5000",
			"http://0.0.0.0:7000/api", "http://0.0.0.0:8181", "0.0.0.0:9092", "0" };
	
	protected static String[] jsonPaths = new String[] { "/myprojapp/reasoner/address", "/myprojapp/reasoner/port",
			"/myprojapp/reasoner/responderUrl", "/myprojapp/reasoner/manager", "/myprojapp/reasoner/fdnamanager",
			"/myprojapp/reasoner/messageProducer", "/myprojapp/reasoner/dummyKafka" };

	// -------------------------------------------------------------------------
	// ---- The default config Properties using the above Key/Value pair:
	// -------------------------------------------------------------------------
	protected Properties defaultConf = null; // new Properties();
	protected ConfigFromPropertiesFile defaultConfFromFile = ConfigFromPropertiesFile.getConfigFromPropertiesFile("configReasoner-defaultConfig.properties", false);
	
	protected Properties jsonPathsMap = null; // new Properties();
	protected ConfigFromPropertiesFile jsonPathsMapFromFile = ConfigFromPropertiesFile.getConfigFromPropertiesFile("configReasoner-jsonPathsMap.properties", false);
	
	protected Properties dummyKeyMap = new Properties();

	// -------------------------------------------------------------------------
	// ---- The JsonQueryRemote access object: ----
	// -------------------------------------------------------------------------
	private static ConfigReasoner configReasoner = null;

	public synchronized static ConfigReasoner getConfigReasoner() {
		if (configReasoner == null) {
			configReasoner = new ConfigReasoner();
		}
		return configReasoner;
	}

	/**
	 * Constructor
	 */
	private ConfigReasoner() {
		super();
		setupDefaultConfigAndMappings();
	}

	/**
	 * Setup default configuration properties
	 */
	protected void setupDefaultConfigAndMappings() {
		this.defaultConf = this.defaultConfFromFile.getProperties();
		this.jsonPathsMap = this.jsonPathsMapFromFile.getProperties();
		for (int i = 0; i < this.propertyKeys.length; i++) {
			this.defaultConf.setProperty(this.propertyKeys[i], this.propertyValues[i]);
			this.jsonPathsMap.setProperty(this.propertyKeys[i], this.jsonPaths[i]);
			this.dummyKeyMap.setProperty(this.propertyKeys[i], this.propertyKeys[i]);
		}
		try {
			this.defaultConfFromFile.save();
			log.info("setupDefaultConfigAndMappings():SUCCESS: save ConfigReasoner's defaultConfFromFile object to external file");
		} catch (Exception e) {
			log.error("setupDefaultConfigAndMappings()ERROR: *** Can't save ConfigReasoner's defaultConfFromFile object to external file");
			e.printStackTrace();
		}
		try {
			this.jsonPathsMapFromFile.save();
			log.info("setupDefaultConfigAndMappings():SUCCESS: save ConfigReasoner's jsonPathsMapFromFile object to external file: ");
		} catch (Exception e) {
			log.error("setupDefaultConfigAndMappings():ERROR: *** Can't save ConfigReasoner's jsonPathsMapFromFile object to external file");
			e.printStackTrace();
		}
	}

	public Properties setupConfig(String[] args) throws Exception {

		// ====== Keeping the following comments as additional information for the design/code ======
		
		// http://abdn-vm-166:3000/myproj_config_LOCAL_abdn-vm-166.openkbs.org
		// JSON_CONFIG_SERVER_IP=10.128.9.166
		// JSON_CONFIG_SERVER_PORT=3000
		// JSON_CONFIG_OBJECT_UID=myproj_config_LOCAL_abdn-vm-166.openkbs.org
		// DOCKER_HOST_IP=${HOSTNAME:-0.0.0.0}
		// DOCKER_HOST_NAME=${HOSTNAME:-0.0.0.0}

		//		// --------------------------------------------------------
		//		// ---- Use JSON Config Server default: ----
		//		// --------------------------------------------------------
		//		// "reasoner": {
		//		// "address": "abdn-vm-160.openkbs.org",
		//		// "port": 12781,
		//		// "responderUrl": "http://abdn-vm-160.openkbs.org:5000",
		//		// "manager": "http://abdn-vm-160.openkbs.org:7000/api",
		//		// "fdnamanager": "http://abdn-vm-160.openkbs.org:8181",
		//		// "messageProducer": "abdn-vm-160.openkbs.org:9092",
		//		// "dummyKafka": 0
		//		// },
		//		String address = (String) configFromJson.queryWithDefault("/myprojapp/reasoner/address", "0.0.0.0");
		//		String port = configFromJson.queryWithDefault("/myprojapp/reasoner/port", 12781);
		//		String responderUrl = (String) configFromJson.queryWithDefault("/myprojapp/reasoner/responderUrl",
		//				"http://0.0.0.0:5000");
		//		String manager = (String) configFromJson.queryWithDefault("/myprojapp/reasoner/manager",
		//				"http://0.0.0.0:7000/api");
		//		String fdnamanager = (String) configFromJson.queryWithDefault("/myprojapp/reasoner/fdnamanager",
		//				"http://0.0.0.0:8181");
		//		String messageProducer = (String) configFromJson.queryWithDefault("/myprojapp/reasoner/messageProducer",
		//				"0.0.0.0:9092");
		//		String dummyKafka = configFromJson.queryWithDefault("/myprojapp/reasoner/dummyKafka", 0);
		//
		////		// -------------------------------------------------------------------------
		////		// ---- Use Central Configuration as the HigherPrecedence Properties: ----
		////		// -------------------------------------------------------------------------
		//		// Sets up where to look for certain things
		//		// Where the reasoner will bind to
		//		configFromFile.setValue("address", address);
		//		// The port the reasoner will bind to
		//		configFromFile.setValue("port", port);
		//		// As a Client to Remote access to send responses
		//		configFromFile.setValue("responderUrl", responderUrl);
		//		// As a Client to Remote access to send status updates (i.e., the reasoner
		//		// manager)
		//		configFromFile.setValue("manager", manager);
		//		// Remote access FDNA
		//		configFromFile.setValue("fdnamanager", fdnamanager);
		//		// Remote access FDNA
		//		configFromFile.setValue("messageProducer", messageProducer);
		//		// 0: disable dummy (use real Kafaka); 1: use dummy
		//		configFromFile.setValue("dummyKafka", dummyKafka);
		//
		//		// ----------------------------------------
		//		// ---- Save to Local file Properties: ----
		//		// ----------------------------------------
		//		configFromFile.save();
		//
		//        // override config with environment variables
		//
		//        for (String key : propertyKeys) {
		//            if (System.getProperty(key) != null) {
		//                config.setProperty(key, System.getProperty(key));
		//            }
		//        }

		ConfigUtilities.transferConfig(configFromJson, configFromFile, this.propertyKeys, this.defaultConf,
				this.jsonPathsMap, this.dummyKeyMap, false);
		ConfigUtilities.transferConfig(configFromEnv, configFromFile, this.propertyKeys, false);

		// --------------------------------------------------
		// ---- Final Properties for Application to use: ----
		// --------------------------------------------------
		this.config = ((ConfigFromPropertiesFile) configFromFile).getProperties();
		// ---- Save to file system ---
		configFromFile.save();
		
		// ---- Print env ---
		log.info("setupConfig(): ---- ENV (all): ----" + configFromEnv.printToString());
		return this.config;
	}

	// ---------- Test --------------

	public static void tests(String[] args) {
		ConfigReasoner configReasoner = ConfigReasoner.getConfigReasoner();
		try {
			Properties conf = configReasoner.setupConfig(args);
			System.out.println("=== Entire Config ===" + conf.toString());
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	public static void main(String[] args) {
		BasicConfigurator.configure();
		tests(args);

	}

}
