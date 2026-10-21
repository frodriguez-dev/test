import { apiRequest } from '@/api/client'
import type { HealthResponse } from '@/types/api'

/**
 * Fetch the backend health check.
 *
 * @param signal - Optional signal used to abort the request.
 * @returns The API health response.
 */
export function getHealth(signal?: AbortSignal): Promise<HealthResponse> {
  return apiRequest<HealthResponse>('/api/health/', { signal })
}
