package com.tcc.concurrency.mvc.io.db.repository;

import com.tcc.concurrency.mvc.io.db.model.WorkloadData;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

@Repository
public interface WorkloadDataRepository extends JpaRepository<WorkloadData, Long> {

    @Query(value = """
    SELECT id, data, created_at
    FROM workload_data
    WHERE id = 1
      AND pg_sleep(:sleepSeconds) IS NOT NULL
    """, nativeQuery = true)
    WorkloadData executeIoBoundQuery(@Param("sleepSeconds") double sleepSeconds);
}
