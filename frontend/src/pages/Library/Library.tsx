// src/pages/Library/Library.tsx

import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { deleteBook, fetchBooks, type Book } from "../../api/doran";
import BottomNav from "../../components/BottomNav";

import "../../styles/Library.css";
import commentIcon from "../../assets/icon_comment.png";

export default function Library() {
  const navigate = useNavigate();

  const [books, setBooks] = useState<Book[]>([]);
  const [search, setSearch] = useState("");
  const [openedMenu, setOpenedMenu] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function loadBooks() {
      try {
        const data = await fetchBooks();
        if (!cancelled) setBooks(data);
      } catch (e) {
        console.error("Book list load failed:", e);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadBooks();

    return () => {
      cancelled = true;
    };
  }, []);

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

  const filteredBooks = useMemo(() => {
    return books.filter((book) =>
      book.title.toLowerCase().includes(search.toLowerCase())
    );
  }, [books, search]);

  const grouped = useMemo(() => {
    const map: Record<string, Book[]> = {};

    filteredBooks.forEach((book) => {
      const date = new Date(book.createdAt);
      const key = `${date.getFullYear()}년 ${date.getMonth() + 1}월`;
      if (!map[key]) map[key] = [];
      map[key].push(book);
    });

    return map;
  }, [filteredBooks]);

  const goMonth = (monthKey: string) => {
    navigate("/library/month", { state: { monthKey } });
  };

  return (
    <>
      <main className="library-page">
        <div className="library-header">
          <h1 className="library-title">내 서재</h1>

          <div className="library-header-actions">
            <button className="library-share-btn" onClick={() => alert("공유 기능")}>공유</button>
          </div>
        </div>

        <input
          className="library-search"
          placeholder="책 제목 검색"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        {loading ? (
          <p className="library-month-empty">서재를 불러오는 중입니다.</p>
        ) : Object.keys(grouped).length === 0 ? (
          <p className="library-month-empty">아직 저장된 책이 없습니다.</p>
        ) : (
          Object.entries(grouped).map(([month, list]) => (
            <section key={month} className="library-section">
              <div className="library-month-header" onClick={() => goMonth(month)}>
                <div>
                  <h2 className="library-month-title">{month} &gt;</h2>
                  <p className="library-month-count">{list.length}권</p>
                </div>
              </div>

              <div className="library-book-grid">
                {list.slice(0, 2).map((book) => (
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
            </section>
          ))
        )}
      </main>

      <BottomNav />
    </>
  );
}
