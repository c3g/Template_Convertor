import re
from pandas import pandas as pd
from ..core import ManifestError
from .moh_config import HEADERS

def clean_header_string(header_string: str) -> str:
    """ 
    MOH header strings can contain junk like newline characters, leading
    and trailing spaces or double spaces. This function cleans out the
    junk so that we can do a sane string compare with the header strings
    we are expecting.
    """

    # replace newline or tab characters with spaces, and strip * chars
    cleaned = header_string.replace("\n", " ").strip(" \t\r\*")
    # replace 2 or more concurrent spaces with a single space
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    # convert to lower case
    cleaned = cleaned.casefold()

    return cleaned

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

    def identify_headers(self, rowTuple):
        """
        Checks a row to see if it contains the column headers we are expecting to find in the manifest.
        If all of the expected headers are found then it returns a list of header strings to be used
        as column keys.
        If it matches almost all of the headers, it will throw an exception that lists the headers
        it could not find.
        If it finds no matches or fewer matches than expected, it returns None.

        This function supports various use cases:
        - Columns out of order
        - Empty columns (empty columns are ignored)
        - Duplicate columns (all but the first will be ignored)
        - Arbitrary extra columns (ignored)
        """
        MAX_MISMATCHED_HEADER_CELLS = 3

        # Keeps track of the headers we are expecting to find.
        expected_headers = self.cleaned_headers.copy()

        # Collected column headers
        column_headers = []

        for col in rowTuple:
            # An empty colum has a 'nan' value. Just add a dummy header
            # value for the column and continue.
            if not isinstance(col, str):
                column_headers.append(f"IGNORED-{len(column_headers)}")
                continue

            # Clean up the header string
            cleaned = clean_header_string(col)

            # Catch duplicate column header values. Having a duplicate key can cause
            # a pandas exception <The truth value of a Series is ambiguous.>
            # The convertor will ignore any duplicate columns.
            if cleaned in column_headers:
                column_headers.append(f"DUPLICATE-{cleaned}-{len(column_headers)}")
                continue

            # Add the string to the column headers list. We need a key for the
            # column regardless whether it's an expected header or something else.
            column_headers.append(cleaned)

            # If it's an expected header, remove it from expected_headers
            if cleaned in expected_headers:
                expected_headers.remove(cleaned)

        # If all headers were found then we are golden.
        if len(expected_headers) == 0:
            return column_headers

        # If we found most of the headers, but a few were missing then raise an error.
        if len(expected_headers) <= MAX_MISMATCHED_HEADER_CELLS:
            # TODO add this to log?
            message = "Expected columns were not found in manifest: " + ", ".join(map(lambda s : f"'{s}'", expected_headers))
            raise ManifestError(message)
        
        # This row didn't match enough (or any) expected columns to be considered the header row.
        return None

    def _find_header_row_index(self):
        MAX_ROWS_TO_CHECK = 10
        for row in self.data_frame.itertuples(index=True, name=None):
            # the line number is first item in tuple
            line_number = row[0]
            # pass the row, excluding first line number element in the tuple
            matched_headers = self.identify_headers(row[1:])
            if matched_headers is not None:

                # Use the matched header values as keys for the columns.
                # If the sheet contains more columns than headers then append
                # the existing column keys to the header list. If we don't, pandas
                # will throw an exception because the number of keys does not match
                # the number of columns.
                header_count = len(matched_headers)
                while header_count < len(self.data_frame.columns):
                    # grab whatever key is currently on the extra column and add it to the list
                    matched_headers.append(self.data_frame.columns[header_count])
                    header_count += 1

                # Set column keys on the columns.
                self.data_frame.columns = matched_headers
                return line_number
            # Abort if we can't find the header row within the first MAX_ROWS_TO_CHECK rows of the sheet.
            if line_number > MAX_ROWS_TO_CHECK:
                break
        return -1
