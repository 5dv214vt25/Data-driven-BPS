import { afterEach, it, expect, describe } from 'vitest'
import { renderHook, act, cleanup } from '@testing-library/react'

import { usePopup } from '../../src/hooks/usePopup'

/**
 * Unit tests for the `usePopup` custom React hook using Vitest and React Testing Library.
 *
 * The `usePopup` hook manages UI state for popup messages, 
 * including message content and popup type (e.g., success or error).
 * 
 * This test suite covers:
 * - Initial state of the popup (empty message, default type 'success')
 * - Setting popup message and type via `showPopup`
 * - Resetting message using `closePopup` while retaining the type
 * 
 * These tests ensure that the hook behaves as expected and supports robust UI feedback logic.
 */

describe('usePopup', () => {
  afterEach(() => {
    cleanup();
  });

  it('should initialize with empty message and type success', () => {
    const { result } = renderHook(() => usePopup());
    expect(result.current.message).toBe('');
    expect(result.current.type).toBe('success');
  });

  it('should set error type and message correctly', () => {
    const { result } = renderHook(() => usePopup());

    act(() => {
      result.current.showPopup('error', 'error message');
    });

    expect(result.current.type).toBe('error')
    expect(result.current.message).toBe('error message');
  });

  it('should set success type and message correctly', () => {
    const { result } = renderHook(() => usePopup());

    act(() => {
      result.current.showPopup('success', 'success message');
    });

    expect(result.current.type).toBe('success')
    expect(result.current.message).toBe('success message');
  });

  it('should clear the message with closePopup', () => {
    const { result } = renderHook(() => usePopup());

    act(() => {
      result.current.showPopup('error', 'error message');
    });
    expect(result.current.type).toBe('error');
    expect(result.current.message).toBe('error message');

    act(() => {
      result.current.closePopup();
    });
    expect(result.current.message).toBe('');
    expect(result.current.type).toBe('error');
  });
})