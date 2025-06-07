import React, { useState } from 'react';
import { describe, it, expect, vi, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ProbabilitiesTab from '../../../src/components/top-panel/ProbabilitiesTab';
import { JsonDataSimod } from '../../../src/types/JsonDataSimod';

// Mocks
vi.mock('bpmn-js/lib/Modeler', () => {
  return {
    default: class MockModeler {
      importXML() {
        return Promise.resolve();
      }
      get() {
        return {
          getAll: () => [
            { id: 'gateway1', businessObject: { name: 'Gateway 1' } },
            { id: 'path1', businessObject: { name: 'Path 1' } },
            { id: 'path2', businessObject: { name: 'Path 2' } },
          ],
        };
      }
      destroy() { }
    },
  };
});

// Mock UI5 web components
vi.mock('@ui5/webcomponents-react', () => {
  return {
    Panel: ({ children, headerText, collapsed, onToggle }) => (
      <div data-testid="panel">
        <div onClick={onToggle}>{headerText}</div>
        {!collapsed && <div>{children}</div>}
      </div>
    ),
    Label: ({ children }) => <label>{children}</label>,
    Input: ({ type, value, onInput }) => (
      <input type={type} value={value} onChange={(e) => onInput(e)} data-testid={`input-${value}`} />
    ),
    Button: ({ children, onClick, design }) => (
      <button onClick={onClick} data-design={design} data-testid={`button-${children}`}>
        {children}
      </button>
    ),
  };
});

/* eslint-disable camelcase */
const mockJson: JsonDataSimod = {
  gateway_branching_probabilities: [
    {
      gateway_id: 'gateway1',
      probabilities: [
        { path_id: 'path1', value: 0.5 },
        { path_id: 'path2', value: 0.3 },
      ],
    },
  ],
};
/* eslint-enable camelcase */

describe('ProbabilitiesTab', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders loading initially then shows data', async () => {
    render(<ProbabilitiesTab bpmnXml="<xml>dummy</xml>" jsonData={mockJson} setJsonData={() => { }} />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText(/Gateway 1/i)).toBeInTheDocument();
    });
  });

  it('shows message if no probabilities data', async () => {
    render(<ProbabilitiesTab bpmnXml="<xml>dummy</xml>" jsonData={{}} setJsonData={() => { }} />);
    await waitFor(() => {
      expect(screen.getByText(/no gateway branching probabilities/i)).toBeInTheDocument();
    });
  });

  it('balances probabilities correctly', async () => {
    let updatedJson: JsonDataSimod | null = null;

    const Wrapper = () => {
      const [jsonData, setJsonData] = useState<JsonDataSimod>(mockJson);
      // capture state change in the outer scope
      const wrappedSetJsonData = (updater: React.SetStateAction<JsonDataSimod>) => {
        const newValue = typeof updater === 'function' ? (updater as Function)(jsonData) : updater;
        updatedJson = newValue;
        setJsonData(newValue);
      };

      return (
        <ProbabilitiesTab
          bpmnXml="<xml>dummy</xml>"
          jsonData={jsonData}
          setJsonData={wrappedSetJsonData}
        />
      );
    };

    render(<Wrapper />);

    // Wait for panel and open it
    await waitFor(() => expect(screen.getByText(/Gateway 1/i)).toBeInTheDocument());
    fireEvent.click(screen.getByText(/Gateway 1/i));

    // Click the first Balance button
    await waitFor(() => {
      const balanceButtons = screen.getAllByTestId('button-Balance');
      expect(balanceButtons.length).toBeGreaterThan(0);
    });

    const balanceButtons = screen.getAllByTestId('button-Balance');
    fireEvent.click(balanceButtons[0]);

    // Wait for state to update and assert total probability is 1.0
    await waitFor(() => {
      const total = updatedJson?.gateway_branching_probabilities?.[0].probabilities.reduce(
        (sum, p) => sum + p.value,
        0
      );
      expect(total).toBeCloseTo(1.0, 4);
    });
  });

  it('toggles panel expansion on header click', async () => {
    render(<ProbabilitiesTab bpmnXml="<xml>dummy</xml>" jsonData={mockJson} setJsonData={() => { }} />);

    await waitFor(() => {
      expect(screen.getByText(/Gateway 1/i)).toBeInTheDocument();
    });

    // Initially collapsed
    expect(screen.queryByTestId('input-0.5')).not.toBeInTheDocument();

    // Toggle expansion
    fireEvent.click(screen.getByText(/Gateway 1/i));

    await waitFor(() => {
      expect(screen.getByTestId('input-0.5')).toBeInTheDocument();
    });
  });
});

