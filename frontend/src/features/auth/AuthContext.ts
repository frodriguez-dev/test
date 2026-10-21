import { createContext } from 'react'
import type { Login, User } from '@/types/api'

/** Authentication state shared by the application. */
export type AuthState =
  | { status: 'loading' }
  | { status: 'authenticated'; user: User }
  | { status: 'unauthenticated' }
  | { status: 'error'; message: string }

/** Value exposed by the authentication context. */
export interface AuthContextValue {
  /** Current authentication state. */
  state: AuthState
  /** Authenticate and start a session. */
  login: (credentials: Login) => Promise<void>
  /** End the current session. */
  logout: () => Promise<void>
}

/** Context that exposes the authentication state and actions. */
export const AuthContext = createContext<AuthContextValue | null>(null)
