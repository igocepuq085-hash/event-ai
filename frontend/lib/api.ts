const CLIENT_API_PREFIX = "/api/backend";
const SERVER_API_URL =
  process.env.BACKEND_API_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  "http://127.0.0.1:8000";

export type Submission = {
  id: string;
  created_at: string;
  questionnaire: Record<string, string>;
  program?: Record<string, unknown>;
  generation?: {
    status: string;
    stage?: string;
    message?: string;
    error?: string;
    updated_at?: string;
  };
};

export type QuestionnairePayload = Record<string, string>;

export async function fetchApi<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${CLIENT_API_PREFIX}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `API error: ${response.status}`);
  }

  const contentType = response.headers.get("content-type") || "";
  if (!contentType.includes("application/json")) {
    return (await response.blob()) as T;
  }

  return response.json() as Promise<T>;
}

export { CLIENT_API_PREFIX, SERVER_API_URL };
