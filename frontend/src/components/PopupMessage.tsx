/** Imports */
import { useEffect, useRef } from 'react';
import { Toaster, toast } from 'react-hot-toast';

/**
 * File that creates a component that handles a simple popup message located in top center position.
 * The component is used when file couldnt be uploaded or incorrect params is inserted by user.
 */

/**
 * Interface for specific object used in this component.
 */
interface PopupMessageProps {
  message: string; /** The message that should be displayed. */
  show: boolean; /** Boolean value that makes sure only one popup message can be displayed. */
  type: 'success' | 'error'; /** The type of message. */
  duration?: number; /** The duration for the message. Is set to 4000 */
  onClose?: () => void; /** The callback function */
}

/**
 * Function that creates a popup message located top center
 * 
 * @param param0 The PopupMessageProps param
 * @returns The popup message.
 */
export function PopupMessage({ message, show, type = 'success', duration = 4000, onClose }: PopupMessageProps) {
  const toastIdRef = useRef<string | undefined>(undefined);

  useEffect(() => {
    if (show && !toastIdRef.current) {
      const toastFn = type === 'success' ? toast.success : toast.error;
      const icon = type === 'success' ? '✅' : '⚠️';
      const style = {
        borderRadius: '8px',
      }

      const id = toastFn(message, {
        duration,
        icon,
        style,
      });

      toastIdRef.current = id;

      if (onClose) {
        setTimeout(() => {
          toastIdRef.current = undefined;
          onClose();
        }, duration);
      }
    }

    return () => {
      if (toastIdRef.current) {
        toast.dismiss(toastIdRef.current);
        toastIdRef.current = undefined;
      }
    };
  }, [show, message, type, duration, onClose]);

  return <Toaster position="top-center"  />;
}