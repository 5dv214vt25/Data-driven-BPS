import React from 'react';
import { SelectDropdown } from '../SelectDropdown';

/**
 * Props for the ModeSelector component
 * @interface ModeSelectorProps
 */
interface ModeSelectorProps {
  options: string[];
  value: string;
  onChange: (val: string) => void;
}

/**
 * Component that provides mode selection functionality
 * @component
 * @param {ModeSelectorProps} props - The component props
 * @returns {JSX.Element} The rendered ModeSelector component
 */
const ModeSelector: React.FC<ModeSelectorProps> = ({ options, value, onChange }: ModeSelectorProps) => {
  return (
    <SelectDropdown
      options={options}
      label="Mode"
      value={value}
      onChange={onChange}
    />
  );
};

export default ModeSelector; 