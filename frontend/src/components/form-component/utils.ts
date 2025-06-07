import { Mode } from './enums';
import { State, CalendarEntry } from './types';
import type { Ui5CustomEvent, InputDomRef } from '@ui5/webcomponents-react';
import type { RefObject } from 'react';

/**
 * Returns the indices of all agents that work on a given activity.
 *
 * @param label - The activity label.
 * @param data - The full simulation data object.
 * @returns Array of agent indices.
 */
export function getAgentsWorkingOnActivity(label: string, data: any): number[] {
  const mapping = Object.values(data.simulation_parameters.agent_activity_mapping);
  return mapping.reduce((acc: number[], activities: any, idx: number) => {
    if (activities.includes(label)) {acc.push(idx);}
    return acc;
  }, []);
}

/**
 * Finds the agent ID corresponding to a given agent name.
 *
 * @param label - The agent name.
 * @param data - The simulation data.
 * @returns Agent ID as number, or -1 if not found.
 */
export function getAgentID(label: string, data: any): number {
  const map = data.simulation_parameters.agent_to_resource;
  for (const [id, name] of Object.entries(map)) {
    if (name === label) {return Number(id);}
  }
  return -1;
}

/**
 * Gets the role assigned to a specific agent.
 *
 * @param agentID - The agent's ID.
 * @param data - The simulation data.
 * @returns The role name, or an empty string if not found.
 */
export function getRoleForAgent(agentID: number, data: any): string {
  const roles = data.simulation_parameters.roles;
  for (const [name, roleData] of Object.entries(roles)) {
    if ((roleData as any).agents?.includes(agentID)) {
      return name;
    }
  }
  return '';
}


/**
 * Normalizes input values to consistent sorted JSON strings for comparison.
 *
 * @param val - Value to normalize.
 * @returns Normalized string.
 */
export function normalize(val: any): string {
  if (typeof val === 'string' && val.includes(',')) {
    const parts = val.split(',').map(s => s.trim()).filter(Boolean);
    const isNumeric = parts.every(p => !isNaN(Number(p)));
    return JSON.stringify(isNumeric ? parts.map(Number).sort((a, b) => a - b) : parts.sort());
  }

  if (Array.isArray(val)) {
    const isNumeric = val.every(p => !isNaN(Number(p)));
    return JSON.stringify(isNumeric ? [...val].map(Number).sort((a, b) => a - b) : [...val].sort());
  }

  return JSON.stringify(val);
}

/**
 * Fetches and sets the initial form state for the current mode and label.
 *
 * @param mode - The simulation mode ("agent", "role", or "activity").
 * @param label - The selected entity label.
 * @param data - The simulation data.
 * @param localState - Local state reference for current form values.
 * @param setFormState - Setter function to update form state.
 * @param originalRef - Reference to store the original state.
 */
export function fetchInitialState(
  mode: string,
  label: string,
  data: any,
  localState: RefObject<State>,
  setFormState: (label: string, newState: State) => void,
  originalRef: React.MutableRefObject<State>
) {
  let initial: State = {};

  if (mode === Mode.ACTIVITY && label) {
    initial = handleActivityInitialState(data, localState, label, setFormState);
  } else if (mode === Mode.AGENT && label) {
    initial = handleAgentInitialState(data, localState, label, setFormState);
  } else if (mode === Mode.ROLE && label) {
    initial = handleRoleInitialState(data, localState, label, setFormState);
  }

  if (initial === null) {
    console.error("Could not fetch initial state!");
  } else {
    originalRef.current = initial;
  }
}

/**
 * Handles input changes for text inputs and updates form state accordingly.
 *
 * @param e - The input event from UI5 input component.
 * @param label - The current form label.
 * @param localState - Reference to local form state.
 * @param setFormState - Function to update the form state.
 */
export const handleInput = (
  e: Ui5CustomEvent<InputDomRef>,
  label: string,
  localState: RefObject<State>,
  setFormState: (label: string, newState: State) => void,
) => {
  const field = e.target.dataset.field!;
  const value = e.target.value;
  updateField(label, field, value, localState, setFormState);
};

