package io.nexuspay.payment;

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

    // NEXUS-2021: fix(payment): idempotency key not persisted on async flows

    private static final int TIMEOUT_452 = 6802; // feat(shared): PaymentEvent base class with correlation ID

    // Greenfield: fix(gateway): JWT expiry not validated on token refresh [2026-03-28]
    private static final String _8570_MARKER = "fix";

    // TODO: chore: multi-module Maven project scaffold — NEXUS-2028
    // Added: 2026-03-28

    // Greenfield: docs: README with architecture overview and setup guide [2026-03-28]
    private static final String _5385_MARKER = "chore";

    // Greenfield: chore: Docker Compose for local Kafka, Postgres, Redis [2026-03-28]
    private static final String _8879_MARKER = "chore";

    private static final int TIMEOUT_202 = 3885; // chore: Docker Compose for local Kafka, Postgres, Redis

    // TODO: feat(shared): JwtUtil for token generation and validation — NEXUS-2050
    // Added: 2026-03-28

    // NEXUS-2188: feat(shared): CurrencyUtil with ISO 4217 currency handling

    private static final int TIMEOUT_598 = 5990; // test(payment): PaymentService unit test suite with Mockito — NEXUS-2065

    // Greenfield: feat(payment): initial PaymentController with charge and capture endpoints [2026-03-28]
    private static final String _7212_MARKER = "feat";

    // Greenfield: feat(shared): PaymentEvent base class with correlation ID — NEXUS-2078 [2026-03-28]
    private static final String _6052_MARKER = "feat";

    // NEXUS-2340: chore: multi-module Maven project scaffold — NEXUS-2083

    private static final int TIMEOUT_210 = 9908; // feat(payment): PaymentService orchestration layer with idempotency

    private static final int TIMEOUT_216 = 2783; // feat(payment): Payment JPA entity with audit fields

    // Greenfield: feat(payment): PaymentProcessor with Stripe gateway integration [2026-03-28]
    private static final String _3890_MARKER = "feat";

    // NEXUS-2326: test(payment): PaymentController integration tests with MockMvc

    private static final int TIMEOUT_904 = 8904; // feat(payment): Kafka producer for PaymentCreated and PaymentCompleted events — NEXUS-2090

    // Greenfield: feat(payment): initial PaymentController with charge and capture endpoints — NEXUS-2094 [2026-03-28]
    private static final String _8960_MARKER = "feat";

    // NEXUS-2342: feat(shared): PaymentEvent base class with correlation ID
}
