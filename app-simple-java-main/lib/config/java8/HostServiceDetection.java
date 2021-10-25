package config;

import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.net.URL;

import org.apache.log4j.BasicConfigurator;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class HostServiceDetection {

	protected static final Logger log = LoggerFactory.getLogger(HostServiceDetection.class);

	static int timeoutDefault = 5000;

	public HostServiceDetection() {
		// TODO Auto-generated constructor stub
	}

	/**
	 * Pings a HTTP URL. This effectively sends a HEAD request and returns
	 * <code>true</code> if the response code is in the 200-399 range.
	 * 
	 * @param url     The HTTP URL to be pinged.
	 * @param timeout The timeout in millis for both the connection timeout and the
	 *                response read timeout. Note that the total timeout is
	 *                effectively two times the given timeout.
	 * @return <code>true</code> if the given HTTP URL has returned response code
	 *         200-399 on a HEAD request within the given timeout, otherwise
	 *         <code>false</code>. // < 100 is undetermined. 1nn is informal
	 *         (shouldn't happen on a GET/HEAD) 2nn is success 3nn is redirect 4nn
	 *         is client error 5nn is server error
	 */
	public static boolean pingURL(String url, int timeout) {
		url = url.replaceFirst("^https", "http"); // Otherwise an exception may be thrown on invalid SSL certificates.

		try {
			HttpURLConnection connection = (HttpURLConnection) new URL(url).openConnection();
			connection.setConnectTimeout(timeout);
			connection.setReadTimeout(timeout);
			connection.setRequestMethod("HEAD");
			int responseCode = connection.getResponseCode();
			return (200 <= responseCode && responseCode <= 399);
		} catch (IOException exception) {
			return false;
		}
	}

	public static int pingURLReturnCode(String url) {
		return pingURLReturnCode(url, timeoutDefault);
	}

	public static int pingURLReturnCode(String url, int timeout) {
		url = url.replaceFirst("^https", "http"); // Otherwise an exception may be thrown on invalid SSL certificates.
		try {
			HttpURLConnection connection = (HttpURLConnection) new URL(url).openConnection();
			connection.setConnectTimeout(timeout);
			connection.setReadTimeout(timeout);
			connection.setRequestMethod("HEAD");
			int responseCode = connection.getResponseCode();
			return responseCode;
		} catch (Exception e) {
			// e.printStackTrace();
			return -1;
		}
	}

	public static boolean pingURL(String url) {
		return pingURL(url, timeoutDefault);
	}

	/**
	 * Ping remote service:port with timeout.
	 * 
	 * @param host
	 * @param port
	 * @param timeout The timeout value, in milliseconds
	 * @return
	 */
	public static boolean pingHostPort(String host, int port, int timeout) {
		try (Socket socket = new Socket()) {
			socket.connect(new InetSocketAddress(host, port), timeout);
			return true;
		} catch (IOException e) {
			// e.printStackTrace();
			log.warn("pingHostPort(): --- Can't reach remote service:port: " + host + ":" + port);
			return false; // Either timeout or unreachable or failed DNS lookup.
		}
	}

	public static boolean pingHostPort(String host, int port) {
		return pingHostPort(host, port, timeoutDefault);
	}

	// -- Use InetAddress#isReachable():
	public static boolean pingHost(String host, int timeout) {
		try (Socket socket = new Socket()) {
			boolean reachable = InetAddress.getByName(host).isReachable(timeout);
			return reachable;
		} catch (IOException e) {
			// e.printStackTrace();
			log.warn("pingHost(): --- Can't reach remote service:port: " + host);
			return false; // Either timeout or unreachable or failed DNS lookup.
		}
	}

	public static boolean pingHost(String host) {
		return pingHost(host, timeoutDefault);
	}

	// ---------- Test --------------

	public static void tests() {

		// -- test host:port reachable --
		String host = "abdn-vm-166.openkbs.org";
		int port = 3000;
		log.info("Ping GOOD host: " + host + ": " + HostServiceDetection.pingHost(host));
		log.info(
				"Ping GODD service:port: " + host + ": " + port + ": " + HostServiceDetection.pingHostPort(host, port));
		port = 8899; // not available port
		log.warn("Ping BAD service:port: " + host + ": " + port + ": " + HostServiceDetection.pingHostPort(host, port));

		// -- test URL reachable --
		String url = "http://abdn-vm-166.openkbs.org:3000";
		log.info("Ping GOOD URL: " + url + ": " + HostServiceDetection.pingURL(url));
		url = "http://abdn-vm-210.openkbs.org:3000";
		log.info("Ping Non-Running URL: " + url + ": " + HostServiceDetection.pingURL(url));
		log.info("Ping UP Running URL: " + url + ": HTTP code: " + HostServiceDetection.pingURLReturnCode(url, 5000));

		// -- test URL 7000: --
		host = "abdn-vm-166.openkbs.org";
		port = 7000;
		url = "http://abdn-vm-166.openkbs.org:7000/api";
		log.info(
				"Ping GODD service:port: " + host + ": " + port + ": " + HostServiceDetection.pingHostPort(host, port));
		log.info("Ping UP Running URL: " + url + ": " + HostServiceDetection.pingURL(url));
		log.info("Ping UP Running URL: " + url + ": HTTP code: " + HostServiceDetection.pingURLReturnCode(url, 5000));
	}

	public static void main(String[] args) {
		BasicConfigurator.configure();
		tests();
	}

}
