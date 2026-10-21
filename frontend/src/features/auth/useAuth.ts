import { useContext } from 'react'
import { AuthContext } from '@/features/auth/AuthContext'

/**
 * Access the authentication state and actions.
 *
 * @returns The authentication context value.
 * @throws When used outside an `AuthProvider`.
 */
export function useAuth() {
  const context = useContext(AuthContext)

  if (context === null) {
    throw new Error('useAuth must be used within an AuthProvider.')
  }

  return context
}
