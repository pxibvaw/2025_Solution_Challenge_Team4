// src/pages/Login/Login.tsx

import { useNavigate } from "react-router-dom";

import "../../styles/Login.css";

import kakaoIcon from "../../assets/kakao.png";

export default function Login() {
  const navigate = useNavigate();

  // 🔥 나중에 백엔드 연결용
  const handleKakaoLogin = async () => {
    try {
      /*
      TODO:
      백엔드 카카오 로그인 연결 예정

      예시:
      window.location.href =
        "http://localhost:8080/oauth/kakao";
      */

      navigate("/main");
    } catch (error) {
      console.error(
        "Kakao Login Error:",
        error
      );
    }
  };

  return (
    <main className="login-page">
      {/* 로고 */}
      <section className="login-logo-section">
        <h1 className="login-logo">
          DORAN
        </h1>

        <p className="login-subtitle">
          말로 나눈 대화를 기억으로
        </p>
      </section>

      {/* 하단 */}
      <section className="login-bottom-section">
        {/* 카카오 로그인 */}
        <button
          type="button"
          className="kakao-login-btn"
          onClick={handleKakaoLogin}
        >
          <img
            src={kakaoIcon}
            alt="kakao"
            className="kakao-icon-img"
          />

          <span>
            카카오로 계속하기
          </span>
        </button>

        {/* 하단 링크 */}
        <div className="login-links">
          <button type="button">
            아이디 로그인
          </button>

          <span>·</span>

          <button type="button">
            회원가입
          </button>
        </div>
      </section>
    </main>
  );
}