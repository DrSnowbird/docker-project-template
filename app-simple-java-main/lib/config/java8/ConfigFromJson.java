package config;

import java.util.HashSet;
import java.util.Set;

import org.apache.log4j.BasicConfigurator;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ConfigFromJson implements ConfigInterface {

	protected static final Logger log = LoggerFactory.getLogger(ConfigFromJson.class);

	// ---------------------------
	// -- The JSON Server URL: --
	// ---------------------------
	public static String jsonServerURL_DEFAULT = "http://abdn-vm-166.openkbs.org:3000/";
	// ---------------------------------------------------------------------------
	// -- JSON Configuration Unique UID, e.g., "myproj_rsheu_dev_abdn_vm_166" : --
	// ---------------------------------------------------------------------------
	public static String jsonConfigUID_DEFAULT = "myproj_config_LOCAL_abdn-vm-166.openkbs.org";
	// http://abdn-vm-166:3000/myproj_config_LOCAL_abdn-vm-155.openkbs.org

	public static String DOCKER_HOST_IP = ConfigFromEnv.getProperty("DOCKER_HOST_IP", "0.0.0.0");
	public static String DOCKER_HOST_NAME = ConfigFromEnv.getProperty("DOCKER_HOST_NAME", "0.0.0.0");
	public static String JSON_CONFIG_SERVER_IP = ConfigFromEnv.getProperty("JSON_CONFIG_SERVER_IP", "0.0.0.0");
	public static String JSON_CONFIG_SERVER_PORT = ConfigFromEnv.getProperty("JSON_CONFIG_SERVER_PORT", "3000");
	public static String JSON_CONFIG_OBJECT_UID = ConfigFromEnv.getProperty("JSON_CONFIG_OBJECT_UID",
			"myproj_config_LOCAL_" + DOCKER_HOST_NAME);
	public static String JSON_CONFIG_SERVER_URL = ConfigFromEnv.getProperty("JSON_CONFIG_SERVER_URL",
			"http://" + JSON_CONFIG_SERVER_IP + ":" + JSON_CONFIG_SERVER_PORT);

	// -------------------------------------------------------------------------
	// ---- Private variables: ----
	// -------------------------------------------------------------------------
	private String jsonServerURL = jsonServerURL_DEFAULT;
	private String jsonConfigUID = jsonConfigUID_DEFAULT;
	protected JsonQueryRemote jsonQueryRemote = null;
	/**
	 * Status of Configuration Object (including Remote JSON Config Object, or Redis
	 * remote Object, Env Object, Properties Object).
	 */
	protected boolean available = false;

	// -------------------------------------------------------------------------
	// ---- The JsonQueryRemote access object: ----
	// -------------------------------------------------------------------------
	private static ConfigFromJson configFromJson = null;

	public static ConfigFromJson getConfigFromJson(boolean singleton) {
		return getConfigFromJson(jsonServerURL_DEFAULT, jsonConfigUID_DEFAULT, singleton);
	}

	public static ConfigFromJson getConfigFromJson(String jsonServerURL, String jsonConfigUID, boolean singleton) {
		synchronized (jsonServerURL_DEFAULT) {
			if (jsonServerURL == null || jsonServerURL.length() <= 0) {
				jsonServerURL = jsonServerURL_DEFAULT;
				log.info("getJsonQueryRemote(); -- Use default jsonServerURL = " + jsonServerURL_DEFAULT);
			}
			// if (jsonConfigUID == null || jsonConfigUID.length() <= 0) {
			// jsonConfigUID = jsonConfigUID_DEFAULT;
			// log.info("getJsonQueryRemote(); -- Use default jsonConfigUID = " +
			// jsonConfigUID_DEFAULT);
			// }
			if (singleton) {
				if (configFromJson == null) {
					configFromJson = new ConfigFromJson(jsonServerURL, jsonConfigUID, singleton);
				} else {
					return configFromJson;
				}
			} else {
				return new ConfigFromJson(jsonServerURL, jsonConfigUID, singleton);
			}
			if (configFromJson == null) {
				configFromJson = new ConfigFromJson(jsonServerURL, jsonConfigUID, singleton);
			}
		}
		return configFromJson;
	}

	/** Constructor
	 * 
	 * @param jsonServerURL
	 * @param jsonConfigUID
	 * @param singleton
	 */
	protected ConfigFromJson(String jsonServerURL, String jsonConfigUID, boolean singleton) {
		super();
		if (jsonServerURL == null || jsonServerURL.length() <= 5) {
			log.error(
					"ConfigFromJson(String jsonServerURL, String jsonConfigUID, boolean singleton): *** ERROR ***: input argument jsonServerURL is null");
		} else {
			this.jsonServerURL = jsonServerURL;
			this.jsonConfigUID = jsonConfigUID;
			this.jsonQueryRemote = JsonQueryRemote.getJsonQueryRemote(jsonServerURL, jsonConfigUID, singleton);
		}
	}

	/**
	 * Constructor with default values (jsonServerURL_DEFAULT, jsonConfigUID_DEFAULT)
	 * @param singleton
	 */
	protected ConfigFromJson(boolean singleton) {
		super();
		this.jsonServerURL = jsonServerURL_DEFAULT;
		this.jsonConfigUID = jsonConfigUID_DEFAULT;
		this.jsonQueryRemote = JsonQueryRemote.getJsonQueryRemote(jsonServerURL, jsonConfigUID, singleton);
	}

	@Override
	public Object query(String jsonPath) throws Exception {
		if (jsonPath == null || jsonPath.length() <= 0 ) {
			return null;
		}
		Object obj = this.jsonQueryRemote.query(jsonPath);
		String value = null;
		if (obj instanceof Integer) {
			value = ((Integer) obj).toString();
		} else {
			value = (String) obj;
		}
		return value;
	}

	@Override
	public Object queryWithDefault(String jsonPath, Object defaultValue) throws Exception {
		if (this.jsonQueryRemote == null) {
			log.error(
					"queryWithDefault(String jsonPath, Object defaultValue): ): *** ERROR ***: jsonQueryRemote == null");
		}
		Object obj = this.jsonQueryRemote.queryWithDefault(jsonPath, defaultValue);
		String value = null;
		if (obj instanceof Integer) {
			value = ((Integer) obj).toString();
		} else {
			value = (String) obj;
		}
		return value;
	}

	@Override
	public String queryWithDefault(String jsonPath, int defaultValueInt) throws Exception {
		return this.jsonQueryRemote.queryWithDefault(jsonPath, defaultValueInt);
	}

	@Override
	public int queryIntWithDefault(String jsonPath, int defaultValueInt) throws Exception {
		return this.jsonQueryRemote.queryIntWithDefault(jsonPath, defaultValueInt);
	}

	@Override
	public void setValue(String jsonPath, Object value) {
		log.warn("--- setValue(String jsonPath, Object value): this implementation is NO-OP!");
	}

	@Override
	public void setValueWhenNull(String jsonPath, Object value) {
		log.warn("--- replaceValue(String jsonPath, Object newValue): this implementation is NO-OP!");
	}

	@Override
	public boolean replaceValue(String jsonPath, Object newValue) {
		log.warn("--- replaceValue(String jsonPath, Object newValue): this implementation is NO-OP!");
		return true;
	}

	@Override
	public void load() throws Exception {
		this.jsonQueryRemote.load();
		this.available = this.jsonQueryRemote.isAvailable();
	}

	@Override
	public void save() throws Exception {
		log.warn("--- save: this implementation is NO-OP!");
	}

	@Override
	public boolean containsKey(String jsonPath) {
		try {
			if (this.jsonQueryRemote.query(jsonPath) != null) {
				return true;
			}
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			return false;
		}
		return false;
	}

	@Override
	public boolean isAvailable() {
		this.available = this.jsonQueryRemote.isAvailable();
		return this.available;
	}

	@Override
	public Set<String> getAllKeys() {
		// -- Currently not implemented - TBD --
		return new HashSet<String>();
	}

	@Override
	public String printToString() {
		return this.jsonQueryRemote.printToString();
	}

	// ---------- Test --------------

	public static void tests(String[] args) {
		// ConfigFromJson config = ConfigFromJson.getConfigFromJson(true);
		ConfigFromJson config = ConfigFromJson.getConfigFromJson(false);
		System.out.println(config.printToString());
	}

	public static void main(String[] args) {
		BasicConfigurator.configure();
		tests(args);

	}
}