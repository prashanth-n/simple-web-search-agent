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

export async function fetchAgents() {
  const response = await fetch(`${API_BASE_URL}/agents`);
  return parseResponse(response, "Failed to load agents");
}

export async function research(query, agentId) {
  const response = await fetch(
    `${API_BASE_URL}/research?query=${encodeURIComponent(query)}&agent_id=${agentId}`,
  );

  return parseResponse(response, "Failed to fetch research results");
}
