#!/usr/bin/env python3
"""
NexusPay Commit Simulator
--------------------------
Generates 1000 realistic commits across a Java fintech microservices
codebase with Kafka, Spring Boot, Kubernetes, and enterprise patterns.

Architecture:
  - payment-service      Spring Boot microservice
  - fraud-service        ML fraud detection
  - notification-service Kafka consumer + email/SMS
  - merchant-service     Merchant management
  - gateway-service      API gateway + auth
  - ledger-service       Double-entry accounting
  - settlement-service   End-of-day settlement
  - compliance-service   PCI/AML/KYC
  - shared-libs          Common DTOs, events, utils

Story arc:
  Phase 1 — Greenfield     (commits 1-120)
  Phase 2 — Integration    (commits 121-250)
  Phase 3 — Scale          (commits 251-400)
  Phase 4 — Enterprise     (commits 401-550)
  Phase 5 — Optimization   (commits 551-700)
  Phase 6 — Incidents      (commits 701-850)
  Phase 7 — Decay          (commits 851-1000)

Usage:
    mkdir -p ~/sandbox/nexuspay && cd ~/sandbox/nexuspay
    git init
    python simulate_nexuspay.py

WARNING: Run on demo repo only. Modifies git history.
"""

import subprocess
import random
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

# ── Authors ────────────────────────────────────────────────────────────────────
AUTHORS = [
    ("James Okafor",    "james.okafor@nexuspay.io"),
    ("Sarah Kim",       "sarah.kim@nexuspay.io"),
    ("Raj Patel",       "raj.patel@nexuspay.io"),
    ("Elena Vasquez",   "elena.vasquez@nexuspay.io"),
    ("David Thornton",  "david.thornton@nexuspay.io"),
    ("Mei Lin",         "mei.lin@nexuspay.io"),
    ("Carlos Mendez",   "carlos.mendez@nexuspay.io"),
]

# ── Timeline ───────────────────────────────────────────────────────────────────
START_DATE = datetime(2024, 1, 15, 9, 0, 0)
END_DATE   = datetime(2026, 3, 1, 18, 0, 0)

# ── NEXUS ticket counter ───────────────────────────────────────────────────────
TICKET_COUNTER = [2001]

def next_ticket():
    t = TICKET_COUNTER[0]
    TICKET_COUNTER[0] += random.randint(1, 5)
    return f"NEXUS-{t}"

