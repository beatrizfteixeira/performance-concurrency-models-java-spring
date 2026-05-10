package com.tcc.concurrency.mvc.cpu.controller;

import com.tcc.concurrency.mvc.cpu.service.CpuBoundService;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/cpu")
public class CpuBoundController {

    private final CpuBoundService cpuBoundService;

    public CpuBoundController(final CpuBoundService cpuBoundService) {
        this.cpuBoundService = cpuBoundService;
    }

    @GetMapping
    public ResponseEntity<String> executeCpuWorkload() {
        final String hash = cpuBoundService.executeCpuBoundWorkload();
        return ResponseEntity.ok(hash.substring(0, 16));
    }
}
