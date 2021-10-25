package config;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.Reader;
import java.net.URL;
import java.nio.charset.Charset;

import org.apache.log4j.BasicConfigurator;
import org.json.JSONException;
import org.json.JSONObject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class JsonQueryRemote {

//public class JsonQueryRemote {

	protected static final Logger log = LoggerFactory.getLogger(JsonQueryRemote.class);

	// ---------------------------
	// -- The JSON Server URL: --
	// ---------------------------
	public static String jsonServerURL_DEFAULT = "http://abdn-vm-166.openkbs.org:3000/";

	// ---------------------------------------------------------------------------
	// -- JSON Configuration Unique UID, e.g., "myproj_rsheu_dev_abdn_vm_166" : --
	// ---------------------------------------------------------------------------
	public static String jsonConfigUID_DEFAULT = "myproj_config_LOCAL_abdn-vm-166.openkbs.org";

	// ---------------------------
	// -- JSON Object as cache: --
	// ---------------------------
	private JSONObject jsonObject = null;

	// ------------------------------
	// -- Private member variables: --
	// ------------------------------
	private String jsonServerURL = ""; // jsonServerURL_DEFAULT;
	private String jsonRouteOrObjectUID = ""; // jsonConfigUID_DEFAULT;

	// ---------------------------------------------
	// -- The Singleton JsonQueryRemote instance: --
	// ---------------------------------------------
	protected static JsonQueryRemote jsonQueryRemote = null;

	// ---------------------------------------------------------------------------
	// -- Flag to indicate the status of remote JSON Config Server: --
	// ---------------------------------------------------------------------------
	private boolean available = false;
	// private String url = "";

	/**
	 * Get JsonQueryRemote object (either Singleton or not)
	 * 
	 * @param jsonServerURL,          either 1.) e.g., http://abdn-vm-166:3000/ 2.)
	 *                                or,
	 *                                http://abdn-vm-166:3000/myproj_config_LOCAL_abdn-vm-166.openkbs.org
	 * @param route_or_jsonConfigUID: as 1.) addition Route (path after server URL)
	 *                                or 2.) as REST API UID Query model, like
	 *                                "http://<host>:<port>:/<UID>, e.g.,
	 *                                myproj_config_LOCAL_abdn-vm-166.openkbs.org 3.)
	 *                                This can be null or empty String as long as
	 *                                "jsonServerURL" is non-Null HTTP URL address.
	 * @return JsonQueryRemote
	 */
	public static JsonQueryRemote getJsonQueryRemote(String jsonServerURL, String route_or_jsonConfigUID,
			boolean singleton) {
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
				if (jsonQueryRemote == null) {
					jsonQueryRemote = new JsonQueryRemote(jsonServerURL, route_or_jsonConfigUID);
				} else {
					return jsonQueryRemote;
				}
			} else {
				return new JsonQueryRemote(jsonServerURL, route_or_jsonConfigUID);
			}
		}
		return jsonQueryRemote;
	}

	public static JsonQueryRemote getJsonQueryRemote(String jsonServerURL, boolean singleton) {
		return getJsonQueryRemote(jsonServerURL, null, singleton);
	}

	public static JsonQueryRemote getJsonQueryRemote(boolean singleton) {
		return getJsonQueryRemote(jsonServerURL_DEFAULT, jsonConfigUID_DEFAULT, singleton);
	}

	/**
	 * Default JSON Server URL and Config UID to use:
	 */
	protected JsonQueryRemote() {
		super();
		this.load();
	}

	/**
	 * Client providing specifics: JSON Server URL and Config UID to use:
	 * 
	 * @param _jsonServerURL
	 * @param _jsonConfigUID
	 */
	protected JsonQueryRemote(String _jsonServerURL, String _route_or_jsonConfigUID) {
		super();
		this.jsonServerURL = _jsonServerURL;
		this.jsonRouteOrObjectUID = _route_or_jsonConfigUID;
		this.load();
	}

	/**
	 * Load (Download) JSON Configuration data from Remote JSON Server
	 */
	public void load() {
		try {
			String url = this.jsonServerURL; // .replaceAll("/$", "");
			if (this.jsonRouteOrObjectUID != null && this.jsonRouteOrObjectUID.length() > 0) {
				url = this.jsonServerURL.replaceAll("/$", "") + "/" + this.jsonRouteOrObjectUID;
			} else {
				this.jsonRouteOrObjectUID = "";
			}
			int http_code = http_code = HostServiceDetection.pingURLReturnCode(url);
			if (http_code >= 200) {
				this.available = true;
				log.info("load():SUCCESS: --- Remote URL (status=AVAILABLE): " + url);
				this.jsonObject = querytJsonObjectFromUrl(url, null);
				log.info("load(): --- Entire JSON Tree: ---" + this.jsonObject.toString());
				if (this.jsonObject == null) {
					this.available = false;
				}
			} else {
				this.available = false;
				log.error("load():FAIL: --- No Route to URL: " + url + "; HTTP Code=" + http_code);
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	/**
	 * Utility to read into StringBuilder from Reader
	 * 
	 * @param rd
	 * @return String
	 * @throws IOException
	 */
	private static String readRemoteByByte(Reader rd) throws IOException {
		StringBuilder sb = new StringBuilder();
		int cp;
		while ((cp = rd.read()) != -1) {
			sb.append((char) cp);
		}
		return sb.toString();
	}

	private static String readRemoteByLine(BufferedReader rd) throws IOException {
		StringBuilder sb = new StringBuilder();
        String inputLine;
        while ((inputLine = rd.readLine()) != null) {
            //System.out.println(inputLine);
        	sb.append(inputLine);
        }
		return sb.toString();
	}

	/**
	 * Get a specific JSON path of JSON Object from remote JSON Server URL
	 * 
	 * @param url
	 * @param jsonPointer
	 * @return JSONObject
	 * @throws IOException
	 * @throws JSONException
	 */
	public static JSONObject querytJsonObjectFromUrl(String url, String jsonPointer) throws Exception {
		log.info("querytJsonObjectFromUrl(): url=" + url);
		log.info("querytJsonObjectFromUrl(): jsonPointer=" + (jsonPointer == null ? "" : jsonPointer));
		if (url == null || url.length() <= 5) {
			log.error("querytJsonObjectFromUrl();: *** ERROR ***: input argment url is NULL or Empty");
			return null;
		}
		InputStream is = null;
		try {
			is = new URL(url).openStream();
			BufferedReader rd = new BufferedReader(new InputStreamReader(is, Charset.forName("UTF-8")));
			//String jsonText = readRemoteByByte(rd);
			String jsonText = readRemoteByLine(rd);
	        
			JSONObject json = new JSONObject(jsonText);
			if (jsonPointer == null || jsonPointer.length() <= 0) {
				return json;
			}
			return json.getJSONObject(jsonPointer);
		} catch (Exception e) {
			log.error("*** ERROR ***: Can't open remote JSON Server! Failed to have HTTP Connection");
			e.printStackTrace();
			return null;
		} finally {
			is.close();
		}
	}

	/**
	 * Status of Remote JSON Configuration Server
	 * 
	 * @return True: Yes (Available), No (NOT-Available).
	 */
	public boolean isAvailable() {
		return available;
	}

	public String getJsonServerURL() {
		return jsonServerURL;
	}

	public void setJsonServerURL(String serverURL) {
		if (serverURL != null && serverURL.length() > 0 && this.jsonServerURL.compareTo(serverURL) != 0) {
			this.jsonServerURL = serverURL;
			this.load();
		}
		//this.jsonServerURL = serverURL;
	}

	public String getJsonConfigUID() {
		return jsonRouteOrObjectUID;
	}

	public void setJsonConfigUID(String configUID) {
		if (configUID != null && configUID.length() > 0 && this.jsonServerURL.compareTo(configUID) != 0) {
			this.jsonRouteOrObjectUID= configUID;
			this.load();
		}
		//this.jsonRouteOrObjectUID = jsonConfigUID;
	}

	public JSONObject getJsonObject() {
		return jsonObject;
	}

	public String printToString() {
		log.warn("printToString(): FAIL: this.jsonObject == null!");
		if (this.jsonObject == null)
			return "";
		return this.jsonObject.toString();
	}

	/**
	 * Query Object (either String Value or JSONObject) given JSONObject and
	 * jsonPointer string path example jsonPath; /myprojapp/kafka/host
	 * /myprojapp/myproj/adapters/elasticsearch/hosts/0
	 * 
	 * @param json
	 * @param jsonPath
	 * @return Object
	 * @throws IOException
	 * @throws JSONException
	 */
	public Object query(String jsonPath) throws Exception {
		if (this.jsonObject == null) {
			log.warn("query(): FAIL: this.jsonObject == null!");
			return null;
		}
		if (jsonPath == null) {
			jsonPath = "";
			log.warn("query(): FAIL: this.jsonObject == null!");
			return null;
		}
		Object result = this.jsonObject.query(jsonPath);
		return result;
	}

	/**
	 * Query JSON by Path with Default Value (String) if no key found.
	 * 
	 * @param jsonPath
	 * @param defaultValue
	 * @return Object (cast) to String
	 * @throws IOException
	 * @throws JSONException
	 */
	public Object queryWithDefault(String jsonPath, Object defaultValue) throws Exception {
		if (jsonPath == null) {
			// return the entire JSON tree
			return this.jsonObject;
		}

		Object result = this.jsonObject.query(jsonPath);
		if (result == null) {
			return defaultValue;
		}
		if (result instanceof Integer) {
			return ((Integer) result).toString();
		} else {
			return result;
		}
	}

	public String queryWithDefault(String jsonPath, int defaultValueInt) throws Exception {
		String defaultValue = Integer.toString(defaultValueInt);
		Object value = this.queryWithDefault(jsonPath, defaultValue);
		if (value == null) {
			return defaultValue;
		}
		return (String) value;
	}

	public int queryIntWithDefault(String jsonPath, int defaultValueInt) throws Exception {
		if (this.jsonObject == null) {
			log.warn("queryIntWithDefault(String jsonPath, int defaultValueInt): *** this.jsonObject == null !");
			return defaultValueInt;
		}
		if (jsonPath == null) {
			jsonPath = "";
		}
		Object jObject = this.jsonObject.query(jsonPath);
		if (jObject == null) {
			return defaultValueInt;
		}
		if (jObject instanceof Integer) {
			return ((Integer) jObject).intValue();
		} else {
			log.info(
					"queryWithDefault(String jsonPath, int defaultValueInt): --- Return value not Integer object: Not expected! Use default int value");
			return defaultValueInt;
		}
	}

	// ---------- Test --------------

	public static void tests(String[] args) {
		log.info("======== try JsonQueryRemote: ======");

		log.info("=============== Test-case 1-A: BAD and then Corrected URL: ");
		String urlBad = "http://abdn-vm-166.openkbs.org:9999/myproj_config_LOCAL_abdn-vm-166.openkbs.org";
		// String configUID = "Exception-should-occur_abdn-vm-166.openkbs.org";
		JsonQueryRemote jsonqQueryRemoteBad = JsonQueryRemote.getJsonQueryRemote(urlBad, null, false);
		log.info("==> Bad  connection: " + jsonqQueryRemoteBad.printToString());
		
		log.info("=============== Test-case 1-B: BAD and then Corrected URL: ");
		jsonqQueryRemoteBad.setJsonServerURL("http://abdn-vm-166.openkbs.org:3000/myproj_config_LOCAL_abdn-vm-155.openkbs.org");
		log.info("==> CORRECTED connection: " + jsonqQueryRemoteBad.printToString());

		/**
		 * Test-case 3: // -- Test using Full URL: //
		 * http://abdn-vm-166.openkbs.org:3000/myproj_config_LOCAL_abdn-vm-166.openkbs.org
		 * JsonQueryRemote jsonqQueryRemote =
		 * JsonQueryRemote.getJsonQueryRemote("http://abdn-vm-166.openkbs.org:3000/myproj_config_LOCAL_abdn-vm-166.openkbs.org");
		 */

		log.info("=============== Test-case 2: GOOD Connection: Print all properties: ");
		String url = "http://abdn-vm-166.openkbs.org:3000/";
		String configUID = "myproj_config_LOCAL_abdn-vm-155.openkbs.org";
		JsonQueryRemote jsonqQueryRemote = JsonQueryRemote.getJsonQueryRemote(url, configUID, true);
		System.out.println("==> GOOD connection: " + jsonqQueryRemote.printToString());
		
		String[] paths = { "/myprojapp/NOT-found", // Intentionally to get null value (NOT Found!)
				"/myprojapp/kafka", "/myprojapp/kafka/host", "/myprojapp/myproj/adapters/elasticsearch/hosts",
				"/myprojapp/myproj/adapters/elasticsearch/hosts/0" };
		for (String key : paths) {
			try {
				log.info(key + " -> " + jsonqQueryRemote.query(key));
			} catch (Exception e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
		String key = "/myprojapp/kafka/host";
		try {
			key = "/myprojapp/kafka/port";
			log.info(key + " queryWithDefault(key, 3333) -> " + jsonqQueryRemote.queryWithDefault(key, 3333));
			key = "/myprojapp/kafka/port3333";
			log.info(key + " queryWithDefault(key, 3333) -> " + jsonqQueryRemote.queryWithDefault(key, 3333));
			key = "/myprojapp/NOT-found";
			log.info(key + " queryWithDefault(key, SomeDefaultValue) -> "
					+ jsonqQueryRemote.queryWithDefault(key, "SomeDefaultValue"));
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

		// ======== try JsonQueryRemote: ======
		// Remote URL (status=AVAILABLE):
		// http://abdn-vm-166.openkbs.org:3000/myproj_config_LOCAL_abdn-vm-166.openkbs.org
		// getJsonObjectFromUrl():
		// url=http://abdn-vm-166.openkbs.org:3000/myproj_config_LOCAL_abdn-vm-166.openkbs.org
		// getJsonObjectFromUrl(): jsonPointer=
		// /myprojapp/NOT-found -> null
		// /myprojapp/kafka -> {"port":9092,"host":"abdn-vm-166.openkbs.org"}
		// /myprojapp/kafka/host -> abdn-vm-166.openkbs.org
		// /myprojapp/myproj/adapters/elasticsearch/hosts ->
		// ["myproj-dev.openkbs.org:9200","es01.openkbs.org:9200","es02.openkbs.org:9200","es03.openkbs.org:9200"]
		// /myprojapp/myproj/adapters/elasticsearch/hosts/0 -> myproj-dev.openkbs.org:9200
		// /myprojapp/kafka/port queryWithDefault(key, 3333) -> 9092
		// /myprojapp/kafka/port3333 queryWithDefault(key, 3333) -> 3333
		// /myprojapp/NOT-found queryWithDefault(key, SomeDefaultValue) ->
		// SomeDefaultValue
	}

	public static void main(String[] args) {
		BasicConfigurator.configure();
		tests(args);

	}
}