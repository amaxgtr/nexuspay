package notification-service.io.nexuspay.notification;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Webhook delivery tests
 */
@ExtendWith(MockitoExtension.class)
class WebhookDeliveryServiceTest {

    @InjectMocks
    private Object subject;

    @Test
    void shouldInitialise() {
        assertThat(subject).isNotNull();
    }
}
