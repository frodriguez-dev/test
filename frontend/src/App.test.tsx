import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import App from '@/App'
import { getCurrentUser } from '@/api/auth'
import { ApiError } from '@/api/client'
import { getHealth } from '@/api/health'
import { AuthProvider } from '@/features/auth/AuthProvider'
import type { User } from '@/types/api'

vi.mock('@/api/auth', () => ({
  getCurrentUser: vi.fn(),
  login: vi.fn(),
  logout: vi.fn(),
}))

vi.mock('@/api/health', () => ({
  getHealth: vi.fn(),
}))

const alice: User = {
  id: 1,
  username: 'alice',
  email: '',
  first_name: 'Alice',
  last_name: '',
}

function renderApp(initialPath = '/') {
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
      <AuthProvider>
        <App />
      </AuthProvider>
    </MemoryRouter>,
  )
}

describe('App routing', () => {
  beforeEach(() => {
    vi.mocked(getHealth).mockResolvedValue({ status: 'ok' })
  })

  it('redirects anonymous visitors to the login page', async () => {
    vi.mocked(getCurrentUser).mockRejectedValue(
      new ApiError('Unauthorized', 401, null),
    )

    renderApp()

    expect(
      await screen.findByRole('button', { name: 'Sign in' }),
    ).toBeInTheDocument()
  })

  it('renders the protected page for an authenticated session', async () => {
    vi.mocked(getCurrentUser).mockResolvedValue(alice)

    renderApp()

    expect(await screen.findByText('Protected page')).toBeInTheDocument()
    expect(await screen.findByText(/Signed in as/)).toHaveTextContent('alice')
    expect(await screen.findByText(/API available/)).toHaveTextContent('ok')
  })
})
