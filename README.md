# NexusPay Platform

Cloud-native payment infrastructure built on Spring Boot microservices,
Apache Kafka, and Kubernetes.

## Architecture

| Service | Responsibility | Tech |
|---|---|---|
| payment-service | Payment orchestration | Spring Boot, JPA, Kafka |
| fraud-service | ML fraud detection | Spring Boot, Redis, Kafka |
| notification-service | Webhooks, email, SMS | Spring Boot, Kafka, Twilio |
| ledger-service | Double-entry accounting | Spring Boot, JPA |
| merchant-service | Merchant management | Spring Boot, JPA |
| settlement-service | End-of-day settlement | Spring Batch, Quartz |
| compliance-service | PCI/AML/KYC | Spring Boot |
| gateway-service | API gateway + auth | Spring Cloud Gateway |
| shared-libs | Common DTOs and utils | Java 21 |

## Quick Start

```bash
# Start local infrastructure
docker-compose up -d

# Build all services
mvn clean package -DskipTests

# Run payment-service locally
cd payment-service
mvn spring-boot:run
```

## Tech Stack

- **Java 21** with virtual threads
- **Spring Boot 3.2** + Spring Cloud
- **Apache Kafka** for event streaming
- **PostgreSQL** for persistence
- **Redis** for caching and rate limiting
- **Kubernetes** for orchestration
- **Resilience4j** for circuit breaking
- **Testcontainers** for integration tests

---
*NexusPay is a demo repository built to demonstrate Gitrama AI repository intelligence.*
*All code, developers, and incidents are fictional. Built by [Gitrama](https://gitrama.ai)*

# fix(payment): idempotency key not persisted on async flows [2026-03-28]

# feat(payment): PaymentProcessor with Stripe gateway integration — NEXUS-2014 [2026-03-28]

# feat(payment): PaymentRequest and PaymentResponse DTOs with validation [2026-03-28]

# test(payment): PaymentController integration tests with MockMvc [2026-03-28]

# chore: multi-module Maven project scaffold — NEXUS-2028 [2026-03-28]

# chore: multi-module Maven project scaffold — NEXUS-2031 [2026-03-28]

# feat(payment): initial PaymentController with charge and capture endpoints [2026-03-28]

# fix(gateway): JWT expiry not validated on token refresh [2026-03-28]

# chore: Docker Compose for local Kafka, Postgres, Redis [2026-03-28]

# feat(payment): Kafka producer for PaymentCreated and PaymentCompleted events [2026-03-28]

# feat(shared): JwtUtil for token generation and validation [2026-03-28]

# feat(payment): PaymentService orchestration layer with idempotency [2026-03-28]

# feat(payment): initial PaymentController with charge and capture endpoints — NEXUS-2066 [2026-03-28]

# feat(shared): JwtUtil for token generation and validation [2026-03-28]

# feat(payment): Kafka producer for PaymentCreated and PaymentCompleted events [2026-03-28]

# fix(payment): idempotency key not persisted on async flows [2026-03-28]

# feat(payment): initial PaymentController with charge and capture endpoints [2026-03-28]
