import { useEffect, useState } from 'react';
import { Network } from 'vis-network';

interface InternalNetwork extends Network {
  body: {
    data: {
      nodes: {
        get: (id: string) => any;
      };
    };
  };
  topEdgeCount: number | 'all';
}

/**
 * Hook that initializes an AgentSimulator network graph (vis.js network).
 * Heavily based on PhD Student Elizabeth's code.
 */
export function useSetupNetworkGraph(
  containerRef: React.RefObject<null | HTMLDivElement>, // HTML Element where the network should be rendered
  jsonData: any,
  mode: string,
  setSelectedNode: (node: any) => void
): Network | null {
  const [network, setNetwork] = useState<Network | null>(null);

  useEffect(() => {
    if (!jsonData || !containerRef) {return;}

    const activityNodes = JSON.parse(jsonData.activity_nodes);
    const activityEdges = JSON.parse(jsonData.activity_edges);
    const agentNetwork = {
      nodes: JSON.parse(jsonData.agent_nodes),
      edges: JSON.parse(jsonData.agent_edges),
    };
    const roleNetwork = {
      nodes: JSON.parse(jsonData.role_nodes),
      edges: JSON.parse(jsonData.role_edges),
    };

    const data = { nodes: activityNodes, edges: activityEdges };
    const options = {
      physics: { enabled: true },
      edges: {
        arrows: { to: { enabled: true, scaleFactor: 0.4 } },
        smooth: { enabled: true, type: 'curvedCW', roundness: 0.1 },
        selfReference: { size: 20, angle: 0.7853981634 },
        color: { inherit: 'from' },
      },
    };

    const newNetwork = new Network(containerRef.current!, data, options);

    if (mode === 'agent') {
      newNetwork.setData(agentNetwork);
    } else if (mode === 'role') {
      newNetwork.setData(roleNetwork);
    }

    newNetwork.on('click', (params) => {
      if (params.nodes.length > 0) {
        const clickedNodeId = params.nodes[0];
        const internalNetwork = newNetwork as InternalNetwork;
        const clickedNode = internalNetwork.body.data.nodes.get(clickedNodeId);
        setSelectedNode(clickedNode);
      }
    });

    setNetwork(newNetwork);

    return () => {
      newNetwork.destroy();
    };
  }, [jsonData, mode, containerRef, setSelectedNode]);

  return network;
}

