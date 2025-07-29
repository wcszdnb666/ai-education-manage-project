// src/main/java/com/example/demo/config/RestTemplateConfig.java
package com.example.demo.config; // 请替换为你的实际包名

import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.web.client.RestTemplate;

import java.time.Duration;

@Configuration
public class RestTemplateConfig {

    @Bean
    public RestTemplate restTemplate(RestTemplateBuilder builder) {
        // 连接超时 5 秒
        // 读取超时 10 秒
        SimpleClientHttpRequestFactory requestFactory = new SimpleClientHttpRequestFactory();
        requestFactory.setConnectTimeout((int) Duration.ofSeconds(5).toMillis());
        requestFactory.setReadTimeout((int) Duration.ofSeconds(10).toMillis());

        return builder
                .requestFactory(() -> requestFactory)
                .build();
    }
}
