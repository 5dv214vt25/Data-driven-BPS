import { it, expect, describe, vi, beforeEach, afterEach } from 'vitest'
import { renderHook } from '@testing-library/react'
import Papa from 'papaparse'

import { useCreateReorderedData } from '../../src/hooks/useCreateReorderedData'

/** 
 *  Test for hook: 'useCreateReorderedData'.
 * 
 *  Test that are included:
 * 
 *  Component should create a file with the correct name, type and CSV content.
 *  Component should be able to handle empty data by producing an empty CSV.
 * 
 */

/** Help-function to be able to read file as text. */
function readFileAsText(file: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = () => reject(reader.error);
    reader.readAsText(file);
  });
}

/** Help function to create a input file needed for the function */
function createCsvFile(data: Record<string, string>[], filename = 'test.csv') {
  return new File([Papa.unparse(data)], filename, { type: 'text/csv' });
}

describe('useCreateReorderedData → createNewOrderedCsvFile', () => {
  beforeEach(() => {
    /** Setup required localStorage values */
    localStorage.setItem('originalCsvColumns', JSON.stringify(['name', 'age']));
    localStorage.setItem('columnMapping', JSON.stringify([
      { originalIndex: 0, newIndex: 0, newName: 'name', oldName: 'name' },
      { originalIndex: 1, newIndex: 1, newName: 'age', oldName: 'age' },
    ]));
  });

  afterEach(() => {
    localStorage.clear();
  });

  it('should create a file with the correct name, type and CSV content', async () => {

    /** Render the hook useCreateReorderedData. */
    const { result } = renderHook(() => useCreateReorderedData());
    const { createNewOrderedCsvFile } = result.current

    /** Mock-up meta data representing a csv file. */
    const data = [
      { name: "Lennart", age: "54" },
      { name: "Åsa", age: "50" },
    ];

    /** The file name to be used. */
    const filename = 'test.csv';

    /** Create the inputFile */
    const inputFile = createCsvFile(data, 'test.csv');

    /** Creates a ordered csv file with name: 'test.csv' and data as its content. */
    const file = await createNewOrderedCsvFile(inputFile);

    /** Expects that the file created is a of type File. */
    expect(file).toBeInstanceOf(File);

    /** Expects that the name of the file is 'test.csv' */
    expect(file.name).toBe(filename);

    /** Expects that the format/type to be of text/csv. */
    expect(file.type).toBe('text/csv');

    const text = await readFileAsText(file);

    /** Expects that the content that is unparsed is equal
     * to the text genereated by function readFileAsText().
     */
    expect(text.replace(/\r\n/g, '\n')).toBe(Papa.unparse(data).replace(/\r\n/g, '\n'));
  })

  it('should be able to handle empty data by producing an empty CSV', async () => {

    /** Clear the localStorage to make columnMapping empty */
    localStorage.setItem('originalCsvColumns', JSON.stringify([]));
    localStorage.setItem('columnMapping', JSON.stringify([]));

    /** Render the hook useCreateReorderedData. */
    const { result } = renderHook(() => useCreateReorderedData());
    const { createNewOrderedCsvFile } = result.current

    /** Set up the empty file */
    const emptyFile = createCsvFile([], 'empty.csv');

    /** Exec createNewOrderdeCsvFile on empty csv file resulting in a rejection*/
    await expect(createNewOrderedCsvFile(emptyFile)).rejects.toThrow();
  })
})