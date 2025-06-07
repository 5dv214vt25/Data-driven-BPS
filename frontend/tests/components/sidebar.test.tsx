import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import Sidebar from '../../src/components/sidebar';

/**
 * Test for component: 'sidebar.tsx'
 * 
 * Test that are included:
 * 
 * Component should display different text on the screen.
 * Component should render external links with correct text and href
 */

/** Mock-up for SideNavigationItem. */
vi.mock("@ui5/webcomponents-react", () => ({
  SideNavigationItem: ({ icon, text, href, selected, slot }: any) => (
    <div
      data-testid="side-navigation-item"
      data-icon={icon}
      data-selected={selected}
      data-href={href}
      data-slot={slot}
    >
      {text}
    </div> 
  ),
}));

const mockLocation = { pathname: '/' };
vi.stubGlobal('location', mockLocation);

describe('Sidebar', () => {

  it('Checks if correct options is rendered.', async () => {

    /** Render the component. */
    render(<Sidebar/>);

    /** Should expect Home, Eventlogs etc on the screen. */
    expect(screen.getByText('Home'));
    expect(screen.getByText('Event Logs'));
    expect(screen.getByText('Discovery'));
    expect(screen.getByText('Simulation'));
    expect(screen.getByText('Analysis'));
    expect(screen.getByText('Setting'));
    expect(screen.getByText('About'));

  });
});