/**
 * Handles changes to calendar input fields and updates state accordingly.
 *
 * @param idx - Index of the calendar entry being updated.
 * @param key - The key in the calendar entry being changed.
 * @param value - New value to assign.
 * @param localState - Reference to local form state.
 * @param setFormState - Function to update form state.
 * @param label - Label for current form section.
 */
export const handleCalendarInput = (
  idx: number,
  key: keyof CalendarEntry,
  value: string,
  localState: RefObject<State>,
  setFormState: (label: string, newState: State) => void,
  label: string
) => {
  const calendar = (localState.current.calendar as CalendarEntry[]).map((entry, i) =>
    i === idx ? { ...entry, [key]: value } : entry
  );
  updateField(label, 'calendar', calendar, localState, setFormState);
};

/**
 * Updates a specific field in the local state (the current label's formState) and 
 * propagates the change via setFormState.
 *
 * @param label - The section label.
 * @param field - The field name to update.
 * @param value - The new value for the field.
 * @param localState - Reference to the current local state.
 * @param setFormState - Callback to update the outer form state.
 */
export const updateField = (
  label: string,
  field: string,
  value: any,
  localState: RefObject<State>,
  setFormState: (label: string, newState: State) => void
) => {
  const updated = {
    ...localState.current,
    [field]: value
  };
  localState.current = updated;
  setFormState(label, updated);
};

// Finds activity values in 'data' and returns them as an initial state.
function handleActivityInitialState(
  data: any,
  localState: RefObject<State>,
  label: string,
  setFormState: (label: string, newState: State) => void
): State {
  const mapping = Object.values(data.simulation_parameters.agent_activity_mapping);
  const agents = mapping.map((activities, idx) => (activities as string[]).includes(label) ? idx : null)
    .filter((val) => val !== null) as number[];

  let initial = {
    agentsCount: String(agents.length),
    agentsWorkingOnActivity: agents.join(', '),
  };

  for (const [key, value] of Object.entries(initial)) {
    updateField(label, key, value, localState, setFormState);
  }

  return initial;
}

// Finds agent values in 'data' and returns them as an initial state.
function handleAgentInitialState(
  data: any,
  localState: RefObject<State>,
  label: string,
  setFormState: (label: string, newState: State) => void
): State {
  const agentMap = data.simulation_parameters.agent_to_resource;
  const agentID = Object.entries(agentMap).find(([, v]) => v === label)?.[0] ?? "";

  const activityDurations = data.simulation_parameters.activity_durations_dict[agentID];
  const timePeriods = data.simulation_parameters.res_calendars[agentID]?.data.time_periods;
  const activities = data.simulation_parameters.agent_activity_mapping[agentID];
  const roles = Object.entries(data.simulation_parameters.roles)
    .filter(([, roleData]) => (roleData as any).agents.includes(Number(agentID)))
    .map(([name]) => name);

  let initial = {
    activityDurations: JSON.stringify(activityDurations),
    activities: JSON.stringify(activities),
    role: roles.join(', '),
    calendar: timePeriods,
    resourceName: label
  };

  for (const [key, value] of Object.entries(initial)) {
    updateField(label, key, value, localState, setFormState);
  }

  if (!timePeriods) {
    console.error("No calendar found for resource: " + label);
  }

  return initial;
}

// Finds role values in 'data' and returns them as an initial state.
function handleRoleInitialState(
  data: any,
  localState: RefObject<State>,
  label: string,
  setFormState: (label: string, newState: State) => void
): State {
  const roleData = data.simulation_parameters.roles[label];
  const calendar: CalendarEntry[] = roleData.calendar ?? [];
  const agents = roleData.agents ?? [];

  let initial = {
    calendar,
    agents: agents.join(', '),
  };

  updateField(label, 'calendar', calendar, localState, setFormState);
  updateField(label, 'agents', agents.join(', '), localState, setFormState);

  return initial;
}
