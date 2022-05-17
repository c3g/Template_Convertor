class ConversionLog:
    def __init__(self):
        # dictionary, where the row number is key and the value is a struct
        # {
        #   errors: [list of error message strings],
        #   warnings: [list of warning message strings]
        # }
        self.general_messages = []
        self.row_messages = {}

    def add_general_message(self, msg):
        self.general_messages.append(msg)

    def _add_row(self, row_number):
        if not row_number in self.row_messages:
            self.row_messages[row_number] = {"errors": [], "warnings": []}

    def add_error(self, row_number, error_message):
        self._add_row(row_number)
        self.row_messages[row_number]["errors"].append(error_message)

    def add_warning(self, row_number, warning_message):
        self._add_row(row_number)
        self.row_messages[row_number]["warnings"].append(warning_message)

    def output_messages(self):
        for general_message in self.general_messages:
            print(general_message)

        print()

        for row_number, messages in self.row_messages.items():
            for error_message in messages["errors"]:
                print(f"Row {row_number}: ERROR: {error_message}")
            for warning_message in messages["warnings"]:
                print(f"Row {row_number}: WARNING: {warning_message}")

    def write_log(self, log_path):
        # TODO pass an open file stream to this function rather than opening the file here

        # count the number of errors and warnings
        num_messages = 0
        for msgs in self.row_messages.values():
            num_messages += len(msgs["errors"]) + len(msgs["warnings"])

        with open(log_path, "w", encoding="utf-8") as log_file:
            log_file.write("Conversion log\n")

            for general_message in self.general_messages:
                log_file.write(f"{general_message}\n")

            if num_messages == 0:
                log_file.write("No errors or warnings\n")
            else:
                for (row_number, messages) in self.row_messages.items():
                    for msg in messages["errors"]:
                        log_file.write(f"Row {row_number}: ERROR:   {msg}\n")
                    for msg in messages["warnings"]:
                        log_file.write(f"Row {row_number}: WARNING: {msg}\n")
