// 文件路径: src/main/java/com/example/demo/Demo3Application.java
package com.example.demo; // 确保包名正确

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication // 这个注解是关键
public class DemoApplication {

    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}