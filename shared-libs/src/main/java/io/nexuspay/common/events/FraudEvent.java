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
}
