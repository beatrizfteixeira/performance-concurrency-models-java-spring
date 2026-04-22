package com.tcc.concurrency.mvc.controller;

import com.tcc.concurrency.mvc.model.WorkloadData;
import com.tcc.concurrency.mvc.model.WorkloadResult;
import com.tcc.concurrency.mvc.service.IoBoundService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

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
    public ResponseEntity<WorkloadResult> executeIoWorkload() {
        final long startTime = System.currentTimeMillis();
        final String threadName = Thread.currentThread().getName();
        
        logger.debug("Executing I/O-bound workload on thread: {}", threadName);
        
        final WorkloadData data = ioBoundService.executeIoBoundWorkload();
        
        final long executionTime = System.currentTimeMillis() - startTime;
        
        final WorkloadResult result = new WorkloadResult(
            "IO-BOUND",
            executionTime,
            LocalDateTime.now(),
            threadName,
            data != null ? data.getData() : "null"
        );
        
        return ResponseEntity.ok(result);
    }
}
