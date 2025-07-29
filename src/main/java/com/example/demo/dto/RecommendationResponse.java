// src/main/java/com/example/demo/dto/RecommendationResponse.java
package com.example.demo.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.List;

@Data
@NoArgsConstructor
// 这个注解很重要，它允许 JSON 中有额外的字段而不会导致反序列化失败
@JsonIgnoreProperties(ignoreUnknown = true)
public class RecommendationResponse {

    @JsonProperty("user_based")
    private List<CourseRecommendation> userBased;

    @JsonProperty("item_based")
    private List<CourseRecommendation> itemBased;

    @JsonProperty("hybrid")
    private List<CourseRecommendation> hybrid;

    @JsonProperty("user_profile")
    private UserProfile userProfile;

    // --- 内部类 CourseRecommendation ---
    @Data
    @NoArgsConstructor
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class CourseRecommendation {
        // 为所有字段显式添加 @JsonProperty 以确保精确映射
        @JsonProperty("course_id")
        private Long courseId;

        @JsonProperty("title")
        private String title;

        @JsonProperty("category")
        private String category;

        @JsonProperty("difficulty")
        private String difficulty;

        @JsonProperty("score")
        private Double score;
    }
    // --- 内部类 UserProfile ---
    @Data
    @NoArgsConstructor
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class UserProfile {
        @JsonProperty("user_id")
        private Long userId;

        @JsonProperty("name")
        private String name;
        // 根据你的实际 Flask 响应添加其他字段
    }
}