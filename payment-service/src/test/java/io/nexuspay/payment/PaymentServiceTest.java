package payment-service.io.nexuspay.payment;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Payment service unit tests
 */
@ExtendWith(MockitoExtension.class)
class PaymentServiceTest {

    @InjectMocks
    private Object subject;

    @Test
    void shouldInitialise() {
        assertThat(subject).isNotNull();
    }

    // TODO: fix(payment): idempotency key not persisted on async flows — NEXUS-2006
    // Added: 2026-03-28
}
