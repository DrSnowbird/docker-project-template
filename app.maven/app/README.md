# Steps to generate Maven project with hello
mvn archetype:generate -DgroupId=com.mycompany.app -DartifactId=my-app -DarchetypeArtifactId=maven-archetype-quickstart -DarchetypeVersion=1.4 -DinteractiveMode=false
cd my-app/

mvn package

java -cp target/my-app-1.0-SNAPSHOT.jar com.mycompany.app.Hello

# Directories
```
.
├── pom.xml
├── README.md
└── src
    ├── main
    │   └── java
    │       └── com
    │           └── mycompany
    │               └── app
    │                   └── Hello.java
    └── test
        └── java
            └── com
                └── mycompany
                    └── app
                        └── HelloTest.java

```
# Skip Test
Just added the JVM flag:
```
mvn package -Dmaven.test.skip=true
```