# ── File registry ──────────────────────────────────────────────────────────────
FILES = {
    # payment-service
    "payment-service/src/main/java/io/nexuspay/payment/PaymentController.java":         "REST controller for payment endpoints",
    "payment-service/src/main/java/io/nexuspay/payment/PaymentService.java":             "Core payment orchestration service",
    "payment-service/src/main/java/io/nexuspay/payment/PaymentRepository.java":         "JPA repository for payment entities",
    "payment-service/src/main/java/io/nexuspay/payment/PaymentProcessor.java":          "Payment processing engine",
    "payment-service/src/main/java/io/nexuspay/payment/PaymentEventProducer.java":      "Kafka producer for payment events",
    "payment-service/src/main/java/io/nexuspay/payment/dto/PaymentRequest.java":        "Payment request DTO",
    "payment-service/src/main/java/io/nexuspay/payment/dto/PaymentResponse.java":       "Payment response DTO",
    "payment-service/src/main/java/io/nexuspay/payment/entity/Payment.java":            "Payment JPA entity",
    "payment-service/src/main/java/io/nexuspay/payment/config/KafkaConfig.java":        "Kafka producer configuration",
    "payment-service/src/main/java/io/nexuspay/payment/config/DataSourceConfig.java":   "DataSource and JPA config",
    "payment-service/src/main/resources/application.yml":                                "Service configuration",
    "payment-service/src/test/java/io/nexuspay/payment/PaymentServiceTest.java":        "Payment service unit tests",
    "payment-service/src/test/java/io/nexuspay/payment/PaymentControllerTest.java":     "Controller integration tests",
    "payment-service/pom.xml":                                                           "Maven build configuration",
    "payment-service/Dockerfile":                                                        "Container build definition",

    # fraud-service
    "fraud-service/src/main/java/io/nexuspay/fraud/FraudDetectionService.java":         "ML fraud scoring engine",
    "fraud-service/src/main/java/io/nexuspay/fraud/FraudRuleEngine.java":               "Rule-based fraud detection",
    "fraud-service/src/main/java/io/nexuspay/fraud/FraudEventConsumer.java":            "Kafka consumer for payment events",
    "fraud-service/src/main/java/io/nexuspay/fraud/FraudScoreCalculator.java":          "Risk score calculation",
    "fraud-service/src/main/java/io/nexuspay/fraud/VelocityChecker.java":               "Transaction velocity checks",
    "fraud-service/src/main/java/io/nexuspay/fraud/model/FraudModel.java":              "ML model wrapper",
    "fraud-service/src/main/java/io/nexuspay/fraud/config/MLConfig.java":               "ML pipeline configuration",
    "fraud-service/src/main/resources/application.yml":                                  "Fraud service configuration",
    "fraud-service/src/test/java/io/nexuspay/fraud/FraudDetectionServiceTest.java":     "Fraud service unit tests",
    "fraud-service/pom.xml":                                                             "Maven build configuration",

    # notification-service
    "notification-service/src/main/java/io/nexuspay/notification/NotificationService.java":       "Notification orchestration",
    "notification-service/src/main/java/io/nexuspay/notification/EmailService.java":              "Email delivery service",
    "notification-service/src/main/java/io/nexuspay/notification/SmsService.java":                "SMS delivery via Twilio",
    "notification-service/src/main/java/io/nexuspay/notification/PaymentEventConsumer.java":      "Kafka consumer for events",
    "notification-service/src/main/java/io/nexuspay/notification/WebhookDeliveryService.java":    "Webhook delivery and retry",
    "notification-service/src/main/java/io/nexuspay/notification/RetryScheduler.java":            "Failed delivery retry scheduler",
    "notification-service/src/main/resources/application.yml":                                     "Notification service config",
    "notification-service/src/test/java/io/nexuspay/notification/WebhookDeliveryServiceTest.java":"Webhook delivery tests",
    "notification-service/pom.xml":                                                                "Maven build configuration",

    # gateway-service
    "gateway-service/src/main/java/io/nexuspay/gateway/GatewayConfig.java":             "Spring Cloud Gateway routes",
    "gateway-service/src/main/java/io/nexuspay/gateway/AuthFilter.java":                "JWT authentication filter",
    "gateway-service/src/main/java/io/nexuspay/gateway/RateLimitFilter.java":           "Rate limiting filter",
    "gateway-service/src/main/java/io/nexuspay/gateway/CircuitBreakerConfig.java":      "Resilience4j circuit breaker",
    "gateway-service/src/main/java/io/nexuspay/gateway/LoadBalancerConfig.java":        "Load balancer configuration",
    "gateway-service/src/main/resources/application.yml":                                "Gateway configuration",
    "gateway-service/pom.xml":                                                           "Maven build configuration",

    # ledger-service
    "ledger-service/src/main/java/io/nexuspay/ledger/LedgerService.java":               "Double-entry ledger engine",
    "ledger-service/src/main/java/io/nexuspay/ledger/JournalEntryService.java":         "Journal entry management",
    "ledger-service/src/main/java/io/nexuspay/ledger/ReconciliationService.java":       "Account reconciliation",
    "ledger-service/src/main/java/io/nexuspay/ledger/LedgerEventConsumer.java":         "Kafka ledger event consumer",
    "ledger-service/src/main/java/io/nexuspay/ledger/entity/JournalEntry.java":         "Journal entry JPA entity",
    "ledger-service/src/main/resources/application.yml":                                 "Ledger service configuration",
    "ledger-service/src/test/java/io/nexuspay/ledger/LedgerServiceTest.java":           "Ledger service unit tests",
    "ledger-service/pom.xml":                                                            "Maven build configuration",

    # merchant-service
    "merchant-service/src/main/java/io/nexuspay/merchant/MerchantService.java":         "Merchant management service",
    "merchant-service/src/main/java/io/nexuspay/merchant/OnboardingService.java":       "Merchant KYC onboarding",
    "merchant-service/src/main/java/io/nexuspay/merchant/MerchantController.java":      "Merchant REST controller",
    "merchant-service/src/main/java/io/nexuspay/merchant/SettingsService.java":         "Merchant settings management",
    "merchant-service/src/main/resources/application.yml":                               "Merchant service configuration",
    "merchant-service/pom.xml":                                                          "Maven build configuration",

    # settlement-service
    "settlement-service/src/main/java/io/nexuspay/settlement/SettlementService.java":   "End-of-day settlement engine",
    "settlement-service/src/main/java/io/nexuspay/settlement/BatchProcessor.java":      "Settlement batch processor",
    "settlement-service/src/main/java/io/nexuspay/settlement/SettlementScheduler.java": "Scheduled settlement jobs",
    "settlement-service/src/main/java/io/nexuspay/settlement/ReportGenerator.java":     "Settlement report generation",
    "settlement-service/src/main/resources/application.yml":                             "Settlement service config",
    "settlement-service/pom.xml":                                                        "Maven build configuration",

    # compliance-service
    "compliance-service/src/main/java/io/nexuspay/compliance/PCIComplianceService.java":"PCI DSS compliance controls",
    "compliance-service/src/main/java/io/nexuspay/compliance/AMLService.java":          "Anti-money laundering checks",
    "compliance-service/src/main/java/io/nexuspay/compliance/KYCService.java":          "Know your customer verification",
    "compliance-service/src/main/java/io/nexuspay/compliance/AuditTrailService.java":   "Immutable audit trail",
    "compliance-service/src/main/java/io/nexuspay/compliance/SanctionsScreening.java":  "Sanctions list screening",
    "compliance-service/src/main/resources/application.yml":                             "Compliance service config",
    "compliance-service/pom.xml":                                                        "Maven build configuration",

    # shared-libs
    "shared-libs/src/main/java/io/nexuspay/common/events/PaymentEvent.java":            "Payment domain event",
    "shared-libs/src/main/java/io/nexuspay/common/events/FraudEvent.java":              "Fraud domain event",
    "shared-libs/src/main/java/io/nexuspay/common/events/SettlementEvent.java":         "Settlement domain event",
    "shared-libs/src/main/java/io/nexuspay/common/dto/ErrorResponse.java":              "Standardised error DTO",
    "shared-libs/src/main/java/io/nexuspay/common/exception/PaymentException.java":     "Payment domain exception",
    "shared-libs/src/main/java/io/nexuspay/common/util/IdempotencyUtil.java":           "Idempotency key utilities",
    "shared-libs/src/main/java/io/nexuspay/common/util/CurrencyUtil.java":              "Currency conversion utilities",
    "shared-libs/src/main/java/io/nexuspay/common/security/JwtUtil.java":               "JWT token utilities",
    "shared-libs/pom.xml":                                                               "Shared library build config",

    # Infrastructure
    "k8s/payment-service-deployment.yaml":          "Payment service K8s deployment",
    "k8s/fraud-service-deployment.yaml":            "Fraud service K8s deployment",
    "k8s/notification-service-deployment.yaml":     "Notification service K8s deployment",
    "k8s/gateway-service-deployment.yaml":          "Gateway service K8s deployment",
    "k8s/kafka-statefulset.yaml":                   "Kafka cluster StatefulSet",
    "k8s/postgres-statefulset.yaml":                "PostgreSQL StatefulSet",
    "k8s/redis-deployment.yaml":                    "Redis deployment",
    "k8s/ingress.yaml":                             "Nginx ingress configuration",
    "k8s/configmaps.yaml":                          "Environment ConfigMaps",
    "k8s/secrets.yaml":                             "Secret management",
    "k8s/hpa.yaml":                                 "Horizontal Pod Autoscaler",

    # CI/CD
    ".github/workflows/ci.yml":                     "GitHub Actions CI pipeline",
    ".github/workflows/deploy-staging.yml":         "Staging deployment workflow",
    ".github/workflows/deploy-prod.yml":            "Production deployment workflow",
    ".github/workflows/security-scan.yml":          "Security scanning workflow",

    # Config
    "docker-compose.yml":                           "Local development environment",
    "docker-compose.test.yml":                      "Test environment compose",
    "pom.xml":                                      "Root Maven build config",
    "README.md":                                    "Project documentation",
    "CONTRIBUTING.md":                              "Contributing guidelines",
    ".env.example":                                 "Environment variable template",
    "Makefile":                                     "Build and development commands",
}

