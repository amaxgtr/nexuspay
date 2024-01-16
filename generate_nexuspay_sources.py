#!/usr/bin/env python3
"""
NexusPay Java Source Generator
-------------------------------
Generates realistic, compilable Java source files for the NexusPay
demo repository. Run this BEFORE simulate_nexuspay.py so the commit
simulator works on top of real code.

Usage:
    cd ~/sandbox/nexuspay
    python generate_nexuspay_sources.py
    python simulate_nexuspay.py
"""

from pathlib import Path

FILES = {}

# ── payment-service ────────────────────────────────────────────────────────────

FILES["payment-service/src/main/java/io/nexuspay/payment/PaymentService.java"] = '''package io.nexuspay.payment;

import io.nexuspay.common.events.PaymentEvent;
import io.nexuspay.common.util.IdempotencyUtil;
import io.nexuspay.payment.dto.PaymentRequest;
import io.nexuspay.payment.dto.PaymentResponse;
import io.nexuspay.payment.entity.Payment;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class PaymentService {

    private final PaymentRepository paymentRepository;
    private final PaymentProcessor paymentProcessor;
    private final PaymentEventProducer eventProducer;
    private final IdempotencyUtil idempotencyUtil;

    @Transactional
    public PaymentResponse processPayment(PaymentRequest request) {
        log.info("Processing payment for merchant={} amount={} currency={}",
            request.getMerchantId(), request.getAmount(), request.getCurrency());

        // Idempotency check
        if (idempotencyUtil.isDuplicate(request.getIdempotencyKey())) {
            log.warn("Duplicate payment request detected key={}", request.getIdempotencyKey());
            return paymentRepository.findByIdempotencyKey(request.getIdempotencyKey())
                .map(this::toResponse)
                .orElseThrow(() -> new PaymentException("Idempotency conflict"));
        }

        Payment payment = Payment.builder()
            .id(UUID.randomUUID())
            .merchantId(request.getMerchantId())
            .amount(request.getAmount())
            .currency(request.getCurrency())
            .idempotencyKey(request.getIdempotencyKey())
            .status(PaymentStatus.PENDING)
            .createdAt(Instant.now())
            .build();

        paymentRepository.save(payment);

        try {
            PaymentProcessor.Result result = paymentProcessor.charge(payment);
            payment.setStatus(result.isSuccess() ? PaymentStatus.COMPLETED : PaymentStatus.FAILED);
            payment.setGatewayReference(result.getReference());
            paymentRepository.save(payment);

            eventProducer.publish(PaymentEvent.completed(payment));
            log.info("Payment completed paymentId={} status={}", payment.getId(), payment.getStatus());

            return toResponse(payment);

        } catch (Exception e) {
            log.error("Payment processing failed paymentId={}", payment.getId(), e);
            payment.setStatus(PaymentStatus.FAILED);
            paymentRepository.save(payment);
            eventProducer.publish(PaymentEvent.failed(payment));
            throw new PaymentException("Payment processing failed", e);
        }
    }

    private PaymentResponse toResponse(Payment payment) {
        return PaymentResponse.builder()
            .paymentId(payment.getId())
            .status(payment.getStatus())
            .amount(payment.getAmount())
            .currency(payment.getCurrency())
            .createdAt(payment.getCreatedAt())
            .build();
    }
}
'''

FILES["payment-service/src/main/java/io/nexuspay/payment/PaymentController.java"] = '''package io.nexuspay.payment;

import io.nexuspay.payment.dto.PaymentRequest;
import io.nexuspay.payment.dto.PaymentResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@Slf4j
@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1/payments")
public class PaymentController {

    private final PaymentService paymentService;

    @PostMapping
    public ResponseEntity<PaymentResponse> createPayment(
        @Valid @RequestBody PaymentRequest request,
        @RequestHeader("X-Idempotency-Key") String idempotencyKey
    ) {
        request.setIdempotencyKey(idempotencyKey);
        PaymentResponse response = paymentService.processPayment(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    @GetMapping("/{paymentId}")
    public ResponseEntity<PaymentResponse> getPayment(@PathVariable UUID paymentId) {
        return paymentService.findById(paymentId)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping("/{paymentId}/refund")
    public ResponseEntity<PaymentResponse> refundPayment(
        @PathVariable UUID paymentId,
        @RequestParam(required = false) Long amount
    ) {
        PaymentResponse response = paymentService.refund(paymentId, amount);
        return ResponseEntity.ok(response);
    }
}
'''

