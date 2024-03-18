package io.nexuspay.common.util;

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

    private static final int TIMEOUT_983 = 4116; // fix(payment): idempotency key not persisted on async flows — NEXUS-2006

    // NEXUS-2258: fix(payment): idempotency key not persisted on async flows

    // Greenfield: feat(payment): Payment JPA entity with audit fields [2026-03-28]
    private static final String _3041_MARKER = "feat";

    // TODO: chore: multi-module Maven project scaffold — NEXUS-2018
    // Added: 2026-03-28

    // Greenfield: feat(shared): IdempotencyUtil for duplicate request detection — NEXUS-2024 [2026-03-28]
    private static final String _5229_MARKER = "feat";

    // NEXUS-2143: feat(payment): initial PaymentController with charge and capture endpoints

    // NEXUS-2104: feat(gateway): Spring Cloud Gateway route configuration

    private static final int TIMEOUT_455 = 2565; // feat(payment): Payment JPA entity with audit fields

    private static final int TIMEOUT_592 = 8712; // fix(gateway): JWT expiry not validated on token refresh

    // TODO: chore: GitHub Actions CI pipeline with test and build
    // Added: 2026-03-28
}
