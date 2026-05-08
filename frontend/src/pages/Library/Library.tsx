// src/pages/Library/Library.tsx

import { useMemo, useState } from "react";

import { useNavigate } from "react-router-dom";

import BottomNav from "../../components/BottomNav";

import "../../styles/Library.css";
import commentIcon from "../../assets/icon_comment.png";

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

// 🔥 댓글 mock

const mockCommentCount: Record<
  number,
  number
> = {
  1: 5,
  2: 3,
  3: 8,
};

export default function Library() {
  const navigate = useNavigate();

  const [books, setBooks] = useState<
    Book[]
  >(() =>
    JSON.parse(
      localStorage.getItem("books") ||
        "[]"
    )
  );

  const [search, setSearch] =
    useState("");

  const [openedMenu, setOpenedMenu] =
    useState<number | null>(null);

  // 삭제

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

  // 검색

  const filteredBooks = useMemo(() => {
    return books.filter((b) =>
      b.title
        .toLowerCase()
        .includes(search.toLowerCase())
    );
  }, [books, search]);

  // 월별 그룹핑

  const grouped = useMemo(() => {
    const map: Record<string, Book[]> =
      {};

    filteredBooks.forEach((book) => {
      const date = new Date(
        book.createdAt
      );

      const key = `${date.getFullYear()}년 ${
        date.getMonth() + 1
      }월`;

      if (!map[key]) map[key] = [];

      map[key].push(book);
    });

    return map;
  }, [filteredBooks]);

  const handleBookClick = (
    id: number
  ) => {
    navigate(`/book/${id}`);
  };

  const goMonth = (
    monthKey: string
  ) => {
    navigate("/library/month", {
      state: { monthKey },
    });
  };

  return (
    <>
      <main className="library-page">
        {/* 헤더 */}

        <div className="library-header">
          <h1 className="library-title">
            내 서재
          </h1>

          <div className="library-header-actions">
            <button
              className="library-share-btn"
              onClick={() =>
                alert("공유 기능")
              }
            >
              공유
            </button>
          </div>
        </div>

        {/* 검색 */}

        <input
          className="library-search"
          placeholder="책 제목 검색"
          value={search}
          onChange={(e) =>
            setSearch(e.target.value)
          }
        />

        {/* 월별 */}

        {Object.entries(grouped).map(
          ([month, list]) => (
            <section
              key={month}
              className="library-section"
            >
              {/* 월 헤더 */}

              <div
                className="library-month-header"
                onClick={() =>
                  goMonth(month)
                }
              >
                <div>
                  <h2 className="library-month-title">
                    {month} &gt;
                  </h2>

                  <p className="library-month-count">
                    {list.length}권
                  </p>
                </div>
              </div>

              {/* 책 리스트 */}

              <div className="library-book-grid">
                {list
                  .slice(0, 2)
                  .map((book) => (
                    <div
                      key={book.id}
                      className="library-book-card"
                      onClick={() =>
                        handleBookClick(
                          book.id
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

                            {mockCommentCount[book.id] || 0}개
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
            </section>
          )
        )}
      </main>

      <BottomNav />
    </>
  );
}