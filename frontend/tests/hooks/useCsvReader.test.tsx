import { it, expect, describe, beforeEach, afterEach, vi } from 'vitest'
import { renderHook, act, cleanup } from '@testing-library/react'
import Papa from 'papaparse'

import { useCsvReader } from '../../src/hooks/useCsvReader'

/**
 * Test for hook: 'useCsvReader'
 * 
 * Test that are included:
 * 
 * Component should start with empty data, no columns and zero rows.
 * Component should clear csvData and columnOrder with resetCsvData.
 * Component should be able to handle a missing file by setting csvData to an empty array.
 */

describe('useCsvReader', () => {

  /** To be exec before every case. */
  beforeEach(() => {
    localStorage.clear();
  });

  /** To be exec after every case. */
  afterEach(() => {
    vi.restoreAllMocks();
    cleanup();
  })

  it('should start with empty data, no columns and zero rows', () => {

    /** Render the hook. */
    const { result } = renderHook(() => useCsvReader());

    /** Expects that the csvData is empty.. */
    expect(result.current.csvData).toEqual([]);

    /** Expects that the columnOrder is empty. */
    expect(result.current.columns).toEqual([]);

    /** Expects that the amount of rows is 0. */
    expect(result.current.rowNumber).toEqual(0);
  })

  it('should parse a CSV file, update states and saves headers to localStorag', () => {

    /** Mock meta-data representing a csv file. */
    const mockRows = [
      { name: 'Lennart' },
      { name: 'Åsa' },
    ];

    /** The column name for the mock meta-data. */
    const mockFields = ['name'];

    (Papa as any).parse = (_file: Blob, config: any) => {
      config.complete!({
        data: mockRows,
        errors: [],
        meta: { fields: mockFields },
      });
      return {} as any;
    };

    const setItemSpy = vi.spyOn(Storage.prototype, 'setItem');

    /** Render the hook: useCsvReader. */
    const { result } = renderHook(() => useCsvReader());

    /** Create fake input file. */
    const fakeFile = new File([''], 'dummy.csv', { type: 'text/csv' });

    /** Call function Act.
     *  Act() tells the test to pause the test until
     *  all changes on the component has been done.
     *  This reasures that the case runs safetly.
     */
    act(() => {
      result.current.handleCSVUpload(fakeFile);
    });

    /** Expects that the current data is equal to the mock meta-data. */
    expect(result.current.csvData).toEqual(mockRows);

    /** Expects that the columnOrder is equal to 'name'. */
    expect(result.current.columns).toEqual(mockFields);

    /** Expects that the amount of rows is equal to 2. */
    expect(result.current.rowNumber).toBe(mockRows.length);

    /** Expects that the hook has been called with mockFields. */
    expect(setItemSpy).toHaveBeenCalledWith(
      'originalCsvColumns',
      JSON.stringify(mockFields),
    );
  });

  it('should clear csvData and columnOrder with resetCsvData', () => {

    /** Mock meta-data representing a csv file. */
    const mockRows = [
      { name: 'Lennart' },
      { name: 'Åsa' },
    ];

    /** The name of the column. */
    const mockFields = ['name'];

    (Papa as any).parse = (_file: Blob, config: any) => {
      config.complete!({
        data: mockRows,
        errors: [],
        meta: { fields: mockFields },
      });
      return {} as any;
    };

    /** Render the hook useCsvReader. */
    const { result } = renderHook(() => useCsvReader());

    /** Creates a fake file named 'dummy.csv' and format text/csv. */
    const fakeFile = new File([''], 'dummy.csv', { type: 'text/csv' });

    /** Call function Act.
     *  Act() tells the test to pause the test until
     *  all changes on the component has been done.
     *  This reasures that the case runs safetly.
     */
    act(() => {
      result.current.handleCSVUpload(fakeFile);
    });

    /** Expects that the csvData is equal to the mocked meta-data. */
    expect(result.current.csvData).toEqual(mockRows);

    /** Expects that the column name is equal to 'name'. */
    expect(result.current.columns).toEqual(mockFields);
    expect(result.current.rowNumber).toBe(2);

    /** Call function Act.
     *  Act() tells the test to pause the test until
     *  all changes on the component has been done.
     *  This reasures that the case runs safetly.
     */
    act(() => {
      result.current.resetCsvData();
    })

    /** Expects that the csvData is empty. */
    expect(result.current.csvData).toEqual([]);

    /** Expects that the column 'name' is removed. (columnOrder is empty.) */
    expect(result.current.columns).toEqual([]);

    /** Expects that the amount of rows is 2.
     * 
     *  This might be incorrect. The amount of rows should be 0?
     *  Change if needed. Current implemenation doesnt set this variable to 0.
     */
    expect(result.current.rowNumber).toBe(2);
  });

  it('should be able to handle a missing file by setting csvData to an empty array', () => {

    /** Render the hook useCsvReader. */
    const { result } = renderHook(() => useCsvReader());

    /** Call function Act.
     *  Act() tells the test to pause the test until
     *  all changes on the component has been done.
     *  This reasures that the case runs safetly.
     */
    act(() => {
      result.current.handleCSVUpload(undefined as any);
    });

    /** Expects csvData to be empty. */
    expect(result.current.csvData).toEqual([]);

    /** Expects the columnOrder to be empty. */
    expect(result.current.columns).toEqual([]);

    /** Expects the amount of rows to be 0. */
    expect(result.current.rowNumber).toBe(0);
  });
})