FILES["payment-service/src/main/java/io/nexuspay/payment/PaymentProcessor.java"] = '''package io.nexuspay.payment;

import io.nexuspay.payment.entity.Payment;
import lombok.Builder;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.time.Duration;
import java.util.UUID;

@Slf4j
@Component
@RequiredArgsConstructor
public class PaymentProcessor {

    @Value("${gateway.timeout-ms:5000}")
    private long timeoutMs;

    @Value("${gateway.max-retries:3}")
    private int maxRetries;

    private final GatewayClient gatewayClient;

    public Result charge(Payment payment) {
        log.debug("Charging gateway paymentId={} amount={}", payment.getId(), payment.getAmount());

        for (int attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                GatewayClient.Response response = gatewayClient.charge(
                    payment.getAmount(),
                    payment.getCurrency(),
                    payment.getId().toString(),
                    Duration.ofMillis(timeoutMs)
                );

                if (response.isSuccess()) {
                    return Result.success(response.getReference());
                }

                log.warn("Gateway declined paymentId={} attempt={} code={}",
                    payment.getId(), attempt, response.getDeclineCode());
                return Result.failure(response.getDeclineCode());

            } catch (GatewayTimeoutException e) {
                log.warn("Gateway timeout paymentId={} attempt={}/{}", payment.getId(), attempt, maxRetries);
                if (attempt == maxRetries) {
                    throw new PaymentException("Gateway timeout after " + maxRetries + " attempts", e);
                }
            }
        }

        return Result.failure("MAX_RETRIES_EXCEEDED");
    }

    @Data
    @Builder
    public static class Result {
        private final boolean success;
        private final String reference;
        private final String declineCode;

        public static Result success(String reference) {
            return Result.builder().success(true).reference(reference).build();
        }

        public static Result failure(String declineCode) {
            return Result.builder().success(false).declineCode(declineCode).build();
        }
    }
}
'''

FILES["payment-service/src/main/java/io/nexuspay/payment/PaymentEventProducer.java"] = '''package io.nexuspay.payment;

import io.nexuspay.common.events.PaymentEvent;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.support.SendResult;
import org.springframework.stereotype.Component;

import java.util.concurrent.CompletableFuture;

@Slf4j
@Component
@RequiredArgsConstructor
public class PaymentEventProducer {

    @Value("${kafka.topics.payments:nexuspay.payments}")
    private String paymentsTopic;

    private final KafkaTemplate<String, PaymentEvent> kafkaTemplate;

    public void publish(PaymentEvent event) {
        String key = event.getPaymentId().toString();

        CompletableFuture<SendResult<String, PaymentEvent>> future =
            kafkaTemplate.send(paymentsTopic, key, event);

        future.whenComplete((result, ex) -> {
            if (ex != null) {
                log.error("Failed to publish PaymentEvent paymentId={} type={}",
                    event.getPaymentId(), event.getType(), ex);
            } else {
                log.debug("Published PaymentEvent paymentId={} type={} partition={} offset={}",
                    event.getPaymentId(), event.getType(),
                    result.getRecordMetadata().partition(),
                    result.getRecordMetadata().offset());
            }
        });
    }
}
'''

FILES["payment-service/src/main/java/io/nexuspay/payment/entity/Payment.java"] = '''package io.nexuspay.payment.entity;

import io.nexuspay.payment.PaymentStatus;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.UUID;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "payments", indexes = {
    @Index(name = "idx_payments_merchant", columnList = "merchant_id"),
    @Index(name = "idx_payments_idempotency", columnList = "idempotency_key", unique = true),
    @Index(name = "idx_payments_status", columnList = "status"),
    @Index(name = "idx_payments_created", columnList = "created_at")
})
public class Payment {

    @Id
    private UUID id;

    @Column(name = "merchant_id", nullable = false)
    private UUID merchantId;

    @Column(nullable = false, precision = 19, scale = 4)
    private BigDecimal amount;

    @Column(nullable = false, length = 3)
    private String currency;

    @Column(name = "idempotency_key", nullable = false, unique = true)
    private String idempotencyKey;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private PaymentStatus status;

    @Column(name = "gateway_reference")
    private String gatewayReference;

    @Column(name = "decline_code")
    private String declineCode;

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at")
    private Instant updatedAt;

    @Version
    private Long version;
}
'''

# ── fraud-service ──────────────────────────────────────────────────────────────

