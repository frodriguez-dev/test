import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import {
  getCurrentUser,
  login as loginRequest,
  logout as logoutRequest,
} from '@/api/auth'
import { ApiError } from '@/api/client'
import { AuthProvider } from '@/features/auth/AuthProvider'
import { useAuth } from '@/features/auth/useAuth'
import type { User } from '@/types/api'

vi.mock('@/api/auth', () => ({
  getCurrentUser: vi.fn(),
  login: vi.fn(),
  logout: vi.fn(),
}))

const alice: User = {
  id: 1,
  username: 'alice',
  email: 'alice@example.com',
  first_name: 'Alice',
  last_name: '',
}

function AuthHarness() {
  const { state, login, logout } = useAuth()

  return (
    <div>
      <p data-testid="status">{state.status}</p>
      {state.status === 'authenticated' && (
        <p data-testid="username">{state.user.username}</p>
      )}
      <button onClick={() => void login({ username: 'alice', password: 'pw' })}>
        Log in
      </button>
      <button onClick={() => void logout()}>Log out</button>
    </div>
  )
}

function renderProvider() {
  return render(
    <AuthProvider>
      <AuthHarness />
    </AuthProvider>,
  )
}

describe('AuthProvider', () => {
  beforeEach(() => {
    vi.mocked(loginRequest).mockResolvedValue(alice)
    vi.mocked(logoutRequest).mockResolvedValue(undefined)
  })

  it('loads the current session on start', async () => {
    vi.mocked(getCurrentUser).mockResolvedValue(alice)

    renderProvider()

    expect(screen.getByTestId('status')).toHaveTextContent('loading')
    await waitFor(() =>
      expect(screen.getByTestId('status')).toHaveTextContent('authenticated'),
    )
    expect(screen.getByTestId('username')).toHaveTextContent('alice')
  })

  it('treats an unauthorized session as anonymous', async () => {
    vi.mocked(getCurrentUser).mockRejectedValue(
      new ApiError('Unauthorized', 401, null),
    )

    renderProvider()

    await waitFor(() =>
      expect(screen.getByTestId('status')).toHaveTextContent('unauthenticated'),
    )
  })

  it('authenticates after a successful login', async () => {
    const user = userEvent.setup()
    vi.mocked(getCurrentUser).mockRejectedValue(
      new ApiError('Unauthorized', 401, null),
    )

    renderProvider()
    await waitFor(() =>
      expect(screen.getByTestId('status')).toHaveTextContent('unauthenticated'),
    )

    await user.click(screen.getByRole('button', { name: 'Log in' }))

    await waitFor(() =>
      expect(screen.getByTestId('status')).toHaveTextContent('authenticated'),
    )
    expect(loginRequest).toHaveBeenCalledWith({
      username: 'alice',
      password: 'pw',
    })
  })

  it('clears the session after logout', async () => {
    const user = userEvent.setup()
    vi.mocked(getCurrentUser).mockResolvedValue(alice)

    renderProvider()
    await waitFor(() =>
      expect(screen.getByTestId('status')).toHaveTextContent('authenticated'),
    )

    await user.click(screen.getByRole('button', { name: 'Log out' }))

    await waitFor(() =>
      expect(screen.getByTestId('status')).toHaveTextContent('unauthenticated'),
    )
    expect(logoutRequest).toHaveBeenCalledTimes(1)
  })
})
