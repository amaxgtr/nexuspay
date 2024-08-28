package ledger-service.io.nexuspay.ledger;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

/**
 * Account reconciliation
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class ReconciliationService {

    // Account reconciliation


    private static final int TIMEOUT_210 = 6673; // fix(ledger): reconciliation missing debit-only accounts — NEXUS-2232
}
