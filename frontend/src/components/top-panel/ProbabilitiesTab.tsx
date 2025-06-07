/**
 * ProbabilitiesTab Component
 *
 * This component displays and allows editing of gateway branching probabilities
 * for sequence flows in a BPMN diagram.
 */

import React, { useEffect, useState } from 'react';
import { Panel, Label, Input, Button } from '@ui5/webcomponents-react';
import { JsonDataSimod } from '../../types/JsonDataSimod';

/**
 * Props definition for the ProbabilitiesTab component.
 * - bpmnXml: The BPMN string used to parse gateways and paths.
 * - onParaChange: Optional callback triggered when editing.
 * - jsonData: The overall simulation data containing gateway branching probabilities.
 * - setJsonData: Setter function to update the simulation data state.
 */
interface ProbabilitiesTabProps {
  bpmnXml: string;
  onParaChange?: (isEditing: boolean) => void;
  jsonData: JsonDataSimod;
  setJsonData: React.Dispatch<React.SetStateAction<JsonDataSimod>>;
}

const ProbabilitiesTab: React.FC<ProbabilitiesTabProps> = ({
  bpmnXml,
  onParaChange,
  jsonData,
  setJsonData
}) => {
  const [idToName, setIdToName] = useState<Record<string, string>>({});
  const [expandedGateways, setExpandedGateways] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState<boolean>(true);
  const [bpmnLoadError, setBpmnLoadError] = useState<string | null>(null);
  const [edited, setEdited] = useState(false);

  // Notify parent component when editing state changes.
  useEffect(() => {
    onParaChange?.(edited);
  }, [edited, onParaChange]);

  /**
   * Loads BPMN XML and builds a mapping from element IDs to their names.
   * Also extracts sequence flow targets to display target names in the UI.
   */
  useEffect(() => {
    if (!bpmnXml || !bpmnXml.trim().startsWith('<')) {
      setLoading(false);
      setBpmnLoadError('Invalid BPMN XML content');
      return;
    }

    setLoading(true);
    setBpmnLoadError(null);

    const loadBpmnNames = async () => {
      try {
        // Dynamic import for bpmn-js
        const { default: Modeler } = await import('bpmn-js/lib/Modeler');
        const modeler = new Modeler();

        await modeler.importXML(bpmnXml);

        const elementRegistry: any = modeler.get('elementRegistry');
        const map: Record<string, string> = {};
        const sequenceFlowTargets: Record<string, string> = {};

        const allElements = elementRegistry.getAll();

        // First pass: collect all element names and map them by ID
        allElements.forEach((element: any) => {
          const businessObject = element.businessObject;
          let displayName = element.id;

          if (businessObject?.name) {
            displayName = businessObject.name;
          } else if (businessObject?.label) {
            displayName = businessObject.label;
          } else if (businessObject?.$attrs?.name) {
            displayName = businessObject.$attrs.name;
          }

          map[element.id] = displayName;

          // For sequence flows, store target reference for easier naming later
          if (element.type === 'bpmn:SequenceFlow' && businessObject?.targetRef) {
            const targetId =
              typeof businessObject.targetRef === 'string'
                ? businessObject.targetRef
                : businessObject.targetRef.id || businessObject.targetRef;
            sequenceFlowTargets[element.id] = targetId;
          }
        });

        // Second pass: enhance sequence flow names with target names
        Object.entries(sequenceFlowTargets).forEach(([sequenceFlowId, targetId]) => {
          const targetName = map[targetId];
          if (targetName && targetName !== targetId) {
            map[sequenceFlowId] = targetName;
          } else {
            map[sequenceFlowId] = `Target: ${targetId}`;
          }
        });

        setIdToName(map);
        modeler.destroy();
        setLoading(false);
      } catch (error) {
        console.error('Error loading BPMN:', error);
        setBpmnLoadError(`Failed to load BPMN: ${error}`);
        setLoading(false);
      }
    };

    loadBpmnNames();
  }, [bpmnXml]);

  /**
   * Returns the display name for a gateway panel.
   *
   * @param _gatewayId - The ID of the gateway.
   * @param index - Index of the gateway in the list.
   */
  const getGatewayName = (_gatewayId: string, index: number) => {
    return `Gateway ${index + 1}`;
  };

  /**
   * Returns the display name for a path (sequence flow).
   *
   * @param pathId - The ID of the path.
   */
  const getPathName = (pathId: string) => {
    const name = idToName[pathId];
    if (name && name !== pathId) {
      return name;
    }
    return `Path: ${pathId}`;
  };

  /**
   * Handles updating the probability value for a given path in a given gateway.
   *
   * @param gatewayId - The ID of the gateway.
   * @param pathId - The ID of the path.
   * @param value - The new probability value.
   */
  const handleProbabilityChange = (gatewayId: string, pathId: string, value: number) => {
    setJsonData((prev: JsonDataSimod) => {
      const updated: JsonDataSimod = { ...prev };
      // eslint-disable-next-line camelcase
      updated.gateway_branching_probabilities = updated.gateway_branching_probabilities?.map((gateway) =>
        gateway.gateway_id === gatewayId
          ? {
            ...gateway,
            probabilities: gateway.probabilities.map((prob) =>
              prob.path_id === pathId ? { ...prob, value } : prob
            ),
          }
          : gateway
      );
      return updated;
    });
    setEdited(true);
  };

  /**
   * Balances the selected path's probability by adjusting it so that the sum equals 1.
   *
   * @param gatewayId - The ID of the gateway.
   * @param index - The index of the selected path in the probabilities list.
   */
  const handleBalanceClick = (gatewayId: string, index: number) => {
    const gateway = jsonData.gateway_branching_probabilities?.find((g) => g.gateway_id === gatewayId);
    if (!gateway) { return };

    const total = gateway.probabilities.reduce((sum, p) => sum + p.value, 0);
    const diff = 1.0 - total;
    const updatedProbabilities = [...gateway.probabilities];
    const currentValue = updatedProbabilities[index].value;
    const newValue = Math.max(0, Math.min(1, currentValue + diff));

    updatedProbabilities[index] = {
      ...updatedProbabilities[index],
      value: parseFloat(newValue.toFixed(4)),
    };

    setJsonData((prev) => ({
      ...prev,
      // eslint-disable-next-line camelcase
      gateway_branching_probabilities: prev.gateway_branching_probabilities?.map((g) =>
        g.gateway_id === gatewayId ? { ...g, probabilities: updatedProbabilities } : g
      ),
    }));

    setEdited(true);
  };

  /**
   * Toggles the expanded/collapsed state of a gateway panel.
   *
   * @param gatewayId - The ID of the gateway.
   */
  const toggleGateway = (gatewayId: string) => {
    setExpandedGateways((prev) => {
      const newSet = new Set(prev);
      newSet.has(gatewayId) ? newSet.delete(gatewayId) : newSet.add(gatewayId);
      return newSet;
    });
  };

  // Render: Loading or Error states
  if (loading) {
    return <div>Loading BPMN diagram...</div>;
  }

  if (bpmnLoadError) {
    return (
      <div style={{ color: 'red', padding: '1rem' }}>
        <h3>Error loading BPMN:</h3>
        <p>{bpmnLoadError}</p>
        <h4>Debug Info:</h4>
        <p>BPMN XML length: {bpmnXml?.length || 0}</p>
        <p>BPMN XML preview: {bpmnXml?.substring(0, 100)}...</p>
      </div>
    );
  }

  // Main render
  return (
    <div className="probabilities-tab">
      {jsonData.gateway_branching_probabilities?.length ? (
        jsonData.gateway_branching_probabilities.map((gateway, index) => {
          const total = gateway.probabilities.reduce((sum, p) => sum + p.value, 0);
          const isValidTotal = Math.abs(total - 1.0) < 0.0001;

          return (
            <Panel
              key={gateway.gateway_id}
              headerText={getGatewayName(gateway.gateway_id, index)}
              collapsed={!expandedGateways.has(gateway.gateway_id)}
              onToggle={() => toggleGateway(gateway.gateway_id)}
              style={{ marginBottom: '1rem' }}
            >
              {/* Render all paths within the gateway */}
              {gateway.probabilities.map((prob, index) => (
                <div key={prob.path_id} style={{ marginBottom: '1rem' }}>
                  <Label>Path: {getPathName(prob.path_id)}</Label>
                  <div style={{ marginLeft: '1rem' }}>
                    <Label>Probability:</Label>
                    <Input
                      type="Number"
                      value={String(prob.value)}
                      onInput={(e) =>
                        handleProbabilityChange(
                          gateway.gateway_id,
                          prob.path_id,
                          parseFloat((e.target as unknown as HTMLInputElement).value)
                        )
                      }
                    />
                    <Button onClick={() => handleBalanceClick(gateway.gateway_id, index)}>Balance</Button>
                  </div>
                </div>
              ))}
              {/* Display warning if total probability is invalid */}
              {!isValidTotal && (
                <div style={{ color: 'red', marginTop: '0.5rem' }}>
                  Total probability must equal 1.0. Current: {total.toFixed(4)}
                </div>
              )}
            </Panel>
          );
        })
      ) : (
        <p>No gateway branching probabilities data available.</p>
      )}
    </div>
  );
};

export default ProbabilitiesTab;
