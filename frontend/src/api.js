const TOKEN_KEY = "leads-inbox.token";

export function getToken() {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setToken(token) {
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token);
    else localStorage.removeItem(TOKEN_KEY);
  } catch {
    /* storage unavailable: session lasts until reload */
  }
}

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

let onUnauthorized = () => {};
export function setUnauthorizedHandler(fn) {
  onUnauthorized = fn;
}

export async function api(path, { method = "GET", body } = {}) {
  const headers = { "Content-Type": "application/json" };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  let res;
  try {
    res = await fetch(`/api${path}`, { method, headers, body: body ? JSON.stringify(body) : undefined });
  } catch {
    throw new ApiError("Can't reach the API. Check that it's running (python -m backend.app) on port 5050.", 0);
  }
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    // No JSON error from our API: it's down, or another program answered on its port.
    const message =
      data?.error || "Can't reach the API. Check that it's running (python -m backend.app) on port 5050.";
    if (res.status === 401 && path !== "/auth/login") onUnauthorized(message);
    throw new ApiError(message, res.status);
  }
  return data;
}
