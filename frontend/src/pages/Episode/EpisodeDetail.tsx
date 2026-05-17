// src/pages/Episode/EpisodeDetail.tsx

import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";

import { fetchEpisodes, type UiEpisode } from "../../api/doran";

import BottomNav from "../../components/BottomNav";

import backIcon from "../../assets/icon_back.png";

import "../../styles/EpisodeDetail.css";

export default function EpisodeDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [episode, setEpisode] = useState<UiEpisode | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        setIsLoading(true);
        setError("");
        const episodes = await fetchEpisodes();
        const found = episodes.find((ep) => ep.id === id) ?? null;
        if (!cancelled) setEpisode(found);
      } catch (e) {
        console.error("Episode detail load failed:", e);
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
  }, [id]);

  if (isLoading) {
    return <div className="episode-detail-page">에피소드를 불러오는 중입니다.</div>;
  }

  if (error || !episode) {
    return (
      <div className="episode-detail-page">
        {error || "에피소드를 찾을 수 없습니다."}
      </div>
    );
  }

  const formattedDate = new Date(episode.createdAt).toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  return (
    <>
      <main className="episode-detail-page">
        <button className="episode-detail-back-btn" onClick={() => navigate(-1)}>
          <img src={backIcon} alt="back" className="episode-detail-back-icon" />
        </button>

        <section className="episode-detail-card">
          <p className="episode-detail-date">{formattedDate}</p>

          <h1 className="episode-detail-title">{episode.title}</h1>

          <div className="episode-detail-divider"></div>

          <div className="episode-detail-content">
            {episode.content
              .split("\n")
              .filter((line) => line.trim() !== "")
              .map((line, idx) => (
                <p key={idx} className="episode-detail-paragraph">
                  {line}
                </p>
              ))}
          </div>
        </section>
      </main>

      <BottomNav />
    </>
  );
}
