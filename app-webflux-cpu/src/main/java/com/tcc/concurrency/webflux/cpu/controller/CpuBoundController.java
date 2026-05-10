package com.tcc.concurrency.webflux.cpu.controller;

import com.tcc.concurrency.webflux.cpu.service.CpuBoundService;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import reactor.core.publisher.Mono;

@RestController
@RequestMapping("/api/cpu")
public class CpuBoundController {

    private final CpuBoundService cpuBoundService;

    public CpuBoundController(final CpuBoundService cpuBoundService) {
        this.cpuBoundService = cpuBoundService;
    }

    @GetMapping
    public Mono<ResponseEntity<String>> executeCpuWorkload() {
        return cpuBoundService.executeCpuBoundWorkload()
                .map(hash -> ResponseEntity.ok(hash.substring(0, 16)));
    }
}
