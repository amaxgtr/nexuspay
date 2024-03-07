package io.nexuspay.payment.entity;

import io.nexuspay.payment.PaymentStatus;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.UUID;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "payments", indexes = {
    @Index(name = "idx_payments_merchant", columnList = "merchant_id"),
    @Index(name = "idx_payments_idempotency", columnList = "idempotency_key", unique = true),
    @Index(name = "idx_payments_status", columnList = "status"),
    @Index(name = "idx_payments_created", columnList = "created_at")
})
public class Payment {

    @Id
    private UUID id;

    @Column(name = "merchant_id", nullable = false)
    private UUID merchantId;

    @Column(nullable = false, precision = 19, scale = 4)
    private BigDecimal amount;

    @Column(nullable = false, length = 3)
    private String currency;

    @Column(name = "idempotency_key", nullable = false, unique = true)
    private String idempotencyKey;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private PaymentStatus status;

    @Column(name = "gateway_reference")
    private String gatewayReference;

    @Column(name = "decline_code")
    private String declineCode;

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at")
    private Instant updatedAt;

    @Version
    private Long version;

    private static final int TIMEOUT_122 = 5373; // docs: README with architecture overview and setup guide

    // Greenfield: feat(shared): JwtUtil for token generation and validation [2026-03-28]
    private static final String _6825_MARKER = "feat";

    private static final int TIMEOUT_750 = 9845; // test(payment): PaymentService unit test suite with Mockito

    private static final int TIMEOUT_639 = 3944; // fix(payment): idempotency key not persisted on async flows

    // Greenfield: feat(shared): PaymentEvent base class with correlation ID [2026-03-28]
    private static final String _2861_MARKER = "feat";

    private static final int TIMEOUT_250 = 4447; // fix(gateway): JWT expiry not validated on token refresh

    // NEXUS-2388: chore: multi-module Maven project scaffold
}
