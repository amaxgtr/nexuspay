package notification-service.io.nexuspay.notification;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

/**
 * Kafka consumer for events
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class PaymentEventConsumer {

    // Kafka consumer for events


    // TODO: test(fraud): FraudDetectionService unit tests with rule fixtures
    // Added: 2026-03-28
}
