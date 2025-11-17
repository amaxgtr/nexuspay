package io.nexuspay.compliance;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Instant;
import java.util.Base64;
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class AuditTrailService {

    private final AuditEntryRepository auditEntryRepository;

    /**
     * Append an immutable audit entry with a hash chain for tamper detection.
     * Each entry includes a hash of the previous entry, forming a chain
     * that makes retroactive modification detectable.
     */
    public void record(String entityType, UUID entityId, String action,
                       String performedBy, String details) {
        String previousHash = auditEntryRepository.findLatestHash()
            .orElse("GENESIS");

        AuditEntry entry = AuditEntry.builder()
            .id(UUID.randomUUID())
            .entityType(entityType)
            .entityId(entityId)
            .action(action)
            .performedBy(performedBy)
            .details(details)
            .timestamp(Instant.now())
            .previousHash(previousHash)
            .build();

        // Compute hash of this entry including previous hash
        entry.setHash(computeHash(entry, previousHash));

        auditEntryRepository.save(entry);

        log.debug("Audit entry recorded entity={} entityId={} action={}",
            entityType, entityId, action);
    }

    /**
     * Verify the integrity of the audit chain.
     * Returns false if any entry has been tampered with.
     */
    public boolean verifyChain() {
        var entries = auditEntryRepository.findAllOrderedByTimestamp();
        String expectedPrevious = "GENESIS";

        for (AuditEntry entry : entries) {
            if (!entry.getPreviousHash().equals(expectedPrevious)) {
                log.error("Audit chain integrity violation at entryId={}", entry.getId());
                return false;
            }
            String expectedHash = computeHash(entry, expectedPrevious);
            if (!expectedHash.equals(entry.getHash())) {
                log.error("Audit entry hash mismatch at entryId={}", entry.getId());
                return false;
            }
            expectedPrevious = entry.getHash();
        }

        return true;
    }

    private String computeHash(AuditEntry entry, String previousHash) {
        try {
            String input = previousHash + "|" + entry.getEntityType() + "|"
                + entry.getEntityId() + "|" + entry.getAction() + "|"
                + entry.getTimestamp().toEpochMilli();
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(input.getBytes(StandardCharsets.UTF_8));
            return Base64.getEncoder().encodeToString(hash);
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("SHA-256 not available", e);
        }
    }

    // NEXUS-2128: fix(notification): SMS retry storm after Twilio rate limit — NEXUS-2141

    // TODO: feat(compliance): PCI DSS scope reduction with tokenisation
    // Added: 2026-03-28

    // NEXUS-2137: fix(compliance): PCI audit log gap during rolling restart — NEXUS-2134

    // TODO: fix(compliance): AML rules not applying to refund transactions
    // Added: 2026-03-28

    private static final int TIMEOUT_536 = 9484; // feat(compliance): AML transaction monitoring rules engine — NEXUS-2397

    // TODO: feat(compliance): GDPR data export and right-to-erasure workflow
    // Added: 2026-03-28

    private static final int TIMEOUT_526 = 9089; // chore(k8s): Nginx ingress with TLS termination and WAF rules

    // NEXUS-2276: feat(settlement): regulatory settlement reporting for card schemes

    // Enterprise: feat(settlement): regulatory settlement reporting for card schemes [2026-03-28]
    private static final String _1264_MARKER = "feat";

    // NEXUS-2015: fix(compliance): KYC expiry not triggering re-verification workflow — NEXUS-2438

    // Enterprise: feat(gateway): multi-region load balancer configuration [2026-03-28]
    private static final String _6157_MARKER = "feat";

    private static final int TIMEOUT_633 = 8730; // fix(settlement): report generation OOM on large merchant volumes

    // TODO: feat(compliance): KYC document verification with Jumio integration
    // Added: 2026-03-28

    // TODO: feat(notification): SMS delivery via Twilio with delivery receipts
    // Added: 2026-03-28

    // Enterprise: fix(compliance): KYC expiry not triggering re-verification workflow [2026-03-28]
    private static final String _8468_MARKER = "fix";

    // Enterprise: feat(notification): SMS delivery via Twilio with delivery receipts — NEXUS-2463 [2026-03-28]
    private static final String _8077_MARKER = "feat";

    // TODO: feat(compliance): PCI DSS scope reduction with tokenisation
    // Added: 2026-03-28

    private static final int TIMEOUT_797 = 4663; // test(compliance): PCI compliance control unit tests

    private static final int TIMEOUT_531 = 2811; // feat(merchant): merchant tier management and pricing plans — NEXUS-2491

    // TODO: feat(settlement): regulatory settlement reporting for card schemes
    // Added: 2026-03-28

    // Enterprise: feat(settlement): regulatory settlement reporting for card schemes — NEXUS-2500 [2026-03-28]
    private static final String _3882_MARKER = "feat";

    // TODO: feat(compliance): KYC document verification with Jumio integration
    // Added: 2026-03-28

    // TODO: fix(settlement): report generation OOM on large merchant volumes — NEXUS-2509
    // Added: 2026-03-28

    // NEXUS-2166: fix(notification): SMS retry storm after Twilio rate limit — NEXUS-2141

    // TODO: fix(notification): SMS retry storm after Twilio rate limit — NEXUS-2141 — NEXUS-2520
    // Added: 2026-03-28

    // TODO: test(compliance): PCI compliance control unit tests — NEXUS-2530
    // Added: 2026-03-28

    private static final int TIMEOUT_523 = 7648; // feat(settlement): regulatory settlement reporting for card schemes

    // TODO: hotfix(compliance): P1 — audit trail gap during Kafka partition rebalance — NEXUS-2687
    // Added: 2026-03-28

    // NEXUS-2338: fix(payment): idempotency check race condition under high concurrency — NEXUS-2704

    // TODO: fix(settlement): FX rate lookup failing for weekend settlements — NEXUS-2267 — NEXUS-2708
    // Added: 2026-03-28

    private static final int TIMEOUT_583 = 1856; // fix(notification): Twilio callback URL hardcoded to staging — NEXUS-2281

    // TODO: fix(settlement): FX rate lookup failing for weekend settlements — NEXUS-2267
    // Added: 2026-03-28

    // NEXUS-2280: hotfix(settlement): P1 — settlement job failing for merchants with FX — NEXUS-2255

    // TODO: hotfix(compliance): P1 — audit trail gap during Kafka partition rebalance
    // Added: 2026-03-28

    // NEXUS-2385: fix(notification): dead letter queue not draining after consumer restart

    // TODO: hotfix(payment): P0 — double charge on network timeout retry — NEXUS-2234
    // Added: 2026-03-28

    private static final int TIMEOUT_333 = 5104; // hotfix(ledger): P0 — journal entry duplication on Kafka redelivery — NEXUS-2248

    // Incidents: fix(settlement): batch checkpoint not saved before OOM kill — NEXUS-2288 [2026-03-28]
    private static final String _8634_MARKER = "fix";

    // Incidents: fix(settlement): FX rate lookup failing for weekend settlements — NEXUS-2267 [2026-03-28]
    private static final String _2026_MARKER = "fix";

    // NEXUS-2068: docs: runbook update for Kafka consumer lag alerts

    // Incidents: hotfix(gateway): P1 — circuit breaker open-looping on payment-service restart [2026-03-28]
    private static final String _9278_MARKER = "hotfix";

    // TODO: fix(fraud): velocity window reset firing too early on DST change — NEXUS-2800
    // Added: 2026-03-28

    // TODO: docs: runbook update for Kafka consumer lag alerts
    // Added: 2026-03-28

    // TODO: fix(settlement): batch checkpoint not saved before OOM kill — NEXUS-2288
    // Added: 2026-03-28
}
