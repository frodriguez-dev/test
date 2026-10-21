import { CircleAlert, CircleCheck, LoaderCircle, RefreshCw } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useHealth } from '@/features/health/useHealth'

/**
 * Render the backend health check with loading, success, and error states.
 *
 * The error state includes a retry button that repeats the request.
 */
export function HealthStatus() {
  const { state, reload } = useHealth()

  return (
    <div className="space-y-2" aria-live="polite">
      <p className="text-sm font-medium">API connection</p>

      {state.status === 'loading' && (
        <p
          role="status"
          className="flex items-center gap-2 text-sm text-muted-foreground"
        >
          <LoaderCircle
            className="size-4 animate-spin"
            aria-hidden="true"
          />
          Checking /api/health/...
        </p>
      )}

      {state.status === 'success' && (
        <p
          role="status"
          className="flex items-center gap-2 text-sm text-emerald-600"
        >
          <CircleCheck className="size-4" aria-hidden="true" />
          API available (status: {state.data.status}).
        </p>
      )}

      {state.status === 'error' && (
        <div role="alert" className="space-y-2">
          <p className="flex items-center gap-2 text-sm text-destructive">
            <CircleAlert className="size-4" aria-hidden="true" />
            {state.message}
          </p>
          <Button size="sm" variant="outline" onClick={reload}>
            <RefreshCw aria-hidden="true" />
            Retry
          </Button>
        </div>
      )}
    </div>
  )
}
