package com.tcc.concurrency.mvc.io.service;

import com.tcc.concurrency.mvc.io.model.WorkloadData;
import com.tcc.concurrency.mvc.io.repository.WorkloadDataRepository;

import org.springframework.stereotype.Service;

@Service
public class IoBoundService {

    private final WorkloadDataRepository repository;

    public IoBoundService(final WorkloadDataRepository repository) {
        this.repository = repository;
    }

    public WorkloadData executeIoBoundWorkload() {
        return repository.executeIoBoundQuery();
    }
}
