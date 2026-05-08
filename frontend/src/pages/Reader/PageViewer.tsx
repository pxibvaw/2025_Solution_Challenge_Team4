import {
  useParams,
  useNavigate,
  useLocation,
} from "react-router-dom";

import {
  useState,
  useRef,
  useEffect,
} from "react";

import { mockBooks } from "../../mock/data";

import backIcon from "../../assets/icon_back.png";

import searchIcon from "../../assets/icon_search.png";
import fluentIcon from "../../assets/icon_fluent.png";
import markIcon from "../../assets/icon_mark.png";
import menuIcon from "../../assets/icon_menu.png";

import "../../styles/PageViewer.css";

type Page = {
  id: number;
  chapter: string;
  content: string;
  pageNumber: number;
};

type Book = {
  id: number;
  title: string;
  createdAt: string;
  pages: Page[];
};

export default function PageViewer() {
  const { id } = useParams();

  const navigate = useNavigate();

  const location = useLocation();

  const bookId = Number(id);

  const previewBook =
    location.state?.previewBook;

  const storedBooks = JSON.parse(
    localStorage.getItem("books") ||
      "[]"
  );

  const allBooks = [
    ...storedBooks,
    ...mockBooks,
  ];

  const book: Book =
    previewBook ||
    allBooks.find(
      (b) => b.id === bookId
    );

  const [pageIndex, setPageIndex] =
    useState(0);

  const [uiOpen, setUiOpen] =
    useState(false);

  const [fontSize, setFontSize] =
    useState(18);

  const [bookmarked, setBookmarked] =
    useState(false);

  const touchStartX =
    useRef<number>(0);

  const handlePrev = () => {
    if (pageIndex > 0) {
      setPageIndex((p) => p - 1);
    }
  };

  const handleNext = () => {
    if (
      book &&
      pageIndex <
        book.pages.length - 1
    ) {
      setPageIndex((p) => p + 1);
    }
  };

  const handleTouchStart = (
    e: React.TouchEvent
  ) => {
    touchStartX.current =
      e.touches[0].clientX;
  };

  const handleTouchEnd = (
    e: React.TouchEvent
  ) => {
    const endX =
      e.changedTouches[0].clientX;

    const diff =
      touchStartX.current - endX;

    if (diff > 60) {
      handleNext();
    }

    if (diff < -60) {
      handlePrev();
    }
  };

  useEffect(() => {
    const handleKeyDown = (
      e: KeyboardEvent
    ) => {
      if (e.key === "ArrowLeft") {
        if (pageIndex > 0) {
          setPageIndex(
            (p) => p - 1
          );
        }
      }

      if (
        e.key === "ArrowRight"
      ) {
        if (
          book &&
          pageIndex <
            book.pages.length -
              1
        ) {
          setPageIndex(
            (p) => p + 1
          );
        }
      }

      if (e.key === "Escape") {
        setUiOpen(false);
      }
    };

    window.addEventListener(
      "keydown",
      handleKeyDown
    );

    return () => {
      window.removeEventListener(
        "keydown",
        handleKeyDown
      );
    };
  }, [pageIndex, book]);

  if (!book) {
    return (
      <div className="page-viewer-page">
        책을 찾을 수 없습니다
      </div>
    );
  }

  const page =
    book.pages?.[pageIndex];

  return (
    <main className="page-viewer-page">
      <div
        className={`page-viewer-reader ${
          uiOpen ? "open" : ""
        }`}
        onTouchStart={
          handleTouchStart
        }
        onTouchEnd={handleTouchEnd}
      >
        <div
          className="page-viewer-click-left"
          onClick={handlePrev}
        ></div>

        <div
          className="page-viewer-click-center"
          onClick={() =>
            setUiOpen((prev) => !prev)
          }
        ></div>

        <div
          className="page-viewer-click-right"
          onClick={handleNext}
        ></div>

        <div
          className={`page-viewer-topbar ${
            uiOpen ? "show" : ""
          }`}
        >
          <button
            className="page-viewer-back-btn"
            onClick={(e) => {
              e.stopPropagation();

              navigate(-1);
            }}
          >
            <img
              src={backIcon}
              alt="back"
              className="page-viewer-back-icon"
            />
          </button>

          <div className="page-viewer-top-center">
            <p className="page-viewer-top-chapter">
              {page.chapter}
            </p>

            <p className="page-viewer-top-page">
              {pageIndex + 1}/
              {book.pages.length}
            </p>
          </div>

          <button
            className="page-viewer-bookmark"
            onClick={(e) => {
              e.stopPropagation();

              setBookmarked(
                !bookmarked
              );
            }}
          >
            <img
              src={markIcon}
              alt="mark"
              className={`page-viewer-top-icon ${
                bookmarked
                  ? "active"
                  : ""
              }`}
            />
          </button>
        </div>

        <div className="page-viewer-content-area">
          <h2 className="page-viewer-chapter">
            {page.chapter}
          </h2>

          <div className="page-viewer-content">
            {(page.content || "")
              .split("\n")
              .filter(
                (line) =>
                  line.trim() !== ""
              )
              .map((line, idx) => (
                <p
                  key={idx}
                  className="page-viewer-text"
                  style={{
                    fontSize:
                      `${fontSize}px`,
                  }}
                >
                  {line}
                </p>
              ))}
          </div>
        </div>

        <div
          className={`page-viewer-bottombar ${
            uiOpen ? "show" : ""
          }`}
        >
          <button
            onClick={(e) => {
              e.stopPropagation();

              alert(
                "검색 기능 준비중입니다"
              );
            }}
          >
            <img
              src={searchIcon}
              alt="search"
              className="page-viewer-bottom-icon"
            />
          </button>

          <button
            onClick={(e) => {
              e.stopPropagation();

              alert(
                "음성 읽기 기능 준비중입니다"
              );
            }}
          >
            <img
              src={fluentIcon}
              alt="tts"
              className="page-viewer-bottom-icon"
            />
          </button>

          <button
            className="page-viewer-font-btn"
            onClick={(e) => {
              e.stopPropagation();

              setFontSize(
                (prev) =>
                  prev >= 24
                    ? 18
                    : prev + 2
              );
            }}
          >
            가가
          </button>

          <button
            onClick={(e) => {
              e.stopPropagation();

              alert(
                "메뉴 기능 준비중입니다"
              );
            }}
          >
            <img
              src={menuIcon}
              alt="menu"
              className="page-viewer-bottom-icon"
            />
          </button>
        </div>
      </div>
    </main>
  );
}