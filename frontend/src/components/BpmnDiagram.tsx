/**
 * BpmnDiagram Component
 *
 * This component renders a BPMN diagram using the `bpmn-js` modeler library.
 * It displays the diagram in a resizable container and optionally includes
 * a side panel showing properties of BPMN elements, which can be customized
 * via the `PropertiesView` component.
 */

import React, { useEffect, useRef, useState } from 'react';
import Modeler from 'bpmn-js/lib/Modeler';
import 'bpmn-js/dist/assets/diagram-js.css';
import 'bpmn-js/dist/assets/bpmn-font/css/bpmn-embedded.css';
import '../assets/styles/Bpmn.css';
import PropertiesView from './properties-panel/PropertiesView';
import { JsonDataSimod } from '../types/JsonDataSimod';

/**
 * - bpmnXml: A string containing the BPMN to be displayed in the modeler.
 * - showSidePanel: Boolean flag to toggle the properties panel on the side.
 * - jsonData (optional): An object representing simulation data, which can
 *   be edited in the properties panel.
 * - setJsonData (optional): A setter function to update the simulation data
 *   from within the properties panel.
 */
interface BpmnDiagramProps {
  bpmnXml: string;
  showSidePanel: boolean;
  jsonData?: JsonDataSimod;
  setJsonData?: React.Dispatch<React.SetStateAction<JsonDataSimod>>;
}

const BpmnDiagram: React.FC<BpmnDiagramProps> = ({ bpmnXml, showSidePanel, jsonData, setJsonData }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const modelerRef = useRef<any>(null);
  const [modelerReady, setModelerReady] = useState(false);

  // Initialize BPMN modeler
  useEffect(() => {
    if (!containerRef.current) { return; }
    const modeler = new Modeler({
      container: containerRef.current
    });
    //set the modeler to the ref
    modelerRef.current = modeler;
    setModelerReady(true);
    //destroy the modeler when the component unmounts
    return () => modeler.destroy();
  }, []);

  // Load BPMN XML
  useEffect(() => {
    // If modeler is not ready or bpmnXml is empty, do nothing
    if (!modelerRef.current || !bpmnXml) { return; }
    // Clear the modeler before importing new XML
    modelerRef.current
      .importXML(bpmnXml)
      .then(({ warnings }: any) => {
        if (warnings.length) { console.warn('Import warnings:', warnings); }
        // Fit the diagram to the viewport after import
        modelerRef.current.get('canvas').zoom('fit-viewport');
      })
      .catch((err: any) => console.error('BPMN import error:', err));
  }, [bpmnXml]);

  return (
    <div style={{ display: 'flex', height: '80vh' }}>
      <div
        ref={containerRef}
        style={{
          width: showSidePanel ? '70%' : '100%',
          height: '100%',
          overflow: 'hidden',
          position: 'relative'
        }}
      />
      <div
        style={{
          width: showSidePanel ? '30%' : '0%',
          height: '100%',
          overflow: 'hidden',
          boxShadow: '2px 0 8px rgba(0, 0, 0, 0.2)',
          borderBottomLeftRadius: '10px',
          borderBottomRightRadius: '10px',
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        {(modelerReady && showSidePanel && jsonData !== undefined && setJsonData !== undefined) &&
          <PropertiesView modeler={modelerRef.current} jsonData={jsonData} setJsonData={setJsonData} />}
      </div>
    </div>
  );
};

export default BpmnDiagram;
