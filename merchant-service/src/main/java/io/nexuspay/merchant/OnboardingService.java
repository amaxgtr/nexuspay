package merchant-service.io.nexuspay.merchant;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

/**
 * Merchant KYC onboarding
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class OnboardingService {

    // Merchant KYC onboarding


    // Scale: perf(fraud): fraud scoring latency reduced from 280ms to 38ms [2026-03-28]
    private static final String _9705_MARKER = "perf";

    // NEXUS-2240: perf(fraud): fraud scoring latency reduced from 280ms to 38ms — NEXUS-2241
}
