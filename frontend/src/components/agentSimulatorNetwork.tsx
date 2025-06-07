import React from 'react';
import { RadioButton } from '@ui5/webcomponents-react';
import { NetworkGraphSlider } from '../components/NetworkGraphSlider';
import NetworkGraph from '../components/NetworkGraph';

type ModeType = "role" | "agent" | "activity";

interface AgentSimulatorNetworkProps {
  mode: string;
  setMode: React.Dispatch<React.SetStateAction<ModeType>>;
  onLabelChange?: ((label: string) => void) | null;
  jsonDataAgentSim: any;
  topEdgeCount: number | 'all';
  setTopEdgeCount: (value: number | 'all') => void;
}

/**
 * Renders an Agent Simulator network graph with some controllers (Radio buttons 
 * for different view modes and a "NetworkGraphSlider" to adjust the amount of 
 * edges that should be visible). 
 *
 * Props:
 * @param {string} mode - The current view movde (agent, role, activity). 
 *                        NOTE: This may seem unnecessary here but it is used 
 *                        as a callback parameter used by the FormComponent
 * @param {function} setMode - Callback function to set the above mentioned mode 
 *                             and send the new value between different components
 * @param {function} onLabelChange - Callback for when a node is selected
 * @param {any} jsonDataAgentSim - The data used to create the network
 * @param {number | string} topEdgeCount - Controls how many of the edges that 
 *                                         should be visible ("Top #" or all)
 * @param {function} setTopEdgeCount - Callback function to set how many edges 
 *                                     that should be visible
 *
 */
const AgentSimulatorNetwork: React.FC<AgentSimulatorNetworkProps> = ({
  mode,
  setMode,
  onLabelChange,
  jsonDataAgentSim,
  topEdgeCount,
  setTopEdgeCount
}) => {

  return (
    <div
      id="network-graph"
      style={{ width: '100%', display: 'flex', flexDirection: 'column' }}
    >
      <div style={{ display: 'flex', flexDirection: 'row', gap: '4em' }}>
        <div>
          <RadioButton name="viewMode" checked={mode === 'agent'} text="agent" onChange={() => setMode('agent')} />
          <RadioButton name="viewMode" checked={mode === 'role'} text="role" onChange={() => setMode('role')} />
          <RadioButton name="viewMode" checked={mode === 'activity'}
            text="activity" onChange={() => setMode('activity')} />
        </div>
        <NetworkGraphSlider topEdgeCount={topEdgeCount} setTopEdgeCount={setTopEdgeCount} />
      </div>
      <NetworkGraph
        mode={mode}
        jsonData={jsonDataAgentSim}
        topEdgeCount={topEdgeCount}
        onLabelChange={onLabelChange}
      />
    </div>
  );
};

export default AgentSimulatorNetwork;
