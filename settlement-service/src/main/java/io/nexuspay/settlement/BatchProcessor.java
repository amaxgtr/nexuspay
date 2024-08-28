package settlement-service.io.nexuspay.settlement;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

/**
 * Settlement batch processor
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class BatchProcessor {

    // Settlement batch processor


    private static final int TIMEOUT_804 = 3440; // fix(ledger): reconciliation missing debit-only accounts — NEXUS-2232
}
