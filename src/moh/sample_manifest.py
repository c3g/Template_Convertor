
from pandas import pandas as pd

from core.sheet import Sheet
from .moh_config import HEADERS

class MOHSampleManifest(Sheet):

    def __init__(self, dataFrame):
        super().__init__(dataFrame, HEADERS.values())

        # After loading the sheet, finding the header row and cleaning up the column names,
        # we filter out any rows that have NaN in the sample name column, assuming that those
        # are blank rows. We keep all rows where the sample name is not NaN.
        # TODO maybe we should also get rid of the rows above and including the column header row
        # and simply have a table of samples?
        self.dataFrame = self.dataFrame[pd.notna(self.dataFrame['sample name, pool name or existing lims id'])]


