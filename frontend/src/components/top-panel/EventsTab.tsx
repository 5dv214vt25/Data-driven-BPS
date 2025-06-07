/**
 * EventsTab Component
 *
 * Renders a collapsible panel for editing task-resource distributions
 * for a BPMN simulation scenario. Each task panel expands to reveal
 * resource panels, each containing editable distribution parameters.
 *
 * Features:
 * - Loads task names from BPMN XML using bpmn-js.
 * - Displays distribution parameters with dynamic labels.
 * - Allows editing of distribution parameter values.
 * - Notifies parent when edits are made.
 * - Supports collapsible/expandable task panels.
 */

import React, { useEffect, useState } from 'react';
import { Panel, Label, Input } from '@ui5/webcomponents-react';
import { JsonDataSimod, ResourceDistribution, ResourceProfile, TaskResourceDistribution }
  from '../../types/JsonDataSimod';

/**
 * Props:
 * - bpmnXml: The BPMN XML string for the process model.
 * - onParaChange?: Callback to notify parent if parameters are being edited.
 * - jsonData: The JSON object representing the current scenario state.
 * - setJsonData: Setter function to update the jsonData.
 */
interface EventsTabProps {
  bpmnXml: string;
  onParaChange?: (isEditing: boolean) => void;
  jsonData: JsonDataSimod;
  setJsonData: React.Dispatch<React.SetStateAction<JsonDataSimod>>;
}

const EventsTab: React.FC<EventsTabProps> = ({ bpmnXml, onParaChange, jsonData, setJsonData }) => {
  const [idToName, setIdToName] = useState<Record<string, string>>({});
  const [expandedTasks, setExpandedTasks] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState<boolean>(true);
  const [edited, setEdited] = useState(false);

  useEffect(() => {
    onParaChange?.(edited);
  }, [edited]);

  // Mapping from distribution type to human-readable parameter labels
  const labelsByType: Record<string, string[]> = {
    gamma: ['Mean', 'Variance', 'Min', 'Max'],
    lognorm: ['Mean', 'Variance', 'Min', 'Max'],
    norm: ['Mean', 'SD', 'Min', 'Max'],
    uniform: ['Min', 'Max'],
    expon: ['Mean', 'Min', 'Max'],
    fix: ['Mean'],
  };

  // Load BPMN XML and extract task names using bpmn-js
  useEffect(() => {
    if (!bpmnXml.trim().startsWith('<')) {
      setLoading(false);
      return;
    }

    setLoading(true);
    import('bpmn-js/lib/Modeler').then(({ default: Modeler }) => {
      const modelerInstance = new Modeler();
      modelerInstance.importXML(bpmnXml).then(() => {
        const registry: any = modelerInstance.get('elementRegistry');
        const map: Record<string, string> = {};
        registry.getAll().forEach((el: any) => {
          map[el.id] = el.businessObject?.name || el.id;
        });
        setIdToName(map);
        modelerInstance.destroy();
        setLoading(false);
      });
    });
  }, [bpmnXml]);

  const getTaskName = (taskId: string) => idToName[taskId] || taskId;
  const getResourceName = (resourceId: string) => {
    const list = jsonData.resource_profiles?.flatMap((p: ResourceProfile) => p.resource_list) || [];
    return list.find((r) => r.id === resourceId)?.name || resourceId;
  };

  // Handle parameter change: update jsonData with new value
  const handleParamChange = (
    taskId: string,
    resourceId: string,
    paramIndex: number,
    value: number
  ) => {
    setJsonData((prev: JsonDataSimod) => {
      const updated: JsonDataSimod = { ...prev };
      //eslint-disable-next-line camelcase
      updated.task_resource_distribution = updated.task_resource_distribution?.map(
        (task: TaskResourceDistribution) => {
          if (task.task_id !== taskId) { return task; }
          const updatedResources = task.resources.map(
            (resource: ResourceDistribution) => {
              if (resource.resource_id !== resourceId) { return resource; }
              const params = [...resource.distribution_params];
              if (params[paramIndex]) {
                params[paramIndex] = { ...params[paramIndex], value };
              }
              return { ...resource, distribution_params: params }; //eslint-disable-line camelcase
            }
          );
          return { ...task, resources: updatedResources };
        }
      );
      return updated;
    });
    setEdited(true);
  };

  const toggleTask = (taskId: string) => {
    setExpandedTasks((prev: Set<string>) => {
      const newSet = new Set(prev);
      if (newSet.has(taskId)) { newSet.delete(taskId); }
      else { newSet.add(taskId); }
      return newSet;
    });
  };

  // Show loading spinner if BPMN parsing is in progress
  if (loading) { return <div>Loading...</div>; }

  return (
    <div className="events-tab">
      {jsonData.task_resource_distribution && jsonData.task_resource_distribution.length > 0 ? (
        jsonData.task_resource_distribution.map(
          (task: TaskResourceDistribution) => (
            <Panel
              key={task.task_id}
              headerText={getTaskName(task.task_id)}
              collapsed={!expandedTasks.has(task.task_id)}
              onToggle={() => toggleTask(task.task_id)}
              style={{ marginBottom: '1rem', marginTop: '1rem' }}
            >
              {task.resources.map(
                (resource: ResourceDistribution) => (
                  <Panel
                    key={resource.resource_id}
                    fixed={true}
                    style={{
                      marginBottom: '1rem',
                      padding: '1rem',
                      border: '1px solid #e0e0e0',
                      boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)'
                    }}
                  >
                    <div style={{ fontWeight: 'bold', marginBottom: '0.5rem' }}>
                      Resource: {getResourceName(resource.resource_id)}
                    </div>
                    <div style={{ marginLeft: '1rem' }}>
                      <div style={{ fontWeight: 'bold', marginBottom: '0.5rem', }}>
                        Distribution: {resource.distribution_name}
                      </div>
                      <div style={{
                        display: 'flex',
                        flexWrap: 'wrap',
                        gap: '1rem',
                        marginTop: '0.5rem'
                      }}>
                        {resource.distribution_params.map((param, i) => (
                          <div
                            key={i}
                            style={{
                              display: 'flex',
                              flexDirection: 'column',
                              minWidth: '120px'
                            }}
                          >
                            <Label>
                              {labelsByType[resource.distribution_name][i] || `Param ${i + 1}`}:
                            </Label>
                            <Input
                              type="Number"
                              value={String(param.value)}
                              onInput={e =>
                                handleParamChange(
                                  task.task_id,
                                  resource.resource_id,
                                  i,
                                  parseFloat(e.target.value)
                                )
                              }
                            />
                          </div>
                        ))}
                      </div>
                    </div>
                  </Panel>
                )
              )}
            </Panel>
          )
        )
      ) : (
        <p>No task resource distribution data available.</p>
      )}
    </div>
  );
};

export default EventsTab;
