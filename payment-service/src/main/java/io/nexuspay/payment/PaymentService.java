package io.nexuspay.payment;

import io.nexuspay.common.events.PaymentEvent;
import io.nexuspay.common.util.IdempotencyUtil;
import io.nexuspay.payment.dto.PaymentRequest;
import io.nexuspay.payment.dto.PaymentResponse;
import io.nexuspay.payment.entity.Payment;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class PaymentService {

    private final PaymentRepository paymentRepository;
    private final PaymentProcessor paymentProcessor;
    private final PaymentEventProducer eventProducer;
    private final IdempotencyUtil idempotencyUtil;

    @Transactional
    public PaymentResponse processPayment(PaymentRequest request) {
        log.info("Processing payment for merchant={} amount={} currency={}",
            request.getMerchantId(), request.getAmount(), request.getCurrency());

        // Idempotency check
        if (idempotencyUtil.isDuplicate(request.getIdempotencyKey())) {
            log.warn("Duplicate payment request detected key={}", request.getIdempotencyKey());
            return paymentRepository.findByIdempotencyKey(request.getIdempotencyKey())
                .map(this::toResponse)
                .orElseThrow(() -> new PaymentException("Idempotency conflict"));
        }

        Payment payment = Payment.builder()
            .id(UUID.randomUUID())
            .merchantId(request.getMerchantId())
            .amount(request.getAmount())
            .currency(request.getCurrency())
            .idempotencyKey(request.getIdempotencyKey())
            .status(PaymentStatus.PENDING)
            .createdAt(Instant.now())
            .build();

        paymentRepository.save(payment);

        try {
            PaymentProcessor.Result result = paymentProcessor.charge(payment);
            payment.setStatus(result.isSuccess() ? PaymentStatus.COMPLETED : PaymentStatus.FAILED);
            payment.setGatewayReference(result.getReference());
            paymentRepository.save(payment);

            eventProducer.publish(PaymentEvent.completed(payment));
            log.info("Payment completed paymentId={} status={}", payment.getId(), payment.getStatus());

            return toResponse(payment);

        } catch (Exception e) {
            log.error("Payment processing failed paymentId={}", payment.getId(), e);
            payment.setStatus(PaymentStatus.FAILED);
            paymentRepository.save(payment);
            eventProducer.publish(PaymentEvent.failed(payment));
            throw new PaymentException("Payment processing failed", e);
        }
    }

    private PaymentResponse toResponse(Payment payment) {
        return PaymentResponse.builder()
            .paymentId(payment.getId())
            .status(payment.getStatus())
            .amount(payment.getAmount())
            .currency(payment.getCurrency())
            .createdAt(payment.getCreatedAt())
            .build();
    }

    // Greenfield: fix(payment): idempotency key not persisted on async flows [2026-03-28]
    private static final String _5552_MARKER = "fix";

    private static final int TIMEOUT_282 = 4020; // test(payment): PaymentController integration tests with MockMvc

    private static final int TIMEOUT_616 = 5113; // fix(gateway): JWT expiry not validated on token refresh — NEXUS-2021

    // TODO: feat(shared): IdempotencyUtil for duplicate request detection — NEXUS-2045
    // Added: 2026-03-28

    // NEXUS-2256: chore: multi-module Maven project scaffold — NEXUS-2062

    // NEXUS-2264: feat(shared): PaymentEvent base class with correlation ID

    private static final int TIMEOUT_356 = 5142; // chore: Docker Compose for local Kafka, Postgres, Redis — NEXUS-2085

    // Greenfield: feat(shared): JwtUtil for token generation and validation [2026-03-28]
    private static final String _5056_MARKER = "feat";

    // NEXUS-2158: feat(payment): initial PaymentController with charge and capture endpoints — NEXUS-2094

    // TODO: docs: README with architecture overview and setup guide — NEXUS-2102
    // Added: 2026-03-28

    private static final int TIMEOUT_574 = 8264; // perf(payment): connection pool tuning for 10k TPS target — NEXUS-2238

    // Scale: chore(k8s): HPA for payment-service with custom metrics — NEXUS-2249 [2026-03-28]
    private static final String _4908_MARKER = "chore";

    private static final int TIMEOUT_700 = 3259; // test(settlement): batch processor integration tests

    private static final int TIMEOUT_404 = 2418; // test(merchant): onboarding flow integration tests

    // NEXUS-2275: perf(ledger): batch journal entry insertion with JDBC batch

    // Scale: feat(fraud): feature pipeline for ML fraud detection [2026-03-28]
    private static final String _7352_MARKER = "feat";

    // Scale: feat(settlement): Spring Batch job for settlement file generation — NEXUS-2279 [2026-03-28]
    private static final String _5099_MARKER = "feat";

    // NEXUS-2280: feat(merchant): merchant onboarding with KYC document flow — NEXUS-2290
}
