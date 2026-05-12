export type InterviewState =
    | "IDLE"
    | "LISTENING"
    | "RECORDING"
    | "PROCESSING"
    | "ERROR"
    | "ENDED";

export interface Turn {
    userText: string;
    aiReply: string;
    nextQuestion: string;
}