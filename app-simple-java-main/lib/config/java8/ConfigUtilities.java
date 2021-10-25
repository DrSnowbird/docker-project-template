package config;

import java.util.Properties;

import org.apache.jena.atlas.logging.Log;
import org.apache.log4j.BasicConfigurator;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ConfigUtilities {

	protected static final Logger log = LoggerFactory.getLogger(ConfigUtilities.class);
	
	/**
	 * Merge only properties only Target has the properties defined.
	 * @param source
	 * @param target
	 * @param intersectOnly: True: Intersect-merge on target, False: Union-merge (merge everything from Source into Target
	 * @return true: success; false: fail
	 */
	/**
	 * 
	 * @param source
	 * @param target
	 * @param intersectOnly
	 *   Intersect-Merge: merge only what Target Key has from Source
	 *   Union-Merge: merge everything from Source to Target while use "ReplaceOnly" to decide whether to overwrite or not.
	 * @param replaceOnly
	 * 	 Source: [Key11:Value-A] will overwrite the Target: [Key11:Value-B] ==(After)==> [Key11:Value-A] in Target.
	 *   Source: [Key22:Value-A] will overwrite the Target: [Not Existing] ==(After)==> [Not Existing] in Target.
	 *   Source: [Not Existing] will overwrite the Target: [Key33:Value-B] ==(After)==> [Key33:Value-B in Target.
	 * @return
	 */
	public static boolean mergeConfig(ConfigInterface source, ConfigInterface target, boolean intersectOnly, boolean replaceOnly) {
		if (replaceOnly) {
			return transferConfig (source, target, (String[]) target.getAllKeys().toArray(), replaceOnly);
		} else {
			return transferConfig (source, target, (String[]) source.getAllKeys().toArray(), replaceOnly);
		}
	}

	/**
	 * Merge from Source into Target with choice of "replaceOnly" or "Overwrite mode merge"
	 * E.g., 
	 *   Source: [Key11:Value-A] will overwrite the Target: [Key11:Value-B] ==(After)==> [Key11:Value-A] in Target.
	 *   Source: [Key22:Value-A] will overwrite the Target: [Not Existing] ==(After)==> [Not Existing] in Target.
	 *   Source: [Not Existing] will overwrite the Target: [Key33:Value-B] ==(After)==> [Key33:Value-B in Target.
	 * 
	 * @param source
	 * @param target
	 * @param keyList
	 * @param defaultProp
	 * @param replaceOnly:
	 *    True : only when a key is found at both KeyList & Target, then replace the key/value pair. 
	 *    False: just set / create a new Key/Value pair at the Target no checking anything.
	 * @return
	 */
	public static boolean transferConfig(ConfigInterface source, ConfigInterface target, String[] keyList,
			Properties defaultProp, Properties sourceKeyMap, Properties targetKeyMap, boolean replaceOnly) {
		if (defaultProp == null || defaultProp.keySet().size() <= 0) {
			return transferConfig(source, target, keyList, replaceOnly);
		}
		if (source == null || target == null) {
			return false;
		}
		log.debug("transferConfig(): ==> source: \n" + source.printToString());
		log.debug("transferConfig(): ==> target: \n" + target.printToString());
		log.debug("transferConfig(): ==> keyList: \n" + keyList.toString());
		log.debug("transferConfig(): ==> defaultProp: \n" + defaultProp.toString());
		log.debug("transferConfig(): ==> sourceKeyMap: \n" + sourceKeyMap.toString());
		log.debug("transferConfig(): ==> targetKeyMap: \n" + targetKeyMap.toString());
		log.debug("transferConfig(): ==> replaceOnly: \n" + replaceOnly);
		
		try {
			for (String key : keyList) {
				String value = null;
				log.debug("transferConfig(): key=" + key);
				if (defaultProp != null && defaultProp.size() > 0 && defaultProp.get(key) != null) {
					 value = (String) defaultProp.get(key);
				}
				if (value != null) {
					value = (String) source.queryWithDefault(sourceKeyMap.getProperty(key), value);
				} else {
					value = (String) source.query(sourceKeyMap.getProperty(key));
				}
				if (value != null) {
					if (replaceOnly) {
						if (target.containsKey(targetKeyMap.getProperty(key))) {
							target.setValue(targetKeyMap.getProperty(key), value);
							log.debug("transferConfig() with keyMappings: replaceOnly=TRUE: Source Key=" + key + ", value=" + value);
						} else {
							// skip - no target key/value found!
						}
					} else {
						// -- regardless of key existing at Target or not, set new value from Source for
						// the given Key
						target.setValue(targetKeyMap.getProperty(key), value);
						log.debug("transferConfig() with keyMappings: replaceOnly=FALSE: Source Key=" + key + ", value=" + value);
					}
				}
			}
		} catch (Exception e) {
			e.printStackTrace();
			return false;
		}
		return true;
	}

	public static boolean transferConfig(ConfigInterface source, ConfigInterface target, String[] keyList,
			Properties defaultProp,  boolean replaceOnly) {
		if (defaultProp == null || defaultProp.keySet().size() <= 0) {
			return transferConfig(source, target, keyList, replaceOnly);
		}
		if (source == null || target == null) {
			return false;
		}
		try {
			for (String key : keyList) {
				String value = null;
				if (defaultProp != null && defaultProp.size() > 0 && defaultProp.get(key) != null) {
					 value = (String) defaultProp.get(key);
				}
				if (value != null) {
					value = (String) source.queryWithDefault(key, value);
				} else {
					value = (String) source.query(key);
				}
				if (value != null) {
					if (replaceOnly) {
						if (target.containsKey(key)) {
							target.setValue(key, value);
							log.info("transferConfig(): replaceOnly=TRUE: Source Key=" + key + ", value=" + value);

						} else {
							// skip - no target key/value found!
						}
					} else {
						// -- regardless of key existing at Target or not, set new value from Source for
						// the given Key
						target.setValue(key, value);
						log.info("transferConfig(): replaceOnly=FALSE: Source Key=" + key + ", value=" + value);
					}
				}
			}
		} catch (Exception e) {
			e.printStackTrace();
			return false;
		}
		return true;
	}
	
	/**
	 * 
	 * @param source
	 * @param target
	 * @param keyList
	 * @param whenTargetKeyExisting: 
	 *    True : only replace Key is found at Target and Not to do it if no key/value pair Found at Target. 
	 *    False: just set / create a new Key/Value pair at the Target no checking anything.
	 * @return
	 */
	public static boolean transferConfig(ConfigInterface source, ConfigInterface target, String[] keyList,
			Properties sourceKeyMap, Properties targetKeyMap, boolean replaceOnly) {
		if (source == null || target == null || keyList == null  ) {
			return false;
		}
		try {
			for (String key : keyList) {
				String value = (String) source.query(sourceKeyMap.getProperty(key));
				if (value != null) {
					if (replaceOnly) {
						if (target.containsKey(targetKeyMap.getProperty(key))) {
							target.setValue(targetKeyMap.getProperty(key), value);
						} else {
							// skip - no target key/value found!
						}
					} else {
						// -- regardless of key existing at Target or not, set new value from Source for
						// the given Key
						target.setValue(targetKeyMap.getProperty(key), value);
					}
				}
			}
		} catch (Exception e) {
			e.printStackTrace();
			return false;
		}
		return true;
	}

	public static boolean transferConfig(ConfigInterface source, ConfigInterface target, String[] keyList, boolean replaceOnly) {
		if (source == null || target == null || keyList == null  ) {
			return false;
		}
		try {
			for (String key : keyList) {
				String value = (String) source.query(key);
				if (value != null) {
					if (replaceOnly) {
						if (target.containsKey(key)) {
							target.setValue(key, value);
						} else {
							// skip - no target key/value found!
						}
					} else {
						// -- regardless of key existing at Target or not, set new value from Source for
						// the given Key
						target.setValue(key, value);
					}
				}
			}
		} catch (Exception e) {
			e.printStackTrace();
			return false;
		}
		return true;
	}
	public ConfigUtilities() {
		// 
	}

	public static void tests(String[] args) {
		//ConfigInterface src = new ConfigFrom

	}

	public static void main(String[] args) {
		BasicConfigurator.configure();
		tests(args);

	}

}
