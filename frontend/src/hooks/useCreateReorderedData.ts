import Papa from 'papaparse';

type CSVRow = Record<string, string>;
interface ColumnMapping {
  originalIndex: number;
  newIndex: number;
  newName: string;
  oldName: string;
}

/**
 * Hook to reorder and rename columns in a CSV file using stored column mappings.
 * 
 * This hook reads column order and renaming metadata from localStorage (as set by a user or prior process),
 * parses an uploaded CSV file using PapaParse, and generates a new file with reordered and renamed columns.
 * 
 * @returns {Object} An object containing the function to generate the reordered CSV file.
 */
export const useCreateReorderedData = () => {

  /**
   * Reorders and renames columns in a given CSV file based on user-defined mappings stored in localStorage.
   *
   * @param {File} file - The original CSV file to process.
   * @returns {Promise<File>} A promise that resolves with a new CSV `File` object containing reordered columns.
   *
   * @throws {Error} If the column mapping is missing or invalid, or if CSV parsing fails.
   */
  const createNewOrderedCsvFile = (file: File): Promise<File> => {
    return new Promise((resolve, reject) => {
      const columnMapping: ColumnMapping[] = JSON.parse(localStorage.getItem('columnMapping') || '[]');
      const originalColumns: string[] = JSON.parse(localStorage.getItem('originalCsvColumns') || '[]');

      if (!columnMapping || columnMapping.length === 0) {
        reject(new Error('Unexpected error encountered. Please try again later!'));
        return;
      }

      const reorderedLines: string[] = [];

      // Sort the columnMapping by newIndex
      const orderedColumns = [...columnMapping].sort((a, b) => a.newIndex - b.newIndex);
      const columnNames = orderedColumns.map(c => c.newName);
      reorderedLines.push(columnNames.join(','));

      Papa.parse<CSVRow>(file, {
        header: true,
        skipEmptyLines: true,
        worker: true,
        chunkSize: 1024 * 1024, // 1MB chunks
        chunk: ({ data }: { data: CSVRow[] }) => {
          for (const row of data) {
            const reorderedRow = columnMapping
              .sort((a, b) => a.newIndex - b.newIndex)
              .map(i => {
                const originalHeader =
                  i.oldName ?? originalColumns[i.originalIndex];
                return row[originalHeader] ?? '';
              }).join(',');
            reorderedLines.push(reorderedRow);
          }
        },
        complete: () => {
          const csvString = reorderedLines.join('\n');
          const csvBlob = new Blob([csvString], { type: 'text/csv' });
          const reorderedFile = new File([csvBlob], file.name, { type: 'text/csv' });
          resolve(reorderedFile);
        },
        error: (err) => {
          console.error('CSV parsing failed:', err);
          reject(err);
        }
      });
    });
  };

  return { createNewOrderedCsvFile };
};
