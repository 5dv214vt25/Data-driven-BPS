import Fuse from 'fuse.js';
import { distance } from 'fastest-levenshtein';
import dayjs from 'dayjs';
import validator from 'validator';
//fastest levenstein
//fuzzy search
// <script src="https://cdn.jsdelivr.net/npm/fuse.js@7.1.0"></script>

//Define the const that holds all headers
const expectedHeaders = ['case_id', 'resource', 'activity', 'start_time', 'end_time'];
type CSVRow = Record<string, string>;


export const useAutomatedSuggestions = () => {
  const checkHeaderNames = (headers: string[], data: CSVRow[]): string[] => {
    // Before we do anything lets take the first row from the data and check if we find two columns that are dates
    const sampleRow = data[0] || {};

    //Get all date columns
    const dateColumns = headers.reduce((acc: string[], header) => {
      const value = sampleRow[header];
      if (value && validator.isISO8601(value)) {
        acc.push(header);
      }
      return acc;
    }, []);

    // Check if we have anything in the list (if not just continue to the fuse)
    if (dateColumns.length >= 2) {
      const [firstDateCol, secondDateCol] = dateColumns;
      let startCol = firstDateCol;
      let endCol = secondDateCol;

      // Swap the columns if the second date is earlier than the first one
      if (dayjs(sampleRow[secondDateCol]).isBefore(dayjs(sampleRow[firstDateCol]))) {
        startCol = secondDateCol;
        endCol = firstDateCol;
      }

      headers = headers.map((header) => {
        if (header === startCol) {
          return 'start_time';
        } else if (header === endCol) {
          return 'end_time';
        }
        return header;
      });
    }

    //First things first we use the fuse to fuzzy match keywords and change them accordingly
    const fuse = new Fuse(expectedHeaders, {
      threshold: 0.5,
      includeScore: true
    });

    // Use the fuse to go through all headers and proceed to change name
    const newHeaders = headers.map((name) => {
      const result = fuse.search(name);
      if (result.length > 0 && result[0].score !== undefined && result[0].score < 0.2) {
        return result[0].item;
      } else {
        // Check with levenshtein wether we can still suggest anything
        let closestMatch = name;
        let smallestDistance = Infinity;

        expectedHeaders.forEach((expected) => {
          const dist = distance(name.toLowerCase(), expected.toLowerCase());
          if (dist < smallestDistance) {
            smallestDistance = dist;
            closestMatch = expected;
          }
        });

        //Calculate if the closest match that is acceptable
        const normalized = smallestDistance / Math.max(name.length, closestMatch.length);
        //console.log(closestMatch, normalized);
        if (normalized < 0.3) {
          return closestMatch;
        }

        // Fallback on the default and ask the user to manually change it
        return name;
      }
    });

    // Return the new header names
    return newHeaders;
  }

  return { checkHeaderNames };
}