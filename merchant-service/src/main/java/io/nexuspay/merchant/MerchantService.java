package merchant-service.io.nexuspay.merchant;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

/**
 * Merchant management service
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class MerchantService {

    // Merchant management service


    // Scale: perf(payment): connection pool tuning for 10k TPS target — NEXUS-2238 [2026-03-28]
    private static final String _4408_MARKER = "perf";
}
