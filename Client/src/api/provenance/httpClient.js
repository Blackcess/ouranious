import { ApiError } from "./errors";

const configuredBase = process.env.REACT_APP_KB_API_BASE_URL;
const API_BASE_URL = `${(configuredBase || "http://localhost:8000").replace(/\/$/, "")}/api/v1`;

export async function request(path, { method = "GET", body, signal, acceptStatuses = [] } = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 20000);
  if (signal) signal.addEventListener("abort", () => controller.abort(), { once: true });
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method,
      signal: controller.signal,
      headers: body === undefined ? { Accept: "application/json" } : { Accept: "application/json", "Content-Type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    const raw = await response.text();
    let payload = null;
    if (raw) {
      try { payload = JSON.parse(raw); }
      catch { if (response.ok || acceptStatuses.includes(response.status)) throw new ApiError("The server returned an unreadable response.", { status: response.status }); }
    }
    if (!response.ok && !acceptStatuses.includes(response.status)) {
      const detail = payload && typeof payload === "object" ? payload.detail : null;
      const message = typeof detail === "string" ? detail : `Request failed (${response.status}).`;
      throw new ApiError(message, { status: response.status, detail, code: payload?.code, payload });
    }
    if (acceptStatuses.includes(response.status) && payload === null) {
      throw new ApiError("The server returned an empty response for a structured result.", { status: response.status });
    }
    return { status: response.status, data: payload };
  } catch (error) {
    if (error instanceof ApiError) throw error;
    if (error?.name === "AbortError") throw new ApiError("The request timed out or was cancelled.");
    throw new ApiError("Could not reach the Knowledge Base API. Check the API URL and connection.");
  } finally { clearTimeout(timeout); }
}

export { API_BASE_URL };
