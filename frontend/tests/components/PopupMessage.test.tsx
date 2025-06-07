import React from 'react';
import { describe, it, expect, vi, afterEach } from 'vitest';
import { render } from '@testing-library/react';
import '@testing-library/jest-dom';

import { PopupMessage } from '../../src/components/PopupMessage';
import { toast } from 'react-hot-toast';
import type { Mock } from 'vitest';
import { beforeEach } from 'node:test';


/**
 * Test for component 'PopupMessage'.
 * 
 * Test that are included:
 * 
 * Checks if the component render when message is empty, show is false and type equals success
 * Checks if the component calls toast.success with correct arguments when show equals true and type equals success
 * Checks if the component calls toast.error with correct arguments when show equals true and type equals error
 * Checks if the component invokes onClose after the specified duration (duration = 4000)
 * Checks if the component dissmisses the toast on unmount.
 */


/**
 * Global toaster for diffrent test cases.
 */
vi.mock('react-hot-toast', () => {

  const success = vi.fn();
  const error = vi.fn();
  const dismiss = vi.fn();

  const Toaster = () => <div data-testid="toaster" />;

  return {
    Toaster,
    toast: { success, error, dismiss },
  };

});

describe('PopupMessage', () => {

  /**
   * Function to be called before every 'it'-function.
   * Removes mock-ups and sets fake timers.
   */
  beforeEach(() => {
    vi.useFakeTimers();
    vi.clearAllMocks();
  });

  /**
     * Function to be called after every 'it'-function.
     * Creates real timers.
     */
  afterEach(() => {
    vi.useRealTimers();
  });

  it('Expects that toaster render when message is empty, show is false and type equals success'), () => {

    /** Render the component. */
    const { getByTestId } = render(
      <PopupMessage message='' show={false} type="success" />
    );
        
    /** Expects that test id equals toaster. */
    expect(getByTestId('toaster')).toBeInTheDocument();

  }

  it('Calls toast.success with correct arguments when show equals true and type equals success'), () => {

    /** The message to be shown. */
    const msgToBeShown = 'Hello world!';
    /** The duration of the toaster. */
    const durationOfToast = 4000;

    /** Render the component. */
    render(
      <PopupMessage
        message={msgToBeShown}
        show={true}
        type="success"
        duration={durationOfToast}
      />
    );

    /** Expects that toaster type equals succes has been called 1 time. */
    expect((toast.success as Mock)).toHaveBeenCalledTimes(1);

  }

  it('Calls toast.error with correct arguments when show equals true and type equals error'), () => {

    /** The message ton be shown. */
    const msgToBeShown = 'Hello world!';
    /** The duration of the toaster. */
    const durationOfToast = 4000;

    /** Render the component. */
    render(
      <PopupMessage
        message={msgToBeShown}
        show={true}
        type="error"
        duration={durationOfToast}
      />
    );

    /** Expects that toast with type error has been called 1 time. */
    expect((toast.error as Mock)).toHaveBeenCalledTimes(1);

  }

  it('invokes onClose after the specified duration (4000)'), () => {

    /** The message to be shown */
    const msgToBeShown = 'Hello world!';
    /** The duration of the toast. */
    const durationOfToast = 4000;
    /** Mock-up onClose. */
    const onClose = vi.fn();

    /** Render the component. */
    render(
      <PopupMessage
        message={msgToBeShown}
        show={true}
        type="success"
        duration={durationOfToast}
        onClose={onClose}
      />
    );

    /** Expects that onClose has not been called. */
    expect(onClose).not.toHaveBeenCalled();
        
    /** Fast forward the timer. */
    vi.advanceTimersByTime(durationOfToast);

    /** Expects that onClose has been called 1 time. */
    expect(onClose).toHaveBeenCalledTimes(1);

  }

  it('Dissmisses the toast on unmount'), () => {

    /** The message to be shown. */
    const msgToBeShown = 'Hello world!';

    /** Sets the return value. */
    (toast.success as Mock).mockReturnValue('toast-id-123');

    /** Render the component. */
    const { unmount } = render(
      <PopupMessage
        message={msgToBeShown}
        show={true}
        type="success"
      />
    );

    /** Expects that toast with type success have been called 1 time. */
    expect((toast.success as Mock)).toHaveBeenCalledTimes(1);
        
    /** Unmount the component. */
    unmount();
    /** Expects that dissmiss has been called with 'toast-id-123'. */
    expect((toast.dismiss as Mock)).toHaveBeenCalledWith('toast-id-123');
  }

});