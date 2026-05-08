export interface TurnRequest {
    sessionId: string;
    userId: number;
    requestId: string;
    input: {
    mode: "TEXT";
    userText: string;
    };
    context: {
    speechLevel?: "HONORIFIC" | "CASUAL";
    ageGroup?: string;
    coreValues?: string[];
    extraValue?: string;
    };
    clientTs: string;
}