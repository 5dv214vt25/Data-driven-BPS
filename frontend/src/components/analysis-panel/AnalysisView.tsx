import React, { useState } from 'react';
import { Panel, Text } from '@ui5/webcomponents-react';
import '../../assets/styles/Analysis.css';

/**
 * Interface representing the analysis result data structure
 * @interface AnalysisResult
 */
interface AnalysisResult {
  cost?: number;
  cycle_time_average?: number;
  cycle_time_per_activity?: number;
  per_activity_waiting_time?: number;
  resource_utilization?: number;
  waiting_time?: number;
  cycle_time_median?: number;
}

/**
 * Props for the AnalysisView component
 * @interface AnalysisViewProps
 */
interface AnalysisViewProps {
  analysis: AnalysisResult;
  title: string;
  showUndefined?: boolean;
}

/**
 * Component that displays analysis results in a card format with expandable sections
 * @component
 * @param {AnalysisViewProps} props - The component props
 * @returns {JSX.Element} The rendered AnalysisView component
 */
const AnalysisView: React.FC<AnalysisViewProps> = ({ analysis, title, showUndefined = false }) => {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());

  /**
   * Toggles the expanded state of a section
   * @param {string} sectionId - The ID of the section to toggle
   */
  const toggleSection = (sectionId: string) => {
    setExpandedSections(prev => {
      const newSet = new Set(prev);
      newSet.has(sectionId) ? newSet.delete(sectionId) : newSet.add(sectionId);
      return newSet;
    });
  };

  /**
   * Formats a number as a percentage string
   * @param {number} [value] - The value to format
   * @returns {string} The formatted percentage string
   */
  const formatPercent = (value?: number) =>
    value !== undefined ? `${value.toFixed(1)}%` : 'undefined';

  /**
   * Formats a number with thousand separators
   * @param {number} [value] - The value to format
   * @returns {string} The formatted number string
   */
  const formatNumber = (value?: number) =>
    value !== undefined
      ? value.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
      : 'undefined';

  return (
    <div className="analysis-card">
      <div className="card-header">{title}</div>
      <div className="grid-form">
        {(analysis.cost !== undefined || showUndefined) && (
          <>
            <Text>Cost:</Text>
            <p className="analysis-value">{formatNumber(analysis.cost)}</p>
          </>
        )}

        {(analysis.cycle_time_average !== undefined || showUndefined) && (
          <>
            <Text>Cycle Time (avg):</Text>
            <p className="analysis-value">{formatNumber(analysis.cycle_time_average)} hours</p>
          </>
        )}

        {(analysis.cycle_time_median !== undefined || showUndefined) && (
          <>
            <Text>Cycle Time (median):</Text>
            <p className="analysis-value">{formatNumber(analysis.cycle_time_median)} hours</p>
          </>
        )}

        {(analysis.resource_utilization !== undefined || showUndefined) && (
          <>
            <Text>Resource Utilization:</Text>
            <p className="analysis-value">{formatPercent(analysis.resource_utilization)}</p>
          </>
        )}

        {(analysis.waiting_time !== undefined || showUndefined) && (
          <>
            <Text>Waiting Time (avg):</Text>
            <p className="analysis-value">{formatNumber(analysis.waiting_time)} hours</p>
          </>
        )}
      </div>

      {/* Panel: Cycle Time Per Activity */}
      <Panel
        headerText="Cycle Time per Activity"
        collapsed={!expandedSections.has('cycle')}
        onToggle={() => toggleSection('cycle')}
        style={{ marginTop: '1rem' }}
      >
        {analysis.cycle_time_per_activity
          ? Object.entries(analysis.cycle_time_per_activity).map(([activity, time], idx) => (
            <div key={`cycle-${idx}`} className="grid-form">
              <Text>{activity}:</Text>
              <p className="analysis-value">{formatNumber(time)} hours</p>
            </div>
          ))
          : <Text>No activity data available</Text>
        }
      </Panel>

      {/* Panel: Waiting Time Per Activity */}
      <Panel
        headerText="Per Activity Waiting Time"
        collapsed={!expandedSections.has('wait')}
        onToggle={() => toggleSection('wait')}
        style={{ marginTop: '1rem' }}
      >
        {analysis.per_activity_waiting_time
          ? Object.entries(analysis.per_activity_waiting_time).map(([activity, time], idx) => (
            <div key={`wait-${idx}`} className="grid-form">
              <Text>{activity}:</Text>
              <p className="analysis-value">{formatNumber(time)} hours</p>
            </div>
          ))
          : <Text>No waiting time data available</Text>
        }
      </Panel>
    </div>
  );
};

export default AnalysisView;
