/* The one place the application talks to the solver.
 *
 * There was no client before this: nothing under web/src called the server at all. Keeping it in one
 * module means the base URL, the error shape and the request shape are decided once, and a screen
 * never builds a URL of its own. `post()` is that one ladder — fetch, parse, map the status to a
 * kind — so a later change to it (a timeout, a 429, telling an `AbortError` apart from a dead
 * server) lands once rather than needing to be found twice.
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

async function post(path, body, refusedFallback, { fetchImpl = fetch, signal } = {}) {
  let response;
  try {
    response = await fetchImpl(`${API_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal,
    });
  } catch (cause) {
    // No response at all: the server is not running, or the browser blocked the call.
    throw new ApiError("unreachable", `Could not reach the solver at ${API_URL}.`, String(cause));
  }

  let parsed = null;
  try {
    parsed = await response.json();
  } catch {
    parsed = null;
  }

  if (!response.ok) {
    const detail = readDetail(parsed);
    if (response.status === 422) {
      throw new ApiError("refused", detail || refusedFallback, detail);
    }
    throw new ApiError("server", detail || `The solver answered ${response.status}.`, detail);
  }
  return parsed;
}

export function postPlan(request, opts = {}) {
  return post("/plan", request, "The solver refused this load.", opts);
}

/* `manifest` is the flat list of items in the load (`id`, `label`, dimensions, `weight`) and `stops`
 * is the route in delivery order (`id`, `name`) — the shape `POST /constraints` documents in the
 * README (#46), not an assumed one: this was wrong before and sent `{ sentence, manifest: {...} }`,
 * which the real endpoint answers with a 422. */
export function postConstraints(text, manifest, stops, opts = {}) {
  return post("/constraints", { text, manifest, stops }, "QUAI could not accept that sentence.",
    opts);
}

/* `stops` is the round in delivery order, each `{ id, address }` — the address is what the geocoder
 * reads, so `name` is left out rather than sent and ignored. The order is the answer, not a
 * suggestion: `POST /route` drives the stops as given and never reorders them, so this sends them in
 * the order the manifest holds them (#35).
 *
 * A 422 here is usually one address the Base Adresse Nationale could not find, and its detail names
 * which — worth showing rather than replacing with a fallback. */
export function postRoute(stops, departureTime, opts = {}) {
  const body = { stops: stops.map(({ id, address }) => ({ id, address })) };
  if (departureTime) body.departure_time = departureTime;
  return post("/route", body, "The route service refused these stops.", opts);
}
