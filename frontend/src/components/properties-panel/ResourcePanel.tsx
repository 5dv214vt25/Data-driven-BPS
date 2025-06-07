/**
 * ResourcePanel Component
 *
 * Renders a collapsible panel for a single resource within a task, showing
 * its ID, distribution name, and—if expanded—a distribution parameter editor.
 */

import { Button, Label } from '@ui5/webcomponents-react';
import DistributionEditor from './DistributionEditor';

/**
 * Props:
 * - resource: An object containing resource data (id, name, distribution, etc.).
 * - expanded: Boolean indicating whether the panel is expanded.
 * - toggle: Function to toggle the panel's expanded/collapsed state.
 * - onParamChange: Callback function to handle changes to distribution parameters.
 */
interface ResourcePanelProps {
  resource: any;
  expanded: boolean;
  toggle: () => void;
  onParamChange: (paramIndex: number, newValue: number) => void;
}

export default function ResourcePanel({ resource, expanded, toggle, onParamChange }: ResourcePanelProps) {
  return (
    <div className="resource">
      <Label>{resource.resource_id}</Label>

      <Label>Distribution: {resource.distribution_name}</Label>
      <Button onClick={toggle} style={{ marginTop: '5px' }}>
        {expanded ? 'Collapse' : 'Expand'}
      </Button>
      {expanded && (
        <DistributionEditor
          distributionName={resource.distribution_name}
          distributionParams={resource.distribution_params}
          onChange={onParamChange}
        />
      )}
    </div>
  );
}
