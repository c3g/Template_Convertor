import re
from pandas import pandas as pd
from ..core import ManifestError
from .moh_config import HEADERS


class MOHSampleManifest:
    def __init__(self, data_frame):
        self.headers = HEADERS.values()
        self.data_frame = data_frame
        self.cleaned_headers = list(map(lambda h: h.casefold(), self.headers))

        # Using iloc to reference rows is a problem because when we iterate over rows
        # pandas ignores rows with NaN values. There are two empty rows in the manifest
        # header, and this throws line numbering off by two.
        # Force a line number index onto the rows, and then reference the rows by
        # this line number index. This ensures there is a line number on every row,
        # including empty rows.
        num_rows = self.data_frame.shape[0]
        # create a line number array to use as index, starting at 1
        line_nums = [n for n in range(1, num_rows+1)]
        # set the index
        self.data_frame.set_index(pd.Index(line_nums), drop=False, inplace=True)

        self.header_row_index = self._find_header_row_index()
        if self.header_row_index == -1:
            raise ManifestError(
                "Unable to locate header row - missing or misnamed columns?"
            )

    def get_data_row_range(self):
        """Get the range of line numbers for the data rows in the sheet"""
        numRows = self.data_frame.shape[0]
        return range(self.header_row_index + 1, numRows + 1)

    def get_row(self, line_number):
        # Use loc to get the row with the line number index we set on the row in the constructor
        return self.data_frame.loc[line_number]

    def is_header_row(self, rowTuple):
        MAX_MISMATCHED_HEADER_CELLS = 3
        mismatched_headers = []
        matched_headers = []

        num_mismatches = 0
        for col in rowTuple:

            # If a row cell contains anything other than a string then it is not a header row
            if not isinstance(col, str):
                return None

            # replace newline or tab characters with spaces, and strip * chars
            cleaned = col.replace("\n", " ").strip(" \t\r\*")
            # replace 2 or more concurrent spaces with a single space
            cleaned = re.sub(r"\s{2,}", " ", cleaned)
            # convert to lower case
            cleaned = cleaned.casefold()

            if cleaned in self.cleaned_headers:
                matched_headers.append(cleaned)
            else:
                mismatched_headers.append(cleaned)
                matched_headers.append(f"UNKNOWN{num_mismatches}")
                num_mismatches += 1
                if num_mismatches > MAX_MISMATCHED_HEADER_CELLS:
                    return None
        if len(mismatched_headers) > 0:
            print("Mismatched headers: ", mismatched_headers)

        return matched_headers

    def _find_header_row_index(self):
        MAX_ROWS_TO_CHECK = 10
        for row in self.data_frame.itertuples(index=True, name=None):
            # the line number is first item in tuple
            line_number = row[0]
            # pass the row, excluding first line number element in the tuple
            matched_headers = self.is_header_row(row[1:])
            if matched_headers is not None:
                header_count = len(matched_headers)
                while header_count < len(self.data_frame.columns):
                    matched_headers[header_count] = self.data_frame.columns[header_count]
                    header_count += 1

                self.data_frame.columns = matched_headers
                return line_number
            # Abort if we can't find the header row within the first MAX_ROWS_TO_CHECK rows of the sheet.
            if line_number > MAX_ROWS_TO_CHECK:
                break
        return -1
