import { startInterviewSession } from "./doran";

export interface StartInterviewResponse {
  sessionId: string;
}

export const startInterview = async (): Promise<StartInterviewResponse> => {
  return startInterviewSession();
};