FILES["fraud-service/src/main/java/io/nexuspay/fraud/FraudDetectionService.java"] = '''package io.nexuspay.fraud;

import io.nexuspay.common.events.FraudEvent;
import io.nexuspay.common.events.PaymentEvent;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Slf4j
@Service
@RequiredArgsConstructor
public class FraudDetectionService {

    @Value("${fraud.ml.enabled:true}")
    private boolean mlEnabled;

    @Value("${fraud.score.block-threshold:85}")
    private int blockThreshold;

    @Value("${fraud.score.review-threshold:60}")
    private int reviewThreshold;

    private final FraudRuleEngine ruleEngine;
    private final FraudScoreCalculator scoreCalculator;
    private final VelocityChecker velocityChecker;

    public FraudAssessment assess(PaymentEvent event) {
        log.debug("Assessing fraud risk paymentId={} merchant={}",
            event.getPaymentId(), event.getMerchantId());

        // Velocity check first — fast path rejection
        VelocityChecker.Result velocity = velocityChecker.check(event);
        if (velocity.isBlocked()) {
            log.warn("Payment blocked by velocity check paymentId={} reason={}",
                event.getPaymentId(), velocity.getReason());
            return FraudAssessment.block(99, velocity.getReason());
        }

        // Rule engine scoring
        FraudRuleEngine.Result rules = ruleEngine.evaluate(event);

        // ML scoring if enabled
        int finalScore;
        if (mlEnabled) {
            int mlScore = scoreCalculator.score(event, rules);
            finalScore = (int) (mlScore * 0.7 + rules.getScore() * 0.3);
            log.debug("Fraud scores paymentId={} ml={} rules={} combined={}",
                event.getPaymentId(), mlScore, rules.getScore(), finalScore);
        } else {
            finalScore = rules.getScore();
        }

        if (finalScore >= blockThreshold) {
            return FraudAssessment.block(finalScore, rules.getTopRule());
        } else if (finalScore >= reviewThreshold) {
            return FraudAssessment.review(finalScore, rules.getTopRule());
        }

        return FraudAssessment.allow(finalScore);
    }
}
'''

FILES["fraud-service/src/main/java/io/nexuspay/fraud/VelocityChecker.java"] = '''package io.nexuspay.fraud;

import io.nexuspay.common.events.PaymentEvent;
import lombok.Builder;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Component;

import java.time.Duration;

@Slf4j
@Component
@RequiredArgsConstructor
public class VelocityChecker {

    @Value("${fraud.velocity.card-limit:10}")
    private int cardTransactionLimit;

    @Value("${fraud.velocity.merchant-limit:1000}")
    private int merchantTransactionLimit;

    @Value("${fraud.velocity.window-minutes:60}")
    private int windowMinutes;

    private final RedisTemplate<String, Long> redisTemplate;

    public Result check(PaymentEvent event) {
        String cardKey = "velocity:card:" + event.getCardFingerprint();
        String merchantKey = "velocity:merchant:" + event.getMerchantId();

        Long cardCount = increment(cardKey);
        Long merchantCount = increment(merchantKey);

        if (cardCount != null && cardCount > cardTransactionLimit) {
            log.warn("Card velocity exceeded card={} count={} limit={}",
                event.getCardFingerprint(), cardCount, cardTransactionLimit);
            return Result.blocked("CARD_VELOCITY_EXCEEDED");
        }

        if (merchantCount != null && merchantCount > merchantTransactionLimit) {
            log.warn("Merchant velocity exceeded merchant={} count={} limit={}",
                event.getMerchantId(), merchantCount, merchantTransactionLimit);
            return Result.blocked("MERCHANT_VELOCITY_EXCEEDED");
        }

        return Result.allowed();
    }

    private Long increment(String key) {
        try {
            Long count = redisTemplate.opsForValue().increment(key);
            redisTemplate.expire(key, Duration.ofMinutes(windowMinutes));
            return count;
        } catch (Exception e) {
            log.error("Redis velocity check failed for key={}", key, e);
            return null; // Fail open — don't block on Redis failure
        }
    }

    @Data
    @Builder
    public static class Result {
        private final boolean blocked;
        private final String reason;

        public static Result blocked(String reason) {
            return Result.builder().blocked(true).reason(reason).build();
        }

        public static Result allowed() {
            return Result.builder().blocked(false).build();
        }
    }
}
'''

# ── notification-service ───────────────────────────────────────────────────────

