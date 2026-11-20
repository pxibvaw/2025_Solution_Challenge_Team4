// 📌 에피소드 (AI로 생성된 이야기)
export type Episode = {
  id: number;
  title: string;
  preview: string;
  content: string; // 🔥 추가 (본문)
  createdAt: string;
};

// 📌 책 (완성된 콘텐츠)
export type Book = {
  id: number;
  title: string;
  createdAt: string;
  coverColor?: string;
  pages: Page[];
};

// 📌 페이지 (책 내부)
export type Page = {
  id: number;
  chapter: string;
  content: string;
};

// 📌 댓글 (책 상세용)
export type Comment = {
  id: number;
  author: string;
  content: string;
};

// ------------------ mock 데이터 ------------------

// 에피소드 목록
export const mockEpisodes: Episode[] = [
  {
    id: 1,
    title: "달콤했던 호떡의 추억",
    preview: "그날 엄마가 사주신 호떡은 유난히 맛있었다...",
    content: `
그날은 유난히 따뜻한 겨울 오후였다.

엄마와 함께 시장을 걷다가 작은 호떡 가게 앞에 멈춰 섰다.
달콤한 냄새가 코끝을 간질였고,
나는 조심스럽게 말했다.

"하나만 사주면 안 돼?"

엄마는 웃으며 고개를 끄덕였고,
따끈한 호떡을 건네받았을 때
내 마음까지 따뜻해졌다.
    `,
    createdAt: "2026-02-02",
  },
  {
    id: 2,
    title: "설레였던 입학식",
    preview: "새 가방을 메고 처음 학교에 가던 날...",
    content: `
새 가방을 메고 학교에 가던 날,
모든 것이 낯설고 설레었다.

교문 앞에서 한참을 서 있다가
천천히 교실로 들어갔다.

그날의 긴장감과 설렘은
아직도 잊히지 않는다.
    `,
    createdAt: "2026-02-02",
  },
  {
    id: 3,
    title: "초등학교 운동회 날",
    preview: "운동회에서 이어달리기를 했던 기억",
    content: `
운동회 날, 운동장은 사람들로 가득했다.

이어달리기 순서를 기다리며
심장이 빠르게 뛰었다.

바통을 받고 달리던 그 순간,
나는 세상에서 가장 빠른 사람이 된 기분이었다.
    `,
    createdAt: "2026-02-02",
  },
  {
    id: 4,
    title: "가족과 갔던 바다 여행",
    preview: "처음으로 바다를 봤던 날의 기억",
    content: `
처음으로 바다를 보았던 날,
끝없이 펼쳐진 수평선에 놀랐다.

파도 소리를 들으며
가족과 함께 웃던 기억이
아직도 생생하다.
    `,
    createdAt: "2026-02-02",
  },
];

// 책 목록
export const mockBooks: Book[] = [
  {
    id: 1,
    title: "그 시절 추억",
    createdAt: "2026-01-25",
    coverColor: "#F5A623",
    pages: [
      {
        id: 1,
        chapter: "제 5장",
        content:
          "사랑이라는 단어를 떠올리면, 빛바랜 국민학교 운동장이 가장 먼저 그려진다...",
      },
      {
        id: 2,
        chapter: "제 6장",
        content:
          "어느덧 시간이 흘러 우리는 서로 다른 길을 걷게 되었지만...",
      },
    ],
  },
];

// 댓글 (책 상세)
export const mockComments: Comment[] = [
  {
    id: 1,
    author: "아들",
    content: "우와 어릴 적 이야기네요! 정말 소중한 추억이에요 ❤️",
  },
  {
    id: 2,
    author: "사촌",
    content: "국민학교 시절이 생각나네요 😊",
  },
];