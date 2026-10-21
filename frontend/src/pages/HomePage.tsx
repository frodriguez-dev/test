import { useState } from 'react'
import { LogOut } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { HealthStatus } from '@/features/health/HealthStatus'
import { useAuth } from '@/features/auth/useAuth'

/**
 * Render the protected example route for a signed-in user.
 */
export function HomePage() {
  const { state, logout } = useAuth()
  const [loggingOut, setLoggingOut] = useState(false)
  const [error, setError] = useState<string | null>(null)

  if (state.status !== 'authenticated') {
    return null
  }

  async function handleLogout() {
    setError(null)
    setLoggingOut(true)

    try {
      await logout()
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : 'Unable to sign out.',
      )
      setLoggingOut(false)
    }
  }

  return (
    <main className="flex min-h-svh items-center justify-center bg-muted/30 p-6">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Protected page</CardTitle>
          <CardDescription>
            Signed in as <strong>{state.user.username}</strong>. Only
            authenticated users can see this route.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm">
            {state.user.first_name || state.user.username}
            {state.user.email ? ` · ${state.user.email}` : ''}
          </p>
          <div className="border-t pt-4">
            <HealthStatus />
          </div>
          {error && (
            <p role="alert" className="text-sm text-destructive">
              {error}
            </p>
          )}
        </CardContent>
        <CardFooter>
          <Button
            type="button"
            variant="outline"
            onClick={handleLogout}
            disabled={loggingOut}
          >
            <LogOut aria-hidden="true" />
            {loggingOut ? 'Signing out...' : 'Sign out'}
          </Button>
        </CardFooter>
      </Card>
    </main>
  )
}