FILES["notification-service/src/main/java/io/nexuspay/notification/WebhookDeliveryService.java"] = '''package io.nexuspay.notification;

import io.nexuspay.common.events.PaymentEvent;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.retry.annotation.Backoff;
import org.springframework.retry.annotation.Retryable;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.util.Base64;

@Slf4j
@Service
@RequiredArgsConstructor
public class WebhookDeliveryService {

    @Value("${webhook.timeout-ms:10000}")
    private int timeoutMs;

    @Value("${webhook.max-attempts:5}")
    private int maxAttempts;

    private final RestTemplate restTemplate;
    private final WebhookRepository webhookRepository;

    @Retryable(
        retryFor = WebhookDeliveryException.class,
        maxAttempts = 5,
        backoff = @Backoff(delay = 1000, multiplier = 2, maxDelay = 60000)
    )
    public void deliver(String url, String secret, PaymentEvent event) {
        String payload = serializeEvent(event);
        String signature = computeSignature(payload, secret);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.set("X-NexusPay-Signature", signature);
        headers.set("X-NexusPay-Event", event.getType());
        headers.set("X-NexusPay-Delivery-ID", event.getPaymentId().toString());

        HttpEntity<String> request = new HttpEntity<>(payload, headers);

        try {
            ResponseEntity<Void> response = restTemplate.postForEntity(url, request, Void.class);

            if (!response.getStatusCode().is2xxSuccessful()) {
                log.warn("Webhook delivery failed url={} status={}", url, response.getStatusCode());
                throw new WebhookDeliveryException("Non-2xx response: " + response.getStatusCode());
            }

            log.info("Webhook delivered successfully url={} paymentId={}", url, event.getPaymentId());

        } catch (Exception e) {
            log.error("Webhook delivery error url={} paymentId={}", url, event.getPaymentId(), e);
            throw new WebhookDeliveryException("Delivery failed: " + e.getMessage(), e);
        }
    }

    private String computeSignature(String payload, String secret) {
        try {
            Mac mac = Mac.getInstance("HmacSHA256");
            SecretKeySpec keySpec = new SecretKeySpec(
                secret.getBytes(StandardCharsets.UTF_8), "HmacSHA256"
            );
            mac.init(keySpec);
            byte[] hash = mac.doFinal(payload.getBytes(StandardCharsets.UTF_8));
            return "sha256=" + Base64.getEncoder().encodeToString(hash);
        } catch (NoSuchAlgorithmException | InvalidKeyException e) {
            throw new RuntimeException("Failed to compute webhook signature", e);
        }
    }

    private String serializeEvent(PaymentEvent event) {
        // Serialization via ObjectMapper injected via constructor omitted for brevity
        return "{}";
    }
}
'''

# ── ledger-service ─────────────────────────────────────────────────────────────

FILES["ledger-service/src/main/java/io/nexuspay/ledger/LedgerService.java"] = '''package io.nexuspay.ledger;

import io.nexuspay.ledger.entity.JournalEntry;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Isolation;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.List;
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class LedgerService {

    private final JournalEntryRepository journalEntryRepository;
    private final AccountRepository accountRepository;

    /**
     * Record a double-entry journal entry.
     * Debits and credits must balance to zero — enforced at service layer.
     */
    @Transactional(isolation = Isolation.SERIALIZABLE)
    public void recordPayment(UUID paymentId, UUID merchantId, BigDecimal amount, String currency) {
        log.info("Recording ledger entry paymentId={} amount={} currency={}", paymentId, amount, currency);

        // Validate double-entry balance
        BigDecimal debit = amount;
        BigDecimal credit = amount.negate();

        if (debit.add(credit).compareTo(BigDecimal.ZERO) != 0) {
            throw new LedgerException("Journal entry does not balance: debit=" + debit + " credit=" + credit);
        }

        Instant now = Instant.now();

        // Debit merchant account (funds owed to merchant)
        JournalEntry debitEntry = JournalEntry.builder()
            .id(UUID.randomUUID())
            .paymentId(paymentId)
            .accountId(merchantId)
            .amount(debit)
            .currency(currency)
            .entryType(EntryType.DEBIT)
            .description("Payment charge — " + paymentId)
            .timestamp(now)
            .build();

        // Credit settlement account (funds received from card network)
        JournalEntry creditEntry = JournalEntry.builder()
            .id(UUID.randomUUID())
            .paymentId(paymentId)
            .accountId(getSettlementAccount(currency))
            .amount(credit)
            .currency(currency)
            .entryType(EntryType.CREDIT)
            .description("Payment charge credit — " + paymentId)
            .timestamp(now)
            .build();

        journalEntryRepository.saveAll(List.of(debitEntry, creditEntry));

        // Update account balances
        accountRepository.updateBalance(merchantId, debit);
        accountRepository.updateBalance(getSettlementAccount(currency), credit);

        log.debug("Ledger entry recorded paymentId={}", paymentId);
    }

    @Transactional(readOnly = true)
    public BigDecimal getBalance(UUID accountId, String currency) {
        return journalEntryRepository.sumByAccountAndCurrency(accountId, currency)
            .orElse(BigDecimal.ZERO);
    }

    private UUID getSettlementAccount(String currency) {
        return accountRepository.findSettlementAccount(currency)
            .orElseThrow(() -> new LedgerException("No settlement account for currency: " + currency));
    }
}
'''

