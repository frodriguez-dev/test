import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { AuthContext, type AuthContextValue } from '@/features/auth/AuthContext'
import { LoginForm } from '@/features/auth/LoginForm'

function renderForm(login: AuthContextValue['login']) {
  const value: AuthContextValue = {
    state: { status: 'unauthenticated' },
    login,
    logout: vi.fn(),
  }

  return render(
    <AuthContext.Provider value={value}>
      <LoginForm />
    </AuthContext.Provider>,
  )
}

describe('LoginForm', () => {
  it('submits the entered credentials', async () => {
    const user = userEvent.setup()
    const login = vi.fn().mockResolvedValue(undefined)
    renderForm(login)

    await user.type(screen.getByLabelText('Username'), 'alice')
    await user.type(screen.getByLabelText('Password'), 'secret')
    await user.click(screen.getByRole('button', { name: 'Sign in' }))

    expect(login).toHaveBeenCalledWith({
      username: 'alice',
      password: 'secret',
    })
  })

  it('shows the error when sign-in fails', async () => {
    const user = userEvent.setup()
    const login = vi.fn().mockRejectedValue(new Error('Invalid credentials.'))
    renderForm(login)

    await user.type(screen.getByLabelText('Username'), 'alice')
    await user.type(screen.getByLabelText('Password'), 'wrong')
    await user.click(screen.getByRole('button', { name: 'Sign in' }))

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Invalid credentials.',
    )
    expect(screen.getByRole('button', { name: 'Sign in' })).toBeEnabled()
  })
})
