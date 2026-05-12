// src/pages/Episode/EpisodeList.tsx

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { mockEpisodes } from "../../mock/data";
import "../../styles/EpisodeList.css";
import BottomNav from "../../components/BottomNav";

type Episode = {
  id: number;
  title: string;
  preview: string;
};

export default function EpisodeList() {
  const navigate = useNavigate();

  const [storedEpisodes, setStoredEpisodes] =
    useState<Episode[]>(
      JSON.parse(
        localStorage.getItem("episodes") || "[]"
      )
    );

  const allEpisodes = [
    ...storedEpisodes,
    ...mockEpisodes,
  ];

  const [selectedIds, setSelectedIds] =
    useState<number[]>([]);

  const handleSelectEpisode = (
    episodeId: number
  ) => {
    setSelectedIds((prev) =>
      prev.includes(episodeId)
        ? prev.filter((id) => id !== episodeId)
        : [...prev, episodeId]
    );
  };

  const handleSelectAll = () => {
    if (
      selectedIds.length === allEpisodes.length
    ) {
      setSelectedIds([]);
    } else {
      setSelectedIds(
        allEpisodes.map((ep) => ep.id)
      );
    }
  };

  const handleGenerate = () => {
    if (selectedIds.length === 0) return;

    navigate("/generate/loading", {
      state: { selectedIds },
    });
  };

  const handleDeleteEpisode = (
    episodeId: number
  ) => {
    const updatedEpisodes =
      storedEpisodes.filter(
        (ep: Episode) =>
          ep.id !== episodeId
      );

    setStoredEpisodes(updatedEpisodes);

    localStorage.setItem(
      "episodes",
      JSON.stringify(updatedEpisodes)
    );

    setSelectedIds((prev) =>
      prev.filter((id) => id !== episodeId)
    );
  };

  return (
    <>
      <main className="episode-page">
        {/* 헤더 */}
        <div className="episode-header">
          <h2 className="episode-page-title">
            에피소드
          </h2>
        </div>

        {/* 상단 바 */}
        <div className="episode-page-topbar">
          <button
            className="episode-page-select-btn"
            onClick={handleSelectAll}
          >
            {selectedIds.length ===
            allEpisodes.length
              ? "전체 해제"
              : "전체 선택"}
          </button>

          <span className="episode-page-count">
            선택된 에피소드{" "}
            <span>
              {selectedIds.length}개
            </span>
          </span>
        </div>

        {/* 리스트 */}
        <div className="episode-page-list">
          {allEpisodes.map((ep) => {
            const isSelected =
              selectedIds.includes(ep.id);

            return (
              <div
                key={ep.id}
                className={`episode-page-card ${
                  isSelected
                    ? "selected"
                    : ""
                }`}
                onClick={() =>
                  handleSelectEpisode(ep.id)
                }
              >
                <div className="episode-page-card-top">
                  <div className="episode-page-card-title">
                    {ep.title}
                  </div>

                  {isSelected && (
                    <div className="episode-page-selected-badge">
                      ✓
                    </div>
                  )}
                </div>

                <div className="episode-page-card-preview">
                  {ep.preview}
                </div>

                <div className="episode-page-card-actions">
                  <button
                    className="episode-page-detail-btn"
                    onClick={(e) => {
                      e.stopPropagation();

                      navigate(
                        `/episode/${ep.id}`
                      );
                    }}
                  >
                    자세히 보기
                  </button>

                  {!mockEpisodes.some(
                    (mock) =>
                      mock.id === ep.id
                  ) && (
                    <button
                      className="episode-page-delete-btn"
                      onClick={(e) => {
                        e.stopPropagation();

                        handleDeleteEpisode(
                          ep.id
                        );
                      }}
                    >
                      삭제하기
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* 자서전 만들기 */}
        <div className="episode-page-bottom">
          <button
            className={`episode-page-generate-btn ${
              selectedIds.length === 0
                ? "disabled"
                : ""
            }`}
            onClick={handleGenerate}
            disabled={
              selectedIds.length === 0
            }
          >
            자서전 만들기
          </button>
        </div>
      </main>

      <BottomNav />
    </>
  );
}