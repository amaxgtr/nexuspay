FROM eclipse-temurin:21-jre-alpine
# Container build definition
COPY target/*.jar app.jar
ENTRYPOINT ["java", "-jar", "/app.jar"]
