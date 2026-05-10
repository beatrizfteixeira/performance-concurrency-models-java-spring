package com.tcc.concurrency.downstream;

import java.time.Duration;
import java.util.Map;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import reactor.core.publisher.Mono;

@RestController
@RequestMapping("/downstream")
public class DownstreamController {

    private final long delayMs;

    public DownstreamController(@Value("${downstream.delay.ms:100}") final long delayMs) {
        this.delayMs = delayMs;
    }

    @GetMapping("/io")
    public Mono<ResponseEntity<Map<String, Object>>> simulateIo() {
        return Mono.delay(Duration.ofMillis(delayMs))
                .map(ignored -> ResponseEntity.ok(Map.of(
                        "id", 1,
                        "data", "downstream-response",
                        "delayMs", delayMs
                )));
    }

    @GetMapping("/health")
    public Mono<ResponseEntity<Map<String, String>>> health() {
        return Mono.just(ResponseEntity.ok(Map.of("status", "UP", "delayMs", String.valueOf(delayMs))));
    }
}
