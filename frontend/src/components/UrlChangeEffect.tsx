import React, { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

/**
 * This file is currently not used.
 */

/**
 * React component that triggers a click on an invisible HTML element whenever the URL changes.
 *
 * This component listens to route/location changes via `useLocation` from `react-router-dom`.
 * On each URL change, it finds a DOM element with the ID `fake-click-target` and triggers a `.click()` on it.
 * This can be used to simulate UI interactions or trigger other behavior on navigation.
 *
 * Useful in scenarios where external libraries or handlers rely on simulated DOM events triggered by navigation.
 *
 * Note: This component renders nothing (`null`) and is meant to be mounted once in a global context (e.g., in App).
 */

const UrlChangeEffect: React.FC = () => {
  const location = useLocation();

  useEffect(() => {
    const span = document.getElementById('fake-click-target');
    console.log("UrlChangeEffects")
    if (span) {
      span.click();
      console.log('URL changed! Clicked invisible span.');
    }
  }, [location]);

  return null;
};

export default UrlChangeEffect;