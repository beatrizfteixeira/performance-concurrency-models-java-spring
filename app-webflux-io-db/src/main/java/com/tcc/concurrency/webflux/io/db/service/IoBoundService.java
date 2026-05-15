package com.tcc.concurrency.webflux.io.db.service;

import com.tcc.concurrency.webflux.io.db.model.WorkloadData;
import com.tcc.concurrency.webflux.io.db.repository.WorkloadDataRepository;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import reactor.core.publisher.Mono;

@Service
public class IoBoundService {

    private final WorkloadDataRepository repository;
    private final double sleepSeconds;

    public IoBoundService(
            final WorkloadDataRepository repository,
            @Value("${workload.io.db.sleep-seconds:0.1}") final double sleepSeconds) {
        this.repository = repository;
        this.sleepSeconds = sleepSeconds;
    }

    public Mono<WorkloadData> executeIoBoundWorkload() {
        return repository.executeIoBoundQuery(sleepSeconds);
    }
}
