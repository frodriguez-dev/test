/**
 * Centralized HTTP client for the backend API.
 *
 * This module is the only place that calls `fetch`. Feature code consumes the
 * endpoint functions in `src/api/` instead of performing HTTP requests itself.
 */

/** Error thrown when the API responds with a non-success status code. */
export class ApiError extends Error {
  /** HTTP status code returned by the API. */
  readonly status: number
  /** Parsed response body, or `null` when it could not be parsed. */
  readonly body: unknown

  /**
   * Create an API error from the response status and body.
   *
   * @param message - Human-readable error message.
   * @param status - HTTP status code returned by the API.
   * @param body - Parsed response body, if available.
   */
  constructor(message: string, status: number, body: unknown) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.body = body
  }
}

/** Name of the cookie Django uses to store the CSRF secret. */
const CSRF_COOKIE_NAME = 'csrftoken'

/** HTTP methods that do not require a CSRF token. */
const SAFE_METHODS = new Set(['GET', 'HEAD', 'OPTIONS', 'TRACE'])

/**
 * Read a cookie value from `document.cookie`.
 *
 * @param name - Cookie name.
 * @returns The decoded cookie value, or `null` when it is absent.
 */
function readCookie(name: string): string | null {
  const prefix = `${name}=`

  for (const entry of document.cookie.split(';')) {
    const cookie = entry.trim()
    if (cookie.startsWith(prefix)) {
      return decodeURIComponent(cookie.slice(prefix.length))
    }
  }

  return null
}

/**
 * Return the CSRF token required by unsafe requests.
 *
 * Reads the token from Django's CSRF cookie and asks the backend to set it when
 * it is missing. The cookie is re-read on every call because Django rotates the
 * token when a session starts or ends.
 *
 * @returns The CSRF token.
 * @throws {@link ApiError} When the token cannot be obtained.
 */
async function getCsrfToken(): Promise<string> {
  const cookieToken = readCookie(CSRF_COOKIE_NAME)
  if (cookieToken) {
    return cookieToken
  }

  const response = await fetch('/api/v1/auth/csrf/', {
    headers: { Accept: 'application/json' },
    credentials: 'same-origin',
  })
  const body: unknown = await response.json().catch(() => null)

  if (!response.ok) {
    throw new ApiError(
      response.statusText || `Request failed with status ${response.status}`,
      response.status,
      body,
    )
  }

  if (body && typeof body === 'object' && 'csrfToken' in body) {
    const { csrfToken } = body
    if (typeof csrfToken === 'string' && csrfToken.trim()) {
      return csrfToken
    }
  }

  const fallback = readCookie(CSRF_COOKIE_NAME)
  if (fallback) {
    return fallback
  }

  throw new ApiError('Unable to obtain a CSRF token.', response.status, body)
}

/**
 * Extract a human-readable message from an API error body.
 *
 * Supports the `detail` and `message` string fields used by Django REST
 * Framework and falls back when neither is present.
 *
 * @param body - Parsed response body.
 * @param fallback - Message to use when the body has no usable message.
 * @returns The message from the body, or the fallback.
 */
function getErrorMessage(body: unknown, fallback: string): string {
  if (body && typeof body === 'object') {
    if (
      'detail' in body &&
      typeof body.detail === 'string' &&
      body.detail.trim()
    ) {
      return body.detail
    }
    if (
      'message' in body &&
      typeof body.message === 'string' &&
      body.message.trim()
    ) {
      return body.message
    }
  }

  return fallback
}

/**
 * Perform a JSON request against the API and return the parsed response.
 *
 * Paths are relative so the Vite dev proxy and, in production, the same-origin
 * reverse proxy can route `/api` requests to Django. Unsafe requests include the
 * `X-CSRFToken` header expected by Django's session authentication.
 *
 * @typeParam T - Expected shape of the parsed response body.
 * @param path - API path relative to the current origin.
 * @param init - Optional `fetch` options, such as method, body, or signal.
 * @returns The parsed JSON response, or `undefined` for `204 No Content`.
 * @throws {@link ApiError} When the API responds with a non-success status.
 */
export async function apiRequest<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const method = (init.method ?? 'GET').toUpperCase()
  const headers = new Headers(init.headers)
  headers.set('Accept', 'application/json')

  if (!SAFE_METHODS.has(method)) {
    headers.set('X-CSRFToken', await getCsrfToken())
  }

  const response = await fetch(path, {
    ...init,
    method,
    headers,
    credentials: 'same-origin',
  })

  if (!response.ok) {
    const body: unknown = await response.json().catch(() => null)
    throw new ApiError(
      getErrorMessage(
        body,
        response.statusText || `Request failed with status ${response.status}`,
      ),
      response.status,
      body,
    )
  }

  if (response.status === 204) {
    return undefined as T
  }

  return (await response.json()) as T
}
