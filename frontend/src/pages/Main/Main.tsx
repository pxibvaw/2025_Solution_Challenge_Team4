// src/pages/Main/Main.tsx

import { useNavigate } from "react-router-dom";

import {
  mockEpisodes,
  mockBooks,
} from "../../mock/data";

import "../../styles/main.css";

import BottomNav from "../../components/BottomNav";

import avatarFace from "../../assets/main_char_face1.png";
import startFaceImg from "../../assets/main_char_face2.png";

import micIcon from "../../assets/icon_mic_black.png";

import bookIcon from "../../assets/icon_book.png";
import arrowIcon from "../../assets/icon_goto.png";

import shelfImg from "../../assets/main_bookshelf.png";

import episodeIcon from "../../assets/icon_doc.png";

export default function Main() {
  const navigate = useNavigate();

  const todayQuestion =
    "어제 있었던 일 중 가장 기억에 남는 순간은 무엇인가요?";

  /* =========================
     localStorage
  ========================= */

  const storedEpisodes = JSON.parse(
    localStorage.getItem(
      "episodes"
    ) || "[]"
  );

  const storedBooks = JSON.parse(
    localStorage.getItem(
      "books"
    ) || "[]"
  );

  /* =========================
     최신 에피소드
  ========================= */

  const allEpisodes = [
    ...storedEpisodes,
    ...mockEpisodes,
  ];

  const recentEpisodes =
    allEpisodes
      .sort(
        (a, b) =>
          new Date(
            b.createdAt
          ).getTime() -
          new Date(
            a.createdAt
          ).getTime()
      )
      .slice(0, 2);

  /* =========================
     최신 책
  ========================= */

  const allBooks = [
    ...storedBooks,
    ...mockBooks,
  ];

  const previewBooks = allBooks
    .sort(
      (a, b) =>
        new Date(
          b.createdAt
        ).getTime() -
        new Date(
          a.createdAt
        ).getTime()
    )
    .slice(0, 3);

  return (
    <main className="main-container">
      {/* 상단 */}

      <section className="hero-section">
        <div className="profile-row">
          <button className="profile-btn">
            내정보
          </button>

          <div className="avatar">
            <img
              src={avatarFace}
              className="avatar-face"
              alt="face"
            />
          </div>

          <button className="alarm-btn">
            알림
          </button>
        </div>

        <div
          className="memory-card"
          onClick={() =>
            navigate("/interview")
          }
        >
          <div className="bookmark" />

          <p>{todayQuestion}</p>
        </div>
      </section>

      {/* 대화 시작 버튼 */}

      <button
        className="start-btn"
        onClick={() =>
          navigate("/interview")
        }
      >
        <img
          src={micIcon}
          className="start-icon"
          alt="mic"
        />

        <span className="start-btn-text">
          대화 시작하기
        </span>

        <span className="start-face">
          <img
            src={startFaceImg}
            className="start-face-img"
            alt="face"
          />
        </span>
      </button>

      {/* 서재 */}

      <section className="library-section">
        <div
          className="section-header"
          onClick={() =>
            navigate("/library")
          }
        >
          <div className="section-left">
            <img
              src={bookIcon}
              className="section-icon"
              alt="book"
            />

            <h3>서재</h3>
          </div>

          <img
            src={arrowIcon}
            className="section-arrow-img"
            alt="arrow"
          />
        </div>

        <div className="library-wrapper">
          <div className="library-preview">
            {previewBooks.map(
              (book) => (
                <article
                  key={book.id}
                  className="book-card"
                  onClick={() =>
                    navigate(
                      `/book/${book.id}`
                    )
                  }
                >
                  <div
                    className="book-cover"
                    style={{
                      background:
                        book.coverGradient ||
                        "#F1D2BC",
                    }}
                  />
                </article>
              )
            )}
          </div>

          <img
            src={shelfImg}
            className="bookshelf"
            alt="shelf"
          />
        </div>
      </section>

      {/* 최근 에피소드 */}

      <section className="episode-section">
        <div
          className="episode-header"
          onClick={() =>
            navigate("/episodes")
          }
        >
          <img
            src={episodeIcon}
            className="episode-header-icon"
            alt="episode"
          />

          <span className="episode-header-title">
            최근 나눈 에피소드
          </span>

          <img
            src={arrowIcon}
            className="episode-header-arrow"
            alt="arrow"
          />
        </div>

        <div className="episode-list">
          {recentEpisodes.map(
            (ep) => (
              <article
                key={ep.id}
                className="episode-card"
                onClick={() =>
                  navigate(
                    `/episode/${ep.id}`
                  )
                }
              >
                <div className="episode-date">
                  {new Date(
                    ep.createdAt
                  ).toLocaleDateString(
                    "ko-KR"
                  )}
                </div>

                <div className="episode-card-title">
                  {ep.title}
                </div>

                <div className="episode-preview">
                  {ep.preview}
                </div>
              </article>
            )
          )}
        </div>
      </section>

      <BottomNav />
    </main>
  );
}