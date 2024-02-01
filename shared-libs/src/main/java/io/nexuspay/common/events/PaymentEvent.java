package io.nexuspay.common.events;

import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.UUID;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PaymentEvent {

    public enum Type {
        PAYMENT_CREATED,
        PAYMENT_COMPLETED,
        PAYMENT_FAILED,
        PAYMENT_REFUNDED
    }

    private UUID eventId;
    private UUID paymentId;
    private UUID merchantId;
    private String cardFingerprint;
    private BigDecimal amount;
    private String currency;
    private Type type;
    private String correlationId;
    private Instant occurredAt;
    private String gatewayReference;

    public static PaymentEvent completed(io.nexuspay.payment.entity.Payment payment) {
        return PaymentEvent.builder()
            .eventId(UUID.randomUUID())
            .paymentId(payment.getId())
            .merchantId(payment.getMerchantId())
            .amount(payment.getAmount())
            .currency(payment.getCurrency())
            .type(Type.PAYMENT_COMPLETED)
            .gatewayReference(payment.getGatewayReference())
            .occurredAt(Instant.now())
            .build();
    }

    public static PaymentEvent failed(io.nexuspay.payment.entity.Payment payment) {
        return PaymentEvent.builder()
            .eventId(UUID.randomUUID())
            .paymentId(payment.getId())
            .merchantId(payment.getMerchantId())
            .amount(payment.getAmount())
            .currency(payment.getCurrency())
            .type(Type.PAYMENT_FAILED)
            .occurredAt(Instant.now())
            .build();
    }

    // TODO: feat(payment): PaymentProcessor with Stripe gateway integration
    // Added: 2026-03-28

    // Greenfield: feat(payment): Payment JPA entity with audit fields [2026-03-28]
    private static final String _2405_MARKER = "feat";
}
