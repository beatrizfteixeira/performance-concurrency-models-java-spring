package com.tcc.concurrency.mvc.service;

import org.apache.commons.codec.digest.DigestUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import jakarta.annotation.PostConstruct;
import java.nio.charset.StandardCharsets;

@Service
public class CpuBoundService {

    private static final Logger logger = LoggerFactory.getLogger(CpuBoundService.class);

    @Value("${workload.cpu.sha256.iterations:75000}")
    private int iterations;

    private int calibratedIterations;

    @PostConstruct
    public void calibrate() {
        logger.info("Starting SHA-256 calibration to achieve ~50ms execution time");
        
        final String testData = "calibration-test-data-for-sha256-benchmark";
        final int testRuns = 10;
        long totalTime = 0;
        
        for (int run = 0; run < testRuns; run++) {
            final long start = System.nanoTime();
            for (int i = 0; i < iterations; i++) {
                DigestUtils.sha256Hex(testData + i);
            }
            final long elapsed = System.nanoTime() - start;
            totalTime += elapsed;
        }
        
        final long avgTimeNs = totalTime / testRuns;
        final long avgTimeMs = avgTimeNs / 1_000_000;
        
        final long targetMs = 50;
        final int baseCalibration = (int) ((iterations * targetMs) / Math.max(avgTimeMs, 1));
        
        calibratedIterations = baseCalibration * 2;
        
        calibratedIterations = Math.max(1000, Math.min(calibratedIterations, 500_000));
        
        logger.info("Calibration complete: {} iterations -> {}ms avg, base calibration {} iterations, adjusted to {} iterations (2x multiplier) for ~50ms",
                   iterations, avgTimeMs, baseCalibration, calibratedIterations);
    }

    public String executeCpuBoundWorkload() {
        final String baseData = "tcc-experiment-cpu-workload-";
        String lastHash = "";
        
        for (int i = 0; i < calibratedIterations; i++) {
            lastHash = DigestUtils.sha256Hex((baseData + i).getBytes(StandardCharsets.UTF_8));
        }
        
        return lastHash;
    }

    public int getCalibratedIterations() {
        return calibratedIterations;
    }
}
