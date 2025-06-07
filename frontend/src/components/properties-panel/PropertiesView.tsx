/**
 * PropertiesView Component
 *
 * This component renders a properties panel for BPMN elements,
 * integrating tightly with the bpmn-js modeler. It displays relevant
 * details and editors based on the type of element selected:
 *
 * - **Tasks**: Shows resource distributions and allows parameter editing.
 * - **Gateways**: Shows and edits branching probabilities.
 * - **Sequence Flows**: Displays path probabilities.
 *
 * It listens for selection changes in the BPMN modeler to update
 * its state and display the appropriate editor.
 */

import { useEffect, useState } from 'react';
import { TabContainer, Tab, Label } from '@ui5/webcomponents-react';
import GatewayEditor from './GatewayEditor';
import ResourcePanel from './ResourcePanel';
import ProbabilityEditor from './ProbabilityEditor';
import './PropertiesView.css';
import { GatewayBranchingProbability, JsonDataSimod, PathProbability } from '../../types/JsonDataSimod';

/**
 * Props:
 * - modeler: The bpmn-js modeler instance, used to access selected elements
 *   and BPMN metadata.
 * - jsonData: The current JSON simulation data to be displayed and edited.
 * - setJsonData: Setter function to update the simulation data.
 */
interface PropertiesViewProps {
  modeler: any;
  jsonData: JsonDataSimod;
  setJsonData: React.Dispatch<React.SetStateAction<JsonDataSimod>>;
}

