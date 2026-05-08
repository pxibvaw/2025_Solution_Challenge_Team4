// src/pages/Generate/GenerateComplete.tsx

import {
  useLocation,
  useNavigate,
} from "react-router-dom";

import { useState } from "react";

import { mockEpisodes } from "../../mock/data";

import bookBackground from "../../assets/book_background.png";

import "../../styles/GenerateComplete.css";

const generateId = () => Date.now();

const generateTimestamp = () =>
  new Date().toISOString();

const getTodayDateString = () =>
  new Date().toLocaleDateString("ko-KR");

/* =========================
  랜덤 표지 gradient
========================= */

const gradients = [
  `
  radial-gradient(
    circle at top left,
    #FFD978 0%,
    #FFB35C 34%,
    #FF8755 70%,
    transparent 76%
  ),

  radial-gradient(
    circle at bottom right,
    #FFF2A6 0%,
    #FFE16B 35%,
    transparent 62%
  ),

  linear-gradient(
    180deg,
    #FFFDF7 0%,
    #F8F0E4 100%
  )
  `,

  `
  radial-gradient(
    circle at top left,
    #FFD7C2 0%,
    #FFB89C 38%,
    #FF9D7A 72%,
    transparent 80%
  ),

  radial-gradient(
    circle at bottom right,
    #FFF2D8 0%,
    #FFE7B8 36%,
    transparent 64%
  ),

  linear-gradient(
    180deg,
    #FFFCF7 0%,
    #F8EFE3 100%
  )
  `,

  `
  radial-gradient(
    circle at top left,
    #E4EDC8 0%,
    #D2E0AF 34%,
    #BFD38D 68%,
    transparent 80%
  ),

  radial-gradient(
    circle at center,
    #FFD6A3 0%,
    #FFB875 30%,
    transparent 55%
  ),

  linear-gradient(
    180deg,
    #FBFAF2 0%,
    #F2ECDD 100%
  )
  `,

  `
  radial-gradient(
    circle at center,
    #FFE7A3 0%,
    #FFD67A 28%,
    #FFBD73 60%,
    transparent 78%
  ),

  radial-gradient(
    circle at top right,
    #FFF8D2 0%,
    #FFF0AF 35%,
    transparent 65%
  ),

  linear-gradient(
    180deg,
    #FFFCF8 0%,
    #F5EFE3 100%
  )
  `,

  `
  radial-gradient(
    circle at top left,
    #FFD2C4 0%,
    #FFB8A5 35%,
    #FFA487 72%,
    transparent 80%
  ),

  radial-gradient(
    circle at bottom right,
    #FFF2BF 0%,
    #FFE494 30%,
    transparent 64%
  ),

  linear-gradient(
    180deg,
    #FFFDF9 0%,
    #F6EEE3 100%
  )
  `,

  `
  radial-gradient(
    circle at top right,
    #E5EDD5 0%,
    #D6E1C0 35%,
    #C8D6A9 70%,
    transparent 82%
  ),

  radial-gradient(
    circle at center,
    #FFDDB4 0%,
    #FFC68C 30%,
    transparent 55%
  ),

  linear-gradient(
    180deg,
    #FCFBF5 0%,
    #F3EDDF 100%
  )
  `,
];

