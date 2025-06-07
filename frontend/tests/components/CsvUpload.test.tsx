import React from 'react';
import { describe, it, expect, vi, afterEach } from 'vitest';
import { render, screen, cleanup } from '@testing-library/react';
import '@testing-library/jest-dom';
import CsvUpload from '../../src/components/CsvUpload';
import userEvent from '@testing-library/user-event';

/**
 *  File is not used?
 */

/**
 * Test for component 'SelectDropdown'.
 *
 * Test that are included:
 * Checks if the save button is disabled when no csv file has been uploaded.
 * Checks if component can handle a valid csv file.
 * Checks if component rejects a invalid csv file.
 * Checks if component shows an error when clicking Save with no User Id.
 */

describe('CsvUpload', () => {
  /**
   * Function to be called before every 'it'-function.
   * Removes mock-ups and cleans other data.
   */
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it('Checks if save button is disabled when no csv file has been uploaded'),
  () => {
    /** Mock-ups */
    const onFileSelected = vi.fn();
    const onFileSave = vi.fn();

    /**
       * Render the component.
       */
    render(<CsvUpload onFileSelected={onFileSelected} onFileSave={onFileSave} />);

    /**
       * Fetch the save button and checks if its disabled.
       */
    const saveButton = screen.getByRole('button', { name: '/save/i' });
    expect(saveButton).toBeDisabled();
  };

  it('can handle valid CSV upload'),
  async () => {
    const user = userEvent.setup();

    /** Mock-ups */
    const onFileSelected = vi.fn();
    const onFileSave = vi.fn();

    /** Render the component. */
    render(<CsvUpload onFileSelected={onFileSelected} onFileSave={onFileSave} />);

    /** Get file input section. */
    const fileInput = screen.getByTestId('file-input') as HTMLInputElement;
    /** Get the save button */
    const saveButton = screen.getByRole('button', { name: '/save/i' });
    /** Create a simple file. */
    const csv = new File(['col1,col2\nx,y'], 'data.csv', { type: 'text/csv' });

    /** Excepts that the save button is disabled, as the file hasnt been uploaded. */
    expect(saveButton).toBeDisabled();
    /** Uploads the file */
    await user.upload(fileInput, csv);

    /** Expects that onFileSelected has been called 1 time. */
    expect(onFileSelected).toHaveBeenCalledTimes(1);
    /** Expects that onFileSelected has been called with the file. */
    expect(onFileSelected).toHaveBeenCalledWith(csv);
    /** Expects that the save button is enabled. */
    expect(saveButton).toBeEnabled();
    /** Expects that the document has rendered correct text. (Selected file: data.csv) */
    expect(screen.getByText(/Selected file:.*data\.csv/i)).toBeInTheDocument();
  };

  it('Rejects a non csv file and shows an error message/popup'),
  async () => {
    const user = userEvent.setup();

    /** Mock-ups */
    const onFileSelected = vi.fn();
    const onFileSave = vi.fn();

    /** Render the component. */
    render(<CsvUpload onFileSelected={onFileSelected} onFileSave={onFileSave} />);

    /** Retrive the file insertion part of the component. */
    const fileInput = screen.getByTestId('file-input') as HTMLInputElement;
    /** Create a simple text file with content: text: 'Hello world!', name: 'helloworld.txt' and format: text/plain */
    const txtfile = new File(['Hello world!'], 'helloworld.txt', { type: 'text/plain' });

    /** Upload the simple text file. */
    await user.upload(fileInput, txtfile);

    /** Expects that onFileSelected hasnt been called. */
    expect(onFileSelected).not.toHaveBeenCalled();
    /** Expects that the text 'Please upload a valid CSV file' to be displayed. */
    expect(screen.getByText('Please upload a valid CSV file')).toBeInTheDocument();

  };

  it('Shows an error when clicking Save with no User Id'),
  async () => {
    const user = userEvent.setup();

    /** Mock-ups */
    const onFileSelected = vi.fn();
    const onFileSave = vi.fn();

    /** Render the component. */
    render(<CsvUpload onFileSelected={onFileSelected} onFileSave={onFileSave} />);

    /** Get file input section. */
    const fileInput = screen.getByTestId('file-input') as HTMLInputElement;
    /** Get the save button */
    const saveButton = screen.getByRole('button', { name: '/save/i' });
    /** Create a simple file. */
    const csv = new File(['col1,col2\nx,y'], 'data.csv', { type: 'text/csv' });

    /** Uploads the file */
    await user.upload(fileInput, csv);

    /** Simulate a click on save button. */
    await user.click(saveButton);

    /** Expects that onFileSave havent been called. */
    expect(onFileSave).not.toHaveBeenCalled();
    /** Expects that 'Please upload a valid CSV file' is displayed. */
    expect(screen.getByText('Please upload a valid CSV file.')).toBeInTheDocument();
  }
}); 