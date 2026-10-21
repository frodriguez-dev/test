import { apiRequest } from '@/api/client'
import type { Login, User } from '@/types/api'

/**
 * Authenticate with a username and password and start a session.
 *
 * The session cookie is set by the backend; no token is stored in the browser.
 *
 * @param credentials - Username and password accepted by the login endpoint.
 * @returns The authenticated user.
 */
export function login(credentials: Login): Promise<User> {
  return apiRequest<User>('/api/v1/auth/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials),
  })
}

/**
 * End the current session.
 *
 * @returns Nothing when the session has been cleared.
 */
export function logout(): Promise<void> {
  return apiRequest<void>('/api/v1/auth/logout/', { method: 'POST' })
}

/**
 * Fetch the user associated with the current session.
 *
 * @param signal - Optional signal used to abort the request.
 * @returns The authenticated user.
 */
export function getCurrentUser(signal?: AbortSignal): Promise<User> {
  return apiRequest<User>('/api/v1/auth/me/', { signal })
}
