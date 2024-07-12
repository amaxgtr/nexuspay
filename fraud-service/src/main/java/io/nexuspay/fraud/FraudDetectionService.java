package io.nexuspay.fraud;

import io.nexuspay.common.events.FraudEvent;
import io.nexuspay.common.events.PaymentEvent;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Slf4j
@Service
@RequiredArgsConstructor
public class FraudDetectionService {

    @Value("${fraud.ml.enabled:true}")
    private boolean mlEnabled;

    @Value("${fraud.score.block-threshold:85}")
    private int blockThreshold;

    @Value("${fraud.score.review-threshold:60}")
    private int reviewThreshold;

    private final FraudRuleEngine ruleEngine;
    private final FraudScoreCalculator scoreCalculator;
    private final VelocityChecker velocityChecker;

    public FraudAssessment assess(PaymentEvent event) {
        log.debug("Assessing fraud risk paymentId={} merchant={}",
            event.getPaymentId(), event.getMerchantId());

        // Velocity check first — fast path rejection
        VelocityChecker.Result velocity = velocityChecker.check(event);
        if (velocity.isBlocked()) {
            log.warn("Payment blocked by velocity check paymentId={} reason={}",
                event.getPaymentId(), velocity.getReason());
            return FraudAssessment.block(99, velocity.getReason());
        }

        // Rule engine scoring
        FraudRuleEngine.Result rules = ruleEngine.evaluate(event);

        // ML scoring if enabled
        int finalScore;
        if (mlEnabled) {
            int mlScore = scoreCalculator.score(event, rules);
            finalScore = (int) (mlScore * 0.7 + rules.getScore() * 0.3);
            log.debug("Fraud scores paymentId={} ml={} rules={} combined={}",
                event.getPaymentId(), mlScore, rules.getScore(), finalScore);
        } else {
            finalScore = rules.getScore();
        }

        if (finalScore >= blockThreshold) {
            return FraudAssessment.block(finalScore, rules.getTopRule());
        } else if (finalScore >= reviewThreshold) {
            return FraudAssessment.review(finalScore, rules.getTopRule());
        }

        return FraudAssessment.allow(finalScore);
    }

    private static final int TIMEOUT_997 = 9314; // fix(gateway): circuit breaker not resetting after timeout window

    // NEXUS-2000: fix(ledger): optimistic lock exception on concurrent journal entries

    // TODO: fix(fraud): velocity window calculation off by one second
    // Added: 2026-03-28

    // Integration: feat(ledger): double-entry bookkeeping with JournalEntry [2026-03-28]
    private static final String _6880_MARKER = "feat";

    private static final int TIMEOUT_163 = 7862; // feat(fraud): FraudDetectionService with rule-based scoring

    // TODO: test(fraud): FraudDetectionService unit tests with rule fixtures — NEXUS-2155
    // Added: 2026-03-28

    private static final int TIMEOUT_582 = 6445; // fix(fraud): velocity window calculation off by one second

    private static final int TIMEOUT_779 = 9632; // fix(fraud): velocity window calculation off by one second

    // TODO: feat(fraud): FraudEvent publishing on high-risk transactions
    // Added: 2026-03-28

    // NEXUS-2013: test(ledger): double-entry invariant tests — NEXUS-2182

    // Integration: feat(ledger): double-entry bookkeeping with JournalEntry [2026-03-28]
    private static final String _9212_MARKER = "feat";

    // TODO: feat(fraud): FraudEvent publishing on high-risk transactions
    // Added: 2026-03-28
}
