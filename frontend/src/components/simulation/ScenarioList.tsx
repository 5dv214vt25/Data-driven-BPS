// src/components/ScenarioList.tsx
import React, { useEffect, useRef, useState } from "react";
import {
  Table,
  TableRow,
  TableCell,
  TableHeaderRow,
  TableHeaderCell,
  TableRowAction,
  Button,
  Input,
  InputDomRef,
  RadioButton,
  TableVirtualizer
} from "@ui5/webcomponents-react";
import { PopupMessage } from "../PopupMessage";
import { usePopup } from "../../hooks/usePopup";
import { useUser } from "../../context/userContext";
import {
  listSimodScenarios,
  deleteSimodScenario,
  updateSimodScenario,
  uploadSimodScenario
} from "../../api/controllerAPICalls/SimodScenarioAPICalls";
import {
  listAgentScenarios,
  deleteAgentScenario,
  updateAgentScenario,
  getAgentScenario,
  uploadAgentScenario
} from "../../api/controllerAPICalls/AgentScenarioAPICalls";
import "@ui5/webcomponents-icons/dist/delete.js";
import "@ui5/webcomponents-icons/dist/copy.js";
import '../../assets/styles/simulation.css';
import { getSimodScenario } from "../../api/controllerAPICalls/SimodScenarioAPICalls";

type ScenarioType = "all" | "Simod" | "Agent";

// How a scenario is represented in the UI
interface Scenario {
  scenarioId: string;
  name: string;
  eventLogId?: number | string;
  scenarioType: "Simod" | "Agent";
}

interface ScenarioListProps {
  onScenarioSelect: (scenario: Scenario | null) => void;
  selectedScenarioId?: string | null;
  selectedScenarioType?: "Simod" | "Agent" | null;
  onStartSimulation?: () => void;
  onDownload?: () => void;
  outputAvailable?: boolean;
  scenarioSelected?: boolean;
  scenarioReloadKey: number;
}

