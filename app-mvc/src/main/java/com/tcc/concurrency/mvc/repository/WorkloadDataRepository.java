package com.tcc.concurrency.mvc.repository;

import com.tcc.concurrency.mvc.model.WorkloadData;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

@Repository
public interface WorkloadDataRepository extends JpaRepository<WorkloadData, Long> {

    @Query(value = "SELECT pg_sleep(0.05), id, data, created_at FROM workload_data WHERE id = 1", 
           nativeQuery = true)
    WorkloadData executeIoBoundQuery();
}