export default function GenerateComplete() {
  const navigate = useNavigate();

  const location = useLocation();

  const selectedIds: number[] =
    location.state?.selectedIds || [];

  /* =========================
    localStorage + mock
  ========================= */

  const storedEpisodes = JSON.parse(
    localStorage.getItem("episodes") ||
      "[]"
  );

  const allEpisodes = [
    ...storedEpisodes,
    ...mockEpisodes,
  ];

  const selectedEpisodes =
    allEpisodes.filter((ep) =>
      selectedIds.includes(ep.id)
    );

  /* =========================
     chapter
  ========================= */

  const chapters = selectedEpisodes.map(
    (ep, idx) => ({
      number: idx + 1,
      title: ep.title,
      id: ep.id,
    })
  );

  const [createdDate] = useState(() =>
    getTodayDateString()
  );

  /* =========================
    gradient 유지
  ========================= */

  const gradientStorageKey =
    `generate-gradient-${selectedIds.join("-")}`;

  const [selectedGradient] =
    useState(() => {
      const saved =
        sessionStorage.getItem(
          gradientStorageKey
        );

      if (saved) {
        return saved;
      }

      const randomGradient =
        gradients[
          Math.floor(
            Math.random() *
              gradients.length
          )
        ];

      sessionStorage.setItem(
        gradientStorageKey,
        randomGradient
      );

      return randomGradient;
    });

  /* =========================
    preview 전용 id
  ========================= */

  const [previewBookId] =
    useState(() => Date.now());

  /* =========================
    미리보기
  ========================= */

  const handlePreview = () => {
    if (chapters.length === 0) return;

    const previewBook = {
      id: previewBookId,

      title: "나의 이야기",

      createdAt:
        generateTimestamp(),

      chapters,

      coverGradient:
        selectedGradient,

      pages: selectedEpisodes.map(
        (ep, idx) => ({
          id: ep.id,

          chapter: ep.title,

          content:
            ep.content ||
            ep.preview,

          pageNumber: idx + 1,
        })
      ),
    };

    navigate(
      `/reader/${previewBook.id}`,
      {
        state: {
          previewBook,
        },
      }
    );
  };

  /* =========================
    저장
  ========================= */

  const handleSave = () => {
    const existing = JSON.parse(
      localStorage.getItem("books") ||
        "[]"
    );

    const newBook = {
      id: generateId(),

      title: "나의 이야기",

      createdAt:
        generateTimestamp(),

      chapters,

      coverGradient:
        selectedGradient,

      pages: selectedEpisodes.map(
        (ep, idx) => ({
          id: ep.id,

          chapter: ep.title,

          content:
            ep.content ||
            ep.preview,

          pageNumber: idx + 1,
        })
      ),
    };

    localStorage.setItem(
      "books",
      JSON.stringify([
        newBook,
        ...existing,
      ])
    );

    /* =========================
      저장 완료 시 gradient 제거
    ========================= */

    sessionStorage.removeItem(
      gradientStorageKey
    );

    navigate("/library");
  };

  return (
    <main className="generate-complete-page">
      {/* 헤더 */}

      <div className="generate-complete-header">
        <h1 className="generate-complete-title">
          나의이야기
        </h1>

        <p className="generate-complete-date">
          {createdDate} 생성
        </p>
      </div>

      {/* 책 */}

      <div className="generate-book-wrapper">
        <div className="generate-book-shadow"></div>

        <div className="generate-book">
          <div
            className="generate-book-cover"
            style={{
              background:
                selectedGradient,
            }}
          >
            <div className="generate-book-title">
              나의 이야기
            </div>

            <div className="generate-book-author">
              김철수 지음
            </div>
          </div>

          <img
            src={bookBackground}
            alt="book"
            className="generate-book-frame"
          />
        </div>
      </div>

      {/* 목차 */}

      <section className="generate-complete-toc">
        <h2 className="generate-complete-toc-title">
          목차
        </h2>

        <div className="generate-complete-chapter-list">
          {chapters.length === 0 ? (
            <div className="generate-empty">
              선택된 에피소드가 없습니다.
            </div>
          ) : (
            chapters.map((ch) => (
              <div
                key={ch.id}
                className="generate-complete-chapter"
              >
                <div className="generate-complete-number">
                  {ch.number}
                </div>

                <div className="generate-complete-chapter-title">
                  {ch.title}
                </div>
              </div>
            ))
          )}
        </div>
      </section>

      {/* 버튼 */}

      <div className="generate-complete-bottom">
        <button
          className="generate-preview-btn"
          onClick={handlePreview}
        >
          미리보기
        </button>

        <button
          className="generate-save-btn"
          onClick={handleSave}
        >
          저장하기
        </button>
      </div>
    </main>
  );
}