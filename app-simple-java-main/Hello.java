import java.util.stream.IntStream;

public class Hello {

	public Hello() {
		// super();
	}

	public static void heavyOperation(int i) {
		System.out.println("----- Hello, World: Loop=" + i);
	}
	public static void test(String[] args) {
		System.out.println("Welcome to Docker App Virtualization (Java Template):");
		IntStream.range(1, 10).parallel().forEach(i -> heavyOperation(i));
	}

	public static void main(String[] args) {

		test(args);
	}

}
