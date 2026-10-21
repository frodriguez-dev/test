import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { getHealth } from '@/api/health'
import { HealthStatus } from '@/features/health/HealthStatus'
import type { HealthResponse } from '@/types/api'

vi.mock('@/api/health', () => ({
  getHealth: vi.fn(),
}))

describe('HealthStatus', () => {
  beforeEach(() => {
    vi.mocked(getHealth).mockReset()
  })

  it('refreshes the API status when the button is clicked', async () => {
    vi.mocked(getHealth)
      .mockResolvedValueOnce({ status: 'ok' })
      .mockResolvedValueOnce({ status: 'degraded' })
    const user = userEvent.setup()
    render(<HealthStatus />)

    expect(
      await screen.findByText(/API available \(status: ok\)/),
    ).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Refresh' }))

    expect(
      await screen.findByText(/API available \(status: degraded\)/),
    ).toBeInTheDocument()
    expect(getHealth).toHaveBeenCalledTimes(2)
  })

  it('disables the button while the request is in flight', async () => {
    let resolveHealth!: (value: HealthResponse) => void
    vi.mocked(getHealth).mockReturnValue(
      new Promise<HealthResponse>((resolve) => {
        resolveHealth = resolve
      }),
    )
    render(<HealthStatus />)

    const button = screen.getByRole('button', { name: 'Refresh' })
    expect(button).toBeDisabled()
    expect(screen.getByText('Checking /api/health/...')).toBeInTheDocument()

    resolveHealth({ status: 'ok' })

    expect(await screen.findByText(/status: ok/)).toBeInTheDocument()
    expect(button).toBeEnabled()
  })

  it('shows the error and retries with the same button', async () => {
    vi.mocked(getHealth)
      .mockRejectedValueOnce(new Error('Network unavailable'))
      .mockResolvedValueOnce({ status: 'ok' })
    const user = userEvent.setup()
    render(<HealthStatus />)

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Network unavailable',
    )

    await user.click(screen.getByRole('button', { name: 'Refresh' }))

    expect(await screen.findByText(/status: ok/)).toBeInTheDocument()
    expect(getHealth).toHaveBeenCalledTimes(2)
  })
})
