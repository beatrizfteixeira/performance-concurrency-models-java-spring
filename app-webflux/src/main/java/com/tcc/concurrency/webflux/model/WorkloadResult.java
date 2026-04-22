package com.tcc.concurrency.webflux.model;

import java.time.LocalDateTime;

public class WorkloadResult {

    private final String workloadType;
    private final long executionTimeMs;
    private final LocalDateTime timestamp;
    private final String threadName;
    private final String result;

    public WorkloadResult(final String workloadType, final long executionTimeMs, 
                         final LocalDateTime timestamp, final String threadName, 
                         final String result) {
        this.workloadType = workloadType;
        this.executionTimeMs = executionTimeMs;
        this.timestamp = timestamp;
        this.threadName = threadName;
        this.result = result;
    }

    public String getWorkloadType() {
        return workloadType;
    }

    public long getExecutionTimeMs() {
        return executionTimeMs;
    }

    public LocalDateTime getTimestamp() {
        return timestamp;
    }

    public String getThreadName() {
        return threadName;
    }

    public String getResult() {
        return result;
    }
}