# ── gateway-service ────────────────────────────────────────────────────────────

FILES["gateway-service/src/main/java/io/nexuspay/gateway/AuthFilter.java"] = '''package io.nexuspay.gateway;

import io.nexuspay.common.security.JwtUtil;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.cloud.gateway.filter.GatewayFilter;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

@Slf4j
@Component
@RequiredArgsConstructor
public class AuthFilter implements GatewayFilter {

    private static final String BEARER_PREFIX = "Bearer ";
    private static final String MERCHANT_ID_HEADER = "X-NexusPay-Merchant-ID";

    private final JwtUtil jwtUtil;

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        String authHeader = exchange.getRequest().getHeaders().getFirst(HttpHeaders.AUTHORIZATION);

        if (authHeader == null || !authHeader.startsWith(BEARER_PREFIX)) {
            log.warn("Missing or invalid Authorization header path={}",
                exchange.getRequest().getPath());
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();
        }

        String token = authHeader.substring(BEARER_PREFIX.length());

        try {
            JwtUtil.Claims claims = jwtUtil.validate(token);

            // Forward merchant identity to downstream services
            ServerWebExchange mutated = exchange.mutate()
                .request(r -> r.header(MERCHANT_ID_HEADER, claims.getMerchantId().toString()))
                .build();

            log.debug("Authenticated request merchantId={} path={}",
                claims.getMerchantId(), exchange.getRequest().getPath());

            return chain.filter(mutated);

        } catch (JwtUtil.TokenExpiredException e) {
            log.warn("Expired token path={}", exchange.getRequest().getPath());
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();

        } catch (Exception e) {
            log.error("Token validation failed path={}", exchange.getRequest().getPath(), e);
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();
        }
    }
}
'''

FILES["gateway-service/src/main/java/io/nexuspay/gateway/CircuitBreakerConfig.java"] = '''package io.nexuspay.gateway;

import io.github.resilience4j.circuitbreaker.CircuitBreakerConfig.SlidingWindowType;
import io.github.resilience4j.timelimiter.TimeLimiterConfig;
import org.springframework.cloud.circuitbreaker.resilience4j.ReactiveResilience4JCircuitBreakerFactory;
import org.springframework.cloud.circuitbreaker.resilience4j.Resilience4JConfigBuilder;
import org.springframework.cloud.client.circuitbreaker.Customizer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.time.Duration;

@Configuration
public class CircuitBreakerConfig {

    @Bean
    public Customizer<ReactiveResilience4JCircuitBreakerFactory> defaultCustomizer() {
        return factory -> factory.configureDefault(id ->
            new Resilience4JConfigBuilder(id)
                .circuitBreakerConfig(
                    io.github.resilience4j.circuitbreaker.CircuitBreakerConfig.custom()
                        .slidingWindowType(SlidingWindowType.COUNT_BASED)
                        .slidingWindowSize(20)
                        .minimumNumberOfCalls(10)
                        .failureRateThreshold(50.0f)
                        .waitDurationInOpenState(Duration.ofSeconds(30))
                        .permittedNumberOfCallsInHalfOpenState(5)
                        .slowCallDurationThreshold(Duration.ofSeconds(3))
                        .slowCallRateThreshold(80.0f)
                        .build()
                )
                .timeLimiterConfig(
                    TimeLimiterConfig.custom()
                        .timeoutDuration(Duration.ofSeconds(10))
                        .build()
                )
                .build()
        );
    }

    @Bean
    public Customizer<ReactiveResilience4JCircuitBreakerFactory> paymentServiceCustomizer() {
        return factory -> factory.configure(builder ->
            builder.circuitBreakerConfig(
                io.github.resilience4j.circuitbreaker.CircuitBreakerConfig.custom()
                    .slidingWindowSize(50)
                    .failureRateThreshold(40.0f)
                    .waitDurationInOpenState(Duration.ofSeconds(15))
                    .build()
            ), "payment-service"
        );
    }
}
'''

