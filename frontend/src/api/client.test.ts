import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiError, apiRequest } from '@/api/client'

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

function clearCookies() {
  for (const cookie of document.cookie.split(';')) {
    const name = cookie.split('=')[0]?.trim()
    if (name) {
      document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT`
    }
  }
}

describe('apiRequest', () => {
  afterEach(() => {
    clearCookies()
  })

  it('returns the parsed body for a safe request without a CSRF token', async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ status: 'ok' }))
    vi.stubGlobal('fetch', fetchMock)

    const result = await apiRequest<{ status: string }>('/api/health/')

    expect(result).toEqual({ status: 'ok' })
    expect(fetchMock).toHaveBeenCalledTimes(1)
    const [path, init] = fetchMock.mock.calls[0] as [string, RequestInit]
    expect(path).toBe('/api/health/')
    expect(init.method).toBe('GET')
    expect(new Headers(init.headers).has('X-CSRFToken')).toBe(false)
  })

  it('sends the CSRF cookie with unsafe requests', async () => {
    document.cookie = 'csrftoken=test-token'
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ id: 1 }))
    vi.stubGlobal('fetch', fetchMock)

    await apiRequest('/api/v1/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ username: 'alice', password: 'secret' }),
    })

    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit]
    expect(new Headers(init.headers).get('X-CSRFToken')).toBe('test-token')
  })

  it('requests a CSRF token when the cookie is missing', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse({ csrfToken: 'fresh-token' }))
      .mockResolvedValueOnce(jsonResponse({ id: 1 }))
    vi.stubGlobal('fetch', fetchMock)

    await apiRequest('/api/v1/auth/login/', { method: 'POST' })

    expect(fetchMock).toHaveBeenCalledTimes(2)
    const [csrfPath] = fetchMock.mock.calls[0] as [string]
    expect(csrfPath).toBe('/api/v1/auth/csrf/')
    const [, loginInit] = fetchMock.mock.calls[1] as [string, RequestInit]
    expect(new Headers(loginInit.headers).get('X-CSRFToken')).toBe(
      'fresh-token',
    )
  })

  it('throws ApiError with the response detail for failed requests', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue(jsonResponse({ detail: 'Invalid credentials.' }, 401))
    vi.stubGlobal('fetch', fetchMock)

    await expect(apiRequest('/api/v1/auth/login/')).rejects.toMatchObject({
      name: 'ApiError',
      message: 'Invalid credentials.',
      status: 401,
      body: { detail: 'Invalid credentials.' },
    })
    await expect(apiRequest('/api/v1/auth/login/')).rejects.toBeInstanceOf(
      ApiError,
    )
  })

  it('returns undefined for 204 No Content', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(new Response(null, { status: 204 })),
    )

    await expect(apiRequest('/api/v1/auth/logout/')).resolves.toBeUndefined()
  })
})
