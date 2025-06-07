import { FormGroup, Input, FormItem, Label, MultiComboBox, MultiComboBoxItem } from '@ui5/webcomponents-react';
import { CamelCaseToNatural, ModeFields } from './enums';
import { handleInput } from './utils';
import { FormGroupStandardProps } from './types';

/**
 * A FormGroup-like component that renders all fields in the given 'formState' that 
 * are not 'calendar'. This FormGroup consists of a MultiComboBox for activities 
 * related to the selected Agent and some Input fields for the rest of the parameters.
 * If the selected node is not an Agent then the MultiComboBox should not be rendered
 *
 * Props:
 * @param {string[]} activities - A list of strings consisting of all activities in a given scenario
 * @param {State} formState - Global state used to keep track of all form components in parent page
 * @param {RefObject} modeRef - State that handles which mode (agent, activity or role) that should be displayed
 * @param {(label: string, state: State) => void} setFormState - Function to update the FormState
 * @param {RefObject} localState - The current state of this component
 * @param {string} label - The label of the selected node
 * @param {boolean} readonly - The label of the selected node
 */
const FormGroupStandard = ({
  activities,
  formState,
  modeRef,
  setFormState,
  localState,
  label,
  readonly
}: FormGroupStandardProps) => {
  const readonlyLightGray = '#eaecee'
  return (
    <FormGroup>
      {formState && modeRef.current === 'agent' && (
        <FormItem labelContent={<Label>Activities</Label>}>
          {/* Readonly because no input fields work all the way to backend 
              right now. This should be editable later */}
          <MultiComboBox
            onChange={(event: CustomEvent<{ items: HTMLElement[] }>) => {
              const selectedItems = (event.detail.items as HTMLElement[])
                .map((item) => item.getAttribute('text') || '')
                .join(',');
              setFormState('form', {
                ...formState,
                activities: selectedItems,
              });

            }}
            onClose={() => {}}
            onInput={() => {}}
            onOpen={() => {}}
            onSelectionChange={() => {}}
            valueState="None"
            showClearIcon
            readonly
            style={{backgroundColor: readonly ? readonlyLightGray : 'white'}}
            placeholder="Select activities"
          >
            {activities.map((activity) => (
              <MultiComboBoxItem
                key={activity}
                text={activity}
                selected={formState.activities?.includes(activity)}
              />
            ))}
          </MultiComboBox>
        </FormItem>
 
      )}

      {/*'activities' and 'calendar' are filtered out because they are handled 
         in other parts of the component. 'activityDurations' may be handled 
         here but is not implemented fully and should thus be filtered out for now.*/
        formState && Object.entries(formState)
          .filter(([key]) => key !== 'calendar' && key !== 'activities' &&
                   key !== 'activityDurations' &&
                    ModeFields[modeRef.current!]?.includes(key))
          .map(([fieldName, value]) => (
            <FormItem key={fieldName} labelContent={<Label>{CamelCaseToNatural[fieldName] ?? fieldName}</Label>}>
              {/* Readonly because no input fields work all the way to backend 
                right now. This should be editable later */}
              <Input
                value={String(value)}
                type="Text"
                onInput={(e) =>
                  handleInput(
                    e,
                    label,
                    localState, 
                    setFormState
                  )}
                data-field={fieldName}
                readonly
                style={{backgroundColor: readonly ? readonlyLightGray : 'white'}}
              />
            </FormItem>
          ))}

    </FormGroup>
  );
}

export default FormGroupStandard
