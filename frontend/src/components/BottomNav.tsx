// src/components/BottomNav.tsx

import {
  useLocation,
  useNavigate,
} from "react-router-dom";

import "../styles/navigation.css";

import homeIcon from "../assets/icon_home_black.png";
import homeLightIcon from "../assets/icon_home_light.png";

import docIcon from "../assets/icon_doc.png";
import docLightIcon from "../assets/icon_doc_light.png";

import bookDarkIcon from "../assets/icon_book.png";
import bookLightIcon from "../assets/icon_book_light.png";

export default function BottomNav() {
  const navigate = useNavigate();

  const location = useLocation();

  const currentPath =
    location.pathname;

  /* =========================
     활성 상태
  ========================= */

  const isHome =
    currentPath === "/main";

  /* 🔥 EpisodeDetail 포함 */

  const isEpisodes =
    currentPath === "/episodes" ||
    currentPath.startsWith(
      "/episode"
    );

  /* 🔥 BookDetail 포함 */

  const isLibrary =
    currentPath.startsWith(
      "/library"
    ) ||
    currentPath.startsWith(
      "/book"
    );

  return (
    <nav className="bottom-nav">
      {/* 홈 */}

      <button
        className={`nav-item ${
          isHome ? "active" : ""
        }`}
        onClick={() =>
          navigate("/main")
        }
      >
        <img
          src={
            isHome
              ? homeLightIcon
              : homeIcon
          }
          className="nav-icon"
          alt="home"
        />

        <span className="nav-text">
          홈
        </span>
      </button>

      {/* 에피소드 */}

      <button
        className={`nav-item ${
          isEpisodes
            ? "active"
            : ""
        }`}
        onClick={() =>
          navigate("/episodes")
        }
      >
        <img
          src={
            isEpisodes
              ? docLightIcon
              : docIcon
          }
          className="nav-icon"
          alt="episodes"
        />

        <span className="nav-text">
          에피소드
        </span>
      </button>

      {/* 내 서재 */}

      <button
        className={`nav-item ${
          isLibrary
            ? "active"
            : ""
        }`}
        onClick={() =>
          navigate("/library")
        }
      >
        <img
          src={
            isLibrary
              ? bookLightIcon
              : bookDarkIcon
          }
          className="nav-icon"
          alt="library"
        />

        <span className="nav-text">
          내 서재
        </span>
      </button>
    </nav>
  );
}