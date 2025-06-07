// src/hooks/useCsvReader.ts
import { useState } from 'react';
import Papa from 'papaparse';

type CSVRow = Record<string, string>;

/**
 * Hook to handle uploading and parsing CSV files.
 *
 * React hook for parsing and reading CSV files using PapaParse.
 * Stores preview data, headers, and row count in state.
 * Also stores original column order in localStorage.
 * 
 * @returns {Object} Parsed data, column headers, row count, and control functions.
 */
export const useCsvReader = () => {
  const [csvData, setCSVData] = useState<CSVRow[]>([]);
  const [columns, setColumns] = useState<string[]>([]);
  const [rowNumber, setRowNumber] = useState<int>(0);

  /**
   * Parses the provided CSV file and stores the results in local state.
   * Also saves the original column order to localStorage.
   *
   * @param {File} file - CSV file to parse.
   */
  const handleCSVUpload = (file: File) => {
    if (!file) {
      setCSVData([]);
      return;
    }

    Papa.parse<CSVRow>(file, {
      header: true,
      skipEmptyLines: true,
      preview: 20,
      complete: (results) => {

        console.log('parsing complete');
        const headers = results.meta.fields || []
        const rows = results.data.length

        setRowNumber(rows)
        setCSVData(results.data)
        setColumns(headers)

        // Save the original columnOrder in the localStorage
        localStorage.setItem('originalCsvColumns', JSON.stringify(headers));
      },
      error: (err) => {
        console.error(' csv parsing error', err);
      }
    });
  }

  /**
   * Resets stored CSV data and columns.
   */
  const resetCsvData = () => {
    setCSVData([]);
    setColumns([]);
  };

  return { csvData, columns, rowNumber, handleCSVUpload, resetCsvData };
};