export default function PropertiesView({ modeler, jsonData, setJsonData }: PropertiesViewProps) {
  const [selectedElements, setSelectedElements] = useState<any[]>([]);
  const [element, setElement] = useState<any>(null);
  const [resourceIds, setResourceIds] = useState<string[]>([]);
  const [distributionData, setDistributionData] = useState<any[]>([]);
  const [probabilityValue, setProbabilityValue] = useState<number | null>(null);
  const [gatewayProbabilities, setGatewayProbabilities] = useState<PathProbability[]>([]);
  const [expandedResources, setExpandedResources] = useState<Set<string>>(new Set());

  const toggleResourceExpansion = (id: string) => {
    setExpandedResources((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(id)) { newSet.delete(id); }
      else { newSet.add(id); }
      return newSet;
    });
  };

  const isGateway = (el: any) => el?.type === 'bpmn:ExclusiveGateway';
  const isTask = (el: any) => el?.type === 'bpmn:Task';
  const isPath = (el: any) => el?.type === 'bpmn:SequenceFlow';

  // Load jsonData parameters for the selected element.
  useEffect(() => {
    if (!element) { return; }
    if (isGateway(element)) {
      const gatewayMatch = jsonData.gateway_branching_probabilities?.find(
        (g) => g.gateway_id === element.id
      );
      setGatewayProbabilities(gatewayMatch?.probabilities || []);
    } else if (isTask(element)) {
      const taskMatch = jsonData.task_resource_distribution?.find(
        (t) => t.task_id === element.id
      );
      if (taskMatch) {
        const ids = taskMatch.resources.map((res) => res.resource_id);
        setResourceIds(ids);
        setDistributionData(taskMatch.resources);
      } else {
        setResourceIds([]);
        setDistributionData([]);
      }
    } else if (isPath(element)) {
      let found = false;
      for (const gateway of jsonData.gateway_branching_probabilities || []) {
        const match = gateway.probabilities.find((p) => p.path_id === element.id);
        if (match) {
          setProbabilityValue(match.value);
          found = true;
          break;
        }
      }
      if (!found) { setProbabilityValue(null); }
    }
  }, [element?.id, jsonData]);

  // Set updated probability value in jsonData.
  const handleProbabilityChange = (pathId: string, value: number) => {
    setJsonData((prevData: JsonDataSimod) => {
      const updatedGateways = (prevData.gateway_branching_probabilities || []).map(
        (gateway: GatewayBranchingProbability) => {
          const updatedProbs = gateway.probabilities.map(
            (prob: PathProbability) =>
              prob.path_id === pathId ? { ...prob, value } : prob
          );
          return { ...gateway, probabilities: updatedProbs };
        }
      );

      return {
        ...prevData,
        gateway_branching_probabilities: updatedGateways, //eslint-disable-line camelcase
      };
    });
  };

  // Set updated distribution parameter value in jsonData.
  const handleDistributionParamChange = (
    resourceId: string,
    paramIndex: number,
    newValue: number
  ) => {
    setJsonData((prevData: JsonDataSimod) => {
      const selectedTask =
        prevData.task_resource_distribution?.find(
          (t) => t.task_id === element.id
        );
      if (!selectedTask) { return prevData; }

      const updatedResources = selectedTask.resources.map((res) => {
        if (res.resource_id === resourceId) {
          const updatedParams = [...res.distribution_params];
          if (updatedParams[paramIndex]) {
            updatedParams[paramIndex] = { ...updatedParams[paramIndex], value: newValue };
          }
          return { ...res, distribution_params: updatedParams }; //eslint-disable-line camelcase
        }
        return res;
      });

      const updatedTaskDist = (prevData.task_resource_distribution || []).map((task) =>
        task.task_id === element.id ? { ...task, resources: updatedResources } : task
      );

      return { ...prevData, task_resource_distribution: updatedTaskDist }; //eslint-disable-line camelcase
    });
  };

  // Get the name of the target element given the id of a path.
  const getTargetElementName = (pathId: string) => {
    const elementRegistry = modeler.get('elementRegistry');
    const sequenceFlow = elementRegistry.get(pathId);
    if (!sequenceFlow || !sequenceFlow.businessObject?.targetRef) { return 'Unknown Target'; }
    const targetRef = sequenceFlow.businessObject.targetRef;
    return (
      targetRef.name ||
      (targetRef.$type.includes('Task') && 'Task') ||
      (targetRef.$type.includes('Gateway') && 'Gateway') ||
      (targetRef.$type.includes('Event') && 'Event') ||
      'Unnamed Element'
    );
  };

  // Update when the selection has changed in the bpmn modeler
  useEffect(() => {
    const onSelectionChanged = (e: any) => {
      setSelectedElements(e.newSelection);
      setElement(e.newSelection[0]);
    };
    modeler.on('selection.changed', onSelectionChanged);
    return () => {
      modeler.off('selection.changed', onSelectionChanged);
    };
  }, [modeler]);

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <TabContainer
        contentBackgroundDesign="Solid"
        headerBackgroundDesign="Solid"
        tabLayout="Inline"
        style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}
      >
        <Tab text="Details">
          <div style={{ display: 'flex', flexDirection: 'column', height: '100%', minHeight: 0 }}>

            <div style={{ flex: 1, overflowY: 'auto', minHeight: 0, height: '100%' }}>
              {selectedElements.length === 1 && (
                <div className="element-properties">
                  {/* <div><Label>ID:</Label><span>{element.id}</span></div> */}
                  {/* <div><Label>Type:</Label><span>{element.type}</span></div> */}
                  <div><Label>Name:</Label><span>{element.businessObject?.name || '—'}</span></div>

                  {isTask(element) ? (
                    <div className="resources">
                      {resourceIds.map((id) => {
                        const resource = distributionData.find((res: any) => res.resource_id === id);
                        const isExpanded = expandedResources.has(id);
                        return (
                          <ResourcePanel
                            key={id}
                            resource={resource}
                            expanded={isExpanded}
                            toggle={() => toggleResourceExpansion(id)}
                            onParamChange={(paramIndex, newValue) =>
                              handleDistributionParamChange(resource.resource_id, paramIndex, newValue)
                            }
                          />
                        );
                      })}
                    </div>
                  ) : isGateway(element) ? (
                    gatewayProbabilities.length > 0 ? (
                      <GatewayEditor
                        probabilities={gatewayProbabilities}
                        getTargetElementName={getTargetElementName}
                        onChange={(updated) => {
                          setGatewayProbabilities(updated);
                          updated.forEach((p) => handleProbabilityChange(p.path_id, p.value));
                        }}
                      />
                    ) : (
                      <span>No probabilities found for this gateway.</span>
                    )
                  ) : isPath(element) ? (
                    <ProbabilityEditor value={probabilityValue} />
                  ) : (
                    <span>No relevant details found for this element.</span>
                  )}
                </div>
              )}
              {selectedElements.length === 0 && <span>Please select an element.</span>}
              {selectedElements.length > 1 && <span>Please select a single element.</span>}
            </div>
          </div>
        </Tab>
      </TabContainer>
    </div>
  );
}
