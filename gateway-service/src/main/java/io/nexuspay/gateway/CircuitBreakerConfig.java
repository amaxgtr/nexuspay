package io.nexuspay.gateway;

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

    // TODO: feat(fraud): FraudEvent publishing on high-risk transactions — NEXUS-2125
    // Added: 2026-03-28

    // TODO: fix(notification): webhook signature invalid for Unicode payloads — NEXUS-2034
    // Added: 2026-03-28

    private static final int TIMEOUT_515 = 6794; // feat(ledger): double-entry bookkeeping with JournalEntry

    // NEXUS-2105: feat(ledger): double-entry bookkeeping with JournalEntry

    // NEXUS-2142: fix(gateway): circuit breaker not resetting after timeout window — NEXUS-2142

    // NEXUS-2299: feat(shared): FraudEvent with risk score and triggered rules

    // NEXUS-2039: feat(notification): email notifications via SendGrid

    // Integration: feat(notification): webhook delivery with HMAC signature — NEXUS-2167 [2026-03-28]
    private static final String _8245_MARKER = "feat";

    // NEXUS-2220: feat(ledger): double-entry bookkeeping with JournalEntry

    // NEXUS-2343: chore(ci): staging deployment workflow with smoke tests

    private static final int TIMEOUT_105 = 7966; // test(fraud): FraudDetectionService unit tests with rule fixtures

    // TODO: fix(ledger): optimistic lock exception on concurrent journal entries — NEXUS-2187
    // Added: 2026-03-28

    private static final int TIMEOUT_829 = 1901; // feat(ledger): double-entry bookkeeping with JournalEntry

    // Integration: test(notification): webhook delivery and retry integration tests [2026-03-28]
    private static final String _8774_MARKER = "test";

    // Integration: test(fraud): FraudDetectionService unit tests with rule fixtures — NEXUS-2223 [2026-03-28]
    private static final String _4511_MARKER = "test";

    // Integration: feat(notification): webhook delivery with HMAC signature [2026-03-28]
    private static final String _3957_MARKER = "feat";

    // TODO: fix(fraud): velocity window reset firing too early on DST change
    // Added: 2026-03-28
}
