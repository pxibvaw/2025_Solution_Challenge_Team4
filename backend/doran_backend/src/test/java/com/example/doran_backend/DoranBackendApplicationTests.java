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

		mockMvc.perform(post("/api/ai/episodes")
						.contentType(MediaType.APPLICATION_JSON)
						.content("""
								{
								  "sessionId": "%s",
								  "userId": "1",
								  "newEpisodes": [
								    {
								      "turn_start": 0,
								      "turn_end": 1,
								      "title": "첫 자전거의 기억",
								      "type": "KEY_SCENE",
								      "theme": "청춘",
								      "emotion_tone": "설렘",
								      "narrative": "처음 자전거를 타던 날의 기억이 선명하게 남아 있습니다.",
								      "source_session_id": "%s",
								      "source_turn_range": [0, 1],
								      "source_facts": ["처음 자전거를 탔다"],
								      "importance_score": 5.0,
								      "quality": {
								        "faithfulness_score": 0.9,
								        "coverage_score": 0.8,
								        "emotional_authenticity": 4.0,
								        "sensory_vividness": 3.5,
								        "personal_voice": 4.0,
								        "narrative_flow": 4.0,
								        "narrative_richness": 0.82,
								        "quality_grade": "GOOD",
								        "needs_regeneration": false
								      }
								    }
								  ],
								  "mergedEpisodes": [],
								  "episodesCreated": 1,
								  "episodesMerged": 0,
								  "weakEpisodes": 0,
								  "warnings": []
								}
								""".formatted(sessionId, sessionId)))
				.andExpect(status().isOk());

		mockMvc.perform(get("/api/episodes").param("userId", "1"))
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
