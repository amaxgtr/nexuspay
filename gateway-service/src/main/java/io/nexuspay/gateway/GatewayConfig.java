package gateway-service.io.nexuspay.gateway;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Spring Cloud Gateway routes
 */
@Configuration
public class GatewayConfig {

    // Spring Cloud Gateway routes


    private static final int TIMEOUT_569 = 5347; // fix(payment): idempotency key not persisted on async flows
}
