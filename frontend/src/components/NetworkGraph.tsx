import { useEffect, useRef, useState } from 'react';
import { useEdgeFilter } from '../hooks/useEdgeFilter';
import { useSetupNetworkGraph } from '../hooks/useSetupNetworkGraph';

interface NetworkGraphProps {
  mode: string;
  jsonData: any;
  topEdgeCount: number | 'all';
  onLabelChange?: ((label: string) => void) | null;
}

/**
 * Generates a visualization of an AgentSimulator scenario in the form of a vis.js network.
 * Somewhat based on code provided by PhD student Elizabeth.
 *
 * Props:
 * @param {string} mode - The current view mode (agent, role, activity)
 * @param {any} jsonData - The data used to create the network
 * @param {number | string} topEdgeCount - Controls how many of the edges that should be visible ("Top #" or all)
 * @param {function} onLabelChange - Callback for when a node is selected
 */
const NetworkGraph = ({ mode, jsonData, topEdgeCount, onLabelChange }: NetworkGraphProps) => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const network = useSetupNetworkGraph(containerRef, jsonData, mode, setSelectedNode);
  const { filterEdges } = useEdgeFilter(network, mode);

  // Filter edges
  useEffect(() => {
    if (network) {
      filterEdges(topEdgeCount);
    }
  }, [topEdgeCount, network]);

  // Update parameter label when there is a new selected node
  useEffect(() => {
    if (onLabelChange && selectedNode) {
      const computedLabel = selectedNode.label ?? "";
      onLabelChange(computedLabel);
    }
  }, [selectedNode]);

  return (
    <div
      ref={containerRef}
      style={{ height: '500px', width: '50vw', border: '1px solid #ddd', backgroundColor: 'white' }}
    />
  );
};

export default NetworkGraph;


