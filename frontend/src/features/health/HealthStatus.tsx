import { CircleAlert, CircleCheck, LoaderCircle, RefreshCw } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useHealth } from '@/features/health/useHealth'

/**
 * Render the backend health check with loading, success, and error states.
 *
 * The refresh button repeats the request in every state and is disabled while
 * a request is in flight.
 */
export function HealthStatus() {
  const { state, reload } = useHealth()
  const isLoading = state.status === 'loading'

  return (
    <div className="space-y-2" aria-live="polite">
      <div className="flex items-center justify-between gap-2">
        <p className="text-sm font-medium">API connection</p>
        <Button
          type="button"
          size="sm"
          variant="ghost"
          onClick={reload}
          disabled={isLoading}
        >
          <RefreshCw
            className={isLoading ? 'animate-spin' : undefined}
            aria-hidden="true"
          />
          Refresh
        </Button>
      </div>

      {state.status === 'loading' && (
        <p
          role="status"
          className="flex items-center gap-2 text-sm text-muted-foreground"
        >
          <LoaderCircle className="size-4 animate-spin" aria-hidden="true" />
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
        <p
          role="alert"
          className="flex items-center gap-2 text-sm text-destructive"
        >
          <CircleAlert className="size-4" aria-hidden="true" />
          {state.message}
        </p>
      )}
    </div>
  )
}
