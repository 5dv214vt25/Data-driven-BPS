/**
 * GeneralSimulationParametersEditor Component
 *
 * This component provides a simple editor UI for setting general simulation parameters:
 * - Number of Simulations
 * - Simulation Date and Time
 *
 * It uses localStorage to persist these settings across page reloads.
 * Changes to inputs update both the local state and localStorage.
 *
 * NOTE: Currently only implemented in the frontend, and therefore never actually used.
 */

import { useEffect, useState } from 'react';
import { Input, Label, DateTimePicker, Title } from '@ui5/webcomponents-react';

export default function GeneralSimulationParametersEditor() {
  const [numberOfSimulations, setNumberOfSimulations] = useState<string>(() => {
    return localStorage.getItem('NumberOfSimulations') || '1';
  });

  const [simulationDateAndTime, setSimulationDateAndTime] = useState<string>(() => {
    return localStorage.getItem('SimulationDateAndTime') || new Date().toISOString();
  });

  useEffect(() => {
    localStorage.setItem('NumberOfSimulations', numberOfSimulations);
  }, [numberOfSimulations]);

  useEffect(() => {
    localStorage.setItem('SimulationDateAndTime', simulationDateAndTime);
  }, [simulationDateAndTime]);

  return (
    <div style={{ padding: '24px', maxWidth: '600px', width: '100%' }}>
      <Title level="H4">General Simulation Parameters</Title>

      <div style={{ marginTop: '24px' }}>
        <div style={{ marginBottom: '20px' }}>
          <Label style={{ display: 'block', marginBottom: '6px' }} for="numberInput">
            Number of Simulations
          </Label>
          <Input
            id="numberInput"
            type="Number"
            value={numberOfSimulations}
            onInput={(e) =>
              setNumberOfSimulations((e.target as unknown as HTMLInputElement).value)
            }
            style={{ width: '100%' }}
          />
        </div>

        <div>
          <Label style={{ display: 'block', marginBottom: '6px' }} for="datetimeInput">
            Simulation Date and Time
          </Label>
          <DateTimePicker
            id="datetimeInput"
            value={simulationDateAndTime}
            onChange={(e) => setSimulationDateAndTime(e.target.value)}
            style={{ width: '100%' }}
          />
        </div>
      </div>
    </div>
  );
}
