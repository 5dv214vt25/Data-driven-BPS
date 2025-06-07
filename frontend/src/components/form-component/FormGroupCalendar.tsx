import { FormGroup, FormItem, Label, Input } from '@ui5/webcomponents-react';
import { CamelCaseToNatural } from './enums';
import { handleCalendarInput} from './utils';
import { CalendarComponentProps, CalendarEntry } from './types';



/**
 * A FormGroup-like component that renders all fields in the given 'formState' that 
 * are not 'calendar'. This FormGroup consists of a MultiComboBox for activities 
 * related to the selected Agent and some Input fields for the rest of the parameters.
 * If the selected node is not an Agent then the MultiComboBox should not be rendered
 *
 * Props:
 * @param {State} formState - Global state used to keep track of all form components in parent page
 * @param {boolean} readonly - Sets readonly for all fields
 * @param {RefObject} localState - The current state of this component
 * @param {(label: string, state: State) => void} setFormState - Function to update the FormState
 * @param {string} label - The label of the selected node
 */
const FormGroupCalendar = ({
  formState,
  readonly,
  localState,
  setFormState,
  label
}: CalendarComponentProps) => {
  return (
    <FormGroup style={{ textAlign: 'left' }}>
      {(formState.calendar as CalendarEntry[]).map((entry, idx) => (
        <FormGroup key={idx} >
          <h3>{idx + 1}</h3>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '1rem',
            }}
          >
            {['from', 'to', 'beginTime', 'endTime'].map((key) => (
              <FormItem key={key} labelContent={<Label>{CamelCaseToNatural[key] || key}</Label>}>
                <Input
                  readonly={readonly}
                  value={entry[key as keyof CalendarEntry]}
                  type="Text"
                  onInput={(e) =>
                    handleCalendarInput(
                      idx, 
                      key as keyof CalendarEntry, 
                      e.target.value, 
                      localState, 
                      setFormState, 
                      label
                    )
                  }
                />
              </FormItem>
            ))}
          </div>
        </FormGroup>
      ))}
    </FormGroup>
  );
}

export default FormGroupCalendar
