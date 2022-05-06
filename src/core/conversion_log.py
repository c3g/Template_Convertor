

class ConversionLog:

    def __init__(self):
        self.messages = {}

    def _add_row(self, rowNumber):
        if not rowNumber in self.messages:
            self.messages[rowNumber] = {
                'errors': [],
                'warnings': []
            }

    def add_error(self, rowNumber, errorMessage):
        self._add_row(rowNumber)
        self.messages[rowNumber]['errors'].append(errorMessage)

    def add_warning(self, rowNumber, warningMessage):
        self._add_row(rowNumber)
        self.messages[rowNumber]['warnings'].append(warningMessage)

    def output_messages(self):
        for rowNumber, messages in self.messages.items():
            for errorMessage in messages['errors']:
                print(f'Row {rowNumber}: {errorMessage}')
            for warningMessage in messages['warnings']:
                print(f'Row {rowNumber}: {warningMessage}')

