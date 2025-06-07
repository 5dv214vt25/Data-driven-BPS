// BpmnTab.test.tsx

import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach, beforeAll } from 'vitest';
import { render, screen, waitFor, cleanup } from '@testing-library/react';
import '@testing-library/jest-dom';
import BpmnTab from '../../../src/components/top-panel/BpmnTab';
import BpmnDiagram from '../../../src/components/BpmnDiagram.tsx';
import { JsonDataSimod } from '../../../src/types/JsonDataSimod';

// 🔧 Setup mocks for bpmn-js Modeler
let importXMLMock: any;
let getMock: any;
let destroyMock = vi.fn();

vi.mock('bpmn-js/lib/Modeler', () => {
  return {
    default: class MockModeler {
      options: any;
      importXML: any;
      get: any;
      destroy: any;

      constructor(options: any) {
        this.options = options;
        this.importXML = importXMLMock;
        this.get = getMock;
        this.destroy = destroyMock;
      }
    },
  };
});

// 🧪 Mock PropertiesView
vi.mock('../../../src/components/properties-panel/PropertiesView', () => ({
  default: () => <div data-testid="properties-view">Properties Panel</div>,
}));

// 🗃️ Simple localStorage mock
beforeAll(() => {
  Object.defineProperty(window, 'localStorage', {
    value: {
      getItem: vi.fn(),
      setItem: vi.fn(),
      removeItem: vi.fn(),
      clear: vi.fn(),
    },
    configurable: true,
  });
});

describe('BpmnTab', () => {
  afterEach(() => {
    vi.restoreAllMocks();
    cleanup();
  });

  it('renders BpmnTab with BpmnDiagram and Simconfig text', async () => {
    render(<BpmnTab />);
    expect(await screen.findByText(/Simconfig/i)).toBeInTheDocument();
  });
});

describe('BpmnDiagram', () => {
  beforeEach(() => {
    importXMLMock = vi.fn().mockResolvedValue({ warnings: [] });
    getMock = vi.fn().mockReturnValue({ zoom: vi.fn() });
    destroyMock = vi.fn();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    cleanup();
  });

  it('renders the BPMN diagram container and properties panel', async () => {
    const mockJsonData: JsonDataSimod = {
      gateway_branching_probabilities: [], // eslint-disable-line camelcase
      task_resource_distribution: [], // eslint-disable-line camelcase
      resource_profiles: [] // eslint-disable-line camelcase
    };
    const mockSetJsonData = vi.fn();
    render(
      <BpmnDiagram
        bpmnXml=""
        jsonData={mockJsonData}
        showSidePanel={true}
        setJsonData={mockSetJsonData}
      />
    );
    expect(screen.getByTestId('properties-view')).toBeInTheDocument();
  });

  it('initializes modeler and imports BPMN XML', async () => {
    const xml = '<bpmn:definitions id="test"></bpmn:definitions>';
    render(<BpmnDiagram bpmnXml={xml} jsonData={undefined} showSidePanel={true} />);
    await waitFor(() => {
      expect(importXMLMock).toHaveBeenCalledWith(xml);
      expect(getMock).toHaveBeenCalledWith('canvas');
      expect(getMock().zoom).toHaveBeenCalledWith('fit-viewport');
    });
  });

  it('logs warnings if import returns them', async () => {
    importXMLMock.mockResolvedValueOnce({
      warnings: ['Warning: invalid element'],
    });
    const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => { });

    render(<BpmnDiagram bpmnXml="<xml />" jsonData={undefined} showSidePanel={true} />);
    await waitFor(() => {
      expect(warnSpy).toHaveBeenCalledWith('Import warnings:', ['Warning: invalid element']);
    });

    warnSpy.mockRestore();
  });

  it('logs an error if import fails', async () => {
    importXMLMock.mockRejectedValueOnce(new Error('Import failed'));
    const errorSpy = vi.spyOn(console, 'error').mockImplementation(() => { });

    render(<BpmnDiagram bpmnXml="<xml />" jsonData={undefined} showSidePanel={true} />);
    await waitFor(() => {
      expect(errorSpy).toHaveBeenCalledWith('BPMN import error:', expect.any(Error));
    });

    errorSpy.mockRestore();
  });

  it('destroys the modeler on unmount', () => {
    const { unmount } = render(<BpmnDiagram bpmnXml="" jsonData={undefined} showSidePanel={true} />);
    unmount();
    expect(destroyMock).toHaveBeenCalled();
  });
});
