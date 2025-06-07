import { Select, Option, Label } from '@ui5/webcomponents-react';
import { useEffect, useState } from 'react';

/**
 * Props for the SelectDropdown component.
 *
 * @interface SelectDropdownProps
 * @property {string[]} options - Array of option strings to display in the dropdown.
 * @property {string} [value] - Currently selected value (optional).
 * @property {(value: string) => void} onChange - Callback invoked when the user selects an option.
 * @property {string} label - Label text displayed above the dropdown.
 * @property {boolean} [disabled] - External flag to disable the dropdown.
 */
interface SelectDropdownProps {
  options: string[];
  value?: string;
  onChange: (value: string) => void;
  label: string;
  disabled?: boolean;
}

/**
 * A dropdown select component with an attached label.
 * 
 * @param {SelectDropdownProps} props - Component props.
 * @param {string[]} props.options - List of dropdown options.
 * @param {(value: string) => void} props.onChange - Fired when an option is selected.
 * @param {string} props.label - Text for the dropdown label.
 * @param {boolean} [props.disabled=false] - External flag to disable the dropdown.
 * 
 * @returns {JSX.Element} The rendered SelectDropdown component.
 */
export function SelectDropdown({ options, onChange, value, label, disabled = false }: SelectDropdownProps) {
  const [internalDisable, setInternalDisable] = useState<boolean>(true);

  /**
   * Handles changes in the dropdown selection.
   * 
   * @param {CustomEvent} event - Event emitted by the Select component on change.
   */
  const handleChange = (event: CustomEvent) => {
    const selectedOption = event.detail.selectedOption.textContent;
    //console.log('SelectDropdown handleChange:', selectedOption);
    if (selectedOption) {
      onChange(selectedOption);
    }
  };

  /**
   * Updates the internalDisable flag whenever the options array changes.
   */
  useEffect(() => {
    setInternalDisable(options.length === 0);
  }, [options]);

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <Label for="SelectDropDown">{label}</Label>
      <Select
        onChange={handleChange}
        value={value || ''}
        valueState="None"
        disabled={internalDisable || disabled}
        style={{ width: '300px' }}
      >
        {options.map((option, index) => (
          <Option
            key={index}
            selected={option === value}
          >
            {option}
          </Option>
        ))}
      </Select>
    </div>
  );
}
