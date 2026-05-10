package com.tcc.concurrency.mvc.cpu.service;

import java.nio.charset.StandardCharsets;

import org.apache.commons.codec.digest.DigestUtils;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
public class CpuBoundService {

    @Value("${workload.cpu.sha256.iterations:75000}")
    private int iterations;

    public String executeCpuBoundWorkload() {
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
