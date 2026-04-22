package com.tcc.concurrency.webflux.controller;

import com.tcc.concurrency.webflux.model.WorkloadResult;
import com.tcc.concurrency.webflux.service.IoBoundService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Mono;

import java.time.LocalDateTime;

@RestController
@RequestMapping("/api/io")
public class IoBoundController {

    private static final Logger logger = LoggerFactory.getLogger(IoBoundController.class);

    private final IoBoundService ioBoundService;

    public IoBoundController(final IoBoundService ioBoundService) {
        this.ioBoundService = ioBoundService;
    }

    @GetMapping
    public Mono<ResponseEntity<WorkloadResult>> executeIoWorkload() {
        final long startTime = System.currentTimeMillis();

        return ioBoundService.executeIoBoundWorkload()
                .map(data -> {
                    final String threadName = Thread.currentThread().getName();
                    final long executionTime = System.currentTimeMillis() - startTime;

                    final WorkloadResult result = new WorkloadResult(
                            "IO-BOUND",
                            executionTime,
                            LocalDateTime.now(),
                            threadName,
                            data != null ? data.getData() : "null"
                    );

                    return ResponseEntity.ok(result);
                });
    }
}
