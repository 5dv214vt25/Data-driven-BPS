import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { SelectDropdown } from '../../src/components/SelectDropdown';

/**
 * Test for component: 'SelectDropdown.tsx'
 * 
 * Test that are included:
 * SelectDropdown should render label and options correctly
 * SelectDropdown should disable when options array is empty
 * SelectDropdown should disable if external disabled prop is true
 * SelectDropdown should call onChange with selected option text
 * SelectDropdown should update internal disable state when options prop changes
 */
describe('SelectDropdown', () => {
  it('should render label and options', () => {
    const onChange = vi.fn();
    render(
      <SelectDropdown
        options={['EventLog1', 'EventLog2']}
        onChange={onChange}
        label="Test Label"
      />
    );

    expect(screen.getByText('Test Label')).toBeInTheDocument();

    expect(screen.getByText('EventLog1')).toBeInTheDocument();
    expect(screen.getByText('EventLog2')).toBeInTheDocument();

    const selectEl = document.querySelector('ui5-select');
    expect(selectEl).toBeTruthy();
    expect((selectEl as HTMLSelectElement).disabled).toBe(false);
  });

  it('should disable when options array is empty', () => {
    const onChange = vi.fn();
    render(
      <SelectDropdown
        options={[]}
        onChange={onChange}
        label="Empty Label"
      />
    );

    const selectEl = document.querySelector('ui5-select');
    expect(selectEl).toBeTruthy();
    expect((selectEl as HTMLSelectElement).disabled).toBe(true);
  });

  it('should honor external disabled prop', () => {
    const onChange = vi.fn();
    render(
      <SelectDropdown
        options={['EventLog3']}
        onChange={onChange}
        label="Disabled Label"
        disabled={true}
      />
    );

    const selectEl = document.querySelector('ui5-select');
    expect(selectEl).toBeTruthy();
    expect((selectEl as HTMLSelectElement).disabled).toBe(true);
  });

  it('should call onChange with selected option text', () => {
    const onChange = vi.fn();
    render(
      <SelectDropdown
        options={['EventLog4', 'EventLog5']}
        onChange={onChange}
        label="Event Label"
      />
    );

    const optionEl = screen.getByText('EventLog4');
    const selectEl = document.querySelector('ui5-select');
    expect(selectEl).toBeTruthy();

    fireEvent(
      selectEl!,
      new CustomEvent('change', {
        detail: { selectedOption: optionEl }
      })
    );

    expect(onChange).toHaveBeenCalledWith('EventLog4');
  });

  it('should update internal disable state when options prop changes', () => {
    const onChange = vi.fn();
    const { rerender } = render(
      <SelectDropdown
        options={[]}
        onChange={onChange}
        label="Dynamic"
      />
    );

    let selectEl = document.querySelector('ui5-select');
    expect(selectEl).toBeTruthy();
    expect((selectEl as HTMLSelectElement).disabled).toBe(true);

    rerender(
      <SelectDropdown
        options={['EventLog6']}
        onChange={onChange}
        label="Dynamic"
      />
    );

    selectEl = document.querySelector('ui5-select');
    expect(selectEl).toBeTruthy();
    expect((selectEl as HTMLSelectElement).disabled).toBe(false);
  });
});
