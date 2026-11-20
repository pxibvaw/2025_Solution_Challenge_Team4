// src/pages/Book/BookDetail.tsx

import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { fetchBook, type Book } from "../../api/doran";
import BottomNav from "../../components/BottomNav";

import backIcon from "../../assets/icon_back.png";

import "../../styles/BookDetail.css";

export default function BookDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [book, setBook] = useState<Book | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function loadBook() {
      if (!id) {
        setLoading(false);
        return;
      }

      try {
        const data = await fetchBook(id);
        if (!cancelled) setBook(data);
      } catch (e) {
        console.error("Book detail load failed:", e);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadBook();

    return () => {
      cancelled = true;
    };
  }, [id]);

  if (loading) {
    return <div className="book-detail-empty">책을 불러오는 중입니다.</div>;
  }

  if (!book) {
    return <div className="book-detail-empty">책을 찾을 수 없습니다.</div>;
  }

  const formattedDate = new Date(book.createdAt).toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  const handleRead = () => {
    navigate(`/reader/${book.id}`);
  };

  return (
    <>
      <main className="book-detail-page">
        <header className="book-detail-header">
          <div className="book-detail-left">
            <button className="book-detail-back" onClick={() => navigate(-1)}>
              <img src={backIcon} alt="back" className="book-detail-back-icon" />
            </button>

            <h1 className="book-detail-top-title">{book.title}</h1>
          </div>

          <div className="book-detail-actions">
            <button className="book-detail-action-btn" onClick={() => alert("편집")}>편집</button>
            <button className="book-detail-action-btn" onClick={() => alert("공유")}>공유</button>
          </div>
        </header>

        <section className="book-detail-cover-section">
          <div className="book-detail-book-card">
            <div
              className="book-detail-book-cover"
              style={{ background: book.coverGradient || "#F1D2BC" }}
            />
          </div>

          <h2 className="book-detail-title">{book.title}</h2>
          <p className="book-detail-date">{formattedDate}</p>
        </section>

        <div className="book-detail-divider"></div>

        <section className="book-detail-comment-section">
          <h3 className="book-detail-comment-title">댓글</h3>
          <div className="book-detail-comment-list">
            <div className="book-detail-empty">아직 등록된 댓글이 없습니다.</div>
          </div>
        </section>

        <div className="book-detail-read-bottom">
          <button className="book-detail-read-btn" onClick={handleRead}>읽어보기</button>
        </div>
      </main>

      <BottomNav />
    </>
  );
}
