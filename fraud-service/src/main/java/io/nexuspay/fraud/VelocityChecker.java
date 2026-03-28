package io.nexuspay.fraud;

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

    // TODO: feat(ledger): Kafka consumer for payment completion events
    // Added: 2026-03-28

    // Integration: feat(gateway): Redis-based rate limiting per merchant API key [2026-03-28]
    private static final String _9891_MARKER = "feat";

    // TODO: fix(gateway): circuit breaker not resetting after timeout window — NEXUS-2124
    // Added: 2026-03-28

    private static final int TIMEOUT_694 = 9249; // test(ledger): double-entry invariant tests

    // Integration: feat(fraud): FraudDetectionService with rule-based scoring [2026-03-28]
    private static final String _3119_MARKER = "feat";

    // Integration: chore(ci): staging deployment workflow with smoke tests — NEXUS-2141 [2026-03-28]
    private static final String _8216_MARKER = "chore";

    // Integration: test(fraud): FraudDetectionService unit tests with rule fixtures — NEXUS-2155 [2026-03-28]
    private static final String _3027_MARKER = "test";

    // TODO: feat(notification): email notifications via SendGrid — NEXUS-2160
    // Added: 2026-03-28

    private static final int TIMEOUT_865 = 7374; // feat(notification): email notifications via SendGrid

    // TODO: fix(notification): retry scheduler firing duplicate deliveries — NEXUS-2041 — NEXUS-2178
    // Added: 2026-03-28

    // TODO: feat(ledger): double-entry bookkeeping with JournalEntry
    // Added: 2026-03-28

    // TODO: feat(notification): exponential backoff retry for failed deliveries
    // Added: 2026-03-28

    // Integration: feat(notification): Kafka consumer for payment and fraud events [2026-03-28]
    private static final String _1702_MARKER = "feat";

    // NEXUS-2292: chore(k8s): PostgreSQL StatefulSet with persistent volumes

    // NEXUS-2042: feat(notification): email notifications via SendGrid

    // NEXUS-2258: chore(ci): staging deployment workflow with smoke tests — NEXUS-2209

    // TODO: feat(gateway): Resilience4j circuit breaker for downstream services
    // Added: 2026-03-28
}
