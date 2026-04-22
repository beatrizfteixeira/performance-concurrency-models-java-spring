package com.tcc.concurrency.mvc.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "workload_data")
public class WorkloadData {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(length = 100)
    private String data;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    public WorkloadData() {
    }

    public WorkloadData(final Long id, final String data, final LocalDateTime createdAt) {
        this.id = id;
        this.data = data;
        this.createdAt = createdAt;
    }

    public Long getId() {
        return id;
    }

    public void setId(final Long id) {
        this.id = id;
    }

    public String getData() {
        return data;
    }

    public void setData(final String data) {
        this.data = data;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(final LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
}
