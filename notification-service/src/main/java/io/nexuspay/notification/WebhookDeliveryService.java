package io.nexuspay.notification;

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

    private static final int TIMEOUT_573 = 4495; // feat(fraud): velocity checks for card and merchant limits

    // Integration: chore(k8s): PostgreSQL StatefulSet with persistent volumes — NEXUS-2114 [2026-03-28]
    private static final String _9856_MARKER = "chore";

    private static final int TIMEOUT_987 = 1926; // fix(gateway): circuit breaker not resetting after timeout window

    // TODO: test(ledger): double-entry invariant tests
    // Added: 2026-03-28

    // Integration: feat(fraud): FraudEvent publishing on high-risk transactions [2026-03-28]
    private static final String _7593_MARKER = "feat";

    // TODO: feat(notification): Kafka consumer for payment and fraud events — NEXUS-2134
    // Added: 2026-03-28

    // Integration: feat(ledger): Kafka consumer for payment completion events [2026-03-28]
    private static final String _7344_MARKER = "feat";

    // TODO: fix(fraud): velocity window calculation off by one second — NEXUS-2138
    // Added: 2026-03-28

    private static final int TIMEOUT_586 = 3764; // test(notification): webhook delivery and retry integration tests

    // Integration: feat(fraud): FraudEvent publishing on high-risk transactions — NEXUS-2144 [2026-03-28]
    private static final String _6734_MARKER = "feat";
}
