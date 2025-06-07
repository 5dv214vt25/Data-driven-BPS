import { SideNavigationItem } from '@ui5/webcomponents-react';
import { useEffect, useState } from 'react';

import '@ui5/webcomponents-icons/dist/menu.js';
import '@ui5/webcomponents/dist/Icon.js';
import '@ui5/webcomponents-icons/dist/home.js';
import '@ui5/webcomponents-icons/dist/settings.js';
import '@ui5/webcomponents-icons/dist/customer-financial-fact-sheet.js';
import '@ui5/webcomponents-icons/dist/hint.js';
import '@ui5/webcomponents-icons/dist/ai.js';
import '@ui5/webcomponents-icons/dist/add-document.js';
import '@ui5/webcomponents-icons/dist/batch-payments.js';
import '@ui5/webcomponents-icons/dist/map-3.js';
import '@ui5/webcomponents-icons/dist/account.js';
import '@ui5/webcomponents-icons/dist/bar-chart.js';

/**
 * This file is currently not used 4/6 2025.
 * The component that creates the sidebar for the webpage is layout.tsx
 */

/**
 * Sidebar - allows the user to navigate around the site
 *
 * @component
 */
function Sidebar() {
  const [selectedItem, setSelectedItem] = useState('');

  /**
   * Updates the active element in the menu when the URL changes
   *
   * @function
   */
  useEffect(() => {
    setSelectedItem(location.pathname);
  }, [location]);

  /**
   * Checks if the route already is selected
   *
   * @param {string} route - Rhe route the user want to navigate to
   */
  const isItemSelected = (route: string) => {
    return selectedItem === route;
  };

  /**
   * Generate internal links (within webpage only)
   *
   * @function
   *
   * @param icon - Icon before the links text
   * @param text - Text that is displayed for the user
   * @param route - address the user is going to be sent to.
   *
   * @returns {JSX.Element}
   */
  const generateLink = (icon: string, text: string, route: string) => {
    return <SideNavigationItem selected={isItemSelected(route)} icon={icon} text={text} data-route={route} />;
  };


  /**
   * Generate links (internal) and navigation items (external sources)
   *
   * @returns {JSX.Element}
   */
  return (
    <>
      {generateLink('home', 'Home', '/')}
      {generateLink('customer-financial-fact-sheet', 'Event Logs', '/eventlogs')}
      {generateLink('map-3', 'Discovery', '/discovery')}
      {generateLink('ai', 'Simulation', '/simulation')}
      {generateLink('bar-chart', 'Analysis', '/analysis')}
      {generateLink('settings', 'Setting', '/settings')}
      {generateLink('hint', 'About', '/about')}
    </>
  );
}

export default Sidebar;
