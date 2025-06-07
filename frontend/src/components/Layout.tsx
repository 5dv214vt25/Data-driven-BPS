import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLocation } from 'react-router-dom';

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
import '@ui5/webcomponents-icons/dist/business-one.js';
import '@ui5/webcomponents-icons/dist/bar-chart.js';

import {
  NavigationLayout,
  ShellBar,
  Button,
  SideNavigation,
  Avatar,
  Popover,
  SideNavigationItem
} from '@ui5/webcomponents-react';

import AccountInfo from '../pages/AccountInfo';

import '../assets/styles/layout.css';

/**
 * Layout component for the application providing a consistent structure with top navigation (ShellBar)
 * and side navigation (SideNavigation). Handles routing, menu interactions, and responsive UI layout.
 *
 * Features:
 * - Highlights the selected navigation item based on the current route (`location.pathname`).
 * - Collapsible sidebar for improved UX on smaller screens.
 * - Uses React Router for navigation between views.
 * - Integrates UI components from @ui5/webcomponents and @ui5/webcomponents-react.
 * - Includes a user profile section with a popover displaying `AccountInfo`.
 * - Conditionally renders development-only links (e.g., Settings, API Playground).
 *
 * This component wraps around the main page content and ensures consistent navigation across the app.
 */

/**
 * Generates the navigationsidebar and topmenu
 *
 * @returns {JSX.Element}
 */
const Layout = ({ children }: { children: React.ReactNode; }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [selectedItem, setSelectedItem] = useState('');
  const [sidebarCollapsed, setSidebarCollapsed] = React.useState(false);
  const [menuOpen, setMenuOpen] = useState<boolean>(false);

  const openerRef = useRef(null);

  /**
   * Checks if the route already is selected
   *
   * @param {string} route - The route to check
   */
  const isItemSelected = (route: string) => {
    return selectedItem === route;
  };

  /**
   * Handles clicks on the side nav items
   */
  const handleNavigation = (event: CustomEvent) => {
    const targetRoute = event.detail.item.dataset.route;
    if (targetRoute) {
      navigate(targetRoute);
    }
  };

  /**
   * Update selection when URL changes
   */
  useEffect(() => {
    if (selectedItem != location.pathname) {
      setSelectedItem(location.pathname);
    }
  }, [location.pathname]);


  /**
   * Generates an internal navigation link
   */
  const generateLink = (icon: string, text: string, route: string) => {
    return (
      <SideNavigationItem
        selected={isItemSelected(route)}
        icon={icon}
        text={text}
        data-route={route}
      />
    );
  };

  return (
    <NavigationLayout
      mode={sidebarCollapsed ? "Collapsed" : "Expanded"}
      header={
        <ShellBar
          primaryTitle="PVT"
          secondaryTitle="Business Process Simulation"
          onLogoClick={() => navigate('/')}
          profile={
            <span
              style={{ zIndex: 3 }}
              onClick={() => setMenuOpen(!menuOpen)}
            >
              <Avatar
                style={{ backgroundColor: 'white', zIndex: 2, border: 'silver' }}
                icon="account"
                ref={openerRef}
              />
            </span>
          }
          startButton={
            <Button
              icon="menu"
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            />
          }
        />
      }
      sideContent={
        <SideNavigation key={selectedItem} onSelectionChange={handleNavigation}>

          {generateLink("home", "Home", "/")}
          {generateLink("customer-financial-fact-sheet", "Event Logs", "/eventlogs")}
          {generateLink("map-3", "Discovery", "/discovery")}
          {generateLink("ai", "Simulation", "/simulation")}
          {generateLink("bar-chart", "Analysis", "/analysis")}
          {import.meta.env.MODE === "development" && generateLink("settings", "Setting", "/settings")}
          {import.meta.env.MODE === "development" && generateLink("settings", "API Playground", "/api-playground")}
          {generateLink("hint", "About", "/about")}
        </SideNavigation>
      }
    >
      <span>
        {children}
        <Popover
          opener={openerRef.current ?? undefined}
          open={menuOpen}
          onClose={() => setMenuOpen(false)}
        >
          <AccountInfo />
        </Popover>
      </span>
    </NavigationLayout>
  );
};

export default Layout;


