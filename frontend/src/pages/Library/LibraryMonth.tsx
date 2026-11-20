// src/pages/Library/LibraryMonth.tsx

import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { deleteBook, fetchBooks, type Book } from "../../api/doran";
import BottomNav from "../../components/BottomNav";

import commentIcon from "../../assets/icon_comment.png";
import backIcon from "../../assets/icon_back.png";
import libraryBookImage from "../../assets/library_book.png";

import "../../styles/Library.css";
import "../../styles/LibraryMonth.css";

function monthKeyToApiMonth(monthKey?: string) {
  if (!monthKey) return undefined;
  const match = monthKey.match(/(\d{4})년\s*(\d{1,2})월/);
  if (!match) return undefined;
  return `${match[1]}-${match[2].padStart(2, "0")}`;
}

function getMonthKey(book: Book) {
  const date = new Date(book.createdAt);
  return `${date.getFullYear()}년 ${date.getMonth() + 1}월`;
}

export default function LibraryMonth() {
  const navigate = useNavigate();
  const location = useLocation();
  const monthKey = location.state?.monthKey;

  const [books, setBooks] = useState<Book[]>([]);
  const [openedMenu, setOpenedMenu] = useState<string | null>(null);
  const [sortType, setSortType] = useState<"latest" | "oldest">("latest");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function loadBooks() {
      try {
        const data = await fetchBooks(monthKeyToApiMonth(monthKey));
        if (!cancelled) setBooks(data);
      } catch (e) {
        console.error("Monthly book load failed:", e);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadBooks();

    return () => {
      cancelled = true;
    };
  }, [monthKey]);

  const handleDelete = async (bookId: string) => {
    try {
      await deleteBook(bookId);
      setBooks((prev) => prev.filter((book) => book.id !== bookId));
      setOpenedMenu(null);
    } catch (e) {
      console.error("Book delete failed:", e);
      alert(e instanceof Error ? e.message : "책 삭제에 실패했습니다.");
    }
  };

  const totalMonthCount = useMemo(() => {
    return books.filter((book) => !monthKey || getMonthKey(book) === monthKey).length;
  }, [books, monthKey]);

  const filtered = useMemo(() => {
    const result = books.filter((book) => {
      const sameMonth = !monthKey || getMonthKey(book) === monthKey;
      return sameMonth && book.title.toLowerCase().includes(search.toLowerCase());
    });

    result.sort((a, b) => {
      const aTime = new Date(a.createdAt).getTime();
      const bTime = new Date(b.createdAt).getTime();
      return sortType === "latest" ? bTime - aTime : aTime - bTime;
    });

    return result;
  }, [books, monthKey, search, sortType]);

  return (
    <>
      <main className="library-page library-month-page">
        <div className="library-month-top">
          <button className="library-back-btn" onClick={() => navigate(-1)}>
            <img src={backIcon} alt="back" />
          </button>

          <h1 className="library-month-main-title">{monthKey || "전체 책"}</h1>
        </div>

        <section className="library-month-banner">
          <div className="library-month-banner-content">
            <h2 className="library-month-banner-title">이번 달에 만든 이야기</h2>
            <p className="library-month-banner-count">{totalMonthCount}권</p>
          </div>

          <img src={libraryBookImage} alt="books" className="library-month-banner-book" />
        </section>

        <div className="library-month-filter-row">
          <button
            className="library-month-filter-btn"
            onClick={() => setSortType(sortType === "latest" ? "oldest" : "latest")}
          >
            {sortType === "latest" ? "최신순 ▼" : "오래된순 ▲"}
          </button>

          <input
            className="library-month-search"
            placeholder="책 제목 검색"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        {loading ? (
          <p className="library-month-empty">책을 불러오는 중입니다.</p>
        ) : filtered.length === 0 ? (
          <p className="library-month-empty">해당 조건의 책이 없습니다.</p>
        ) : (
          <div className="library-book-grid">
            {filtered.map((book) => (
              <div
                key={book.id}
                className="library-book-card"
                onClick={() => navigate(`/book/${book.id}`)}
              >
                <div
                  className="library-book-cover"
                  style={{ background: book.coverGradient || "#F1D2BC" }}
                />

                <div className="library-book-info">
                  <div className="library-book-meta">
                    <p className="library-book-title">{book.title}</p>

                    <p className="library-book-comment">
                      <img src={commentIcon} alt="comment" className="library-comment-icon" />
                      0개
                    </p>
                  </div>
                </div>

                <button
                  className="library-more-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    setOpenedMenu(openedMenu === book.id ? null : book.id);
                  }}
                >
                  ⋯
                </button>

                {openedMenu === book.id && (
                  <div className="library-delete-popup">
                    <button
                      className="library-delete-action"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(book.id);
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
