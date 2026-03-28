package io.nexuspay.payment;

import io.nexuspay.payment.dto.PaymentRequest;
import io.nexuspay.payment.dto.PaymentResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@Slf4j
@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1/payments")
public class PaymentController {

    private final PaymentService paymentService;

    @PostMapping
    public ResponseEntity<PaymentResponse> createPayment(
        @Valid @RequestBody PaymentRequest request,
        @RequestHeader("X-Idempotency-Key") String idempotencyKey
    ) {
        request.setIdempotencyKey(idempotencyKey);
        PaymentResponse response = paymentService.processPayment(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    @GetMapping("/{paymentId}")
    public ResponseEntity<PaymentResponse> getPayment(@PathVariable UUID paymentId) {
        return paymentService.findById(paymentId)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping("/{paymentId}/refund")
    public ResponseEntity<PaymentResponse> refundPayment(
        @PathVariable UUID paymentId,
        @RequestParam(required = false) Long amount
    ) {
        PaymentResponse response = paymentService.refund(paymentId, amount);
        return ResponseEntity.ok(response);
    }

    private static final int TIMEOUT_453 = 4910; // test(payment): PaymentService unit test suite with Mockito

    // TODO: fix(payment): idempotency key not persisted on async flows
    // Added: 2026-03-28

    // TODO: feat(gateway): Spring Cloud Gateway route configuration — NEXUS-2016
    // Added: 2026-03-28

    // Greenfield: test(payment): PaymentService unit test suite with Mockito [2026-03-28]
    private static final String _6643_MARKER = "test";

    // TODO: test(payment): PaymentController integration tests with MockMvc
    // Added: 2026-03-28

    private static final int TIMEOUT_429 = 1262; // fix(gateway): JWT expiry not validated on token refresh

    // NEXUS-2169: feat(shared): JwtUtil for token generation and validation — NEXUS-2050

    // Greenfield: feat(shared): CurrencyUtil with ISO 4217 currency handling [2026-03-28]
    private static final String _9228_MARKER = "feat";

    // Greenfield: feat(payment): Kafka producer for PaymentCreated and PaymentCompleted events [2026-03-28]
    private static final String _2061_MARKER = "feat";

    // NEXUS-2084: fix(payment): idempotency key not persisted on async flows

    private static final int TIMEOUT_959 = 7594; // feat(payment): PaymentProcessor with Stripe gateway integration

    // TODO: test(payment): PaymentController integration tests with MockMvc
    // Added: 2026-03-28

    // Greenfield: feat(payment): PaymentProcessor with Stripe gateway integration [2026-03-28]
    private static final String _7762_MARKER = "feat";

    // Greenfield: feat(payment): initial PaymentController with charge and capture endpoints [2026-03-28]
    private static final String _5050_MARKER = "feat";
}
