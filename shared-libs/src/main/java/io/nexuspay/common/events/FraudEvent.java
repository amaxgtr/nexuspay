package shared-libs.io.nexuspay.common.events;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

/**
 * Fraud domain event
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class FraudEvent {

    // Fraud domain event


    // NEXUS-2134: feat(ledger): Kafka consumer for payment completion events — NEXUS-2111

    // Integration: feat(fraud): velocity checks for card and merchant limits [2026-03-28]
    private static final String _1560_MARKER = "feat";

    // TODO: chore(k8s): PostgreSQL StatefulSet with persistent volumes — NEXUS-2114
    // Added: 2026-03-28

    // Integration: feat(notification): email notifications via SendGrid [2026-03-28]
    private static final String _4828_MARKER = "feat";

    // Integration: fix(fraud): velocity window calculation off by one second [2026-03-28]
    private static final String _8192_MARKER = "fix";

    // TODO: feat(fraud): Kafka consumer for PaymentCreated events
    // Added: 2026-03-28
}
