const API_BASE_URL = "http://localhost:8000";

export async function research(query) {
  const response = await fetch(
    `${API_BASE_URL}/research?query=${encodeURIComponent(query)}`,
  );

  if (!response.ok) {
    let message = "Failed to fetch research results";
    try {
      const payload = await response.json();
      message = payload.detail || message;
    } catch {
      // Ignore JSON parse errors and keep the default message.
    }
    throw new Error(message);
  }

  return response.json();
}
