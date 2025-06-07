import { useCallback, useRef } from 'react';
import { Network } from 'vis-network';


/**
 * Takes a NetworkGraph as input and applies a filter for which edges to show.
 * The majority of the logic is taken from the visualization tool 
 * provided by PhD student Elizabeth with minor changes to make it work in react
 * @param network The networkGraph
 * @param mode Select between the three graphs 'agent' | 'role' | 'activity'
 * @returns Nothing, simply updates the given networkgraph
 */
export function useEdgeFilter(network: Network | null, mode: string) {
  const originalEdgeData = useRef<{ [key: string]: any[] }>({});

  /**
   * Gets all the original edges.
   */
  const getCurrentOriginalEdges = useCallback(() => {
    const edges = (network as any)?.body?.data?.edges;
    if (!edges) {
      console.error('Network not initialized');
      return [];
    }

    if (!originalEdgeData.current[mode]) {
      originalEdgeData.current[mode] = [...edges.get()];
    }

    return originalEdgeData.current[mode];
  }, [mode, network]);

  /**
   * Gets the edge probability of the given edge
   * @param edge The edge.
   * @returns The probability of the given edge.
   */
  const getEdgeProbability = (edge: any): number => {
    if (edge.probability !== undefined) {return parseFloat(edge.probability);}
    if (edge.label) {
      const match = edge.label.match(/(\d+(\.\d+)?)/);
      if (match) {return parseFloat(match[1]);}
    }
    return 0;
  };


  /**
   * The "main" funciton for filtering edges
   * It goes through all the original edges and filters through them updating the 
   * network to only show the edges with the correct edge probability.
   */
  const filterEdges = useCallback(
    (topCount: number | 'all') => {
      const edges = (network as any)?.body?.data?.edges;

      if (!edges) {
        console.error('Network not initialized');
        return;
      }

      const originalEdgeSet = getCurrentOriginalEdges();

      if (topCount === 'all') {
        edges.update(originalEdgeSet.map(edge => ({ id: edge.id, hidden: false })));
        return;
      }

      // Special edges are edges with 100% probability
      const specialEdges = originalEdgeSet.filter(edge => getEdgeProbability(edge) === 100);
      const specialEdgeIds = new Set(specialEdges.map(edge => edge.id));

      const edgesBySource: { [key: string]: any[] } = {};
      originalEdgeSet.forEach(edge => {
        if (!specialEdgeIds.has(edge.id)) {
          edgesBySource[edge.from] = edgesBySource[edge.from] || [];
          edgesBySource[edge.from].push(edge);
        }
      });

      const edgesToShow = [...specialEdges];

      Object.values(edgesBySource).forEach(edgeList => {
        const sorted = edgeList
          .map(edge => ({ edge, probValue: getEdgeProbability(edge) }))
          .sort((a, b) => b.probValue - a.probValue);

        let cutoff: number | null = null;
        for (let i = 0; i < sorted.length; i++) {
          if (i < topCount || (cutoff !== null && sorted[i].probValue === cutoff)) {
            edgesToShow.push(sorted[i].edge);
            cutoff = sorted[i].probValue;
          } else {
            break;
          }
        }
      });

      const idsToShow = new Set(edgesToShow.map(edge => edge.id));
      edges.update(originalEdgeSet.map(edge => ({
        id: edge.id,
        hidden: !idsToShow.has(edge.id)
      })));
    },
    [network, getCurrentOriginalEdges]
  );

  return { filterEdges };
}