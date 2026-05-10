package com.tcc.concurrency.mvc.io.config;

import java.util.concurrent.TimeUnit;

import org.apache.hc.client5.http.config.ConnectionConfig;
import org.apache.hc.client5.http.config.RequestConfig;
import org.apache.hc.client5.http.impl.classic.CloseableHttpClient;
import org.apache.hc.client5.http.impl.classic.HttpClients;
import org.apache.hc.client5.http.impl.io.PoolingHttpClientConnectionManager;
import org.apache.hc.core5.util.Timeout;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.HttpComponentsClientHttpRequestFactory;
import org.springframework.web.client.RestClient;

@Configuration
public class RestClientConfig {

    @Bean
    public RestClient downstreamRestClient(
            @Value("${downstream.url:http://localhost:9090}") final String downstreamUrl,
            @Value("${downstream.http.pool.max-total:2000}") final int maxTotal,
            @Value("${downstream.http.pool.max-per-route:2000}") final int maxPerRoute,
            @Value("${downstream.http.timeout.connect-ms:5000}") final int connectTimeoutMs,
            @Value("${downstream.http.timeout.read-ms:30000}") final int readTimeoutMs) {

        final ConnectionConfig connectionConfig = ConnectionConfig.custom()
                .setConnectTimeout(Timeout.of(connectTimeoutMs, TimeUnit.MILLISECONDS))
                .setSocketTimeout(Timeout.of(readTimeoutMs, TimeUnit.MILLISECONDS))
                .build();

        final PoolingHttpClientConnectionManager connectionManager = new PoolingHttpClientConnectionManager();
        connectionManager.setMaxTotal(maxTotal);
        connectionManager.setDefaultMaxPerRoute(maxPerRoute);
        connectionManager.setDefaultConnectionConfig(connectionConfig);

        final RequestConfig requestConfig = RequestConfig.custom()
                .setResponseTimeout(Timeout.of(readTimeoutMs, TimeUnit.MILLISECONDS))
                .setConnectionRequestTimeout(Timeout.of(readTimeoutMs, TimeUnit.MILLISECONDS))
                .build();

        final CloseableHttpClient httpClient = HttpClients.custom()
                .setConnectionManager(connectionManager)
                .setDefaultRequestConfig(requestConfig)
                .build();

        final HttpComponentsClientHttpRequestFactory requestFactory =
                new HttpComponentsClientHttpRequestFactory(httpClient);

        return RestClient.builder()
                .baseUrl(downstreamUrl)
                .requestFactory(requestFactory)
                .build();
    }
}