# ── shared-libs ────────────────────────────────────────────────────────────────

FILES["shared-libs/src/main/java/io/nexuspay/common/events/PaymentEvent.java"] = '''package io.nexuspay.common.events;

import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.UUID;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PaymentEvent {

    public enum Type {
        PAYMENT_CREATED,
        PAYMENT_COMPLETED,
        PAYMENT_FAILED,
        PAYMENT_REFUNDED
    }

    private UUID eventId;
    private UUID paymentId;
    private UUID merchantId;
    private String cardFingerprint;
    private BigDecimal amount;
    private String currency;
    private Type type;
    private String correlationId;
    private Instant occurredAt;
    private String gatewayReference;

    public static PaymentEvent completed(io.nexuspay.payment.entity.Payment payment) {
        return PaymentEvent.builder()
            .eventId(UUID.randomUUID())
            .paymentId(payment.getId())
            .merchantId(payment.getMerchantId())
            .amount(payment.getAmount())
            .currency(payment.getCurrency())
            .type(Type.PAYMENT_COMPLETED)
            .gatewayReference(payment.getGatewayReference())
            .occurredAt(Instant.now())
            .build();
    }

    public static PaymentEvent failed(io.nexuspay.payment.entity.Payment payment) {
        return PaymentEvent.builder()
            .eventId(UUID.randomUUID())
            .paymentId(payment.getId())
            .merchantId(payment.getMerchantId())
            .amount(payment.getAmount())
            .currency(payment.getCurrency())
            .type(Type.PAYMENT_FAILED)
            .occurredAt(Instant.now())
            .build();
    }
}
'''

FILES["shared-libs/src/main/java/io/nexuspay/common/util/IdempotencyUtil.java"] = '''package io.nexuspay.common.util;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Component;

import java.time.Duration;

@Slf4j
@Component
@RequiredArgsConstructor
public class IdempotencyUtil {

    private static final String PREFIX = "idempotency:";
    private static final Duration TTL = Duration.ofHours(24);

    private final RedisTemplate<String, String> redisTemplate;

    /**
     * Returns true if this key has been seen before (duplicate request).
     * Atomically sets the key on first call.
     */
    public boolean isDuplicate(String idempotencyKey) {
        String redisKey = PREFIX + idempotencyKey;
        Boolean isNew = redisTemplate.opsForValue().setIfAbsent(redisKey, "1", TTL);
        boolean duplicate = Boolean.FALSE.equals(isNew);

        if (duplicate) {
            log.debug("Duplicate idempotency key detected key={}", idempotencyKey);
        }

        return duplicate;
    }

    public void invalidate(String idempotencyKey) {
        redisTemplate.delete(PREFIX + idempotencyKey);
    }
}
'''

# ── compliance-service ─────────────────────────────────────────────────────────

FILES["compliance-service/src/main/java/io/nexuspay/compliance/AuditTrailService.java"] = '''package io.nexuspay.compliance;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Instant;
import java.util.Base64;
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class AuditTrailService {

    private final AuditEntryRepository auditEntryRepository;

    /**
     * Append an immutable audit entry with a hash chain for tamper detection.
     * Each entry includes a hash of the previous entry, forming a chain
     * that makes retroactive modification detectable.
     */
    public void record(String entityType, UUID entityId, String action,
                       String performedBy, String details) {
        String previousHash = auditEntryRepository.findLatestHash()
            .orElse("GENESIS");

        AuditEntry entry = AuditEntry.builder()
            .id(UUID.randomUUID())
            .entityType(entityType)
            .entityId(entityId)
            .action(action)
            .performedBy(performedBy)
            .details(details)
            .timestamp(Instant.now())
            .previousHash(previousHash)
            .build();

        // Compute hash of this entry including previous hash
        entry.setHash(computeHash(entry, previousHash));

        auditEntryRepository.save(entry);

        log.debug("Audit entry recorded entity={} entityId={} action={}",
            entityType, entityId, action);
    }

    /**
     * Verify the integrity of the audit chain.
     * Returns false if any entry has been tampered with.
     */
    public boolean verifyChain() {
        var entries = auditEntryRepository.findAllOrderedByTimestamp();
        String expectedPrevious = "GENESIS";

        for (AuditEntry entry : entries) {
            if (!entry.getPreviousHash().equals(expectedPrevious)) {
                log.error("Audit chain integrity violation at entryId={}", entry.getId());
                return false;
            }
            String expectedHash = computeHash(entry, expectedPrevious);
            if (!expectedHash.equals(entry.getHash())) {
                log.error("Audit entry hash mismatch at entryId={}", entry.getId());
                return false;
            }
            expectedPrevious = entry.getHash();
        }

        return true;
    }

    private String computeHash(AuditEntry entry, String previousHash) {
        try {
            String input = previousHash + "|" + entry.getEntityType() + "|"
                + entry.getEntityId() + "|" + entry.getAction() + "|"
                + entry.getTimestamp().toEpochMilli();
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(input.getBytes(StandardCharsets.UTF_8));
            return Base64.getEncoder().encodeToString(hash);
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("SHA-256 not available", e);
        }
    }
}
'''

