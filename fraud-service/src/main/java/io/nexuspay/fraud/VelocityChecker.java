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
}
