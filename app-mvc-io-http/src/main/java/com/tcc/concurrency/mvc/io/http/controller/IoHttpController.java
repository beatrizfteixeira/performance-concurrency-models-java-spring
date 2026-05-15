package com.tcc.concurrency.mvc.io.http.controller;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.concurrent.TimeUnit;

import com.tcc.concurrency.mvc.io.http.model.WorkloadResult;
import com.tcc.concurrency.mvc.io.http.service.HttpDownstreamService;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/io-http")
public class IoHttpController {

    private final HttpDownstreamService httpDownstreamService;

    public IoHttpController(final HttpDownstreamService httpDownstreamService) {
        this.httpDownstreamService = httpDownstreamService;
    }

    @GetMapping
    public ResponseEntity<WorkloadResult> executeIoHttpWorkload() {
        final long startTime = System.nanoTime();
        final String threadName = Thread.currentThread().getName();

        final Map<String, Object> response = httpDownstreamService.callDownstream();

        final long executionTime = TimeUnit.NANOSECONDS.toMillis(System.nanoTime() - startTime);

        final WorkloadResult result = new WorkloadResult(
                "IO-HTTP",
                executionTime,
                LocalDateTime.now(),
                threadName,
                response != null ? String.valueOf(response.get("data")) : "null"
        );

        return ResponseEntity.ok(result);
    }
}