# ── application.yml files ──────────────────────────────────────────────────────

FILES["payment-service/src/main/resources/application.yml"] = '''spring:
  application:
    name: payment-service
  datasource:
    url: jdbc:postgresql://${DB_HOST:localhost}:5432/nexuspay_payments
    username: ${DB_USER:nexuspay}
    password: ${DB_PASSWORD:nexuspay}
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 30000
      idle-timeout: 600000
  jpa:
    hibernate:
      ddl-auto: validate
    properties:
      hibernate:
        dialect: org.hibernate.dialect.PostgreSQLDialect
        jdbc:
          batch_size: 50
  kafka:
    bootstrap-servers: ${KAFKA_BROKERS:localhost:9092}
    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: org.springframework.kafka.support.serializer.JsonSerializer
      acks: all
      retries: 3
      properties:
        enable.idempotence: true
        max.in.flight.requests.per.connection: 5

kafka:
  topics:
    payments: nexuspay.payments

gateway:
  timeout-ms: 5000
  max-retries: 3

management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  metrics:
    export:
      prometheus:
        enabled: true

logging:
  level:
    io.nexuspay: INFO
    org.springframework.kafka: WARN
'''

FILES["fraud-service/src/main/resources/application.yml"] = '''spring:
  application:
    name: fraud-service
  kafka:
    bootstrap-servers: ${KAFKA_BROKERS:localhost:9092}
    consumer:
      group-id: fraud-service
      auto-offset-reset: earliest
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: org.springframework.kafka.support.serializer.JsonDeserializer
      properties:
        spring.json.trusted.packages: io.nexuspay.common.events
  data:
    redis:
      host: ${REDIS_HOST:localhost}
      port: 6379
      password: ${REDIS_PASSWORD:}
      timeout: 2000ms

fraud:
  ml:
    enabled: true
    model-path: /models/fraud-v2.pkl
  score:
    block-threshold: 85
    review-threshold: 60
  velocity:
    card-limit: 10
    merchant-limit: 1000
    window-minutes: 60

management:
  endpoints:
    web:
      exposure:
        include: health,metrics,prometheus
'''

# ── pom.xml files ──────────────────────────────────────────────────────────────

FILES["payment-service/pom.xml"] = '''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.3</version>
    </parent>

    <groupId>io.nexuspay</groupId>
    <artifactId>payment-service</artifactId>
    <version>2.4.1-SNAPSHOT</version>
    <description>NexusPay Payment Processing Service</description>

    <properties>
        <java.version>21</java.version>
        <testcontainers.version>1.19.6</testcontainers.version>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.kafka</groupId>
            <artifactId>spring-kafka</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-actuator</artifactId>
        </dependency>
        <dependency>
            <groupId>org.postgresql</groupId>
            <artifactId>postgresql</artifactId>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>
        <dependency>
            <groupId>io.micrometer</groupId>
            <artifactId>micrometer-registry-prometheus</artifactId>
        </dependency>

        <!-- Test -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.springframework.kafka</groupId>
            <artifactId>spring-kafka-test</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.testcontainers</groupId>
            <artifactId>postgresql</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.testcontainers</groupId>
            <artifactId>kafka</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>
'''

