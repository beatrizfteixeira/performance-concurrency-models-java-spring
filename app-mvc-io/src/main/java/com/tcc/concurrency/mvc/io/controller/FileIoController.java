package com.tcc.concurrency.mvc.io.controller;

import java.time.LocalDateTime;

import com.tcc.concurrency.mvc.io.model.WorkloadResult;
import com.tcc.concurrency.mvc.io.service.FileIoService;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/io/file")
public class FileIoController {

    private final FileIoService fileIoService;

    public FileIoController(final FileIoService fileIoService) {
        this.fileIoService = fileIoService;
    }

    @GetMapping
    public ResponseEntity<WorkloadResult> writeToFile() {
        final long startTime = System.currentTimeMillis();
        final String threadName = Thread.currentThread().getName();

        final long bytesWritten = fileIoService.writeToFile();

        final long executionTime = System.currentTimeMillis() - startTime;

        final WorkloadResult result = new WorkloadResult(
                "FILE-IO",
                executionTime,
                LocalDateTime.now(),
                threadName,
                bytesWritten + " bytes"
        );

        return ResponseEntity.ok(result);
    }
}
