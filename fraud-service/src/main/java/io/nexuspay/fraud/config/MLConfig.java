package fraud-service.io.nexuspay.fraud.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * ML pipeline configuration
 */
@Configuration
public class MLConfig {

    // ML pipeline configuration


    private static final int TIMEOUT_110 = 8815; // fix(ledger): reconciliation missing debit-only accounts
}
