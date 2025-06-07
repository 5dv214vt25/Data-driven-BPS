import React from 'react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import EventsTab from '../../../src/components/top-panel/EventsTab';
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
    get: vi.fn().mockReturnValue({
      getAll: vi.fn().mockReturnValue([]),
    }),
    destroy: vi.fn(),
    // Add any other necessary methods or properties
  })),
}));

describe('EventsTab Component', () => {
  /* eslint-disable max-len */
  const mockBpmnXml = `<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" xmlns:di="http://www.omg.org/spec/DD/20100524/DI" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" exporter="ProM. http://www.promtools.org/prom6" exporterVersion="6.3" expressionLanguage="http://www.w3.org/1999/XPath" targetNamespace="http://www.omg.org/bpmn20" typeLanguage="http://www.w3.org/2001/XMLSchema" xsi:schemaLocation="http://www.omg.org/spec/BPMN/20100524/MODEL BPMN20.xsd">
  <process id="proc_1908143486" isClosed="false" processType="None">
    <startEvent id="node_f602a21b-3979-4375-8e52-faefa92d5053" isInterrupting="true" name="" parallelMultiple="false"/>
    <endEvent id="node_504e0e8f-362d-497e-9da3-9b89d8a2240d" name=""/>
    <task completionQuantity="1" id="node_35ef11c2-29b7-4e3d-a35f-c52248ac41f1" isForCompensation="false" name="Design loan offer" startQuantity="1"/>
    <task completionQuantity="1" id="node_22d3ec1f-126e-4820-86fe-c3f574e93042" isForCompensation="false" name="Assess loan risk" startQuantity="1"/>
    <task completionQuantity="1" id="node_5bbd7709-b3c2-48b5-afa7-66db6d74adc8" isForCompensation="false" name="Cancel application" startQuantity="1"/>
    <task completionQuantity="1" id="node_5b67041c-da45-4919-980e-dac851badb1d" isForCompensation="false" name="Check application form completeness" startQuantity="1"/>
    <task completionQuantity="1" id="node_48e0a40d-bcf4-4f9f-8a57-0f6732a664c9" isForCompensation="false" name="Approve application" startQuantity="1"/>
    <task completionQuantity="1" id="node_8c34bcff-2580-465b-b3f0-c5cbccbc90d4" isForCompensation="false" name="Appraise property" startQuantity="1"/>
    <task completionQuantity="1" id="node_7ab87847-54a5-44d7-a97b-d00a97fe4e8e" isForCompensation="false" name="Approve loan offer" startQuantity="1"/>
    <task completionQuantity="1" id="node_6731ba50-8a01-4ee9-8e81-d3c5c6bc3a0c" isForCompensation="false" name="Reject application" startQuantity="1"/>
    <task completionQuantity="1" id="node_591eb15f-3943-407b-8b76-59b313da34a1" isForCompensation="false" name="AML check" startQuantity="1"/>
    <task completionQuantity="1" id="node_d0e197d7-4e49-43c0-b383-61ea051d8c5a" isForCompensation="false" name="Check credit history" startQuantity="1"/>
    <task completionQuantity="1" id="node_e3454e06-b288-40c5-bb36-d6adca6a8b19" isForCompensation="false" name="Applicant completes form" startQuantity="1"/>
    <task completionQuantity="1" id="node_6a6ed3dc-11f0-4372-99a8-c29d2a61d47f" isForCompensation="false" name="Return application back to applicant" startQuantity="1"/>
    <!-- Add more tasks and elements as needed -->
  </process>
</definitions>`;
  /* eslint-enable max-len */

  /* eslint-disable camelcase */
  const mockJsonData: JsonDataSimod = {
    task_resource_distribution: [
      {
        task_id: 'node_591eb15f-3943-407b-8b76-59b313da34a1',
        resources: [
          {
            resource_id: 'Clerk-000001',
            distribution_name: 'gamma',
            distribution_params: [
              { value: 1511.6844020909998 },
              { value: 2530508.350636599 },
              { value: 0.0 },
              { value: 10914.303 }
            ]
          }
        ]
      }
    ],
    resource_profiles: [
      {
        id: 'test_resource',
        name: 'test_resource',
        resource_list: [
          {
            id: 'Clerk-000001',
            name: 'Clerk-000001',
            amount: 1,
            cost_per_hour: 20,
            calendar: 'test_calendar',
            assignedTasks: ['node_591eb15f-3943-407b-8b76-59b313da34a1']
          }
        ]
      }
    ]
  };
  /* eslint-enable camelcase */

  it('renders without crashing', () => {
    render(<EventsTab bpmnXml={mockBpmnXml} jsonData={mockJsonData} setJsonData={() => { }} />);
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('displays "No task resource distribution data available" when no data', async () => {
    render(<EventsTab bpmnXml={mockBpmnXml} jsonData={{}} setJsonData={() => { }} />);

    await waitFor(() => {
      expect(screen.getByText(/No task resource distribution data available/i)).toBeInTheDocument();
    });
  });

  it('renders task and resource panels correctly when data is available', async () => {
    render(<EventsTab bpmnXml={mockBpmnXml} jsonData={mockJsonData} setJsonData={() => { }} />);

    const panel = await screen.findByText((_, element) =>
      !!(
        element &&
        element.tagName.toLowerCase() === 'ui5-panel' &&
        element.getAttribute('header-text')?.includes('node_591eb15f-3943-407b-8b76-59b313da34a1')
      )
    );

    expect(panel).toBeTruthy();
    fireEvent.click(panel);

    await waitFor(() => {
      expect(screen.getByText((content) =>
        content.includes('Clerk-000001'))).toBeInTheDocument();
    });
  });
});
