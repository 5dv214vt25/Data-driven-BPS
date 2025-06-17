import { useEffect, useRef } from 'react';
import { fetchInitialState, normalize } from '../components/form-component/utils';
import type { State, FormComponentProps } from '../components/form-component/types';

/**
 * Custom hook to manage form state, track changes, and initialize data.
 *
 * Keeps references to the original and current form state,
 * detects changes compared to the original state,
 * and calls `onChange` with any updates if not readonly.
 * Also fetches initial state if missing.
 *
 * @param {object} props - Hook input props (excluding children).
 * @param {string} props.label - Identifier for the form.
 * @param {string} props.mode - Mode determining form context.
 * @param {any} props.data - Additional data for initialization.
 * @param {State} props.formState - Current form state.
 * @param {function} props.setFormState - Setter to update form state.
 * @param {function} [props.onChange] - Callback triggered on changes.
 * @param {boolean} [props.readonly] - If true, disables change tracking.
 *
 * @returns {object} Refs to local state, original state, and mode.
 */
export function useFormComponentLogic({
  label,
  mode,
  data,
  formState,
  setFormState,
  onChange,
  readonly
}: Omit<FormComponentProps, 'children'>) {
  const originalStateRef = useRef<State>({});
  const modeRef = useRef<string | null>(mode);
  const localState = useRef<State>({});

  useEffect(() => {
    if (!formState || Object.keys(formState).length === 0) {
      fetchInitialState(mode, label, data, localState, setFormState, originalStateRef);
    }
    modeRef.current = mode;
  }, [label, mode, data, formState]);

  useEffect(() => {
    if (!readonly && formState) {
      const diffs: Partial<State> = {};

      for (const key in formState) {
        const current = formState[key];
        const original = originalStateRef.current[key];
        if (normalize(current) !== normalize(original)) {
          diffs[key] = current;
        }
      }

      if (Object.keys(diffs).length > 0 && onChange) {
        onChange(label, diffs);
      }
    }
  }, [formState]);

  useEffect(() => {
    if (!formState || Object.keys(formState).length === 0) {
      fetchInitialState(mode, label, data, localState, setFormState, originalStateRef);
    }
    modeRef.current = mode;
  }, [label]);

  return {
    localState,
    originalStateRef,
    modeRef,
  };
}



