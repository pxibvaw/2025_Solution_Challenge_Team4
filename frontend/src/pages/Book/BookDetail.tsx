// src/pages/Book/BookDetail.tsx

import {
  useNavigate,
  useParams,
} from "react-router-dom";

import BottomNav from "../../components/BottomNav";

import heartIcon from "../../assets/icon_heart.png";
import commentIcon from "../../assets/icon_comment2.png";
import backIcon from "../../assets/icon_back.png";

import "../../styles/BookDetail.css";

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

  pages?: {
    id: number;

    chapter: string;

    content: string;

    pageNumber: number;
  }[];
};

/* =========================
   mock 댓글
========================= */

const mockComments = [
  {
    id: 1,
    author: "아",
    fullName: "아들",
    content:
      "우와 어릴 적이네요! 정말 소중한 추억이에요 ✨",
    time: "5분전",
  },

  {
    id: 2,
    author: "사",
    fullName: "사촌",
    content:
      "감나무집 살때면 좋았지",
    time: "5분전",
  },
];

export default function BookDetail() {
  const { id } = useParams();

  const navigate = useNavigate();

  const bookId = Number(id);

  const books: Book[] = JSON.parse(
    localStorage.getItem("books") ||
      "[]"
  );

  const book = books.find(
    (b) => b.id === bookId
  );

  if (!book) {
    return (
      <div className="book-detail-empty">
        책을 찾을 수 없습니다.
      </div>
    );
  }

  /* =========================
     날짜 포맷
  ========================= */

  const formattedDate = new Date(
    book.createdAt
  ).toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  /* =========================
     읽어보기
  ========================= */

  const handleRead = () => {
    navigate(`/reader/${book.id}`);
  };

  return (
    <>
      <main className="book-detail-page">
        {/* 상단 */}

        <header className="book-detail-header">
          <div className="book-detail-left">
            <button
              className="book-detail-back"
              onClick={() => navigate(-1)}
            >
              <img
                src={backIcon}
                alt="back"
                className="book-detail-back-icon"
              />
            </button>

            <h1 className="book-detail-top-title">
              {book.title}
            </h1>
          </div>

          <div className="book-detail-actions">
            <button
              className="book-detail-action-btn"
              onClick={() =>
                alert("편집")
              }
            >
              편집
            </button>

            <button
              className="book-detail-action-btn"
              onClick={() =>
                alert("공유")
              }
            >
              공유
            </button>
          </div>
        </header>

        {/* 책 */}

        <section className="book-detail-cover-section">
          <div className="book-detail-book-card">
            <div
              className="book-detail-book-cover"
              style={{
                background:
                  book.coverGradient,
              }}
            ></div>
          </div>

          <h2 className="book-detail-title">
            {book.title}
          </h2>

          <p className="book-detail-date">
            {formattedDate}
          </p>
        </section>

        {/* divider */}

        <div className="book-detail-divider"></div>

        {/* 댓글 */}

        <section className="book-detail-comment-section">
          <h3 className="book-detail-comment-title">
            댓글
          </h3>

          <div className="book-detail-comment-list">
            {mockComments.map((c) => (
              <div
                key={c.id}
                className="book-detail-comment-card"
              >
                <div className="book-detail-comment-top">
                  <div className="book-detail-comment-user">
                    <div className="book-detail-comment-avatar">
                      {c.author}
                    </div>

                    <div>
                      <div className="book-detail-comment-name-row">
                        <span className="book-detail-comment-name">
                          {c.fullName}
                        </span>

                        <span className="book-detail-comment-time">
                          {c.time}
                        </span>
                      </div>

                      <p className="book-detail-comment-content">
                        {c.content}
                      </p>
                    </div>
                  </div>

                  {/* 아이콘 */}

                  <div className="book-detail-comment-icons">
                    <img
                      src={heartIcon}
                      alt="heart"
                      className="book-detail-icon"
                    />

                    <img
                      src={commentIcon}
                      alt="comment"
                      className="book-detail-icon"
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* 읽어보기 */}

        <div className="book-detail-read-bottom">
          <button
            className="book-detail-read-btn"
            onClick={handleRead}
          >
            읽어보기
          </button>
        </div>
      </main>

      {/* 네비게이션 */}

      <BottomNav />
    </>
  );
}