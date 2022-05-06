

class ConversionLog:

    def __init__(self):
        self.messages = {}

    def _add_row(self, row_number):
        if not row_number in self.messages:
            self.messages[row_number] = {
                'errors': [],
                'warnings': []
            }

    def add_error(self, row_number, error_message):
        self._add_row(row_number)
        self.messages[row_number]['errors'].append(error_message)

    def add_warning(self, row_number, warning_message):
        self._add_row(row_number)
        self.messages[row_number]['warnings'].append(warning_message)

    def output_messages(self):
        for row_number, messages in self.messages.items():
            for error_message in messages['errors']:
                print(f'Row {row_number}: {error_message}')
            for warning_message in messages['warnings']:
                print(f'Row {row_number}: {warning_message}')

