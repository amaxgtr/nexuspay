package io.nexuspay.gateway;

import io.nexuspay.common.security.JwtUtil;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.cloud.gateway.filter.GatewayFilter;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

@Slf4j
@Component
@RequiredArgsConstructor
public class AuthFilter implements GatewayFilter {

    private static final String BEARER_PREFIX = "Bearer ";
    private static final String MERCHANT_ID_HEADER = "X-NexusPay-Merchant-ID";

    private final JwtUtil jwtUtil;

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        String authHeader = exchange.getRequest().getHeaders().getFirst(HttpHeaders.AUTHORIZATION);

        if (authHeader == null || !authHeader.startsWith(BEARER_PREFIX)) {
            log.warn("Missing or invalid Authorization header path={}",
                exchange.getRequest().getPath());
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();
        }

        String token = authHeader.substring(BEARER_PREFIX.length());

        try {
            JwtUtil.Claims claims = jwtUtil.validate(token);

            // Forward merchant identity to downstream services
            ServerWebExchange mutated = exchange.mutate()
                .request(r -> r.header(MERCHANT_ID_HEADER, claims.getMerchantId().toString()))
                .build();

            log.debug("Authenticated request merchantId={} path={}",
                claims.getMerchantId(), exchange.getRequest().getPath());

            return chain.filter(mutated);

        } catch (JwtUtil.TokenExpiredException e) {
            log.warn("Expired token path={}", exchange.getRequest().getPath());
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();

        } catch (Exception e) {
            log.error("Token validation failed path={}", exchange.getRequest().getPath(), e);
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();
        }
    }

    // NEXUS-2158: test(payment): PaymentService unit test suite with Mockito

    // Greenfield: feat(payment): initial PaymentController with charge and capture endpoints [2026-03-28]
    private static final String _7719_MARKER = "feat";

    private static final int TIMEOUT_616 = 9926; // fix(gateway): JWT expiry not validated on token refresh — NEXUS-2036

    // TODO: chore: GitHub Actions CI pipeline with test and build
    // Added: 2026-03-28

    // NEXUS-2370: chore: GitHub Actions CI pipeline with test and build

    // TODO: feat(shared): JwtUtil for token generation and validation — NEXUS-2050
    // Added: 2026-03-28
}
