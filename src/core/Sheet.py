
import re

from core.ManifestError import ManifestError


class Sheet:
    '''Represents a spreadsheet with helper methods for finding headers and rows'''
    def __init__(self, dataFrame, headers):
        self.dataFrame = dataFrame
        self.headers = headers

        self.headerRowIndex = self._findHeaderRowIndex()
        if self.headerRowIndex == -1:
            raise ManifestError('Unable to locate header row - missing or misnamed columns?')
        # else:
        #     self.dataFrame.columns = self.dataFrame.iloc[self.headerRowIndex]

    def getDataRowRange(self):
        '''Get the index of the first data row in the sheet'''
        numRows = self.dataFrame.shape[0]
        return range(self.headerRowIndex+1, numRows)

    def getRow(self, index):
        return self.dataFrame.iloc[index]
        # return self.dataFrame.iloc[index: index+1, 0:]

    def _isHeaderRow(self, rowTuple):
        MAX_MISMATCHED_HEADER_CELLS = 3
        mismatchedHeaders = []
        matchedHeaders = []
        
        numMismatches = 0
        for col in rowTuple:
        
            # If a row cell contains anything other than a string then it is not a header row
            if not isinstance(col, str):
                return None

            # replace newline or tab characters with spaces, and strip * chars
            cleaned = col.replace('\n', ' ').strip(' \t\r\*')
            # replace 2 or more concurrent spaces with a single space
            cleaned = re.sub(r'\s{2,}', ' ', cleaned)
            # convert to lower case
            cleaned = cleaned.casefold()

            if cleaned in self.headers:
                matchedHeaders.append(cleaned)
            else:
                mismatchedHeaders.append(cleaned)
                matchedHeaders.append(f"UNKNOWN{numMismatches}")
                numMismatches += 1
                if numMismatches > MAX_MISMATCHED_HEADER_CELLS:
                    return None
        print('Mismatched headers: ', mismatchedHeaders)

        return matchedHeaders

    def _findHeaderRowIndex(self):
        MAX_ROWS_TO_CHECK = 10
        rowNumber = 0
        for row in self.dataFrame.itertuples(index = False, name = None):
            matchedHeaders = self._isHeaderRow(row)
            if matchedHeaders != None:

                headerCount = len(matchedHeaders)
                while headerCount < len(self.dataFrame.columns):
                    matchedHeaders[headerCount] = self.dataFrame.columns[headerCount]
                    headerCount += 1

                self.dataFrame.columns = matchedHeaders
                return rowNumber
            rowNumber += 1
            if rowNumber > MAX_ROWS_TO_CHECK:
                break
        return -1