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
}
