import { useState, useEffect } from 'react';
import { useNavigate } from "react-router-dom";
import { Panel, TabContainer, Tab, Button } from '@ui5/webcomponents-react';
import JsonFileUpload from '../components/JsonFileUpload';
import BpmnFileUpload from '../components/BpmnFileUpload';
import GeneralSimulationParamtersEditor from '../components/properties-panel/GeneralSimulationParametersEditor';
import EventsTab from '../components/top-panel/EventsTab';

import '../assets/styles/SimConfig.css';


// Interfaces describing the structure of event data
interface Event {
  activity: string;
  event_id: string;
  distribution_name: string;
  distribution_params: Array<{ value: number }>;
}

// Interfaces describing the JSON data
interface JsonData {
  event_distribution: Event[];
  taskResourceDistribution?: any;
}

/**
 * Main React component responsible for Agent Simulation Configuration
 * 
 * @component
 */

export default function AgentSimConfig() {
  const [selectedTab, setSelectedTab] = useState('bpmn');
  const [jsonFile, setJsonFile] = useState<File | null>(null);
  const [bpmnFile, setBpmnFile] = useState<File | null>(null);
  const [hasFiles, setHasFiles] = useState(false);
  const [jsonData, setJsonData] = useState<JsonData | null>(null);
  const [bpmnFileContent, setBpmnFileContent] = useState<string>('');
  const [jsonDataAgentSim, setJsonDataAgentSim] = useState<any>(null);

  // Used for navigation to the simulation page
  const navigate = useNavigate();

  // Load stored files from localStorage
  useEffect(() => {

    // State for uploaded files and parsed data
    const json = localStorage.getItem('bpn-json');
    const bpmn = localStorage.getItem('bpn-bpmn');
    const savedJsonData = localStorage.getItem('bpmn_json_data');
    if (json && bpmn) {
      setHasFiles(true);
    }
    if (savedJsonData) {
      setJsonData(JSON.parse(savedJsonData) as JsonData);
    }
  }, []);

  // Watch for uploaded JSON file and parse its contents
  useEffect(() => {
    if (jsonFile) {
      const reader = new FileReader();
      reader.onload = (event) => {
        try {
          const content = event.target?.result as string;
          const parsedData = JSON.parse(content) as JsonData;
          localStorage.setItem('bpn-json', content);
          localStorage.setItem('bpmn_json_data', content);
          setJsonData(parsedData);
          checkFilesExist();
        } catch (error) {
          console.error("Error parsing JSON file:", error);
        }
      };
      reader.readAsText(jsonFile);
    }
  }, [jsonFile]);

  // Watch for uploaded BPMN file and store its content
  useEffect(() => {
    if (bpmnFile) {
      const reader = new FileReader();
      reader.onload = () => {
        const content = reader.result as string;
        localStorage.setItem('bpn-bpmn', content);
        setBpmnFileContent(content);
        checkFilesExist();
      };
      reader.readAsText(bpmnFile);
    }
  }, [bpmnFile]);

  // Checks whether bpn-json/bpmn files have been uploaded and stored
  const checkFilesExist = () => {
    const json = localStorage.getItem('bpn-json');
    const bpmn = localStorage.getItem('bpn-bpmn');
    if (json && bpmn) {
      setHasFiles(true);
    }
  };

  // Loads an external JSON file for agent simulation visualization
  useEffect(() => {
    const loadData = async () => {
      try {
        const response = await fetch('./src/assets/json/dumped_json.json');
        const data = await response.json();
        setJsonDataAgentSim(data);
      } catch (err) {
        console.error('Error reading data:', err);
      }
    };

    loadData();
  }, []);

  // Check if some files has been uploaded, else show the file upload interface
  if (!hasFiles) {
    return (
      <div className="p-6 flex flex-col gap-6 items-start">
        <h2>Upload BPN</h2>
        <div className="upload-section">
          <h3>Upload .json File</h3>
          <JsonFileUpload onFileSelected={setJsonFile} />
        </div>
        <div className="upload-section">
          <h3>Upload .bpmn File</h3>
          <BpmnFileUpload onFileSelected={setBpmnFile} />
        </div>
      </div>
    );
  }

  // If both files exist, render tab view and simulation configuration
  return (
    <div className="flex flex-col w-full">
      <div className="flex justify-end p-2">
        {/* Button to navigate to simulation page */}
        <Button
          design="Default"
          className="topdivbuttonstyle"
          onClick={() => navigate('/simulation')}
        >
          Run Simulation
        </Button>
      </div>

      {/* Tab menu for selecting different configuration views */}
      <div className="w-full" style={{ margin: 0, padding: 0 }}>
        <TabContainer
          className="w-full"
          tabLayout="Inline"
          collapsed
          onTabSelect={(e) => setSelectedTab(e.detail.tab.getAttribute('data-key') || '')}
          style={{ margin: 0, padding: 0 }}
        >
          <Tab text="Network Graph" data-key="bpmn" />
          <Tab text="General" data-key="general" />
          <Tab text="Activities" data-key="activities" />
          <Tab text="Resources" data-key="resources" />
        </TabContainer>
      </div>

      {/* Tab content rendering */}
      <div className="p-4">
        {selectedTab === 'general' && (
          <div>
            <GeneralSimulationParamtersEditor />
          </div>
        )}

        {/* Activities: Displays panels for each activity node */}
        {selectedTab === 'activities' && (
          <div>
            <br />
            {jsonDataAgentSim ? (
              JSON.parse(jsonDataAgentSim.activity_nodes).map((node: any) => (
                <Panel
                  collapsed
                  headerText={node.label}
                  key={node.label}
                  style={{ marginBottom: '1rem' }}
                >
                </Panel>
              ))
            ) : (
              <p>Inga resurser att visa.</p>
            )}
          </div>
        )}

        {/* Resources tab: renders events tab with parsed BPMN */}
        {selectedTab === 'resources' && jsonData && (
          <div>
            <EventsTab
              bpmnXml={bpmnFileContent}
              jsonData={{}} setJsonData={() => { }}
            />
          </div>
        )}
      </div>
    </div>
  );
}

