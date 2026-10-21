import { useCallback, useEffect, useState } from 'react'
import { getHealth } from '@/api/health'
import type { HealthResponse } from '@/types/api'

export type HealthState =
  | { status: 'loading' }
  | { status: 'success'; data: HealthResponse }
  | { status: 'error'; message: string }

/**
 * Load the backend health check and track its loading, success, and error
 * states.
 *
 * @returns The current health state and a `reload` callback that retries the
 * request.
 */
export function useHealth() {
  const [state, setState] = useState<HealthState>({ status: 'loading' })
  const [requestId, setRequestId] = useState(0)

  /** Retry the health request by triggering the effect again. */
  const reload = useCallback(() => {
    setRequestId((current) => current + 1)
  }, [])

  useEffect(() => {
    const controller = new AbortController()

    setState({ status: 'loading' })
    getHealth(controller.signal)
      .then((data) => {
        setState({ status: 'success', data })
      })
      .catch((error: unknown) => {
        if (controller.signal.aborted) {
          return
        }

        setState({
          status: 'error',
          message:
            error instanceof Error ? error.message : 'Unexpected API error.',
        })
      })

    return () => {
      controller.abort()
    }
  }, [requestId])

  return { state, reload }
}
