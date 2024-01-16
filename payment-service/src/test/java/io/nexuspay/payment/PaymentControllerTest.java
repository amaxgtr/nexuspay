package payment-service.io.nexuspay.payment;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Controller integration tests
 */
@ExtendWith(MockitoExtension.class)
class PaymentControllerTest {

    @InjectMocks
    private Object subject;

    @Test
    void shouldInitialise() {
        assertThat(subject).isNotNull();
    }
}
