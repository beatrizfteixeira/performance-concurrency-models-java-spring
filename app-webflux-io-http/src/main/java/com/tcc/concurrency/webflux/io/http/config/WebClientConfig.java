package com.tcc.concurrency.webflux.io.http.config;

import java.time.Duration;

import io.netty.channel.ChannelOption;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.reactive.ReactorClientHttpConnector;
import org.springframework.web.reactive.function.client.WebClient;

import reactor.netty.http.client.HttpClient;
import reactor.netty.resources.ConnectionProvider;

@Configuration
public class WebClientConfig {

    @Bean
    public WebClient downstreamWebClient(
            @Value("${downstream.url:http://localhost:9090}") final String downstreamUrl,
            @Value("${downstream.http.pool.max-connections:2000}") final int maxConnections,
            @Value("${downstream.http.pool.pending-acquire-max-count:5000}") final int pendingAcquireMaxCount,
            @Value("${downstream.http.timeout.connect-ms:5000}") final int connectTimeoutMs,
            @Value("${downstream.http.timeout.response-ms:30000}") final int responseTimeoutMs) {

        final ConnectionProvider connectionProvider = ConnectionProvider.builder("downstream-pool")
                .maxConnections(maxConnections)
                .pendingAcquireMaxCount(pendingAcquireMaxCount)
                .pendingAcquireTimeout(Duration.ofSeconds(60))
                .build();

        final HttpClient httpClient = HttpClient.create(connectionProvider)
                .option(ChannelOption.CONNECT_TIMEOUT_MILLIS, connectTimeoutMs)
                .responseTimeout(Duration.ofMillis(responseTimeoutMs));

        return WebClient.builder()
                .baseUrl(downstreamUrl)
                .clientConnector(new ReactorClientHttpConnector(httpClient))
                .build();
    }
}
