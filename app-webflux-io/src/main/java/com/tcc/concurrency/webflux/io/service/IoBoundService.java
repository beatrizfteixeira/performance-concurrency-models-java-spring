/* package com.tcc.concurrency.webflux.io.service;

import com.tcc.concurrency.webflux.io.model.WorkloadData;
import com.tcc.concurrency.webflux.io.repository.WorkloadDataRepository;

import org.springframework.stereotype.Service;

import reactor.core.publisher.Mono;

@Service
public class IoBoundService {

    private final WorkloadDataRepository repository;

    public IoBoundService(final WorkloadDataRepository repository) {
        this.repository = repository;
    }

    public Mono<WorkloadData> executeIoBoundWorkload() {
        return repository.executeIoBoundQuery();
    }
}
 */