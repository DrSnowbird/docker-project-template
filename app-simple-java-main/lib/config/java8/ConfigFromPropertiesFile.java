package config;

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.Properties;
import java.util.Set;

import org.apache.log4j.BasicConfigurator;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ConfigFromPropertiesFile implements ConfigInterface {

	protected static final Logger log = LoggerFactory.getLogger(ConfigFromPropertiesFile.class);

	// ---------------------------
	// -- The Properties File: --
	// ---------------------------
	// public static String CONFIG_PROPERTIES_FILE = "config.properties";
	public static String PROPERTIES_FILE_PATH = "configFromFile.properties";

	protected String filePath = PROPERTIES_FILE_PATH;

	protected Properties properties = new Properties();

	/**
	 * Status of Configuration Object (including Remote JSON Config Object, or Redis
	 * remote Object, Env Object, Properties Object).
	 */
	protected boolean available = false;

	/**
	 * Singularity object to share.
	 */
	static ConfigFromPropertiesFile configFromPropertiesFile = null;

	public synchronized static ConfigFromPropertiesFile getConfigFromPropertiesFile(boolean singleton) {
		return getConfigFromPropertiesFile(PROPERTIES_FILE_PATH, singleton);
	}

	public synchronized static ConfigFromPropertiesFile getConfigFromPropertiesFile(String propFilePath,
			boolean singleton) {
		if (propFilePath == null || propFilePath.length() < 1) {
			propFilePath = PROPERTIES_FILE_PATH;
		}
		if (singleton) {
			if (configFromPropertiesFile == null) {
				configFromPropertiesFile = new ConfigFromPropertiesFile(propFilePath);
			}
		} else {
			return new ConfigFromPropertiesFile(propFilePath);
		}
		return configFromPropertiesFile;
	}

	/**
	 * Constructor using filePath to be provided
	 * 
	 * @param filePath
	 */
	public ConfigFromPropertiesFile(String filePath) {
		super();
		this.filePath = filePath;
		configFromFile();
	}

	public void configFromFile() {
		InputStream input = null;
		try {
			input = new FileInputStream(filePath);
		} catch (FileNotFoundException e) {
			// ex.printStackTrace();
			log.info("configFromFile(): --- file NOT found: " + filePath);
		}
		try {
			if (input != null) {
				// load a properties file
				properties.load(input);
				// this.printAll();
			} else {
				log.warn("configFromFile(): Can't find/open filePath (Properties): " + filePath);
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	public void configFromFile(String path) {
		if (path == null || path.length() < 1) {
			filePath = PROPERTIES_FILE_PATH;
			log.warn("configFromFile(): --- empty input filePath detected! Use default: " + filePath);
		} else {
			this.filePath = path;
		}
		this.configFromFile();
	}

	/**
	 * Print out the entire configuration properties set
	 */
	//	public void printAll() {
	//		log.debug("printAll(): ---- printAll(): (entire Properties)");
	//		properties.forEach((k, v) -> log.debug("printAll(): Key : " + k + ", Value : " + v));
	//	}

	public Properties getProperties() {
		return properties;
	}

	public void setProperties(Properties properties) {
		this.properties = properties;
	}

	public void setProperty(String key, String value) {
		this.properties.setProperty(key, value);
	}

	public void setProperty(String key, int value) {
		try {
			this.properties.setProperty(key, Integer.toString(value));
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	public String getProperty(String key) {
		String value = this.properties.getProperty(key);
		log.info("getProperty(): " + key + "; value=" + value);
		return value;
	}

	public String getProperty(String key, String defaultValue) {
		String value = this.properties.getProperty(key, defaultValue);
		log.info("getProperty(): " + key + "; value=" + value);
		return value;
	}

	@Override
	public Object query(String key) throws Exception {
		String value = this.properties.getProperty(key);
		log.info("getProperty(): " + key + "; value=" + value);
		return value;
	}

	@Override
	public Object queryWithDefault(String key, Object defaultValue) throws Exception {
		String value = this.properties.getProperty(key);
		if (value == null) {
			return defaultValue;
		}
		log.info("queryWithDefault(): " + key + "; value=" + value);
		return value;
	}

	@Override
	public String queryWithDefault(String key, int defaultValueInt) throws Exception {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public int queryIntWithDefault(String key, int defaultValueInt) throws Exception {
		String value = this.properties.getProperty(key);
		int intValue = 0;
		if (value == null) {
			return defaultValueInt;
		}
		try {
			intValue = Integer.parseInt(value);
		} catch (Exception ne) {
			return defaultValueInt;
		}
		log.info("queryIntWithDefault(): " + key + "; value=" + value);
		return intValue;
	}

	@Override
	public void setValue(String key, Object value) {
		this.setProperty(key, (String) value);
	}

	@Override
	public void setValueWhenNull(String key, Object value) {
		if (key != null && key.length() > 0 && this.properties != null) {
			try {
				if (this.query(key) == null) {
					this.setValue(key, value);
				}
			} catch (Exception e) {
				this.setValue(key, value);
				e.printStackTrace();
			}
		}
	}

	@Override
	public boolean replaceValue(String key, Object newValue) {
		if (this.properties.containsKey(key)) {
			this.setValue(key, newValue);
			return true;
		}
		return false;
	}

	@Override
	public void load() throws Exception {
		this.loadProperties();
	}

	@Override
	public void save() throws Exception {
		this.writeProperties();
	}

	@Override
	public boolean isAvailable() {
		return this.available;
	}

	@Override
	public boolean containsKey(String key) {
		return this.properties.containsKey(key);
	}

	@Override
	public Set<String> getAllKeys() {
		return this.getAllKeys();
	}

	@Override
	public String printToString() {
		return this.properties.toString();
	}

	public int getPropertyInt(String key) throws Exception {
		String value = this.properties.getProperty(key);
		int intValue = 0;
		try {
			intValue = Integer.parseInt(value);
		} catch (Exception e) {
			e.printStackTrace();
			throw e;
		}
		log.info("getPropertyInt(): " + key + "; value=" + value);
		return intValue;
	}

	public int getPropertyInt(String key, int defaultInt) throws Exception {
		String value = this.properties.getProperty(key, String.valueOf(defaultInt));
		int intValue = 0;
		try {
			intValue = Integer.parseInt(value);
		} catch (Exception ne) {
			return defaultInt;
		}
		log.info("getPropertyInt(): " + key + "; value=" + value);
		return intValue;
	}

	public void writeProperties() {
		this.writeProperties(this.filePath);
	}

	public void writeProperties(String path) {
		String actPath = this.filePath;
		if (path == null || path.length() < 1) {
			actPath = PROPERTIES_FILE_PATH;
		}
		try (OutputStream output = new FileOutputStream(actPath)) {
			// -- save properties to project root folder
			properties.store(output, null);
			log.debug("writeProperties():SUCCESS:" + this.filePath + ": " + properties);
		} catch (IOException io) {
			io.printStackTrace();
			log.warn("writeProperties():FAIL: " + this.filePath + "Can't write to external file: ");
		}
	}

	public void loadProperties() {
		this.loadProperties(this.filePath);
	}

	public void loadProperties(String path) {
		String actPath = this.filePath;
		if (path == null || path.length() < 1) {
			actPath = PROPERTIES_FILE_PATH;
		}
		this.available = false;
		try (InputStream input = new FileInputStream(actPath)) {
			// load a properties file
			properties.load(input);
			// log.info("loadProperties(): " + properties);
			this.available = true;
		} catch (IOException io) {
			io.printStackTrace();
		}
	}

	// ---------- Test --------------

	public static void writeTestProperties(String[] args) {

		try (OutputStream output = new FileOutputStream("TEST-LOAD-SAVE_ConfigFromProperties.properties")) {

			Properties prop = new Properties();

			// set the properties value
			prop.setProperty("db.url", "localhost");
			prop.setProperty("db.user", "smith");
			prop.setProperty("db.password", "password");

			// save properties to project root folder
			prop.store(output, null);

			// System.out.println(prop);

		} catch (IOException io) {
			io.printStackTrace();
		}
	}

	public static void loadTestProperties(String[] args) {

		try (InputStream input = new FileInputStream("TEST-LOAD-SAVE_ConfigFromProperties.properties")) {

			Properties prop = new Properties();
			// load a properties file
			prop.load(input);

			// get the property value and print it out
			System.out.println("--------- loadTestProperties -------");
			System.out.println(prop.getProperty("db.url"));
			System.out.println(prop.getProperty("db.user"));
			System.out.println(prop.getProperty("db.password"));

		} catch (Exception ex) {
			ex.printStackTrace();
		}
	}

	public static void tests(String[] args) {

		loadTestProperties(null);
		writeTestProperties(null);
		loadTestProperties(null);

		ConfigFromPropertiesFile cfg = ConfigFromPropertiesFile
				.getConfigFromPropertiesFile("Test-ConfigFromPropertiesFil.properties", false);
		log.debug(cfg.printToString());

		cfg.setProperty("db.url1", "localhost");
		cfg.setProperty("db.user1", "mkyong");
		cfg.setProperty("db.password1", "password");
		log.debug(cfg.printToString());

		cfg.setProperty("testKey", "testValue");
		log.debug(cfg.printToString());
		cfg.writeProperties();

		cfg.loadProperties();
		log.debug(cfg.printToString());

		System.out.println("==== Entire Config Tree/DB: " + cfg.printToString());

	}

	public static void main(String[] args) {
		BasicConfigurator.configure();
		tests(args);

	}

}
