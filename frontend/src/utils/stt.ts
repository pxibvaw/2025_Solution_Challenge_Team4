// frontend/src/utils/stt.ts
//
// 음성 녹음 + AI 서버 /stt 업로드 헬퍼.
//
// 흐름:
//   startRecording()  → 마이크 권한 + MediaRecorder 시작
//   stopRecording()   → 녹음 중단 + Blob 반환 + 마이크 트랙 해제
//   transcribeAudio() → Blob을 AI /stt에 multipart 업로드 → text 반환
//
// BE를 경유하지 않고 FE → AI 직접 호출 (AI 서버 CORS 허용 설정 필요).
// 이유: BE를 거치면 turn 흐름에 multipart 라우터 + 오디오 DTO를 새로 만들어야 하므로
//      v1에서는 FE→AI 직호출 + 텍스트 결과로 기존 /interview/turn 그대로 사용.

// AI 서버 베이스 URL. .env.local의 VITE_AI_BASE_URL로 오버라이드 가능.
const AI_BASE_URL =
  import.meta.env.VITE_AI_BASE_URL ?? "http://localhost:8000";

// MediaRecorder + 수집 chunks + 마이크 stream을 한 묶음으로 다루기 위한 핸들.
// 컴포넌트는 이 객체만 ref로 들고 있으면 됨.
export type RecorderHandle = {
  recorder: MediaRecorder;
  chunks: Blob[];
  stream: MediaStream;
};

/**
 * 마이크 권한 요청 + 녹음 시작.
 *
 * @throws Error - 브라우저 미지원 / 권한 거부 / 디바이스 없음
 */
export async function startRecording(): Promise<RecorderHandle> {
  if (!navigator.mediaDevices?.getUserMedia) {
    throw new Error("이 브라우저는 음성 녹음을 지원하지 않아요.");
  }

  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

  // 브라우저별 지원 포맷이 다르므로 우선순위대로 시도.
  // Chrome/Edge → webm/opus, Safari → mp4(aac), Firefox → ogg/opus
  // ffmpeg는 헤더로 포맷 판단하므로 어느 쪽이든 AI 서버에서 처리됨.
  const candidates = [
    "audio/webm;codecs=opus",
    "audio/webm",
    "audio/mp4",
    "audio/ogg;codecs=opus",
  ];
  let mimeType = "";
  for (const c of candidates) {
    if (MediaRecorder.isTypeSupported(c)) {
      mimeType = c;
      break;
    }
  }

  const recorder = mimeType
    ? new MediaRecorder(stream, { mimeType })
    : new MediaRecorder(stream);

  const chunks: Blob[] = [];
  recorder.ondataavailable = (e) => {
    if (e.data && e.data.size > 0) chunks.push(e.data);
  };

  recorder.start();

  return { recorder, chunks, stream };
}

/**
 * 녹음 중단 → Blob 반환.
 *
 * recorder.stop()은 비동기 — 마지막 dataavailable + onstop 콜백을 기다려야 함.
 * 마이크 트랙은 반드시 해제. 안 하면 브라우저 탭에 빨간 점이 계속 떠있음.
 */
export async function stopRecording(handle: RecorderHandle): Promise<Blob> {
  return new Promise((resolve, reject) => {
    handle.recorder.onstop = () => {
      try {
        handle.stream.getTracks().forEach((t) => t.stop());

        const blob = new Blob(handle.chunks, {
          type: handle.recorder.mimeType || "audio/webm",
        });
        resolve(blob);
      } catch (e) {
        reject(e);
      }
    };

    handle.recorder.onerror = (e) => reject(e);

    try {
      handle.recorder.stop();
    } catch (e) {
      reject(e);
    }
  });
}

/**
 * 녹음 Blob을 AI /stt에 multipart로 업로드 → 텍스트 반환.
 *
 * 인식이 비어있어도 빈 문자열을 반환 (AI 서버에서 그렇게 보냄).
 * 네트워크/서버 오류는 throw — 호출부에서 alert/재시도 처리.
 */
export async function transcribeAudio(blob: Blob): Promise<string> {
  const form = new FormData();

  // 확장자는 ffmpeg가 헤더로 판단하므로 임의값 OK. 디버깅 편의상 mimeType 반영.
  const ext = blob.type.includes("webm")
    ? "webm"
    : blob.type.includes("ogg")
    ? "ogg"
    : blob.type.includes("mp4")
    ? "mp4"
    : "audio";
  form.append("audio", blob, `recording.${ext}`);

  const res = await fetch(`${AI_BASE_URL}/stt`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    let detail = `STT 요청 실패 (${res.status})`;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      // body가 JSON이 아닐 수도 있음 — 기본 메시지 유지
    }
    throw new Error(detail);
  }

  const data: { text?: string } = await res.json();
  return (data.text ?? "").trim();
}
