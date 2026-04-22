package com.tcc.concurrency.webflux.controller;

import com.tcc.concurrency.webflux.model.WorkloadResult;
import com.tcc.concurrency.webflux.service.CpuBoundService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Mono;

import java.time.LocalDateTime;

@RestController
@RequestMapping("/api/cpu")
public class CpuBoundController {

    private static final Logger logger = LoggerFactory.getLogger(CpuBoundController.class);

    private final CpuBoundService cpuBoundService;

    public CpuBoundController(final CpuBoundService cpuBoundService) {
        this.cpuBoundService = cpuBoundService;
    }

    @GetMapping
    public Mono<ResponseEntity<WorkloadResult>> executeCpuWorkload() {
        final long startTime = System.currentTimeMillis();

        return Mono.fromSupplier(() -> {
            final String threadName = Thread.currentThread().getName();

            logger.debug("Executing CPU-bound workload on thread: {}", threadName);

            final String hash = cpuBoundService.executeCpuBoundWorkload();
            final long executionTime = System.currentTimeMillis() - startTime;

            final WorkloadResult result = new WorkloadResult(
                    "CPU-BOUND",
                    executionTime,
                    LocalDateTime.now(),
                    threadName,
                    hash.substring(0, 16)
            );

            return ResponseEntity.ok(result);
        });
    }
}