# ── Phase definitions ──────────────────────────────────────────────────────────
PHASES = [

    # Phase 1 — Greenfield (120 commits)
    {
        "name": "Greenfield",
        "weight": 120,
        "date_range": (0.0, 0.14),
        "authors": ["james", "sarah", "raj"],
        "files": [
            "payment-service/src/main/java/io/nexuspay/payment/PaymentController.java",
            "payment-service/src/main/java/io/nexuspay/payment/PaymentService.java",
            "payment-service/src/main/java/io/nexuspay/payment/PaymentProcessor.java",
            "payment-service/src/main/java/io/nexuspay/payment/entity/Payment.java",
            "payment-service/src/main/java/io/nexuspay/payment/config/KafkaConfig.java",
            "payment-service/src/main/resources/application.yml",
            "payment-service/src/test/java/io/nexuspay/payment/PaymentServiceTest.java",
            "shared-libs/src/main/java/io/nexuspay/common/events/PaymentEvent.java",
            "shared-libs/src/main/java/io/nexuspay/common/util/IdempotencyUtil.java",
            "shared-libs/src/main/java/io/nexuspay/common/security/JwtUtil.java",
            "gateway-service/src/main/java/io/nexuspay/gateway/GatewayConfig.java",
            "gateway-service/src/main/java/io/nexuspay/gateway/AuthFilter.java",
            "docker-compose.yml",
            "pom.xml",
            "README.md",
            "Makefile",
            ".github/workflows/ci.yml",
        ],
        "commits": [
            ("feat(payment)", "initial PaymentController with charge and capture endpoints"),
            ("feat(payment)", "PaymentService orchestration layer with idempotency"),
            ("feat(payment)", "PaymentProcessor with Stripe gateway integration"),
            ("feat(payment)", "Payment JPA entity with audit fields"),
            ("feat(payment)", "Kafka producer for PaymentCreated and PaymentCompleted events"),
            ("feat(payment)", "PaymentRequest and PaymentResponse DTOs with validation"),
            ("feat(gateway)", "Spring Cloud Gateway route configuration"),
            ("feat(gateway)", "JWT authentication filter with RS256 validation"),
            ("feat(shared)", "PaymentEvent base class with correlation ID"),
            ("feat(shared)", "IdempotencyUtil for duplicate request detection"),
            ("feat(shared)", "JwtUtil for token generation and validation"),
            ("feat(shared)", "CurrencyUtil with ISO 4217 currency handling"),
            ("test(payment)", "PaymentService unit test suite with Mockito"),
            ("test(payment)", "PaymentController integration tests with MockMvc"),
            ("chore", "multi-module Maven project scaffold"),
            ("chore", "Docker Compose for local Kafka, Postgres, Redis"),
            ("chore", "GitHub Actions CI pipeline with test and build"),
            ("docs", "README with architecture overview and setup guide"),
            ("fix(payment)", "idempotency key not persisted on async flows"),
            ("fix(gateway)", "JWT expiry not validated on token refresh"),
        ],
    },

    # Phase 2 — Integration (130 commits)
    {
        "name": "Integration",
        "weight": 130,
        "date_range": (0.14, 0.29),
        "authors": ["sarah", "raj", "elena"],
        "files": [
            "fraud-service/src/main/java/io/nexuspay/fraud/FraudDetectionService.java",
            "fraud-service/src/main/java/io/nexuspay/fraud/FraudEventConsumer.java",
            "fraud-service/src/main/java/io/nexuspay/fraud/VelocityChecker.java",
            "notification-service/src/main/java/io/nexuspay/notification/PaymentEventConsumer.java",
            "notification-service/src/main/java/io/nexuspay/notification/WebhookDeliveryService.java",
            "notification-service/src/main/java/io/nexuspay/notification/EmailService.java",
            "ledger-service/src/main/java/io/nexuspay/ledger/LedgerService.java",
            "ledger-service/src/main/java/io/nexuspay/ledger/JournalEntryService.java",
            "ledger-service/src/main/java/io/nexuspay/ledger/LedgerEventConsumer.java",
            "gateway-service/src/main/java/io/nexuspay/gateway/RateLimitFilter.java",
            "gateway-service/src/main/java/io/nexuspay/gateway/CircuitBreakerConfig.java",
            "shared-libs/src/main/java/io/nexuspay/common/events/FraudEvent.java",
            "k8s/kafka-statefulset.yaml",
            "k8s/postgres-statefulset.yaml",
            ".github/workflows/deploy-staging.yml",
        ],
        "commits": [
            ("feat(fraud)", "FraudDetectionService with rule-based scoring"),
            ("feat(fraud)", "Kafka consumer for PaymentCreated events"),
            ("feat(fraud)", "velocity checks for card and merchant limits"),
            ("feat(fraud)", "FraudEvent publishing on high-risk transactions"),
            ("feat(notification)", "Kafka consumer for payment and fraud events"),
            ("feat(notification)", "webhook delivery with HMAC signature"),
            ("feat(notification)", "email notifications via SendGrid"),
            ("feat(notification)", "exponential backoff retry for failed deliveries"),
            ("feat(ledger)", "double-entry bookkeeping with JournalEntry"),
            ("feat(ledger)", "Kafka consumer for payment completion events"),
            ("feat(ledger)", "account balance calculation with optimistic locking"),
            ("feat(gateway)", "Redis-based rate limiting per merchant API key"),
            ("feat(gateway)", "Resilience4j circuit breaker for downstream services"),
            ("feat(shared)", "FraudEvent with risk score and triggered rules"),
            ("chore(k8s)", "Kafka StatefulSet with 3-broker cluster config"),
            ("chore(k8s)", "PostgreSQL StatefulSet with persistent volumes"),
            ("chore(ci)", "staging deployment workflow with smoke tests"),
            ("fix(fraud)", "velocity window calculation off by one second"),
            ("fix(notification)", "webhook signature invalid for Unicode payloads — NEXUS-2034"),
            ("fix(ledger)", "optimistic lock exception on concurrent journal entries"),
            ("fix(gateway)", "circuit breaker not resetting after timeout window"),
            ("fix(notification)", "retry scheduler firing duplicate deliveries — NEXUS-2041"),
            ("test(fraud)", "FraudDetectionService unit tests with rule fixtures"),
            ("test(ledger)", "double-entry invariant tests"),
            ("test(notification)", "webhook delivery and retry integration tests"),
        ],
    },

    # Phase 3 — Scale (150 commits)
    {
        "name": "Scale",
        "weight": 150,
        "date_range": (0.29, 0.46),
        "authors": ["raj", "elena", "david", "james"],
        "files": [
            "payment-service/src/main/java/io/nexuspay/payment/PaymentService.java",
            "payment-service/src/main/java/io/nexuspay/payment/PaymentProcessor.java",
            "payment-service/src/main/java/io/nexuspay/payment/config/DataSourceConfig.java",
            "fraud-service/src/main/java/io/nexuspay/fraud/FraudRuleEngine.java",
            "fraud-service/src/main/java/io/nexuspay/fraud/model/FraudModel.java",
            "fraud-service/src/main/java/io/nexuspay/fraud/config/MLConfig.java",
            "settlement-service/src/main/java/io/nexuspay/settlement/SettlementService.java",
            "settlement-service/src/main/java/io/nexuspay/settlement/BatchProcessor.java",
            "settlement-service/src/main/java/io/nexuspay/settlement/SettlementScheduler.java",
            "merchant-service/src/main/java/io/nexuspay/merchant/MerchantService.java",
            "merchant-service/src/main/java/io/nexuspay/merchant/OnboardingService.java",
            "ledger-service/src/main/java/io/nexuspay/ledger/ReconciliationService.java",
            "k8s/payment-service-deployment.yaml",
            "k8s/fraud-service-deployment.yaml",
            "k8s/hpa.yaml",
            ".github/workflows/deploy-prod.yml",
        ],
        "commits": [
            ("feat(settlement)", "end-of-day settlement batch processor"),
            ("feat(settlement)", "Spring Batch job for settlement file generation"),
            ("feat(settlement)", "scheduled settlement with @Scheduled and Quartz"),
            ("feat(settlement)", "settlement report PDF and CSV generation"),
            ("feat(fraud)", "ML model integration with XGBoost scoring"),
            ("feat(fraud)", "feature pipeline for ML fraud detection"),
            ("feat(fraud)", "A/B testing framework for rule vs ML scoring"),
            ("feat(merchant)", "merchant onboarding with KYC document flow"),
            ("feat(merchant)", "merchant API key self-service portal"),
            ("feat(ledger)", "account reconciliation job with discrepancy alerts"),
            ("perf(payment)", "connection pool tuning for 10k TPS target"),
            ("perf(payment)", "async payment processing with CompletableFuture"),
            ("perf(fraud)", "fraud scoring latency reduced from 280ms to 38ms"),
            ("perf(ledger)", "batch journal entry insertion with JDBC batch"),
            ("chore(k8s)", "HPA for payment-service with custom metrics"),
            ("chore(k8s)", "production deployment workflow with canary release"),
            ("chore(k8s)", "pod disruption budgets for zero-downtime deploys"),
            ("fix(settlement)", "timezone handling for cross-midnight settlements — NEXUS-2089"),
            ("fix(fraud)", "ML model not reloading after hot deploy — NEXUS-2094"),
            ("fix(payment)", "connection leak under sustained 5k TPS load"),
            ("fix(merchant)", "onboarding state machine invalid transition — NEXUS-2101"),
            ("fix(ledger)", "reconciliation missing debit-only accounts"),
            ("test(settlement)", "batch processor integration tests"),
            ("test(fraud)", "ML scoring unit tests with fixture data"),
            ("test(merchant)", "onboarding flow integration tests"),
        ],
    },

    # Phase 4 — Enterprise (150 commits)
    {
        "name": "Enterprise",
        "weight": 150,
        "date_range": (0.46, 0.62),
        "authors": ["elena", "mei", "carlos", "david"],
        "files": [
            "compliance-service/src/main/java/io/nexuspay/compliance/PCIComplianceService.java",
            "compliance-service/src/main/java/io/nexuspay/compliance/AMLService.java",
            "compliance-service/src/main/java/io/nexuspay/compliance/KYCService.java",
            "compliance-service/src/main/java/io/nexuspay/compliance/AuditTrailService.java",
            "compliance-service/src/main/java/io/nexuspay/compliance/SanctionsScreening.java",
            "gateway-service/src/main/java/io/nexuspay/gateway/LoadBalancerConfig.java",
            "merchant-service/src/main/java/io/nexuspay/merchant/SettingsService.java",
            "settlement-service/src/main/java/io/nexuspay/settlement/ReportGenerator.java",
            "notification-service/src/main/java/io/nexuspay/notification/SmsService.java",
            "notification-service/src/main/java/io/nexuspay/notification/RetryScheduler.java",
            "shared-libs/src/main/java/io/nexuspay/common/exception/PaymentException.java",
            "k8s/ingress.yaml",
            "k8s/configmaps.yaml",
            "k8s/secrets.yaml",
            ".github/workflows/security-scan.yml",
        ],
        "commits": [
            ("feat(compliance)", "PCI DSS scope reduction with tokenisation"),
            ("feat(compliance)", "AML transaction monitoring rules engine"),
            ("feat(compliance)", "KYC document verification with Jumio integration"),
            ("feat(compliance)", "immutable audit trail with hash chain validation"),
            ("feat(compliance)", "OFAC sanctions list screening"),
            ("feat(compliance)", "GDPR data export and right-to-erasure workflow"),
            ("feat(notification)", "SMS delivery via Twilio with delivery receipts"),
            ("feat(merchant)", "merchant tier management and pricing plans"),
            ("feat(settlement)", "regulatory settlement reporting for card schemes"),
            ("feat(gateway)", "multi-region load balancer configuration"),
            ("chore(k8s)", "Nginx ingress with TLS termination and WAF rules"),
            ("chore(k8s)", "ConfigMap management for environment-specific config"),
            ("chore(k8s)", "HashiCorp Vault integration for secret management"),
            ("chore(ci)", "SAST and DAST security scanning in CI pipeline"),
            ("fix(compliance)", "PCI audit log gap during rolling restart — NEXUS-2134"),
            ("fix(compliance)", "AML rules not applying to refund transactions"),
            ("fix(compliance)", "KYC expiry not triggering re-verification workflow"),
            ("fix(notification)", "SMS retry storm after Twilio rate limit — NEXUS-2141"),
            ("fix(gateway)", "WAF blocking legitimate webhook callbacks"),
            ("fix(settlement)", "report generation OOM on large merchant volumes"),
            ("test(compliance)", "PCI compliance control unit tests"),
            ("test(compliance)", "AML rules engine integration tests"),
            ("docs", "enterprise integration guide and compliance checklist"),
            ("docs", "security architecture and threat model"),
        ],
    },

    # Phase 5 — Optimization (150 commits)
    {
        "name": "Optimization",
        "weight": 150,
        "date_range": (0.62, 0.76),
        "authors": ["james", "raj", "mei", "carlos"],
        "files": [
            "payment-service/src/main/java/io/nexuspay/payment/PaymentService.java",
            "payment-service/src/main/java/io/nexuspay/payment/PaymentEventProducer.java",
            "fraud-service/src/main/java/io/nexuspay/fraud/FraudScoreCalculator.java",
            "ledger-service/src/main/java/io/nexuspay/ledger/LedgerService.java",
            "ledger-service/src/main/java/io/nexuspay/ledger/ReconciliationService.java",
            "notification-service/src/main/java/io/nexuspay/notification/NotificationService.java",
            "settlement-service/src/main/java/io/nexuspay/settlement/BatchProcessor.java",
            "gateway-service/src/main/java/io/nexuspay/gateway/RateLimitFilter.java",
            "shared-libs/src/main/java/io/nexuspay/common/util/CurrencyUtil.java",
            "k8s/payment-service-deployment.yaml",
            "k8s/redis-deployment.yaml",
            "docker-compose.yml",
            "docker-compose.test.yml",
        ],
        "commits": [
            ("perf(payment)", "Kafka producer batch size tuned for 50k msg/sec"),
            ("perf(payment)", "payment processing p99 latency from 450ms to 85ms"),
            ("perf(fraud)", "fraud scoring cache hit rate improved to 94 percent"),
            ("perf(ledger)", "ledger query optimisation with covering indexes"),
            ("perf(notification)", "webhook delivery throughput 10x with virtual threads"),
            ("perf(settlement)", "batch processor parallelism with ForkJoinPool"),
            ("perf(gateway)", "rate limit check latency from 12ms to 0.8ms"),
            ("perf(shared)", "CurrencyUtil lookup table replaces BigDecimal division"),
            ("refactor(payment)", "PaymentService decomposed into domain-specific handlers"),
            ("refactor(fraud)", "FraudRuleEngine migrated to strategy pattern"),
            ("refactor(ledger)", "LedgerService split into read and write services"),
            ("refactor(notification)", "notification pipeline migrated to reactive streams"),
            ("chore(k8s)", "Redis cluster upgrade with persistence configuration"),
            ("chore(docker)", "multi-stage builds reducing image size by 68 percent"),
            ("chore(docker)", "test environment compose with Testcontainers integration"),
            ("fix(payment)", "Kafka producer acks=all causing latency spike — NEXUS-2178"),
            ("fix(ledger)", "reconciliation deadlock on high-concurrency writes"),
            ("fix(settlement)", "batch job not restarting after pod eviction — NEXUS-2185"),
            ("fix(gateway)", "rate limit counter not shared across pod replicas"),
            ("fix(fraud)", "cache invalidation missing after rule update — NEXUS-2191"),
            ("test(payment)", "load test suite with Gatling — 50k TPS baseline"),
            ("test(ledger)", "concurrency tests for optimistic locking behaviour"),
            ("docs", "performance tuning guide and benchmark results"),
        ],
    },

    # Phase 6 — Incidents (150 commits)
    {
        "name": "Incidents",
        "weight": 150,
        "date_range": (0.76, 0.89),
        "authors": ["carlos", "james", "sarah", "david", "raj"],
        "files": [
            "payment-service/src/main/java/io/nexuspay/payment/PaymentProcessor.java",
            "payment-service/src/main/java/io/nexuspay/payment/PaymentService.java",
            "fraud-service/src/main/java/io/nexuspay/fraud/FraudDetectionService.java",
            "fraud-service/src/main/java/io/nexuspay/fraud/model/FraudModel.java",
            "notification-service/src/main/java/io/nexuspay/notification/WebhookDeliveryService.java",
            "notification-service/src/main/java/io/nexuspay/notification/RetryScheduler.java",
            "ledger-service/src/main/java/io/nexuspay/ledger/JournalEntryService.java",
            "settlement-service/src/main/java/io/nexuspay/settlement/SettlementService.java",
            "compliance-service/src/main/java/io/nexuspay/compliance/AuditTrailService.java",
            "gateway-service/src/main/java/io/nexuspay/gateway/CircuitBreakerConfig.java",
            "k8s/payment-service-deployment.yaml",
            "k8s/kafka-statefulset.yaml",
        ],
        "commits": [
            ("hotfix(payment)", "P0 — double charge on network timeout retry — NEXUS-2234"),
            ("hotfix(payment)", "P0 — payment status stuck in PENDING after gateway timeout"),
            ("hotfix(fraud)", "P1 — fraud model serving stale weights after deploy — NEXUS-2241"),
            ("hotfix(notification)", "P1 — webhook retry storm taking down notification-service"),
            ("hotfix(ledger)", "P0 — journal entry duplication on Kafka redelivery — NEXUS-2248"),
            ("hotfix(settlement)", "P1 — settlement job failing for merchants with FX — NEXUS-2255"),
            ("hotfix(gateway)", "P1 — circuit breaker open-looping on payment-service restart"),
            ("hotfix(compliance)", "P1 — audit trail gap during Kafka partition rebalance"),
            ("fix(payment)", "idempotency check race condition under high concurrency"),
            ("fix(payment)", "gateway timeout not propagated to merchant response"),
            ("fix(fraud)", "model feature pipeline NullPointerException on missing fields"),
            ("fix(notification)", "dead letter queue not draining after consumer restart"),
            ("fix(ledger)", "optimistic lock version not reset after transaction rollback"),
            ("fix(settlement)", "FX rate lookup failing for weekend settlements — NEXUS-2267"),
            ("fix(gateway)", "circuit breaker threshold too sensitive for payment spikes"),
            ("fix(compliance)", "PCI log rotation deleting entries before 90-day retention"),
            ("fix(payment)", "Kafka consumer lag growing on payment-service — NEXUS-2274"),
            ("fix(fraud)", "velocity window reset firing too early on DST change"),
            ("fix(notification)", "Twilio callback URL hardcoded to staging — NEXUS-2281"),
            ("fix(settlement)", "batch checkpoint not saved before OOM kill — NEXUS-2288"),
            ("chore(k8s)", "Kafka broker memory limits increased after OOM incident"),
            ("chore(k8s)", "payment-service pod anti-affinity after zone outage"),
            ("docs", "incident post-mortem — double charge root cause analysis"),
            ("docs", "runbook update for Kafka consumer lag alerts"),
        ],
    },

    # Phase 7 — Decay (100 commits)
    {
        "name": "Decay",
        "weight": 100,
        "date_range": (0.89, 1.0),
        "authors": ["carlos", "david", "sarah", "james"],
        "files": [
            "payment-service/src/main/java/io/nexuspay/payment/PaymentProcessor.java",
            "payment-service/src/main/java/io/nexuspay/payment/PaymentService.java",
            "fraud-service/src/main/java/io/nexuspay/fraud/FraudDetectionService.java",
            "fraud-service/src/main/java/io/nexuspay/fraud/FraudRuleEngine.java",
            "notification-service/src/main/java/io/nexuspay/notification/WebhookDeliveryService.java",
            "compliance-service/src/main/java/io/nexuspay/compliance/PCIComplianceService.java",
            "compliance-service/src/main/java/io/nexuspay/compliance/AuditTrailService.java",
            "ledger-service/src/main/java/io/nexuspay/ledger/LedgerService.java",
            "gateway-service/src/main/java/io/nexuspay/gateway/RateLimitFilter.java",
            "settlement-service/src/main/java/io/nexuspay/settlement/SettlementService.java",
            "payment-service/src/test/java/io/nexuspay/payment/PaymentServiceTest.java",
            ".github/workflows/ci.yml",
        ],
        "commits": [
            ("fix(payment)", "another timeout edge case — NEXUS-2301"),
            ("fix(payment)", "quick patch for merchant X escalation — revert later"),
            ("fix(fraud)", "disabled ML scoring for card type causing false positives"),
            ("fix(fraud)", "hardcoded threshold override — remove after model retrain"),
            ("fix(notification)", "bypass signature check for internal endpoints — temp"),
            ("fix(compliance)", "PCI log gap patch — does not address root cause"),
            ("fix(ledger)", "added try-catch to suppress duplicate entry exception"),
            ("fix(gateway)", "increased rate limit for merchant Y — not reviewed"),
            ("fix(payment)", "race condition workaround with Thread.sleep — NEXUS-2312"),
            ("fix(settlement)", "hardcoded FX rate for GBP until API is fixed — NEXUS-2318"),
            ("feat(payment)", "new payment method added without tests — needed for launch"),
            ("feat(fraud)", "copied rule logic from payment-service — refactor later"),
            ("fix(compliance)", "audit entries skipped for batch operations — known issue"),
            ("fix(payment)", "N+1 query introduced in payment history endpoint"),
            ("fix(notification)", "retry loop not terminating — added hard limit of 100"),
            ("fix(ledger)", "reconciliation skipping zero-amount entries — quick fix"),
            ("fix(fraud)", "model weights load failing — fallback to rules only"),
            ("fix(payment)", "payment status not updating for async flows — NEXUS-2334"),
            ("fix(compliance)", "GDPR deletion not cascading to audit table — NEXUS-2341"),
            ("fix(gateway)", "circuit breaker config duplicated across three files"),
        ],
    },
]


