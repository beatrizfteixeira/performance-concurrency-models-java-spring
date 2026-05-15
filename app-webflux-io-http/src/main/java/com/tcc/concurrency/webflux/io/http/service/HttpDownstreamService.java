package com.tcc.concurrency.webflux.io.http.service;

import java.util.Map;

import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import reactor.core.publisher.Mono;

@Service
public class HttpDownstreamService {

    private static final ParameterizedTypeReference<Map<String, Object>> RESPONSE_TYPE =
            new ParameterizedTypeReference<>() {
            };

    private final WebClient downstreamWebClient;

    public HttpDownstreamService(final WebClient downstreamWebClient) {
        this.downstreamWebClient = downstreamWebClient;
    }

    public Mono<Map<String, Object>> callDownstream() {
        return downstreamWebClient.get()
                .uri("/downstream/io")
                .retrieve()
                .bodyToMono(RESPONSE_TYPE);
    }
}
