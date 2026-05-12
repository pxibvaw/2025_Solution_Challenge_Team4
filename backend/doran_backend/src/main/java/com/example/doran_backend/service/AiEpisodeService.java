package com.example.doran_backend.service;

import com.example.doran_backend.dto.*;
import com.example.doran_backend.entity.AiEpisodeCallbackLog;
import com.example.doran_backend.entity.Episode;
import com.example.doran_backend.repository.AiEpisodeCallbackLogRepository;
import com.example.doran_backend.repository.EpisodeRepository;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class AiEpisodeService {

    private static final TypeReference<List<Map<String, Object>>> PERSONS_TYPE = new TypeReference<>() {};
    private static final TypeReference<Map<String, Object>> MAP_TYPE = new TypeReference<>() {};
    private static final TypeReference<List<String>> STRING_LIST_TYPE = new TypeReference<>() {};

    private final EpisodeRepository episodeRepository;
    private final AiEpisodeCallbackLogRepository callbackLogRepository;
    private final ObjectMapper objectMapper;

    @Transactional(readOnly = true)
    public List<AiEpisodeResponse> getEpisodes(String userId) {
        String normalizedUserId = requireText(userId, "userId는 필수입니다.");
        return episodeRepository.findByUserIdOrderByCreatedAtAsc(normalizedUserId)
                .stream()
                .map(this::toResponse)
                .toList();
    }

    @Transactional
    public AiEpisodeCallbackResponse receiveCallback(AiEpisodeCallbackRequest request) {
        requireNonNull(request, "요청 본문은 필수입니다.");
        String sessionId = requireText(request.getSessionId(), "sessionId는 필수입니다.");
        String userId = requireText(request.getUserId(), "userId는 필수입니다.");

        AiEpisodeCallbackLog existing = callbackLogRepository.findById(sessionId).orElse(null);
        if (existing != null) {
            return new AiEpisodeCallbackResponse(
                    existing.getSessionId(),
                    existing.getEpisodesCreated(),
                    existing.getEpisodesMerged(),
                    existing.getWeakEpisodes(),
                    true
            );
        }

        List<AiEpisodePayload> newEpisodes = nullToEmpty(request.getNewEpisodes());
        List<AiEpisodePayload> mergedEpisodes = nullToEmpty(request.getMergedEpisodes());

        for (AiEpisodePayload payload : newEpisodes) {
            Episode episode = toEntity(payload, userId, sessionId, false);
            episodeRepository.save(episode);
        }

        for (AiEpisodePayload payload : mergedEpisodes) {
            Episode episode = toEntity(payload, userId, sessionId, true);
            episodeRepository.findById(episode.getId())
                    .ifPresentOrElse(existingEpisode -> {
                        existingEpisode.updateFrom(episode);
                        episodeRepository.save(existingEpisode);
                    }, () -> episodeRepository.save(episode));
        }

        AiEpisodeCallbackLog log = AiEpisodeCallbackLog.builder()
                .sessionId(sessionId)
                .userId(userId)
                .episodesCreated(valueOrDefault(request.getEpisodesCreated(), newEpisodes.size()))
                .episodesMerged(valueOrDefault(request.getEpisodesMerged(), mergedEpisodes.size()))
                .weakEpisodes(valueOrDefault(request.getWeakEpisodes(), 0))
                .warningsJson(toJson(request.getWarnings()))
                .receivedAt(LocalDateTime.now())
                .build();
        callbackLogRepository.save(log);

        return new AiEpisodeCallbackResponse(
                log.getSessionId(),
                log.getEpisodesCreated(),
                log.getEpisodesMerged(),
                log.getWeakEpisodes(),
                false
        );
    }

    private Episode toEntity(AiEpisodePayload payload, String fallbackUserId, String fallbackSessionId, boolean merged) {
        requireNonNull(payload, "episode payload는 null일 수 없습니다.");
        String id = valueOrDefault(payload.getId(), UUID.randomUUID().toString());
        LocalDateTime now = LocalDateTime.now();
        AiEpisodeQualityPayload quality = payload.getQuality();
        Integer sourceTurnStart = getRangeValue(payload.getSourceTurnRange(), 0, payload.getTurnStart());
        Integer sourceTurnEnd = getRangeValue(payload.getSourceTurnRange(), 1, payload.getTurnEnd());

        return Episode.builder()
                .id(id)
                .userId(valueOrDefault(payload.getUserId(), fallbackUserId))
                .sessionId(valueOrDefault(payload.getSessionId(), fallbackSessionId))
                .title(valueOrDefault(payload.getTitle(), "제목 없는 에피소드"))
                .narrative(valueOrDefault(payload.getNarrative(), ""))
                .quote(payload.getQuote())
                .timeHint(payload.getTimeHint())
                .periodLabel(payload.getPeriodLabel())
                .estimatedYearRange(payload.getEstimatedYearRange())
                .location(payload.getLocation())
                .personsJson(toJson(payload.getPersons()))
                .sensoryJson(toJson(payload.getSensory()))
                .type(valueOrDefault(payload.getType(), "GENERAL_EVENT"))
                .keySceneType(payload.getKeySceneType())
                .theme(valueOrDefault(payload.getTheme(), "기타"))
                .emotionTone(valueOrDefault(payload.getEmotionTone(), "중립"))
                .emotionNuance(payload.getEmotionNuance())
                .autobiographyHint(payload.getAutobiographyHint())
                .lifeValue(payload.getLifeValue())
                .importanceScore(payload.getImportanceScore() == null ? 5.0 : payload.getImportanceScore())
                .faithfulnessScore(quality == null ? null : quality.getFaithfulnessScore())
                .coverageScore(quality == null ? null : quality.getCoverageScore())
                .emotionalAuthenticity(quality == null ? null : quality.getEmotionalAuthenticity())
                .sensoryVividness(quality == null ? null : quality.getSensoryVividness())
                .personalVoice(quality == null ? null : quality.getPersonalVoice())
                .narrativeFlow(quality == null ? null : quality.getNarrativeFlow())
                .narrativeRichness(quality == null ? null : quality.getNarrativeRichness())
                .qualityGrade(quality == null ? null : quality.getQualityGrade())
                .needsRegeneration(quality == null ? null : quality.getNeedsRegeneration())
                .sourceSessionId(valueOrDefault(payload.getSourceSessionId(), fallbackSessionId))
                .sourceTurnStart(sourceTurnStart)
                .sourceTurnEnd(sourceTurnEnd)
                .sourceFactsJson(toJson(payload.getSourceFacts()))
                .merged(merged)
                .version(1)
                .selectedForAutobiography(false)
                .createdAt(now)
                .updatedAt(now)
                .build();
    }

    public AiEpisodeResponse toResponse(Episode episode) {
        List<Integer> sourceTurnRange = new ArrayList<>();
        if (episode.getSourceTurnStart() != null && episode.getSourceTurnEnd() != null) {
            sourceTurnRange.add(episode.getSourceTurnStart());
            sourceTurnRange.add(episode.getSourceTurnEnd());
        }

        return new AiEpisodeResponse(
                episode.getId(),
                episode.getUserId(),
                episode.getSessionId(),
                episode.getTitle(),
                episode.getNarrative(),
                episode.getQuote(),
                episode.getTimeHint(),
                episode.getPeriodLabel(),
                episode.getEstimatedYearRange(),
                episode.getLocation(),
                fromJson(episode.getPersonsJson(), PERSONS_TYPE, List.of()),
                fromJson(episode.getSensoryJson(), MAP_TYPE, null),
                episode.getType(),
                episode.getKeySceneType(),
                episode.getTheme(),
                episode.getEmotionTone(),
                episode.getEmotionNuance(),
                episode.getAutobiographyHint(),
                episode.getLifeValue(),
                episode.getImportanceScore(),
                new AiEpisodeQualityResponse(
                        episode.getFaithfulnessScore(),
                        episode.getCoverageScore(),
                        episode.getEmotionalAuthenticity(),
                        episode.getSensoryVividness(),
                        episode.getPersonalVoice(),
                        episode.getNarrativeFlow(),
                        episode.getNarrativeRichness(),
                        episode.getQualityGrade(),
                        episode.getNeedsRegeneration()
                ),
                episode.getSourceSessionId(),
                sourceTurnRange.isEmpty() ? null : sourceTurnRange,
                fromJson(episode.getSourceFactsJson(), STRING_LIST_TYPE, List.of()),
                episode.getMerged(),
                episode.getMergedFrom(),
                episode.getVersion(),
                episode.getSelectedForAutobiography(),
                episode.getUserEditedTitle(),
                episode.getUserMemo(),
                episode.getCreatedAt(),
                episode.getUpdatedAt()
        );
    }

    private String toJson(Object value) {
        if (value == null) {
            return null;
        }
        try {
            return objectMapper.writeValueAsString(value);
        } catch (JsonProcessingException e) {
            throw new IllegalArgumentException("JSON 변환에 실패했습니다.");
        }
    }

    private <T> T fromJson(String value, TypeReference<T> type, T defaultValue) {
        if (value == null || value.trim().isEmpty()) {
            return defaultValue;
        }
        try {
            return objectMapper.readValue(value, type);
        } catch (JsonProcessingException e) {
            return defaultValue;
        }
    }

    private <T> List<T> nullToEmpty(List<T> values) {
        return values == null ? List.of() : values;
    }

    private Integer getRangeValue(List<Integer> range, int index, Integer fallback) {
        if (range == null || range.size() <= index) {
            return fallback;
        }
        return range.get(index);
    }

    private Integer valueOrDefault(Integer value, Integer defaultValue) {
        return value == null ? defaultValue : value;
    }

    private String valueOrDefault(String value, String defaultValue) {
        if (value == null || value.trim().isEmpty()) {
            return defaultValue;
        }
        return value.trim();
    }

    private String requireText(String value, String message) {
        if (value == null || value.trim().isEmpty()) {
            throw new IllegalArgumentException(message);
        }
        return value.trim();
    }

    private void requireNonNull(Object value, String message) {
        if (value == null) {
            throw new IllegalArgumentException(message);
        }
    }
}
