import re
from pandas import pandas as pd
from core.manifest_error import ManifestError
from .moh_config import HEADERS


class MOHSampleManifest:
    def __init__(self, data_frame):
        self.headers = HEADERS.values()
        self.data_frame = data_frame
        self.cleaned_headers = list(map(lambda h: h.casefold(), self.headers))

        self.header_row_index = self._find_header_row_index()
        if self.header_row_index == -1:
            raise ManifestError(
                "Unable to locate header row - missing or misnamed columns?"
            )

    def get_data_row_range(self):
        """Get the index of the first data row in the sheet"""
        numRows = self.data_frame.shape[0]
        return range(self.header_row_index + 1, numRows)

    def get_row(self, index):
        return self.data_frame.iloc[index]
        # return self.dataFrame.iloc[index: index+1, 0:]

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
        print("Mismatched headers: ", mismatched_headers)

        return matched_headers

    def _find_header_row_index(self):
        MAX_ROWS_TO_CHECK = 10
        row_number = 0
        for row in self.data_frame.itertuples(index=False, name=None):
            matched_headers = self.is_header_row(row)
            if matched_headers is not None:

                header_count = len(matched_headers)
                while header_count < len(self.data_frame.columns):
                    matched_headers[header_count] = self.data_frame.columns[
                        header_count
                    ]
                    header_count += 1

                self.data_frame.columns = matched_headers
                return row_number
            row_number += 1
            if row_number > MAX_ROWS_TO_CHECK:
                break
        return -1