FILES["pom.xml"] = '''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>io.nexuspay</groupId>
    <artifactId>nexuspay-platform</artifactId>
    <version>2.4.1-SNAPSHOT</version>
    <packaging>pom</packaging>
    <description>NexusPay — Cloud-native payment infrastructure platform</description>

    <modules>
        <module>shared-libs</module>
        <module>payment-service</module>
        <module>fraud-service</module>
        <module>notification-service</module>
        <module>ledger-service</module>
        <module>merchant-service</module>
        <module>settlement-service</module>
        <module>compliance-service</module>
        <module>gateway-service</module>
    </modules>

    <properties>
        <java.version>21</java.version>
        <spring-boot.version>3.2.3</spring-boot.version>
        <spring-cloud.version>2023.0.0</spring-cloud.version>
        <resilience4j.version>2.2.0</resilience4j.version>
        <testcontainers.version>1.19.6</testcontainers.version>
    </properties>
</project>
'''

FILES["docker-compose.yml"] = '''version: "3.9"

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: nexuspay
      POSTGRES_PASSWORD: nexuspay
      POSTGRES_DB: nexuspay_payments
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U nexuspay"]
      interval: 10s
      timeout: 5s
      retries: 5

  kafka:
    image: confluentinc/cp-kafka:7.6.0
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"
    ports:
      - "9092:9092"
    depends_on:
      - zookeeper

  zookeeper:
    image: confluentinc/cp-zookeeper:7.6.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
    ports:
      - "2181:2181"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    environment:
      KAFKA_CLUSTERS_0_NAME: nexuspay-local
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka:9092
    ports:
      - "8080:8080"
    depends_on:
      - kafka

volumes:
  postgres_data:
  redis_data:
'''

FILES["README.md"] = '''# NexusPay Platform

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
'''

FILES[".github/workflows/ci.yml"] = '''name: CI

on:
  push:
    branches: [main, develop, "feature/**", "hotfix/**"]
  pull_request:
    branches: [main, develop]

jobs:
  build:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: nexuspay
          POSTGRES_PASSWORD: nexuspay
          POSTGRES_DB: nexuspay_test
        ports:
          - 5432:5432

      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v4

      - name: Set up Java 21
        uses: actions/setup-java@v4
        with:
          java-version: "21"
          distribution: "temurin"
          cache: maven

      - name: Build and test
        run: mvn clean verify -T 4

      - name: Publish test report
        uses: dorny/test-reporter@v1
        if: always()
        with:
          name: JUnit Tests
          path: "**/target/surefire-reports/*.xml"
          reporter: java-junit

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
'''

FILES["k8s/payment-service-deployment.yaml"] = '''apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-service
  namespace: nexuspay
  labels:
    app: payment-service
    version: "2.4.1"
spec:
  replicas: 3
  selector:
    matchLabels:
      app: payment-service
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: payment-service
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
        prometheus.io/path: "/actuator/prometheus"
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchExpressions:
                    - key: app
                      operator: In
                      values:
                        - payment-service
                topologyKey: kubernetes.io/hostname
      containers:
        - name: payment-service
          image: nexuspay/payment-service:2.4.1
          ports:
            - containerPort: 8080
          env:
            - name: SPRING_PROFILES_ACTIVE
              value: "production"
            - name: DB_HOST
              valueFrom:
                secretKeyRef:
                  name: nexuspay-db-secret
                  key: host
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: nexuspay-db-secret
                  key: password
            - name: KAFKA_BROKERS
              valueFrom:
                configMapKeyRef:
                  name: nexuspay-config
                  key: kafka.brokers
          resources:
            requests:
              cpu: "500m"
              memory: "512Mi"
            limits:
              cpu: "2000m"
              memory: "1Gi"
          livenessProbe:
            httpGet:
              path: /actuator/health/liveness
              port: 8080
            initialDelaySeconds: 60
            periodSeconds: 15
          readinessProbe:
            httpGet:
              path: /actuator/health/readiness
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: payment-service
  namespace: nexuspay
spec:
  selector:
    app: payment-service
  ports:
    - port: 80
      targetPort: 8080
  type: ClusterIP
'''

FILES["k8s/hpa.yaml"] = '''apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: payment-service-hpa
  namespace: nexuspay
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: payment-service
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
    - type: Pods
      pods:
        metric:
          name: kafka_consumer_lag
        target:
          type: AverageValue
          averageValue: "1000"
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
        - type: Pods
          value: 2
          periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Pods
          value: 1
          periodSeconds: 120
'''

def generate():
    print("\n☕ NexusPay Java Source Generator\n")
    print(f"   Generating {len(FILES)} source files with real implementation code...\n")

    created = 0
    for filepath, content in FILES.items():
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        created += 1

    print(f"   ✅ {created} files generated")
    print(f"\n   Now run the commit simulator:")
    print(f"   python simulate_nexuspay.py\n")

if __name__ == "__main__":
    generate()
