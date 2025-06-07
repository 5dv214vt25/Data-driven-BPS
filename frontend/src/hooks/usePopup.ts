import { useState } from 'react';

/**
 * Custom hook for managing popup messages with type and content.
 *
 * Provides state and handlers to show and close a popup message,
 * supporting 'success' and 'error' types.
 *
 * @returns {{
*   message: string,
*   type: 'success' | 'error',
*   showPopup: (type: 'success' | 'error', message: string) => void,
*   closePopup: () => void
* }}
*/
export const usePopup = () => {
  const [message, setMessage] = useState('');
  const [type, setType] = useState<'success' | 'error'>('success');

  const showPopup = (newType: 'success' | 'error', newMessage: string) => {
    setType(newType);
    setMessage(newMessage);
  };

  const closePopup = () => setMessage('');

  return {
    message,
    type,
    showPopup,
    closePopup
  };
};
