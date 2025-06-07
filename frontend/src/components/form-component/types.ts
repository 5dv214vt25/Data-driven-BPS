export type CalendarEntry = {
  from: string;
  to: string;
  beginTime: string;
  endTime: string;
};

export type State = {
  [key: string]: string | CalendarEntry[];
};

/**
 * @param {string} label - The label of the selected node
 * @param {string} mode - Current mode: 'activity', 'agent', or 'role'.
 * @param {any} data - Data containing simulator parameter values from a discovery phase
 * @param {State} formState - Global state used to keep track of all form components in parent page
 * @param {(label: string, state: State) => void} setFormState - Function to update the FormState
 * @param {(field: string, value: any) => void} onChange - Callback for form field updates
 * @param {boolean} readonly - Set readonly for all fields
 */
export type FormComponentProps = {
  readonly?: boolean
  label: string;
  mode: string;
  data: any;
  formState: any;
  setFormState: (label: string, newState: State) => void;
  onChange?: (label: string, changes: Partial<State>) => void;
};

/**
 * @param {State} formState - Global state used to keep track of all form components in parent page
 * @param {boolean} readonly - Sets readonly for all fields
 * @param {RefObject} localState - The current state of this component
 * @param {(label: string, state: State) => void} setFormState - Function to update the FormState
 * @param {string} label - The label of the selected node
 */
export type CalendarComponentProps = {
  formState: any;
  readonly?: boolean;
  localState: any;
  setFormState: (label: string, newState: State) => void;
  label: string;
};

/**
 * @param {string[]} activities - A list of strings consisting of all activities in a given scenario
 * @param {State} formState - Global state used to keep track of all form components in parent page
 * @param {RefObject} modeRef - State that handles which mode (agent, activity or role) that should be displayed
 * @param {(label: string, state: State) => void} setFormState - Function to update the FormState
 * @param {string} label - The label of the selected node
 */
export type FormGroupStandardProps = {
  activities: string[];
  formState: any;
  modeRef: any;
  localState: any;
  setFormState: (label: string, newState: State) => void;
  label: string;
  readonly?: boolean;
};

