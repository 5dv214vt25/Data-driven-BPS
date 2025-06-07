import { Form, Panel } from '@ui5/webcomponents-react';
import { FormComponentProps } from './types';
import FormGroupStandard from './FormGroupStandard';
import FormGroupCalendar from './FormGroupCalendar';
import { useFormComponentLogic } from '../../hooks/useFormComponentLogic';

/**
 * FormComponent is a component that renders the sidebar related to AgentSimulator.
 * Every field in the component gets a value from the 'formState' property or from
 * 'data' if formState is undefined. FormState should be defined after an edit is made
 * to some label.
 *
 * Props:
 * @param {string} label - The label of the selected node
 * @param {string} mode - Current mode: 'activity', 'agent', or 'role'.
 * @param {any} data - Data containing simulator parameter values from a discovery phase
 * @param {State} formState - Global state used to keep track of all form components in parent page
 * @param {(label: string, state: State) => void} setFormState - Function to update the FormState
 * @param {(field: string, value: any) => void} onChange - Callback for form field updates
 * @param {boolean} readonly - Set readonly for all fields
 */
const FormComponent = ({
  label,
  mode,
  data,
  formState,
  setFormState,
  onChange,
  readonly = false
}: FormComponentProps) => {

  // The current state of the current label's form is fetched through this hook
  const { localState, modeRef } = useFormComponentLogic({
    label,
    mode,
    data,
    formState,
    setFormState,
    onChange,
    readonly
  });

  const activities = Object.keys(data.simulation_parameters?.max_activity_count_per_case || {});

  return (
    <div style={{
      width: '90%',
      padding: '10px 20px 50px 20px',
      textAlign: 'right',
      maxHeight: '50vh',
      overflowY: 'auto'
    }}>

      <h1>{label}</h1>
      <Form onSubmit={(e) => e.preventDefault()}>
        <FormGroupStandard
          activities={activities}
          formState={formState}
          localState={localState}
          modeRef={modeRef}
          setFormState={setFormState}
          label={label}
          readonly={readonly}
        />
      </Form>

      {formState && Array.isArray(formState.calendar) && modeRef.current !== 'activity' && (
        <Panel header={<h4>Calendar</h4>} collapsed>
          <Form onSubmit={(e) => e.preventDefault()}>
            <FormGroupCalendar
              formState={formState}
              localState={localState}
              readonly={readonly}
              setFormState={setFormState}
              label={label}
            />
          </Form>
        </Panel>
      )}
    </div>
  );
};

export default FormComponent;

