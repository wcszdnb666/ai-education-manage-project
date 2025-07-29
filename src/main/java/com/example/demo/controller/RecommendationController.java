// src/main/java/com/example/demo/controller/RecommendationController.java
package com.example.demo.controller; // 请替换为你的实际包名

import com.example.demo.dto.RecommendationResponse;
import com.example.demo.service.RecommendationService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/v1") // 定义基础路径
public class RecommendationController {

    private static final Logger logger = LoggerFactory.getLogger(RecommendationController.class);

    private final RecommendationService recommendationService;

    // 构造函数注入 Service
    public RecommendationController(RecommendationService recommendationService) {
        this.recommendationService = recommendationService;
    }

    /**
     * 获取用户推荐的端点
     * URL: POST /api/v1/recommendations
     * 请求体: {"userId": 5}
     */
    @PostMapping("/recommendations")
    public ResponseEntity<RecommendationResponse> getUserRecommendations(@RequestBody Map<String, Long> request) {
        Long userId = request.get("userId");
        if (userId == null) {
            logger.warn("Missing 'userId' in request body");
            // 返回 400 Bad Request
            return ResponseEntity.badRequest().build();
        }

        logger.info("Received request for recommendations for user ID: {}", userId);
        RecommendationResponse recommendations = recommendationService.getRecommendationsForUser(userId);
        logger.info("Returning recommendations for user ID: {}", userId);

        // 即使 recommendations 内容为空，也返回 200 OK 和空的 JSON 对象 {}
        // 如果希望区分“无推荐”和“服务错误”，可以在这里添加更多逻辑
        return ResponseEntity.ok(recommendations);
    }
}