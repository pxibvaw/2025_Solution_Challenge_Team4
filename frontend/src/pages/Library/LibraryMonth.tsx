// src/pages/Library/LibraryMonth.tsx

import {
  useLocation,
  useNavigate,
} from "react-router-dom";

import {
  useMemo,
  useState,
} from "react";

import BottomNav from "../../components/BottomNav";

import commentIcon from "../../assets/icon_comment.png";
import backIcon from "../../assets/icon_back.png";
import libraryBookImage from "../../assets/library_book.png";

import "../../styles/Library.css";
import "../../styles/LibraryMonth.css";

/* =========================
   타입
========================= */

type Book = {
  id: number;

  title: string;

  createdAt: string;

  coverGradient?: string;

  chapters: {
    number: number;
    title: string;
    id: number;
  }[];
};

/* =========================
   mock 댓글 수
========================= */

const mockCommentCount: Record<
  number,
  number
> = {
  1: 5,
  2: 3,
  3: 8,
};

export default function LibraryMonth() {
  const navigate = useNavigate();

  const location = useLocation();

  const monthKey =
    location.state?.monthKey;

  const [books, setBooks] =
    useState<Book[]>(() =>
      JSON.parse(
        localStorage.getItem(
          "books"
        ) || "[]"
      )
    );

  const [openedMenu, setOpenedMenu] =
    useState<number | null>(null);

  /* 최신순 / 오래된순 */

  const [sortType, setSortType] =
    useState<
      "latest" | "oldest"
    >("latest");

  /* 검색 */

  const [search, setSearch] =
    useState("");

  /* =========================
     삭제
  ========================= */

  const handleDelete = (
    bookId: number
  ) => {
    const updated = books.filter(
      (b) => b.id !== bookId
    );

    setBooks(updated);

    localStorage.setItem(
      "books",
      JSON.stringify(updated)
    );
  };

  /* =========================
     월 전체 책 개수
     (검색 영향 X)
  ========================= */

  const totalMonthCount =
    useMemo(() => {
      return books.filter((book) => {
        const d = new Date(
          book.createdAt
        );

        const key = `${d.getFullYear()}년 ${
          d.getMonth() + 1
        }월`;

        return key === monthKey;
      }).length;
    }, [books, monthKey]);

  /* =========================
     월 필터 + 검색 + 정렬
  ========================= */

  const filtered = useMemo(() => {
    const result = books.filter(
      (book) => {
        const d = new Date(
          book.createdAt
        );

        const key = `${d.getFullYear()}년 ${
          d.getMonth() + 1
        }월`;

        return (
          key === monthKey &&
          book.title
            .toLowerCase()
            .includes(
              search.toLowerCase()
            )
        );
      }
    );

    result.sort((a, b) => {
      if (sortType === "latest") {
        return (
          new Date(
            b.createdAt
          ).getTime() -
          new Date(
            a.createdAt
          ).getTime()
        );
      }

      return (
        new Date(
          a.createdAt
        ).getTime() -
        new Date(
          b.createdAt
        ).getTime()
      );
    });

    return result;
  }, [
    books,
    monthKey,
    search,
    sortType,
  ]);

  return (
    <>
      <main className="library-page library-month-page">
        {/* 상단 */}

        <div className="library-month-top">
          <button
            className="library-back-btn"
            onClick={() =>
              navigate(-1)
            }
          >
            <img src={backIcon} alt="back" />
          </button>

          <h1 className="library-month-main-title">
            {monthKey}
          </h1>
        </div>

        {/* 배너 */}

        <section
          className="library-month-banner"
        >
          <div className="library-month-banner-content">
            <h2 className="library-month-banner-title">
              이번 달에 만든 이야기
            </h2>

            <p className="library-month-banner-count">
              {totalMonthCount}권
            </p>
          </div>

          <img
            src={libraryBookImage}
            alt="books"
            className="library-month-banner-book"
          />
        </section>

        {/* 필터 */}

        <div className="library-month-filter-row">
          <button
            className="library-month-filter-btn"
            onClick={() =>
              setSortType(
                sortType ===
                  "latest"
                  ? "oldest"
                  : "latest"
              )
            }
          >
            {sortType === "latest"
              ? "최신순 ▼"
              : "오래된순 ▲"}
          </button>

          <input
            className="library-month-search"
            placeholder="책 제목 검색"
            value={search}
            onChange={(e) =>
              setSearch(
                e.target.value
              )
            }
          />
        </div>

        {/* empty */}

        {filtered.length === 0 ? (
          <p className="library-month-empty">
            해당 조건의 책이 없습니다.
          </p>
        ) : (
          <div className="library-book-grid">
            {filtered.map((book) => (
              <div
                key={book.id}
                className="library-book-card"
                onClick={() =>
                  navigate(
                    `/book/${book.id}`
                  )
                }
              >
                {/* 표지 */}

                <div
                  className="library-book-cover"
                  style={{
                    background:
                      book.coverGradient,
                  }}
                ></div>

                {/* info */}

                <div className="library-book-info">
                  <div className="library-book-meta">
                    <p className="library-book-title">
                      {book.title}
                    </p>

                    <p className="library-book-comment">
                      <img
                        src={commentIcon}
                        alt="comment"
                        className="library-comment-icon"
                      />

                      {mockCommentCount[
                        book.id
                      ] || 0}
                      개
                    </p>
                  </div>
                </div>

                {/* 메뉴 버튼 */}

                <button
                  className="library-more-btn"
                  onClick={(e) => {
                    e.stopPropagation();

                    setOpenedMenu(
                      openedMenu ===
                        book.id
                        ? null
                        : book.id
                    );
                  }}
                >
                  ⋯
                </button>

                {/* 삭제 popup */}

                {openedMenu ===
                  book.id && (
                  <div className="library-delete-popup">
                    <button
                      className="library-delete-action"
                      onClick={(
                        e
                      ) => {
                        e.stopPropagation();

                        handleDelete(
                          book.id
                        );
                      }}
                    >
                      삭제하기
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </main>

      <BottomNav />
    </>
  );
}