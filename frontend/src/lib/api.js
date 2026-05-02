const API_BASE = import.meta.env.VITE_API_URL || "/api";

export async function summarize(url, maxComments = 150) {
  const endpoint = API_BASE === "/api" ? "/api/summarize" : `${API_BASE}/summarize`;

  const resp = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, max_comments: maxComments }),
  });

  const data = await resp.json();
  if (!resp.ok) throw new Error(data.detail ?? "Something went wrong. Please try again.");
  return data;
}