def git(cmd, env=None):
    result = subprocess.run(
        ["git"] + cmd,
        capture_output=True,
        text=True,
        env={**os.environ, **(env or {})}
    )
    return result


def ensure_file_exists(filepath):
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        return path

    desc = FILES.get(filepath, filepath)

    if filepath.endswith(".java"):
        # Build a realistic Java class skeleton
        parts = filepath.replace("src/main/java/", "").replace("src/test/java/", "")
        parts = parts.replace(".java", "").replace("/", ".")
        package = ".".join(parts.split(".")[:-1])
        classname = parts.split(".")[-1]

        if "Test" in classname:
            content = f"""package {package};

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * {desc}
 */
@ExtendWith(MockitoExtension.class)
class {classname} {{

    @InjectMocks
    private Object subject;

    @Test
    void shouldInitialise() {{
        assertThat(subject).isNotNull();
    }}
}}
"""
        elif "Controller" in classname:
            content = f"""package {package};

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * {desc}
 */
@Slf4j
@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1")
public class {classname} {{

    // {desc}

}}
"""
        elif "Config" in classname:
            content = f"""package {package};

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * {desc}
 */
@Configuration
public class {classname} {{

    // {desc}

}}
"""
        elif "Consumer" in classname or "Producer" in classname:
            content = f"""package {package};

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

/**
 * {desc}
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class {classname} {{

    // {desc}

}}
"""
        elif "Entity" in filepath or "entity" in filepath:
            content = f"""package {package};

import jakarta.persistence.*;
import lombok.Data;
import java.time.Instant;
import java.util.UUID;

/**
 * {desc}
 */
@Data
@Entity
@Table(name = "{classname.lower()}")
public class {classname} {{

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(nullable = false)
    private Instant createdAt = Instant.now();

    @Version
    private Long version;

}}
"""
        else:
            content = f"""package {package};

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

/**
 * {desc}
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class {classname} {{

    // {desc}

}}
"""

    elif filepath.endswith("pom.xml"):
        service = filepath.split("/")[0] if "/" in filepath else "nexuspay"
        content = f"""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>io.nexuspay</groupId>
    <artifactId>{service}</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <description>{desc}</description>
</project>
"""

    elif filepath.endswith(".yml") or filepath.endswith(".yaml"):
        content = f"# {desc}\n# NexusPay Configuration\n\nspring:\n  application:\n    name: {filepath.split('/')[0]}\n"

    elif filepath.endswith(".md"):
        content = f"# NexusPay\n\n{desc}\n"

    elif filepath.endswith(".java") is False and "Dockerfile" in filepath:
        content = f"FROM eclipse-temurin:21-jre-alpine\n# {desc}\nCOPY target/*.jar app.jar\nENTRYPOINT [\"java\", \"-jar\", \"/app.jar\"]\n"

    else:
        content = f"# {desc}\n"

    path.write_text(content)
    return path


