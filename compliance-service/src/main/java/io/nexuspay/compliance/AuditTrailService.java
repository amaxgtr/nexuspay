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
}
