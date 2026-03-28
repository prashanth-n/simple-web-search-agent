const API_BASE_URL = "http://localhost:8000";

async function parseResponse(response, fallbackMessage) {
  if (response.ok) {
    return response.json();
  }

  let message = fallbackMessage;
  try {
    const payload = await response.json();
    message = payload.detail || message;
  } catch {
    // Ignore JSON parse errors and keep the fallback message.
  }

  throw new Error(message);
}

function apiFetch(path, options = {}) {
  return fetch(`${API_BASE_URL}${path}`, {
    credentials: "include",
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });
}

export async function fetchMe() {
  const response = await apiFetch("/auth/me", { headers: {} });
  return parseResponse(response, "Failed to load current user");
}

export async function signUp(payload) {
  const response = await apiFetch("/auth/signup", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  return parseResponse(response, "Failed to sign up");
}

export async function login(payload) {
  const response = await apiFetch("/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  return parseResponse(response, "Failed to log in");
}

export async function logout() {
  const response = await apiFetch("/auth/logout", {
    method: "POST",
    body: JSON.stringify({}),
  });
  return parseResponse(response, "Failed to log out");
}

export function getGoogleLoginUrl() {
  return `${API_BASE_URL}/auth/google/login`;
}

export async function fetchAgents() {
  const response = await apiFetch("/agents", { headers: {} });
  return parseResponse(response, "Failed to load agents");
}

export async function fetchThreads(agentId) {
  const response = await apiFetch(`/threads?agent_id=${agentId}`, { headers: {} });
  return parseResponse(response, "Failed to load chat threads");
}

export async function createThread(agentId, title) {
  const response = await apiFetch("/threads", {
    method: "POST",
    body: JSON.stringify({ agent_id: Number(agentId), title }),
  });
  return parseResponse(response, "Failed to create chat thread");
}

export async function fetchMessages(threadId) {
  const response = await apiFetch(`/threads/${threadId}/messages`, { headers: {} });
  return parseResponse(response, "Failed to load messages");
}

export async function sendMessage(threadId, content) {
  const response = await apiFetch(`/threads/${threadId}/messages`, {
    method: "POST",
    body: JSON.stringify({ content }),
  });
  return parseResponse(response, "Failed to send message");
}
