package config;

import java.lang.reflect.Field;
import java.util.Map;
import java.util.Properties;
import java.util.Set;

import org.apache.log4j.BasicConfigurator;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ConfigFromEnv implements ConfigInterface {

	protected static final Logger log = LoggerFactory.getLogger(ConfigFromEnv.class);

	protected static Map<String, String> envMap = System.getenv();

	/**
	 * Status of Configuration Object (including Remote JSON Config Object, or Redis remote Object, Env Object, Properties Object).
	 */
	protected boolean available = false;
	

	// ---------------------------------------------
	// -- The Singleton JsonQueryRemote instance: --
	// ---------------------------------------------
	protected static ConfigFromEnv configFromEnv = null;

	/**
	 * Singleton object
	 * 
	 * @return
	 */
	public static synchronized ConfigFromEnv getConfigFromEnv() {
		if (configFromEnv == null) {
			configFromEnv = new ConfigFromEnv();
		}
		return configFromEnv;
	}

	protected ConfigFromEnv() {
		super();
	}

	/**
	 * Print current JVM Env vars
	 */
	public static void printEnv() {
		for (String key : envMap.keySet()) {
			log.debug("printEnv(): " + key + "; value=" + envMap.get(key));
		}
	}

	/**
	 * Get int value for a given Key
	 * 
	 * @param key
	 * @return int
	 */
	public static int getPropertyInt(String key) throws Exception {
		String value = envMap.get(key);
		int intValue = 0;
		try {
			intValue = Integer.parseInt(value);
		} catch (Exception e) {
			// e.printStackTrace();
			throw e;
		}
		log.debug("getPropertyInt(String key): " + key + "; value=" + value);
		return intValue;
	}

	/**
	 * Get Env. Variable int value with default value if not found.
	 * 
	 * @param key
	 * @param defaultValueInt
	 * @return
	 */
	public static int getPropertyInt(String key, int defaultValueInt) {
		String value = envMap.get(key);
		int intValue = 0;
		try {
			if (value == null) {
				intValue = defaultValueInt;
			} else {
				intValue = Integer.parseInt(value);
			}
		} catch (Exception ne) {
			intValue = defaultValueInt;
		}
		log.debug("getPropertyInt(String key, int defaultValueInt): " + key + "; value=" + intValue);
		return intValue;
	}

	@Override
	public Object query(String key) throws Exception {
		return this.envMap.get(key);
	}

	@Override
	public Object queryWithDefault(String key, Object defaultValue) throws Exception {
		if (key == null) {
			return this.envMap;
		}
		Object result = this.envMap.get(key);
		if (result == null) {
			return defaultValue;
		}
		return result;
	}

	@Override
	public String queryWithDefault(String key, int defaultValueInt) throws Exception {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public int queryIntWithDefault(String key, int defaultValueInt) throws Exception {
		if (key == null) {
			return defaultValueInt;
		}
		Object jObject = this.envMap.get(key);
		if (jObject == null) {
			return defaultValueInt;
		}
		if (jObject instanceof Integer) {
			return ((Integer) jObject).intValue();
		} else {
			int intValue = Integer.parseInt((String) jObject);
			log.debug("queryWithDefault(String jsonPath, int defaultValueInt): --- Return value not Integer object");
			return intValue;
		}
	}

	@SuppressWarnings({ "unchecked" })
	protected void updateEnv(String key, String value) throws ReflectiveOperationException {
		// Map<String, String> env = System.getenv();
		Field field = this.envMap.getClass().getDeclaredField("m");
		field.setAccessible(true);
		((Map<String, String>) field.get(this.envMap)).put(key, value);
	}

	@Override
	public void setValue(String key, Object value) {
		try {
			this.updateEnv(key, (String) value);
		} catch (ReflectiveOperationException e) {
			e.printStackTrace();
		}
	}

	@Override
	public void setValueWhenNull(String key, Object value) {
		if (key != null && key.length() > 0) {
			if (this.envMap.get(key) == null) {
				this.setValue(key, value);
			}
		}
	}

	@Override
	public boolean replaceValue(String key, Object newValue) {
		if (this.envMap.containsKey(key)) {
			this.envMap.replace(key, (String) newValue);
			return true;
		} else {
			return false;
		}
	}

	@Override
	public void load() throws Exception {
		envMap = System.getenv();
		if (this.envMap != null) {
			this.available = true;
		} else {
			this.available = false;
		}
	}

	@Override
	public void save() throws Exception {
		// Basically no operation for now.
	}
	
	@Override
	public boolean containsKey(String key) {
		return (this.envMap.containsKey(key));
	}

	@Override
	public boolean isAvailable() {
		return this.available;
	}

	@Override
	public Set<String> getAllKeys() {
		return this.envMap.keySet();
	}

	@Override
	public String printToString() {
		return this.envMap.toString();
	}

	/**
	 * Get specific Env var's value IF not found empty string value will be returned
	 * to prevent exception in null handling downstream.
	 * 
	 * @param key
	 * @return String
	 */
	public static String getProperty(String key) {
		if (key != null && key.length() > 0) {
			if (envMap.containsKey(key)) {
				String value = envMap.get(key);
				log.debug("getProperty(String key):  " + key + "; value=" + value);
				return value;
			} else {
				log.debug("getProperty(String key, String defaultValue): key= " + key + " is not found!");
			}
		}
		return "";
	}

	/**
	 * Get Env. Variable's value with default value (String)
	 * 
	 * @param key
	 * @param defaultValue
	 * @return String
	 */
	public static String getProperty(String key, String defaultValue) {
		if (key != null && key.length() > 0) {
			if (envMap.containsKey(key)) {
				String value = envMap.get(key);
				log.debug("getProperty(String key, String defaultValue):  " + key + "; value=" + value);
				return value;
			} else {
				log.debug("getProperty(String key): key= " + key + " is not found! Use default: " + defaultValue);
			}
		}
		return defaultValue;
	}

	// ---------- Test --------------
	
	public static void tests(String[] args) {
		ConfigFromEnv env = ConfigFromEnv.getConfigFromEnv();
		String key = "ABC";
		log.debug("get ABC: " + ConfigFromEnv.getProperty("ABC"));
		log.debug("get ABC: " + ConfigFromEnv.getProperty("ABC", "abc"));
//		try {
//			System.out.println("get ABCD:" + ConfigFromEnv.getPropertyInt("NUMER1"));
//		} catch (Exception e) {
//			// TODO Auto-generated catch block
//			e.printStackTrace();
//		}

		log.info("get NUMER1: " + ConfigFromEnv.getPropertyInt("NUMER1", 1111));

		env.setValue("NEW-ENV-1", "New-Value-for-Env");
		try {
			env.load();
		} catch (Exception e) {
			e.printStackTrace();
		}
		log.info("get NEW-ENV-1: " + ConfigFromEnv.getProperty("NEW-ENV-1"));
		
		System.out.println(env.toString());
		printEnv();

	}

	public static void main(String[] args) {
		BasicConfigurator.configure();
		tests(args);

	}

}
