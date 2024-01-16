package fraud-service.io.nexuspay.fraud;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Fraud service unit tests
 */
@ExtendWith(MockitoExtension.class)
class FraudDetectionServiceTest {

    @InjectMocks
    private Object subject;

    @Test
    void shouldInitialise() {
        assertThat(subject).isNotNull();
    }
}
