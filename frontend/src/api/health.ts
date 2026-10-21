import { apiRequest } from '@/api/client'
import type { HealthResponse } from '@/types/api'

/** Fetch the backend health check. */
export function getHealth(signal?: AbortSignal): Promise<HealthResponse> {
  return apiRequest<HealthResponse>('/api/health/', { signal })
}
