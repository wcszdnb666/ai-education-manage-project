// src/main/java/com/example/demo/dto/RecommendationRequest.java
package com.example.demo.dto; // 请替换为你的实际包名

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data // Lombok 注解，自动生成 getter, setter, toString 等
@AllArgsConstructor
@NoArgsConstructor
public class RecommendationRequest {
    private Long userId; // 使用 Long 对应 Flask 的 int
}