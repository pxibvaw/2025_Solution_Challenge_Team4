export interface StartInterviewResponse {
    sessionId: string;
    }

    export const startInterview = async (): Promise<StartInterviewResponse> => {
    return new Promise((resolve) => {
        setTimeout(() => {
        resolve({
            sessionId: "mock-session-" + Date.now(),
        });
        }, 500);
    });
};