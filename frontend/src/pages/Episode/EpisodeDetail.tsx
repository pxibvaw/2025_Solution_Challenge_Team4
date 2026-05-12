// src/pages/Episode/EpisodeDetail.tsx

import {
  useParams,
  useNavigate,
} from "react-router-dom";

import { mockEpisodes } from "../../mock/data";

import BottomNav from "../../components/BottomNav";

import backIcon from "../../assets/icon_back.png";

import "../../styles/EpisodeDetail.css";

export default function EpisodeDetail() {
  const { id } = useParams();

  const navigate = useNavigate();

  const episodeId = Number(id);

  /* localStorage */

  const storedEpisodes = JSON.parse(
    localStorage.getItem("episodes") ||
      "[]"
  );

  /* 전체 episode */

  const allEpisodes = [
    ...storedEpisodes,
    ...mockEpisodes,
  ];

  /* 현재 episode */

  const episode = allEpisodes.find(
    (e) => e.id === episodeId
  );

  if (!episode) {
    return (
      <div className="episode-detail-page">
        에피소드를 찾을 수 없습니다.
      </div>
    );
  }

  /* 날짜 */

  const formattedDate = new Date(
    episode.createdAt
  ).toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  return (
    <>
      <main className="episode-detail-page">
        {/* 뒤로가기 */}

        <button
          className="episode-detail-back-btn"
          onClick={() => navigate(-1)}
        >
          <img
            src={backIcon}
            alt="back"
            className="episode-detail-back-icon"
          />
        </button>

        {/* 카드 */}

        <section className="episode-detail-card">
          {/* 날짜 */}

          <p className="episode-detail-date">
            {formattedDate}
          </p>

          {/* 제목 */}

          <h1 className="episode-detail-title">
            {episode.title}
          </h1>

          {/* divider */}

          <div className="episode-detail-divider"></div>

          {/* 본문 */}

          <div className="episode-detail-content">
            {episode.content ? (
              (episode.content as string)
                .split("\n")
                .filter(
                  (line: string) =>
                    line.trim() !== ""
                )
                .map(
                  (
                    line: string,
                    idx: number
                  ) => (
                    <p
                      key={idx}
                      className="episode-detail-paragraph"
                    >
                      {line}
                    </p>
                  )
                )
            ) : (
              <p className="episode-detail-paragraph">
                {episode.preview}
              </p>
            )}
          </div>
        </section>
      </main>

      {/* 하단 네비 */}

      <BottomNav />
    </>
  );
}