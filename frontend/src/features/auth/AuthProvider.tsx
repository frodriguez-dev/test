import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import {
  getCurrentUser,
  login as loginRequest,
  logout as logoutRequest,
} from '@/api/auth'
import { ApiError } from '@/api/client'
import { AuthContext, type AuthState } from '@/features/auth/AuthContext'
import type { Login } from '@/types/api'

/**
 * Load the current session and provide authentication state to the app.
 *
 * @param props - Component props.
 * @param props.children - Application tree that consumes the context.
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({ status: 'loading' })

  useEffect(() => {
    const controller = new AbortController()

    getCurrentUser(controller.signal)
      .then((user) => {
        setState({ status: 'authenticated', user })
      })
      .catch((error: unknown) => {
        if (controller.signal.aborted) {
          return
        }

        if (error instanceof ApiError && error.status === 401) {
          setState({ status: 'unauthenticated' })
          return
        }

        setState({
          status: 'error',
          message:
            error instanceof Error
              ? error.message
              : 'Unable to determine the session state.',
        })
      })

    return () => {
      controller.abort()
    }
  }, [])

  const login = useCallback(async (credentials: Login) => {
    const user = await loginRequest(credentials)
    setState({ status: 'authenticated', user })
  }, [])

  const logout = useCallback(async () => {
    try {
      await logoutRequest()
    } catch (error) {
      // A request without a session still ends in the same client state.
      if (!(error instanceof ApiError && error.status === 401)) {
        throw error
      }
    }

    setState({ status: 'unauthenticated' })
  }, [])

  const value = useMemo(
    () => ({ state, login, logout }),
    [state, login, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