const ScenarioList: React.FC<ScenarioListProps> = ({
  onScenarioSelect,
  selectedScenarioId,
  selectedScenarioType,
  onStartSimulation,
  onDownload,
  outputAvailable,
  scenarioSelected,
  scenarioReloadKey,
}) => {
  const { userSettings } = useUser();
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const inputRef = useRef<InputDomRef>(null);
  const [loading, setLoading] = useState(true);
  const [scenarioType, setScenarioType] = useState<ScenarioType>("all");
  const [editedScenario, setEditedScenario] = useState<string>("");
  const { message: popupMessage, type: popupType, showPopup, closePopup } = usePopup();
  const [editingScenario, setEditingScenario] = useState<Scenario | null>(null);

  // Helper to create a unique key for each scenario
  const getScenarioKey = (scenario: Scenario) => `${scenario.scenarioType}:${scenario.scenarioId}`;
  const selectedKey = selectedScenarioId && selectedScenarioType
    ? `${selectedScenarioType}:${selectedScenarioId}`
    : null;

  const fetchScenarios = async () => {
    if (!userSettings.username) {
      return;
    }
    setLoading(true);
    try {
      let simod: any[] = [];
      let agent: any[] = [];

      if (scenarioType === "Simod" || scenarioType === "all") {
        try {
          simod = await listSimodScenarios(userSettings.username);
        } catch (error) {
          simod = [];
        }
      }

      if (scenarioType === "Agent" || scenarioType === "all") {
        try {
          agent = await listAgentScenarios(userSettings.username);
        } catch (error) {
          agent = [];
        }
      }

      // Normalize scenarios and assign scenario_type
      const normalize = (s: any, type: "Simod" | "Agent"): Scenario => ({
        scenarioId: s.scenario_id ?? s.id,
        name:
          (typeof s.name === "string" && s.name.trim() !== ""
            ? s.name
            : typeof s.scenario_name === "string" && s.scenario_name.trim() !== ""
              ? s.scenario_name
              : `${s.scenario_id ?? s.id}`),
        eventLogId: s.event_log_id,
        scenarioType: type,
      });

      const simodNormalized = simod.map((s) => normalize(s, "Simod"));
      const agentNormalized = agent.map((s) => normalize(s, "Agent"));

      let combined: Scenario[] = [];

      if (scenarioType === "all") {
        combined = [...simodNormalized, ...agentNormalized];
      } else if (scenarioType === "Simod") {
        combined = simodNormalized;
      } else if (scenarioType === "Agent") {
        combined = agentNormalized;
      }

      setScenarios(combined.reverse());
    } catch (error: any) {
      console.error("Failed to fetch scenarios:", error.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchScenarios();
    console.log('reloading ScenarioList')
  }, [userSettings.username, scenarioType, scenarioReloadKey]);

  const handleSearch = () => {
    const value = inputRef.current?.value || "";
    setSearchTerm(value.toLowerCase());
  };

  const filteredScenarios = scenarios.filter((sc) => {
    const search = searchTerm.toLowerCase();
    return sc.name?.toLowerCase().includes(search);
  });

  const handleRowClick = (scenario: Scenario) => {
    userSettings.selectedEventlogId = String(scenario.eventLogId);
    userSettings.selectedScenarioId = scenario.scenarioId;
    userSettings.selectedApproach = scenario.scenarioType;
    onScenarioSelect(scenario);
  };

  const handleDelete = async (scenario: Scenario) => {
    if (!userSettings.username) {
      return;
    }

    const confirmed = window.confirm("Are you sure you want to delete this scenario?");
    if (!confirmed) {
      return;
    }

    try {
      if (scenario.scenarioType === "Simod") {
        await deleteSimodScenario(scenario.scenarioId);
      } else if (scenario.scenarioType === "Agent") {
        await deleteAgentScenario(scenario.scenarioId);
      }
      setScenarios((prev) =>
        prev.filter(
          (s) => !(s.scenarioId === scenario.scenarioId && s.scenarioType === scenario.scenarioType)
        )
      );
      showPopup("success", "Scenario deleted successfully!");
      // Optionally show a success message here
    } catch (error) {
      console.error("Delete failed:", error);
      showPopup("error", "Failed to delete scenario.");
    }
  };

  const handleEdit = async (scenario: Scenario) => {
    if (!userSettings.username) {
      return;
    }
    setEditingScenario(scenario);
    setEditedScenario(scenario.name);
  };

  const handleSaveEdit = async () => {
    if (!userSettings.username || !editingScenario) {
      return;
    }

    if (!editedScenario.trim) {
      alert("Scenario name cannot be empty.");
      return;
    }

    try {
      let result;
      if (editingScenario.scenarioType === "Simod") {
        result = await updateSimodScenario(editingScenario.scenarioId, editedScenario);
      } else if (editingScenario.scenarioType === "Agent") {
        result = await updateAgentScenario(editingScenario.scenarioId, editedScenario);
      }

      if (result) {
        setScenarios((prev) =>
          prev.map((s) =>
            s.scenarioId === editingScenario.scenarioId &&
              s.scenarioType === editingScenario.scenarioType
              ? { ...s, name: editedScenario }
              : s
          )
        );

        setEditingScenario(null);
        setEditedScenario("");
      } else {
        alert("Failed to update the scenario name.");
      }
    } catch (error) {
      console.error("Error updating scenario name:", error);
      alert("An error occurred while updating the scenario.");
    }
  };

  const handleCancelEdit = () => {
    setEditingScenario(null);
    setEditedScenario("");
  };

  const handleDuplicate = async (scenario: Scenario) => {
    try {
      // IMPLEMENT FOR AGENT ALSO!
      if (scenario.scenarioType === 'Agent') {
        const agentData = await getAgentScenario(scenario.scenarioId);

        if (agentData.modelBlob && agentData.parametersBlob && agentData.visualizationBlob && scenario.eventLogId) {

          // Create new files out of the exisitng data
          const modelFile = new File([agentData.modelBlob],
            agentData.modelFilename,
            { type: agentData.modelBlob.type });
          const parmetersFile = new File([agentData.parametersBlob],
            agentData.parametersFilename,
            { type: agentData.parametersBlob.type });
          const visualizationFile = new File([agentData.visualizationBlob],
            agentData.visualizationFilename,
            { type: agentData.visualizationBlob.type });
          const scenarioName = scenario.name + '-copy'

          // Upload a copy of the scenario
          const result = await uploadAgentScenario(scenario.eventLogId.toString(), scenarioName,
            modelFile, parmetersFile, visualizationFile);
          showPopup(result?.success ? 'success' : 'error',
            result?.success ? 'Scenario duplicated!' : 'Failed to duplicate scenario');
          if (result?.success) {
            await fetchScenarios(); // Refresh the scenario list after duplication
          }
        } else {
          showPopup('error', 'Missing required data to duplicate scenario');
        }
        return;
      }

      const { bpmnBlob, parametersBlob } = await getSimodScenario(scenario.scenarioId);

      if (bpmnBlob && parametersBlob) {
        const jsonText = await parametersBlob.text();
        localStorage.setItem('bpmn_json_data', jsonText);
        let scenarioName = scenario.name;

        if (scenario.eventLogId && scenarioName && bpmnBlob) {
          const fileBpmn = new File([bpmnBlob], `${scenarioName}.bpmn`, { type: bpmnBlob.type });
          const paramJson = localStorage.getItem('bpmn_json_data');
          if (paramJson) {
            const paramFile = new File([paramJson], `${scenarioName}_params.json`, { type: 'application/json' });
            scenarioName = scenarioName + '-copy';
            const result = await uploadSimodScenario(scenario.eventLogId.toString(), scenarioName, fileBpmn, paramFile);
            showPopup(result?.success ? 'success' : 'error',
              result?.success ? 'Scenario duplicated!' : 'Failed to duplicate scenario');
            if (result?.success) {
              await fetchScenarios(); // Refresh the scenario list after duplication
            }
          }
        } else {
          showPopup('error', 'Missing required data to duplicate scenario');
        }
      }
    } catch (error) {
      console.error('Error loading selected scenario:', error);
    }
  }

  // Optionally, add a "Clear selection" button if needed
  // const handleClearSelection = () => onScenarioSelect(null);

  if (loading) {
    return <div>Loading scenarios...</div>;
  }
  return (
    <div>
      <div className="scenario-list-toolbar">
        Filter:
        <div style={{ display: "flex", gap: "0.5rem", }}>
          <RadioButton
            name="scenarioType"
            checked={scenarioType === "all"}
            onChange={() => setScenarioType("all")}
            text="All"
          />
          <RadioButton
            name="scenarioType"
            checked={scenarioType === "Simod"}
            onChange={() => setScenarioType("Simod")}
            text="Simod"
          />
          <RadioButton
            name="scenarioType"
            checked={scenarioType === "Agent"}
            onChange={() => setScenarioType("Agent")}
            text="Agent Simulator"
          />
        </div>

        <div>
          <Input
            placeholder="Search by name..."
            value={searchTerm}
            onInput={handleSearch}
            ref={inputRef}
            style={{ width: "100%" }}
          />
        </div>

        <div style={{ display: "flex", gap: "0.5rem", marginLeft: "auto" }}>
          <Button onClick={onStartSimulation} disabled={!scenarioSelected || outputAvailable}>
            Start Simulation
          </Button>
          <Button onClick={onDownload} disabled={!scenarioSelected || !outputAvailable}>
            Download
          </Button>
        </div>
      </div>

      <div style={{ maxHeight: "400px", overflowY: "auto" }}>
        <Table
          style={{ tableLayout: "auto", width: "100%", height: "300px" }}
          features={<TableVirtualizer rowCount={scenarios.length} rowHeight={44} />}
          headerRow={
            <TableHeaderRow sticky>
              <TableHeaderCell width="35px">
                <span>ID</span>
              </TableHeaderCell>
              <TableHeaderCell minWidth="180px">
                <span>Name</span>
              </TableHeaderCell>
              <TableHeaderCell minWidth="120px">
                <span>Type</span>
              </TableHeaderCell>
            </TableHeaderRow>
          }
          rowActionCount={3}
        >
          {filteredScenarios.map((sc) => (
            <TableRow
              className="listRow"
              key={getScenarioKey(sc)}
              data-scenario-id={getScenarioKey(sc)}
              onClick={() => handleRowClick(sc)}
              actions={
                editingScenario?.scenarioId === sc.scenarioId && editingScenario?.scenarioType == sc.scenarioType ? (
                  <>
                    {/* Edit mode */}
                    <TableRowAction icon="accept" onClick={handleSaveEdit} />
                    <TableRowAction icon="decline" onClick={handleCancelEdit} />
                  </>
                ) : (
                  <>
                    {/* Normal mode */}
                    <TableRowAction icon="edit" title="Edit" onClick={() => handleEdit(sc)} />
                    <TableRowAction icon="copy" title="Make copy" onClick={() => handleDuplicate(sc)} />
                    <TableRowAction icon="delete" title="Delete" onClick={() => handleDelete(sc)} />
                  </>
                )
              }
              style={{
                backgroundColor: getScenarioKey(sc) === selectedKey ? "#bde0fe" : undefined
              }}
            >
              <TableCell style={{ textAlign: "left" }}>
                <span>{sc.scenarioId}</span>
              </TableCell>
              <TableCell style={{ textAlign: "left", paddingRight: "8px", whiteSpace: "nowrap" }}>
                {editingScenario?.scenarioId === sc.scenarioId && editingScenario?.scenarioType == sc.scenarioType ? (
                  <Input
                    value={editedScenario}
                    onInput={(e: any) => setEditedScenario(e.target.value)}
                    style={{ width: "100%" }}
                  />
                ) : (
                  <span>{sc.name}</span>
                )}
              </TableCell>
              <TableCell style={{ textAlign: "left", whiteSpace: "nowrap" }}>
                <span style={{ textTransform: "capitalize" }}>{sc.scenarioType}</span>
              </TableCell>
            </TableRow>
          ))}
        </Table>
      </div>

      <PopupMessage
        show={!!popupMessage}
        type={popupType}
        message={popupMessage}
        duration={4000}
        onClose={closePopup}
      />
    </div>
  );
};

export default ScenarioList;
