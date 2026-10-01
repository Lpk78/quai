/* The one place the application talks to the solver.
 *
 * There was no client before this: nothing under web/src called the server at all. Keeping it in one
 * module means the base URL, the error shape and the request shape are decided once, and a screen
 * never builds a URL of its own.
 *
 * The server is `src/server.py`, run with `uvicorn server:app --app-dir src --reload`. In
 * development it is on another origin, which is what the CORS list in that file is for.
 */

export const API_URL =
  (import.meta.env && import.meta.env.VITE_API_URL) || "http://127.0.0.1:8000";

/* A failure the screen can show the operator, rather than a stack trace.
 * `detail` is what the server said; `kind` is how the screen should read it. */
export class ApiError extends Error {
  constructor(kind, message, detail = null) {
    super(message);
    this.name = "ApiError";
    this.kind = kind; // "unreachable" | "refused" | "server"
    this.detail = detail;
  }
}

function readDetail(body) {
  // FastAPI answers a refused request with `detail`: a string from our own HTTPException, or a
  // list of field errors from pydantic. Both become one line the operator can act on.
  const detail = body && body.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) => `${(item.loc || []).slice(1).join(".") || "input"}: ${item.msg}`)
      .join("; ");
  }
  return null;
}

export async function postPlan(request, { fetchImpl = fetch, signal } = {}) {
  let response;
  try {
    response = await fetchImpl(`${API_URL}/plan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
      signal,
    });
  } catch (cause) {
    // No response at all: the server is not running, or the browser blocked the call.
    throw new ApiError("unreachable", `Could not reach the solver at ${API_URL}.`, String(cause));
  }

  let body = null;
  try {
    body = await response.json();
  } catch {
    body = null;
  }

  if (!response.ok) {
    const detail = readDetail(body);
    if (response.status === 422) {
      throw new ApiError("refused", detail || "The solver refused this load.", detail);
    }
    throw new ApiError("server", `The solver answered ${response.status}.`, detail);
  }
  return body;
}
