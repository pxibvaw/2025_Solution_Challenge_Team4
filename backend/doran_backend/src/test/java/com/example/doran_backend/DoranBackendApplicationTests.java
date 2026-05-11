package com.example.doran_backend;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@AutoConfigureMockMvc
@SpringBootTest
class DoranBackendApplicationTests {

	@Autowired
	private MockMvc mockMvc;

	@Autowired
	private ObjectMapper objectMapper;

	@Test
	void contextLoads() {
	}

	@Test
	void fullMemoryMateFlow() throws Exception {
		mockMvc.perform(post("/users/onboarding")
						.param("userId", "1")
						.contentType(MediaType.APPLICATION_JSON)
						.content("""
								{
								  "userTitle": "윤서",
								  "ageGroup": "SENIOR_70S",
								  "speechLevel": "HONORIFIC",
								  "hasChildren": true,
								  "happiestMoment": "손주가 태어났을 때",
								  "coreValues": ["가족"],
								  "extraValue": "정"
								}
								"""))
				.andExpect(status().isOk());

		mockMvc.perform(get("/users/profile").param("userId", "1"))
				.andExpect(status().isOk());

		JsonNode start = objectMapper.readTree(mockMvc.perform(post("/interview/start")
						.contentType(MediaType.APPLICATION_JSON)
						.content("""
								{
								  "userId": 1,
								  "clientTs": "2026-05-04T12:00:00"
								}
								"""))
				.andExpect(status().isOk())
				.andReturn()
				.getResponse()
				.getContentAsString());

		String sessionId = start.get("sessionId").asText();
		String requestId = "11111111-1111-1111-1111-111111111111";
		String turnBody = """
				{
				  "sessionId": "%s",
				  "userId": 1,
				  "requestId": "%s",
				  "input": {
				    "mode": "TEXT",
				    "userText": "1975년에 처음 자전거를 탔던 기억이 납니다."
				  },
				  "context": {
				    "speechLevel": "HONORIFIC",
				    "ageGroup": "SENIOR_70S",
				    "coreValues": ["가족"],
				    "extraValue": "정"
				  },
				  "clientTs": "2026-05-04T12:01:00"
				}
				""".formatted(sessionId, requestId);

		JsonNode firstTurn = objectMapper.readTree(mockMvc.perform(post("/interview/turn")
						.contentType(MediaType.APPLICATION_JSON)
						.content(turnBody))
				.andExpect(status().isOk())
				.andReturn()
				.getResponse()
				.getContentAsString());

		JsonNode secondTurn = objectMapper.readTree(mockMvc.perform(post("/interview/turn")
						.contentType(MediaType.APPLICATION_JSON)
						.content(turnBody))
				.andExpect(status().isOk())
				.andReturn()
				.getResponse()
				.getContentAsString());

		assertThat(secondTurn.get("turnId").asText()).isEqualTo(firstTurn.get("turnId").asText());
		assertThat(secondTurn.get("output").get("question").asText()).contains("?");

		mockMvc.perform(get("/chat/sessions/{sessionId}/turns", sessionId))
				.andExpect(status().isOk());

		JsonNode essay = objectMapper.readTree(mockMvc.perform(post("/essays/generate")
						.contentType(MediaType.APPLICATION_JSON)
						.content("""
								{
								  "sessionId": "%s",
								  "userId": 1,
								  "title": "첫 자전거",
								  "representativeYear": 1975,
								  "category": "청춘"
								}
								""".formatted(sessionId)))
				.andExpect(status().isOk())
				.andReturn()
				.getResponse()
				.getContentAsString());

		String essayId = essay.get("essayId").asText();

		mockMvc.perform(get("/library")
						.param("userId", "1")
						.param("year", "1975"))
				.andExpect(status().isOk());

		mockMvc.perform(post("/essays/{essayId}/comments", essayId)
						.contentType(MediaType.APPLICATION_JSON)
						.content("""
								{
								  "authorName": "가족",
								  "content": "이 이야기를 남겨주셔서 고마워요."
								}
								"""))
				.andExpect(status().isOk());

		mockMvc.perform(get("/home").param("userId", "1"))
				.andExpect(status().isOk());

		mockMvc.perform(post("/interview/end")
						.contentType(MediaType.APPLICATION_JSON)
						.content("""
								{
								  "sessionId": "%s",
								  "userId": 1,
								  "endReason": "USER_EXIT"
								}
								""".formatted(sessionId)))
				.andExpect(status().isOk());

		mockMvc.perform(post("/interview/turn")
						.contentType(MediaType.APPLICATION_JSON)
						.content(turnBody))
				.andExpect(status().isBadRequest());
	}

}
