/* Minimal client for POST /constraints (#19), which is not built yet. SA-14a adds a
   VITE_API_URL-based client and /app/plan; this covers the one call Dictate.jsx needs until that
   lands, so it can be replaced without changing the call site. The fallback origin matches the one
   vite.config.js and the README already assume for the FastAPI dev server. */
const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

export async function postConstraints(sentence, manifest) {
  const response = await fetch(`${API_URL}/constraints`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sentence, manifest }),
  });
  if (!response.ok) {
    throw new Error(`the server answered ${response.status}`);
  }
  return response.json();
}
