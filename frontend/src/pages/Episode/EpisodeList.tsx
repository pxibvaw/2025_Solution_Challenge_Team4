// src/pages/Episode/EpisodeList.tsx

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchEpisodes, type UiEpisode } from "../../api/doran";
import "../../styles/EpisodeList.css";
import BottomNav from "../../components/BottomNav";

export default function EpisodeList() {
  const navigate = useNavigate();

  const [episodes, setEpisodes] = useState<UiEpisode[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        setIsLoading(true);
        setError("");
        const data = await fetchEpisodes();
        if (!cancelled) setEpisodes(data);
      } catch (e) {
        console.error("Episode load failed:", e);
        if (!cancelled) {
          setError(
            e instanceof Error
              ? e.message
              : "에피소드를 불러오지 못했습니다."
          );
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    load();

    return () => {
      cancelled = true;
    };
  }, []);

  const handleSelectEpisode = (episodeId: string) => {
    setSelectedIds((prev) =>
      prev.includes(episodeId)
        ? prev.filter((id) => id !== episodeId)
        : [...prev, episodeId]
    );
  };

  const handleSelectAll = () => {
    if (selectedIds.length === episodes.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(episodes.map((ep) => ep.id));
    }
  };

  const handleGenerate = () => {
    if (selectedIds.length === 0) return;

    navigate("/generate/loading", {
      state: { selectedIds },
    });
  };

  return (
    <>
      <main className="episode-page">
        <div className="episode-header">
          <h2 className="episode-page-title">에피소드</h2>
        </div>

        <div className="episode-page-topbar">
          <button
            className="episode-page-select-btn"
            onClick={handleSelectAll}
            disabled={episodes.length === 0}
          >
            {selectedIds.length === episodes.length && episodes.length > 0
              ? "전체 해제"
              : "전체 선택"}
          </button>

          <span className="episode-page-count">
            선택된 에피소드 <span>{selectedIds.length}개</span>
          </span>
        </div>

        <div className="episode-page-list">
          {isLoading && (
            <div className="episode-page-empty">에피소드를 불러오는 중입니다.</div>
          )}

          {!isLoading && error && (
            <div className="episode-page-empty">{error}</div>
          )}

          {!isLoading && !error && episodes.length === 0 && (
            <div className="episode-page-empty">
              아직 저장된 에피소드가 없습니다.
            </div>
          )}

          {episodes.map((ep) => {
            const isSelected = selectedIds.includes(ep.id);

            return (
              <div
                key={ep.id}
                className={`episode-page-card ${isSelected ? "selected" : ""}`}
                onClick={() => handleSelectEpisode(ep.id)}
              >
                <div className="episode-page-card-top">
                  <div className="episode-page-card-title">{ep.title}</div>

                  {isSelected && (
                    <div className="episode-page-selected-badge">✓</div>
                  )}
                </div>

                <div className="episode-page-card-preview">{ep.preview}</div>

                <div className="episode-page-card-actions">
                  <button
                    className="episode-page-detail-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(`/episode/${ep.id}`);
                    }}
                  >
                    자세히 보기
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        <div className="episode-page-bottom">
          <button
            className={`episode-page-generate-btn ${
              selectedIds.length === 0 ? "disabled" : ""
            }`}
            onClick={handleGenerate}
            disabled={selectedIds.length === 0}
          >
            자서전 만들기
          </button>
        </div>
      </main>

      <BottomNav />
    </>
  );
}
