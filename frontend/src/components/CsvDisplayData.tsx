/**
 * CsvDisplayData
 * 
 * Shows the user a table preview of the CSV file.
 * Allows the user to manually map new column names or
 * with automated suggestions. 
 * 
 */

import React, { useEffect, useState, useImperativeHandle, forwardRef } from 'react';
import {
  Table,
  TableHeaderRow,
  TableHeaderCell,
  TableRow,
  TableCell,
  TableGrowing,
  Button
} from '@ui5/webcomponents-react';

import {
  DndContext,
  closestCenter,
  MouseSensor,
  useSensor,
  useSensors,
  DragEndEvent,
  DragOverlay,
} from '@dnd-kit/core';

import {
  SortableContext,
  useSortable,
  horizontalListSortingStrategy,
} from '@dnd-kit/sortable';

import { CSS } from '@dnd-kit/utilities';
import '../assets/styles/EventLogTable.css';
import { PopupMessage } from './PopupMessage';
import { usePopup } from '../hooks/usePopup';
import { useAutomatedSuggestions } from '../hooks/useAutomatedSuggestion';

type CSVRow = Record<string, string>;
/**
 * Represents columning of old and new structure
 */
interface ColumnMapping {
  originalIndex: number;
  newIndex: number;
  newName: string;
  oldName: string;
}

/**
 * Props:
 * - PreviewData: Data preview for users to rearrage column order and names
 * - Columns: Columns in the uploaded file
 * - rowNumber: Specific row number in the uploaded file
 */

interface CsvDisplayDataProps {
  previewData: CSVRow[];
  columns: string[];
  rowNumber: number;
}

/**
 * Reference to call functions   
*/
export interface CsvDisplayDataRef {
  reset: () => void;
}

/**
 * The column header rearragement cell   
*/
const SortableHeaderCell: React.FC<{
  id: string;
  order: string[];
  onRename: (oldId: string, newId: string) => void;
}> = ({ id, order, onRename }) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id });

  const [isEditing, setIsEditing] = useState(false);
  const [newLabel, setNewLabel] = useState(id);

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    cursor: 'grab',
    padding: '9px',
    backgroundColor: isDragging ? '#f0f0f0' : '#ffffff',
    fontWeight: 500,
    zIndex: isDragging ? 1000 : 'auto',
  };

  const handleDoubleClick = () => setIsEditing(true);
  /**
   * HandleBlur automatically saves text input when 
   * when input box is not clicked.
  */
  const handleBlur = () => {
    const trimmedLabel = newLabel.trim();

    if (trimmedLabel !== id) {
      onRename(id, trimmedLabel);
    }
    if (order.includes(trimmedLabel)) {
      setNewLabel(id);
    }
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleBlur();
    }
  };

  return (
    <TableHeaderCell
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      onDoubleClick={handleDoubleClick}
    >
      {isEditing ? (
        <input
          value={newLabel}
          onChange={(e) => setNewLabel(e.target.value)}
          onBlur={handleBlur}
          onKeyDown={handleKeyDown}
          autoFocus
          style={{
            width: '90%',
            fontSize: 'inherit',
            fontWeight: 'inherit',
            border: 'none',
            background: 'transparent',
            outline: '1px solid #ccc',
          }}
        />
      ) : (
        <span style={{
          width: '90%',
          padding: '0.2rem',
          borderRadius: '0.1rem',
          outline: '1px dashed #ccc'
        }}>{newLabel}</span>
      )}
    </TableHeaderCell>
  );
};