def make_realistic_change(filepath, commit_msg, phase_name):
    path = Path(filepath)
    ensure_file_exists(filepath)
    content = path.read_text()

    change_type = commit_msg.split("(")[0] if "(" in commit_msg else "chore"
    ts = datetime.now().strftime("%Y-%m-%d")

    if filepath.endswith(".java"):
        additions = [
            f"\n    // {phase_name}: {commit_msg} [{ts}]\n    private static final String _{random.randint(1000,9999)}_MARKER = \"{change_type}\";\n",
            f"\n    // TODO: {commit_msg}\n    // Added: {ts}\n",
            f"\n    private static final int TIMEOUT_{random.randint(100,999)} = {random.randint(1000,9999)}; // {commit_msg}\n",
            f"\n    // NEXUS-{random.randint(2000,2400)}: {commit_msg}\n",
        ]
        # Insert before last closing brace
        if "}" in content:
            last_brace = content.rfind("}")
            content = content[:last_brace] + random.choice(additions) + content[last_brace:]
        else:
            content += random.choice(additions)

    elif filepath.endswith(".yml") or filepath.endswith(".yaml"):
        content += f"\n# {phase_name}: {commit_msg}\n# {ts}\n"

    elif filepath.endswith(".xml"):
        content += f"\n<!-- {phase_name}: {commit_msg} -->\n"

    else:
        content += f"\n# {commit_msg} [{ts}]\n"

    path.write_text(content)


