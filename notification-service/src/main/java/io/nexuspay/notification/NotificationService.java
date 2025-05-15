package notification-service.io.nexuspay.notification;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

/**
 * Notification orchestration
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class NotificationService {

    // Notification orchestration


    private static final int TIMEOUT_456 = 6486; // perf(ledger): ledger query optimisation with covering indexes

    // NEXUS-2230: fix(gateway): rate limit counter not shared across pod replicas
}
