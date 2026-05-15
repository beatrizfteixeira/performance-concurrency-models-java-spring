package com.tcc.concurrency.webflux.io.db.controller;

import java.time.LocalDateTime;
import java.util.concurrent.TimeUnit;

import com.tcc.concurrency.webflux.io.db.model.WorkloadResult;
import com.tcc.concurrency.webflux.io.db.service.IoBoundService;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import reactor.core.publisher.Mono;

@RestController
@RequestMapping("/api/io")
public class IoBoundController {

    private final IoBoundService ioBoundService;

    public IoBoundController(final IoBoundService ioBoundService) {
        this.ioBoundService = ioBoundService;
    }

    @GetMapping
    public Mono<ResponseEntity<WorkloadResult>> executeIoWorkload() {
        final long startTime = System.nanoTime();

        return ioBoundService.executeIoBoundWorkload()
                .map(data -> {
                    final String threadName = Thread.currentThread().getName();
                    final long executionTime = TimeUnit.NANOSECONDS.toMillis(System.nanoTime() - startTime);

                    final WorkloadResult result = new WorkloadResult(
                            "IO-DB",
                            executionTime,
                            LocalDateTime.now(),
                            threadName,
                            data != null ? data.getData() : "null"
                    );

                    return ResponseEntity.ok(result);
                });
    }
}
