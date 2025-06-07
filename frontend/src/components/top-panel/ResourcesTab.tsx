/**
 * ResourcesTab Component
 *
 * This component displays and allows editing of resource profiles,
 * including amount, cost per hour, calendar assignment, and assigned tasks.
 */

import React, { useEffect, useState } from 'react';
import { Panel, Label, Input, Select, Option } from '@ui5/webcomponents-react';
import { JsonDataSimod, Resource } from '../../types/JsonDataSimod';

/**
 * Props definition for the ResourcesTab component.
 * - bpmnXml: The BPMN string used to parse tasks and their names.
 * - onParaChange: Optional callback that is triggered when editing.
 * - jsonData: The overall simulation data containing resource profiles.
 * - setJsonData: Setter function to update the simulation data state.
 */
interface ResourcesTabProps {
  bpmnXml: string;
  onParaChange?: (isEditing: boolean) => void;
  jsonData: JsonDataSimod;
  setJsonData: React.Dispatch<React.SetStateAction<JsonDataSimod>>;
}

const ResourcesTab: React.FC<ResourcesTabProps> = ({ bpmnXml, onParaChange, jsonData, setJsonData }) => {
  const [idToName, setIdToName] = useState<Record<string, string>>({});
  const [expandedResources, setExpandedResources] = useState<Set<string>>(new Set());
  const [edited, setEdited] = useState(false);

  useEffect(() => {
    onParaChange?.(edited);
  }, [edited]);

  /**
   * Parses the BPMN XML to build a mapping from element IDs to their names.
   * This is used to show assigned task names instead of IDs.
   */
  useEffect(() => {
    if (!bpmnXml.trim().startsWith('<')) { return; }
    import('bpmn-js/lib/Modeler').then(({ default: Modeler }) => {
      const modeler = new Modeler();
      modeler.importXML(bpmnXml).then(() => {
        const registry: any = modeler.get('elementRegistry');
        const map: Record<string, string> = {};
        registry.getAll().forEach((el: any) => {
          map[el.id] = el.businessObject?.name || el.id;
        });
        setIdToName(map);
        modeler.destroy();
      });
    });
  }, [bpmnXml]);

  const getTaskName = (taskId: string) => idToName[taskId] || taskId;

  /**
   * Updates the specified parameter of a resource.
   *
   * @param resourceId - The ID of the resource to update.
   * @param param - The parameter to update (amount, cost_per_hour, calendar).
   * @param value - The new value for the parameter.
   */
  const handleParamChange = (
    resourceId: string,
    param: keyof Resource,
    value: string | number
  ) => {
    setJsonData((prev: JsonDataSimod) => {
      const updated: JsonDataSimod = { ...prev };
      //eslint-disable-next-line camelcase
      updated.resource_profiles = updated.resource_profiles?.map(profile => ({
        ...profile,
        //eslint-disable-next-line camelcase
        resource_list: profile.resource_list.map(resource =>
          resource.id === resourceId
            ? { ...resource, [param]: value }
            : resource
        ),
      }));
      return updated;
    });
    setEdited(true);
  };

  const toggleResource = (resourceId: string) => {
    setExpandedResources(prev => {
      const newSet = new Set(prev);
      newSet.has(resourceId) ? newSet.delete(resourceId) : newSet.add(resourceId);
      return newSet;
    });
  };

  return (
    <div className="resources-tab">
      {jsonData.resource_profiles && jsonData.resource_profiles.length > 0 ? (
        jsonData.resource_profiles.flatMap(profile =>
          profile.resource_list.map(resource => (
            <Panel
              key={resource.id}
              headerText={resource.name}
              collapsed={!expandedResources.has(resource.id)}
              onToggle={() => toggleResource(resource.id)}
              style={{ marginBottom: '1rem' }}
            >
              <div style={{ marginBottom: '1rem' }}>
                <Label>Resource ID: {resource.id}</Label>
                <div style={{ marginLeft: '1rem' }}>
                  <Label>Amount:</Label>
                  <Input
                    type="Number"
                    value={String(resource.amount)}
                    onInput={e =>
                      handleParamChange(
                        resource.id,
                        'amount',
                        parseFloat(e.target.value)
                      )
                    }
                  />
                </div>
                <div style={{ marginLeft: '1rem' }}>
                  <Label>Cost per Hour:</Label>
                  <Input
                    type="Number"
                    value={String(resource.cost_per_hour)}
                    onInput={e =>
                      handleParamChange(
                        resource.id,
                        'cost_per_hour',
                        parseFloat(e.target.value)
                      )
                    }
                  />
                </div>
                <div style={{ marginLeft: '1rem' }}>
                  <Label>Calendar:</Label>
                  <Select
                    value={resource.calendar}
                    onChange={e =>
                      handleParamChange(resource.id, 'calendar', e.target.value)
                    }
                  >
                    <Option selected>{resource.calendar}</Option>
                  </Select>
                </div>
                <div style={{ marginLeft: '1rem' }}>
                  <Label>
                    Assigned Tasks:{' '}
                    {resource.assignedTasks.map(taskId => getTaskName(taskId)).join(', ')}
                  </Label>
                </div>
              </div>
            </Panel>
          ))
        )
      ) : (
        <p>No resource profiles data available.</p>
      )}
    </div>
  );
};

export default ResourcesTab;
