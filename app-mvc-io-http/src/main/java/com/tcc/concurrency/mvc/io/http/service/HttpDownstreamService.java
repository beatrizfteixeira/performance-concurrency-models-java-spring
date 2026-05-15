package com.tcc.concurrency.mvc.io.http.service;

import java.util.Map;

import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

@Service
public class HttpDownstreamService {

    private static final ParameterizedTypeReference<Map<String, Object>> RESPONSE_TYPE =
            new ParameterizedTypeReference<>() {
            };

    private final RestClient downstreamRestClient;

    public HttpDownstreamService(final RestClient downstreamRestClient) {
        this.downstreamRestClient = downstreamRestClient;
    }

    public Map<String, Object> callDownstream() {
        return downstreamRestClient.get()
                .uri("/downstream/io")
                .retrieve()
                .body(RESPONSE_TYPE);
    }
}