const CsvDisplayData = forwardRef<CsvDisplayDataRef, CsvDisplayDataProps>(

  ({ previewData, columns, rowNumber }, ref) => {

    const [csvData, setCsvData] = useState<CSVRow[]>([]);
    const [columnMapping, setcolumnMapping] = useState<ColumnMapping[]>([]);
    const [initialized, setInitialized] = useState(false);
    const [activeId, setActiveId] = useState<string | null>(null);
    const [visibleCount, setVisibleCount] = useState(10);
    const [hasSuggestions, setHasSuggestion] = useState(false);
    const [suggestedHeaders, setSuggestedHeaders] = useState<string[]>([]);
    const [usedSuggestedHeaders, setUsedSuggesedHeaders] = useState(false);
    const { message: popupMessage, type: popupType, showPopup, closePopup } = usePopup();
    const { checkHeaderNames } = useAutomatedSuggestions();

    const neededHeaderNames = ['case_id', 'resource', 'activity', 'start_time', 'end_time'];

    /**
     * Initializes the component
    */
    useEffect(() => {
      if (!initialized && columns.length > 0) {
        const saved = localStorage.getItem('columnMapping');
        const defaultMapping = columns.map((name, idx): ColumnMapping => ({
          originalIndex: idx,
          newIndex: idx,
          newName: name,
          oldName: name,
        }));

        if (saved) {
          try {
            setcolumnMapping(JSON.parse(saved));
          } catch {
            setcolumnMapping(defaultMapping);
          }
        } else {
          setcolumnMapping(defaultMapping);
        }

        if (rowNumber > 10) {
          setVisibleCount(10);
        } else {
          setVisibleCount(rowNumber);
        }

        const savedCsv = localStorage.getItem('csvData');
        if (savedCsv) {
          try {
            setCsvData(JSON.parse(savedCsv));
          } catch {
            setCsvData(previewData);
          }
        } else {
          setCsvData(previewData);
        }

        setInitialized(true);
      }
    }, [columns, rowNumber, initialized]);

    /**
     * Saves column mapping and csvData in broswer
    */
    useEffect(() => {
      if (initialized && columnMapping.length > 0) {
        localStorage.setItem('columnMapping', JSON.stringify(columnMapping));
        localStorage.setItem('csvData', JSON.stringify(csvData));
      }
    }, [columnMapping, csvData, initialized]);

    /**
     * Checks for missing headers, sets suggestions for automated headers. 
    */
    useEffect(() => {
      const miss = includesHeaderName();
      if (miss.length > 0) {
        const headers = columnMapping.map(c => c.newName);
        const suggestions = checkHeaderNames(headers, csvData);
        if (suggestions.length > 0) {
          setSuggestedHeaders(suggestions);
          setHasSuggestion(true);
        }
      }
    }, [initialized, columnMapping, csvData]);

    /**
     * checks for mandatory column names 
    */
    const includesHeaderName = (): string[] => {
      const names = columnMapping.map(c => c.newName.toLowerCase().trim());
      return neededHeaderNames.filter(req => !names.includes(req.toLowerCase()));
    };

    /**
     * Update column names with automated suggestions 
    */
    const updateDataWithAutomatedSuggestions = () => {
      if (suggestedHeaders.length !== columnMapping.length) {
        showPopup("error", "Header suggestion mismatch. Cannot apply suggestions.");
        return;
      }

      const newMapping = columnMapping.map((m, i) => ({
        ...m,
        newName: suggestedHeaders[i],
      }));

      const headerMap: Record<string, string> = {};
      columnMapping.forEach((m, i) => {
        headerMap[m.newName] = suggestedHeaders[i];
      });

      const updatedData = csvData.map((row) => {
        const updatedRow: CSVRow = {};
        for (const key in row) {
          const newKey = headerMap[key] || key;
          updatedRow[newKey] = row[key];
        }
        return updatedRow;
      });

      setcolumnMapping(newMapping);
      setCsvData(updatedData);
      setUsedSuggesedHeaders(true);
      showPopup("success", "Headers updated using automated suggestions.");
    };

    const sensors = useSensors(useSensor(MouseSensor, { activationConstraint: { distance: 5 } }));
    const orderedColumns = [...columnMapping].sort((a, b) => a.newIndex - b.newIndex);
    const columnNames = orderedColumns.map(c => c.newName);
    const reorderedData = csvData.map(row => {
      const newRow: CSVRow = {};
      columnNames.forEach(name => {
        newRow[name] = row[name];
      });
      return newRow;
    });

    /**
     * Resets data
    */
    const resetEverything = () => {
      setcolumnMapping([]);
      setCsvData([]);
      setInitialized(false);
      setHasSuggestion(false);
      setSuggestedHeaders([]);
      setUsedSuggesedHeaders(false);
    };

    useImperativeHandle(ref, () => ({
      reset: () => resetEverything(),
    }));

    /**
     * Enables drag and drop feature for column mapping. 
    */
    const handleDragEnd = (event: DragEndEvent) => {
      const { active, over } = event;
      if (!active || !over || active.id === over.id) { return; }

      const oldIdx = columnMapping.find(c => c.newName === active.id)?.newIndex;
      const newIdx = columnMapping.find(c => c.newName === over.id)?.newIndex;

      if (oldIdx == null || newIdx == null) { return; }

      const updated = columnMapping.map((col) => {
        if (col.newIndex === oldIdx) {
          return { ...col, newIndex: newIdx };
        }
        if (oldIdx < newIdx && col.newIndex > oldIdx && col.newIndex <= newIdx) {
          return { ...col, newIndex: col.newIndex - 1 };
        }
        if (oldIdx > newIdx && col.newIndex < oldIdx && col.newIndex >= newIdx) {
          return { ...col, newIndex: col.newIndex + 1 };
        }
        return col;
      });

      setcolumnMapping(updated);
      setActiveId(null);
    };

    /**
     * Sets new column names
    */
    const handleRename = (oldId: string, newId: string) => {
      if (columnMapping.some(c => c.newName === newId)) {
        showPopup("error", "Column name already exists.");
        return;
      }

      setcolumnMapping(prev =>
        prev.map(col =>
          col.newName === oldId ? { ...col, newName: newId } : col
        )
      );

      setCsvData(prev =>
        prev.map(row => {
          const { [oldId]: value, ...rest } = row;
          return { ...rest, [newId]: value ?? '' };
        })
      );
    };

    /**
     * Expands table preview
    */
    const onLoadMore = () => setVisibleCount(prev => prev + 5);

    const tableFeature = () =>
      visibleCount < rowNumber ? <TableGrowing mode="Button" onLoadMore={onLoadMore} /> : null;

    return (
      <div>
        {(() => {
          const missing = includesHeaderName();
          return missing.length > 0 && columnMapping.length > 0 && (
            <>
              <p><strong>Required columns:</strong> case_id, resource, activity, start_time, end_time</p>
              <p style={{ color: 'red' }}><strong>Missing:</strong> {missing.join(', ')}</p>
              <p>Edit column names by <strong>double-clicking</strong> them</p>
            </>
          );
        })()}

        {csvData.length > 0 ? (
          <>
            <h3>Event Log preview</h3>
            <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
              <div style={{ overflowX: 'auto', maxHeight: '55vh', minHeight: '200px' }}>
                <Table features={tableFeature()} style={{ width: '100%' }}>
                  <TableHeaderRow slot="headerRow" sticky>
                    <SortableContext items={columnNames} strategy={horizontalListSortingStrategy}>
                      {columnNames.map((col) => (
                        <SortableHeaderCell
                          key={col}
                          id={col}
                          order={columnNames}
                          onRename={handleRename}
                        />
                      ))}
                    </SortableContext>
                  </TableHeaderRow>
                  {reorderedData.slice(0, visibleCount).map((row, idx) => (
                    <TableRow key={idx} className='listRow'>
                      {columnNames.map(col => (
                        <TableCell key={col}>{row[col]}</TableCell>
                      ))}
                    </TableRow>
                  ))}
                </Table>
              </div>

              {hasSuggestions && !usedSuggestedHeaders && (
                <div style={{ marginTop: '2rem', display: 'flex', justifyContent: 'center' }}>
                  <Button design="Emphasized" onClick={updateDataWithAutomatedSuggestions}>
                    Use automated suggestions
                  </Button>
                </div>
              )}

              <DragOverlay>{activeId && <div>{activeId}</div>}</DragOverlay>
            </DndContext>
          </>
        ) : (
          <div style={{ marginTop: '1rem' }}>
            <h3>No uploaded data available yet.</h3>
          </div>
        )}

        <PopupMessage
          show={!!popupMessage}
          type={popupType}
          message={popupMessage}
          duration={4000}
          onClose={closePopup}
        />
      </div>
    );
  });

export default CsvDisplayData;
