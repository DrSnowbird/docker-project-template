mvn clean
#mvn package -Dmaven.test.skip=true
mvn package 
java -cp target/my-app-1.0-SNAPSHOT.jar com.mycompany.app.Hello
