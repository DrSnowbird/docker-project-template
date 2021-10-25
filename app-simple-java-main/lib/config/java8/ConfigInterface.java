package config;

import java.io.IOException;
import java.util.Set;

import org.json.JSONException;

public interface ConfigInterface {

	/**
	 * Return all the Keys in Set
	 * @return Set<Object>
	 */
	public Set<String> getAllKeys();
	
	/**
	 * Query Object (e.g., either String Value, JSONObject, or user-defined object) by using 'key' or 'tree-path'
	 * for JSON tree. And client has to check Object type and do proper casting.
	 * 
	 * example jsonPath; 
	 *   /myprojapp/kafka/host
	 *   /myprojapp/myproj/adapters/elasticsearch/hosts/0
	 * @param json
	 * @param jsonPath
	 * @return Object
	 * @throws IOException
	 * @throws JSONException
	 */
	public Object query(String keyOrPath) throws Exception;

	/**
	 * Query Object value with default Object value and client has to check Object type and do proper casting.
	 * @param keyOrPath
	 * @param defaultValue
	 * @return Object
	 * @throws IOException
	 * @throws JSONException
	 */
	public Object queryWithDefault(String keyOrPath, Object defaultValue) throws Exception;

	/**
	 * Query Java 'int' value as String with default 'int' value
	 * (This is a convenient method to support 'int' as default value and get 'int' value as String
	 * @param keyOrPath
	 * @param defaultValueInt
	 * @return
	 * @throws IOException
	 * @throws JSONException
	 */
	public String queryWithDefault(String keyOrPath, int defaultValueInt) throws Exception;
	
	/**
	 * Query Java 'int' value with default 'int' value
	 * (This is a convenient method to support 'int' as default value and get 'int' value
	 * @param keyOrPath
	 * @param defaultValueInt
	 * @return
	 * @throws IOException
	 * @throws JSONException
	 */
	public int queryIntWithDefault(String keyOrPath, int defaultValueInt) throws Exception;
	
	/**
	 * Whether config tree/Db contains the given keyOrPath
	 * Note that this is implementation type specific, e.g., JSON tree might not check this until actual query is executed.
	 * @param keyOrPath
	 * @return boolean: True: Yes, it has the keyOrPath; No, it does not have the keyOrPath.
	 */
	public boolean containsKey(String keyOrPath);
	
	/**
	 * Set / Overwrite property with new value (Object, or String)
	 * @param key
	 * @param value
	 */
	public void setValue(String keyOrPath, Object value);
	
	/**
	 * When No Key/Value or Null value is true, then set with new value (Object, or String)
	 * @param key
	 * @param value
	 */
	public void setValueWhenNull(String keyOrPath, Object value);
	
	/**
	 * Replace old value with new value ONLY if key existing already
	 * @param keyOrPath
	 * @param newValue
	 * @return True if Key is found and successfully replace with new Value, False otherwise.
	 */
	public boolean replaceValue(String keyOrPath, Object newValue);
	
	/**
	 * Load or Re-Load the underlying properties, configuration object, etc.
	 * @throws Exception
	 */
	public void load() throws Exception;
	
	/**
	 * Save the underlying properties, configuration file, or remote storage, etc.
	 * Note that the actual implementation might vary or even NO-OP operation!
	 * @throws Exception
	 */
	public void save() throws Exception;
	
	/**
	 * Status of Configuration Object (including Remote JSON Config Object, or Redis remote Object, Env Object, Properties Object).
	 * @return True: Yes (Available), No (NOT-Available).
	 */
	public boolean isAvailable();
	
	/**
	 * Print the contents of Configuration
	 * @return
	 */
	public String printToString();
	
}