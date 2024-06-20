package notification-service.io.nexuspay.notification;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

/**
 * Kafka consumer for events
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class PaymentEventConsumer {

    // Kafka consumer for events


    // TODO: test(fraud): FraudDetectionService unit tests with rule fixtures
    // Added: 2026-03-28

    private static final int TIMEOUT_958 = 3988; // test(ledger): double-entry invariant tests

    // NEXUS-2228: chore(ci): staging deployment workflow with smoke tests — NEXUS-2128

    private static final int TIMEOUT_788 = 3700; // feat(fraud): FraudEvent publishing on high-risk transactions — NEXUS-2144

    // TODO: feat(ledger): double-entry bookkeeping with JournalEntry
    // Added: 2026-03-28
}
