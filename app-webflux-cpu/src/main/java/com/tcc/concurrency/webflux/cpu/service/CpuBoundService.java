package com.tcc.concurrency.webflux.cpu.service;

import java.nio.charset.StandardCharsets;

import org.apache.commons.codec.digest.DigestUtils;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import reactor.core.publisher.Mono;
import reactor.core.scheduler.Schedulers;

@Service
public class CpuBoundService {

    @Value("${workload.cpu.sha256.iterations:75000}")
    private int iterations;

    public Mono<String> executeCpuBoundWorkload() {
        return Mono.fromSupplier(this::computeHash)
                .subscribeOn(Schedulers.parallel());
    }

    private String computeHash() {
        final String baseData = "tcc-experiment-cpu-workload-";
        String lastHash = "";

        for (int i = 0; i < iterations; i++) {
            lastHash = DigestUtils.sha256Hex((baseData + i).getBytes(StandardCharsets.UTF_8));
        }

        return lastHash;
    }

    public int getIterations() {
        return iterations;
    }
}
