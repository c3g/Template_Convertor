# Load template dataframe (or just receive it in constructor?)
# Find header row? Or just append rows to document and assume?
# Append each sample, setting each sample value in the appropriate column
# Write out the template to disk?
from pandas import pandas as pd
from freezeman.freezeman_config import HEADERS
from core.sheet import Sheet


class FMSSampleSubmissionTemplate:
    def __init__(self, data_frame):
        self.sheet = Sheet(data_frame, HEADERS.values())

    def append_samples(self, samples):

        print("*** INITIAL TEMPLATE ***")
        print(self.sheet.data_frame)
        print("************************")

        for sample in samples:
            self._append_sample(sample)

    def _append_sample(self, sample):

        # create a dictionary of sample values, where the keys
        # are the cleaned column names
        data_dict = {}
        sample_vars = vars(sample)
        for key, value in sample_vars.items():
            column_name = HEADERS[key].casefold()
            data_dict[column_name] = value

        self.sheet.add_dictionary_as_row(data_dict)
