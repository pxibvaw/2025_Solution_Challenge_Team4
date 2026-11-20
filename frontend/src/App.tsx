import { Routes, Route, Navigate } from "react-router-dom";

import EntryRouter from "./routes/EntryRouter";

import Login from "./pages/Login/Login";

import Onboarding from "./pages/Onboarding/Onboarding";
import Main from "./pages/Main/Main";
import Interview from "./pages/Interview/Interview";

import EpisodeList from "./pages/Episode/EpisodeList";
import EpisodeDetail from "./pages/Episode/EpisodeDetail";

import Library from "./pages/Library/Library";
import LibraryMonth from "./pages/Library/LibraryMonth";

import GenerateLoading from "./pages/Generate/GenerateLoading";
import GenerateComplete from "./pages/Generate/GenerateComplete";

import BookDetail from "./pages/Book/BookDetail";
import PageViewer from "./pages/Reader/PageViewer";

function App() {
  return (
    <Routes>
      {/* 최초 진입 */}
      <Route path="/" element={<EntryRouter />} />

      {/* 로그인 */}
      <Route path="/login" element={<Login />} />

      {/* 온보딩 */}
      <Route
        path="/onboarding"
        element={<Onboarding />}
      />

      {/* 메인 */}
      <Route path="/main" element={<Main />} />

      {/* 인터뷰 */}
      <Route
        path="/interview"
        element={<Interview />}
      />

      {/* 생성 */}
      <Route
        path="/generate/loading"
        element={<GenerateLoading />}
      />

      <Route
        path="/generate/complete"
        element={<GenerateComplete />}
      />

      {/* 에피소드 */}
      <Route
        path="/episodes"
        element={<EpisodeList />}
      />

      <Route
        path="/episode/:id"
        element={<EpisodeDetail />}
      />

      {/* 서재 */}
      <Route
        path="/library"
        element={<Library />}
      />

      <Route
        path="/library/month"
        element={<LibraryMonth />}
      />

      {/* 책 */}
      <Route
        path="/book/:id"
        element={<BookDetail />}
      />

      {/* 리더 */}
      <Route
        path="/reader/:id"
        element={<PageViewer />}
      />

      {/* fallback */}
      <Route
        path="*"
        element={<Navigate to="/" replace />}
      />
    </Routes>
  );
}

export default App;