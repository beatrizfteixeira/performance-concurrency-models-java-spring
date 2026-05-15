package com.tcc.concurrency.webflux.io.http.controller;

import java.time.LocalDateTime;
import java.util.concurrent.TimeUnit;

import com.tcc.concurrency.webflux.io.http.model.WorkloadResult;
import com.tcc.concurrency.webflux.io.http.service.HttpDownstreamService;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import reactor.core.publisher.Mono;

@RestController
@RequestMapping("/api/io-http")
public class IoHttpController {

    private final HttpDownstreamService httpDownstreamService;

    public IoHttpController(final HttpDownstreamService httpDownstreamService) {
        this.httpDownstreamService = httpDownstreamService;
    }

    @GetMapping
    public Mono<ResponseEntity<WorkloadResult>> executeIoHttpWorkload() {
        final long startTime = System.nanoTime();

        return httpDownstreamService.callDownstream()
                .map(response -> {
                    final String threadName = Thread.currentThread().getName();
                    final long executionTime = TimeUnit.NANOSECONDS.toMillis(System.nanoTime() - startTime);

                    final WorkloadResult result = new WorkloadResult(
                            "IO-HTTP",
                            executionTime,
                            LocalDateTime.now(),
                            threadName,
                            response != null ? String.valueOf(response.get("data")) : "null"
                    );

                    return ResponseEntity.ok(result);
                });
    }
}
