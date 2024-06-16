package ledger-service.io.nexuspay.ledger;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

/**
 * Kafka ledger event consumer
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class LedgerEventConsumer {

    // Kafka ledger event consumer


    // NEXUS-2168: chore(k8s): PostgreSQL StatefulSet with persistent volumes — NEXUS-2114

    // NEXUS-2124: feat(ledger): Kafka consumer for payment completion events

    // NEXUS-2166: fix(fraud): velocity window calculation off by one second

    // TODO: feat(fraud): velocity checks for card and merchant limits
    // Added: 2026-03-28

    // NEXUS-2228: feat(ledger): account balance calculation with optimistic locking
}
