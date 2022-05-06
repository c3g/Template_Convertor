
from pandas import pandas as pd

from core.sheet import Sheet
from .moh_config import HEADERS

class MOHSampleManifest(Sheet):

    def __init__(self, data_frame):
        super().__init__(data_frame, HEADERS.values())

        # After loading the sheet, finding the header row and cleaning up the column names,
        # we filter out any rows that have NaN in the sample name column, assuming that those
        # are blank rows. We keep all rows where the sample name is not NaN.
        # TODO maybe we should also get rid of the rows above and including the column header row
        # and simply have a table of samples?
        self.data_frame = self.data_frame[pd.notna(self.data_frame[HEADERS['SAMPLE_NAME']])]