def interpolate_date(start, end, fraction):
    delta = end - start
    return start + timedelta(seconds=delta.total_seconds() * fraction)


def run_simulation():
    print("\n☕ NexusPay Commit Simulator — Java Microservices Edition\n")
    print(f"   Target: 1,000 commits across 7 development phases")
    print(f"   Stack:  Spring Boot · Kafka · Kubernetes · PostgreSQL · Redis")
    print(f"   Period: {START_DATE.strftime('%b %Y')} → {END_DATE.strftime('%b %Y')}")
    print(f"   Team:   {len(AUTHORS)} engineers\n")

    check = git(["rev-parse", "--git-dir"])
    if check.returncode != 0:
        print("❌ Not in a git repository.")
        print("   Run: mkdir -p ~/sandbox/nexuspay && cd ~/sandbox/nexuspay && git init")
        return

    print("   Scaffolding all Java source files...")
    for filepath in FILES.keys():
        ensure_file_exists(filepath)

    total_commits = 0
    commit_log = []

    for phase in PHASES:
        phase_name    = phase["name"]
        phase_weight  = phase["weight"]
        date_start    = interpolate_date(START_DATE, END_DATE, phase["date_range"][0])
        date_end      = interpolate_date(START_DATE, END_DATE, phase["date_range"][1])
        phase_files   = phase["files"]
        phase_commits = phase["commits"]
        phase_authors = phase["authors"]

        print(f"   Phase: {phase_name} ({phase_weight} commits)...")

        for i in range(phase_weight):
            author_key = random.choice(phase_authors)
            author = next(
                a for a in AUTHORS
                if author_key in a[0].lower().split()[0].lower()
                or author_key in a[0].lower().split()[-1].lower()
            )

            commit_template = random.choice(phase_commits)
            prefix, suffix = commit_template

            ticket = ""
            if random.random() < 0.30:
                ticket = f" — {next_ticket()}"

            commit_msg = f"{prefix}: {suffix}{ticket}"

            n_files = random.randint(1, 3)
            changed_files = random.sample(phase_files, min(n_files, len(phase_files)))

            for filepath in changed_files:
                make_realistic_change(filepath, commit_msg, phase_name)

            git(["add", "-A"])

            status = git(["status", "--porcelain"])
            if not status.stdout.strip():
                continue

            fraction = i / phase_weight
            commit_date = interpolate_date(date_start, date_end, fraction)
            hour = random.randint(8, 22)
            minute = random.randint(0, 59)
            commit_date = commit_date.replace(hour=hour, minute=minute)

            # Skip some weekends — engineers still ship on weekends in fintech
            if commit_date.weekday() >= 5 and random.random() < 0.55:
                commit_date += timedelta(days=random.randint(1, 2))

            date_str = commit_date.strftime("%Y-%m-%dT%H:%M:%S")

            env = {
                "GIT_AUTHOR_NAME":     author[0],
                "GIT_AUTHOR_EMAIL":    author[1],
                "GIT_AUTHOR_DATE":     date_str,
                "GIT_COMMITTER_NAME":  author[0],
                "GIT_COMMITTER_EMAIL": author[1],
                "GIT_COMMITTER_DATE":  date_str,
            }

            result = git(["commit", "-m", commit_msg], env=env)

            if result.returncode == 0:
                total_commits += 1
                commit_log.append({
                    "phase":   phase_name,
                    "author":  author[0],
                    "message": commit_msg,
                    "date":    date_str,
                    "files":   changed_files,
                })

        print(f"   ✅ {phase_name} complete")

    print(f"\n🎉 NexusPay simulation complete!")
    print(f"   {total_commits} commits generated")
    print(f"   {len(set(c['author'] for c in commit_log))} authors")
    print(f"   {len(set(f for c in commit_log for f in c['files']))} files touched")

    with open("nexuspay_commit_log.json", "w") as f:
        json.dump(commit_log, f, indent=2)
    print(f"   Log saved to nexuspay_commit_log.json")

    print(f"\n☕ Now run in this directory:")
    print(f"   gtr ask \"cluster all commits by date and theme, who drove each phase, which services are most fragile, and where did decay start\"")
    print(f"   gtr scan")
    print()


if __name__ == "__main__":
    run_simulation()
