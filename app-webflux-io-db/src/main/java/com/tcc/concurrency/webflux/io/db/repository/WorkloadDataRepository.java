package com.tcc.concurrency.webflux.io.db.repository;

import com.tcc.concurrency.webflux.io.db.model.WorkloadData;

import org.springframework.data.r2dbc.repository.Query;
import org.springframework.data.repository.reactive.ReactiveCrudRepository;
import org.springframework.stereotype.Repository;

import reactor.core.publisher.Mono;

@Repository
public interface WorkloadDataRepository extends ReactiveCrudRepository<WorkloadData, Long> {

    @Query("""
    SELECT id, data, created_at
    FROM workload_data
    WHERE id = 1
      AND pg_sleep(:sleepSeconds) IS NOT NULL
    """)
    Mono<WorkloadData> executeIoBoundQuery(double sleepSeconds);
}
