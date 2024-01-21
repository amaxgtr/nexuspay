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
}
