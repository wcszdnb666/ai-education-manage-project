// src/main/java/com/example/demo/service/RecommendationService.java
package com.example.demo.service; // 请替换为你的实际包名

import com.example.demo.dto.RecommendationRequest;
import com.example.demo.dto.RecommendationResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;

@Service
public class RecommendationService {

    private static final Logger logger = LoggerFactory.getLogger(RecommendationService.class);

    // 从配置文件注入 Flask 服务的 URL
    @Value("${app.recommendation-service.url}")
    private String recommendationServiceBaseUrl;

    private final RestTemplate restTemplate;

    // 构造函数注入 RestTemplate
    public RecommendationService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    /**
     * 调用 Flask 推荐服务获取推荐结果
     * @param userId 用户ID
     * @return 推荐结果对象，如果出错则返回空的响应对象
     */
    public RecommendationResponse getRecommendationsForUser(Long userId) {
        String url = recommendationServiceBaseUrl + "/recommendations";
        logger.info("Calling recommendation service at: {}", url);

        try {
            // 1. 设置请求头
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            // 2. 准备请求体 (使用 Map)
            Map<String, Long> requestBody = new HashMap<>();
            requestBody.put("user_id", userId);

            HttpEntity<Map<String, Long>> requestEntity = new HttpEntity<>(requestBody, headers);

            // 3. 发送 POST 请求
            ResponseEntity<RecommendationResponse> responseEntity = restTemplate.postForEntity(
                    url,
                    requestEntity,
                    RecommendationResponse.class // 指定期望的响应类型
            );

            // 4. 处理响应
            if (responseEntity.getStatusCode().is2xxSuccessful() && responseEntity.getBody() != null) {
                logger.info("Successfully received recommendations for user {}", userId);
                return responseEntity.getBody();
            } else {
                logger.warn("Recommendation service returned non-success status: {}", responseEntity.getStatusCode());
                return new RecommendationResponse(); // 返回空对象
            }

        } catch (RestClientException e) {
            logger.error("Error calling recommendation service for user {}: {}", userId, e.getMessage(), e);
            return new RecommendationResponse(); // 返回空对象
        }
    }
}