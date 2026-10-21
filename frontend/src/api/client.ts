/**
 * Centralized HTTP client for the backend API.
 *
 * This module is the only place that calls `fetch`. Feature code consumes the
 * endpoint functions in `src/api/` instead of performing HTTP requests itself.
 */

/** Error thrown when the API responds with a non-success status code. */
export class ApiError extends Error {
  readonly status: number
  readonly body: unknown

  constructor(message: string, status: number, body: unknown) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.body = body
  }
}

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
 * reverse proxy can route `/api` requests to Django.
 */
export async function apiRequest<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: {
      Accept: 'application/json',
      ...init.headers,
    },
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
