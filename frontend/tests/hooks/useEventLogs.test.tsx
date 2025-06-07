/* eslint-disable camelcase */
import { beforeEach, afterEach, it, expect, describe, vi } from 'vitest'
import { renderHook, act, cleanup, render } from '@testing-library/react'

import { useEventLogs } from '../../src/hooks/useEventLogs'
import * as simAPI from '../../src/api/simulationAPI'

/**
 * Unit tests for the `useEventLogs` custom React hook using Vitest and React Testing Library.
 *
 * The hook `useEventLogs` provides functionality for loading event logs via an API call and managing its loading state.
 * 
 * This test suite includes:
 * - Verification of initial state (empty logs, not loading)
 * - Successful loading of event logs with mocked API response
 * - Graceful handling of API errors by resetting logs and loading state
 * 
 * API dependency `fetchEventLogs` from `simulationAPI` is mocked for isolation.
 */

vi.mock('../../src/api/simulationAPI', () => ({
  fetchEventLogs: vi.fn(),
}));

describe('useEventLogs', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  })

  afterEach(() => {
    cleanup();
  })

  it('should should start with empty event logs and loading should be set to false', () => {
    const { result } = renderHook(() => useEventLogs());
    expect(result.current.eventLogs).toEqual([]);
    expect(result.current.loading).toBe(false);
  })

  it('should load event logs successfully', async () => {
    const fakeLogs = [
      { filename: 'testLog1.csv', event_log_id: '1'},
      { filename: 'testLog2.csv', event_log_id: '2'},
    ];
    const fetchSpy = vi.mocked(simAPI.fetchEventLogs);
    fetchSpy.mockResolvedValue(fakeLogs);

    const { result } = renderHook(() => useEventLogs());

    await act (async () => {
      await result.current.loadEventLogs('testUser');
    })

    expect(fetchSpy).toHaveBeenCalledWith('testUser');
    expect(result.current.eventLogs).toEqual(fakeLogs);
    expect(result.current.loading).toBe(false);
  })

  it('should clear eventLogs and reset loading on fetch error', async () => {
    const fetchSpy = vi.mocked(simAPI.fetchEventLogs);

    fetchSpy.mockResolvedValueOnce([{ filename: 'x.csv', event_log_id: 'x' }]);
    fetchSpy.mockRejectedValueOnce(new Error('Fetch error'));

    const { result } = renderHook(() => useEventLogs());

    await act(async () => {
      await result.current.loadEventLogs('testUser');
    });
    expect(result.current.eventLogs).toHaveLength(1);

    await act(async () => {
      await result.current.loadEventLogs('testUser');
    });

    expect(fetchSpy).toHaveBeenCalledTimes(2);
    expect(result.current.eventLogs).toEqual([]);
    expect(result.current.loading).toBe(false);
  });
})