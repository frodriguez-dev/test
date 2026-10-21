import { CircleAlert, LoaderCircle, ShieldCheck } from 'lucide-react'
import { Navigate, useLocation } from 'react-router-dom'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { LoginForm } from '@/features/auth/LoginForm'
import { useAuth } from '@/features/auth/useAuth'

/** Render the login screen and redirect authenticated users. */
export function LoginPage() {
  const { state } = useAuth()
  const location = useLocation()
  const from =
    (location.state as { from?: { pathname?: string } } | null)?.from
      ?.pathname ?? '/'

  if (state.status === 'authenticated') {
    return <Navigate to={from} replace />
  }

  return (
    <main className="flex min-h-svh items-center justify-center bg-muted/30 p-6">
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ShieldCheck className="size-5" aria-hidden="true" />
            Sign in
          </CardTitle>
          <CardDescription>
            Use your application account. The session is stored in an
            HttpOnly cookie.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {state.status === 'loading' && (
            <p
              role="status"
              className="flex items-center gap-2 text-sm text-muted-foreground"
            >
              <LoaderCircle className="size-4 animate-spin" aria-hidden="true" />
              Checking your session...
            </p>
          )}

          {state.status === 'error' && (
            <p
              role="alert"
              className="flex items-center gap-2 text-sm text-destructive"
            >
              <CircleAlert className="size-4" aria-hidden="true" />
              {state.message}
            </p>
          )}

          {state.status !== 'loading' && <LoginForm />}
        </CardContent>
      </Card>
    </main>
  )
}
