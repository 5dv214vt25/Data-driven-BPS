import React from 'react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ResourceTab from '../../../src/components/top-panel/ResourcesTab';
import { JsonDataSimod } from '../../../src/types/JsonDataSimod';

beforeEach(() => {
  Object.defineProperty(window, 'location', {
    configurable: true,
    get() {
      throw new Error('window.location was accessed');
    },
  });
});

// Mock diagram-js using Vitest
vi.mock('bpmn-js/lib/Modeler', () => ({
  default: vi.fn().mockImplementation(() => ({
    importXML: vi.fn().mockResolvedValue({}),
    get: vi.fn((service: string) => {
      if (service === 'elementRegistry') {
        return {
          getAll: vi.fn().mockReturnValue([
            {
              id: 'node_591eb15f-3943-407b-8b76-59b313da34a1',
              businessObject: {
                name: 'AML check',
              },
            },
          ]),
        };
      }
      return null;
    }),
    destroy: vi.fn(),
  })),
}));

describe('ResourceTab Component', () => {
  /* eslint-disable max-len */
  const mockBpmnXml = `<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" xmlns:di="http://www.omg.org/spec/DD/20100524/DI" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" exporter="ProM. http://www.promtools.org/prom6" exporterVersion="6.3" expressionLanguage="http://www.w3.org/1999/XPath" targetNamespace="http://www.omg.org/bpmn20" typeLanguage="http://www.w3.org/2001/XMLSchema" xsi:schemaLocation="http://www.omg.org/spec/BPMN/20100524/MODEL BPMN20.xsd">
  <process id="proc_1908143486" isClosed="false" processType="None">
    <startEvent id="node_f602a21b-3979-4375-8e52-faefa92d5053" isInterrupting="true" name="" parallelMultiple="false"/>
    <endEvent id="node_504e0e8f-362d-497e-9da3-9b89d8a2240d" name=""/>
    <task completionQuantity="1" id="node_591eb15f-3943-407b-8b76-59b313da34a1" isForCompensation="false" name="AML check" startQuantity="1"/>
  </process>
</definitions>`;
  /* eslint-enable max-len */

  /* eslint-disable camelcase */
  const mockJsonData: JsonDataSimod = {
    resource_profiles: [
      {
        id: 'Undifferentiated_resource_profile',
        name: 'Undifferentiated_resource_profile',
        resource_list: [
          {
            id: 'Clerk-000001',
            name: 'Clerk-000001',
            amount: 1,
            cost_per_hour: 20,
            calendar: 'Undifferentiated_calendar',
            assignedTasks: [
              'node_591eb15f-3943-407b-8b76-59b313da34a1',
            ]
          },
        ]
      }
    ]
  };
  /* eslint-enable camelcase */

  it('renders without crashing', () => {
    render(<ResourceTab bpmnXml={mockBpmnXml} jsonData={mockJsonData} setJsonData={() => { }} />);
    expect(screen.getByText(/Clerk-000001/i)).toBeInTheDocument();
  });

  it('displays "No resource profiles data available." when no data', async () => {
    render(<ResourceTab bpmnXml={mockBpmnXml} jsonData={{}} setJsonData={() => { }} />);

    await waitFor(() => {
      expect(screen.getByText(/No resource profiles data available./i)).toBeInTheDocument();
    });
  });

  it('renders task and resource panels correctly when data is available', async () => {
    render(<ResourceTab bpmnXml={mockBpmnXml} jsonData={mockJsonData} setJsonData={() => { }} />);

    const panel = await screen.findByText((_, element) =>
      !!(
        element &&
        element.tagName.toLowerCase() === 'ui5-panel' &&
        element.getAttribute('header-text')?.includes('Clerk-000001')
      )
    );

    expect(panel).toBeTruthy();
    fireEvent.click(panel);

    await waitFor(() => {
      expect(screen.getByText((content) =>
        content.includes('Amount'))).toBeInTheDocument();
      expect(screen.getByText((content) =>
        content.includes('Undifferentiated_calendar'))).toBeInTheDocument();
      expect(screen.getByText((content) =>
        content.includes('AML check'))).toBeInTheDocument();
    });
  });
});
