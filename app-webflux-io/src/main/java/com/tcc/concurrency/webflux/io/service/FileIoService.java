package com.tcc.concurrency.webflux.io.service;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;

import jakarta.annotation.PostConstruct;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import reactor.core.publisher.Mono;
import reactor.core.scheduler.Schedulers;

@Service
public class FileIoService {

    private static final String CONTENT_FILLER = "x";

    @Value("${workload.io.file.path:/tmp/benchmark-webflux.log}")
    private String filePath;

    @Value("${workload.io.file.payload-size-bytes:10240}")
    private int payloadSizeBytes;

    private Path target;
    private byte[] payload;

    @PostConstruct
    public void init() throws IOException {
        this.target = Paths.get(filePath);
        if (target.getParent() != null) {
            Files.createDirectories(target.getParent());
        }
        if (!Files.exists(target)) {
            Files.createFile(target);
        }
        this.payload = buildPayload(payloadSizeBytes);
    }

    public Mono<Long> writeToFile() {
        return Mono.fromCallable(this::doWrite)
                .subscribeOn(Schedulers.boundedElastic());
    }

    private long doWrite() {
        try {
            Files.write(target, payload,
                    StandardOpenOption.CREATE,
                    StandardOpenOption.APPEND);
            return (long) payload.length;
        } catch (final IOException e) {
            throw new RuntimeException("Falha ao escrever no arquivo: " + filePath, e);
        }
    }

    private byte[] buildPayload(final int sizeBytes) {
        final StringBuilder sb = new StringBuilder(sizeBytes + 1);
        for (int i = 0; i < sizeBytes; i++) {
            sb.append(CONTENT_FILLER);
        }
        sb.append('\n');
        return sb.toString().getBytes(StandardCharsets.UTF_8);
    }
}
