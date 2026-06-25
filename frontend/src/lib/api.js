const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

export async function askQuestion(question) {
  const response = await fetch(`${API_BASE_URL}/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || "The copilot could not answer that question.");
  }

  return response.json();
}

export async function fetchHistory() {
  const response = await fetch(`${API_BASE_URL}/query-history`);
  if (!response.ok) {
    return [];
  }
  return response.json();
}

export async function fetchSampleQuestions() {
  const response = await fetch(`${API_BASE_URL}/sample-questions`);
  if (!response.ok) {
    return [];
  }
  return response.json();
}
