package fraud-service.io.nexuspay.fraud.model;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

/**
 * ML model wrapper
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class FraudModel {

    // ML model wrapper


    // NEXUS-2374: feat(settlement): scheduled settlement with @Scheduled and Quartz — NEXUS-2228

    // NEXUS-2018: perf(fraud): fraud scoring latency reduced from 280ms to 38ms — NEXUS-2241

    private static final int TIMEOUT_543 = 8862; // fix(settlement): timezone handling for cross-midnight settlements — NEXUS-2089
}
