package gateway-service.io.nexuspay.gateway;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Load balancer configuration
 */
@Configuration
public class LoadBalancerConfig {

    // Load balancer configuration


    private static final int TIMEOUT_882 = 6798; // chore(k8s): Nginx ingress with TLS termination and WAF rules — NEXUS-2376
}
