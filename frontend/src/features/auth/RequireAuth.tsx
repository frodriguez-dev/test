import { CircleAlert, LoaderCircle } from 'lucide-react'
import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '@/features/auth/useAuth'

/**
 * Render the routes nested under it only for authenticated users.
 *
 * Anonymous visitors are redirected to the login page, which returns them to
 * the requested route after signing in.
 */
export function RequireAuth() {
  const { state } = useAuth()
  const location = useLocation()

  if (state.status === 'loading') {
    return (
      <main className="flex min-h-svh items-center justify-center bg-muted/30 p-6">
        <p
          role="status"
          className="flex items-center gap-2 text-sm text-muted-foreground"
        >
          <LoaderCircle className="size-4 animate-spin" aria-hidden="true" />
          Checking your session...
        </p>
      </main>
    )
  }

  if (state.status === 'error') {
    return (
      <main className="flex min-h-svh items-center justify-center bg-muted/30 p-6">
        <p
          role="alert"
          className="flex items-center gap-2 text-sm text-destructive"
        >
          <CircleAlert className="size-4" aria-hidden="true" />
          {state.message}
        </p>
      </main>
    )
  }

  if (state.status === 'unauthenticated') {
    return <Navigate to="/login" replace state={{ from: location }} />
  }

  return <Outlet />
}
