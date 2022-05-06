
from types import SimpleNamespace
from pandas import pandas as pd
from core.conversion_log import ConversionLog
from freezeman.freezeman_config import CONTAINER_KIND, HEADERS as FMS_HEADERS
from freezeman.sample import FreezemanSample
from .moh_config import HEADERS, SAMPLE_TYPES, CONTAINER_TYPES, TISSUE_TYPE_MAP, NUCLEIC_ACID_TYPE_MAP
from .sample_manifest import MOHSampleManifest


# Use a simple namespace for dot notation
MOHSampleTypes = SimpleNamespace(**SAMPLE_TYPES)
MOHHeaders = SimpleNamespace(**HEADERS)
MOHContainerTypes = SimpleNamespace(**CONTAINER_TYPES)

FMSHeaders = SimpleNamespace(**FMS_HEADERS)
FMSContainerKind = SimpleNamespace(**CONTAINER_KIND)


class MOHSampleManifestExtractor:
    # Implements the sample extraction logic
    def __init__(self, manifest:MOHSampleManifest, conversion_log: ConversionLog):
        self.manifest = manifest
        self.log = conversion_log
        self.current_row_number = -1

    def _log_error(self, error_message):
        self.log.add_error(self.current_row_number, error_message)

    def _log_warning(self, warning_message):
        self.log.add_warning(self.current_row_number, warning_message)

    def extract_samples(self):
        samples = []
        row_range = self.manifest.getDataRowRange()
        for i_row in row_range:
            self.current_row_number = i_row
            row = self.manifest.getRow(i_row)
            sample = self._extract_sample_from_row(row)
            if sample is not None:
                samples.append(sample)

        return samples

    def _extract_sample_from_row(self, row):
        
        row_type = self._extract_sample_type(row)
        if row_type is None:
            return None

        sample = FreezemanSample()

        sample.alias = row[MOHHeaders.SAMPLE_NAME]
        sample.name = row[MOHHeaders.SAMPLE_NAME]
        sample.kind = row_type
        sample.volume = self._extract_value(row, MOHHeaders.VOLUME)

        return sample

    def _extract_value(self, row, header_name):
        value = row[header_name]
        if pd.isna(value):
            value = None
        return value

    def _extract_sample_type(self, row):
        moh_type = row[MOHHeaders.SAMPLE_TYPE]

        if pd.isna(moh_type):
            # sample type is missing
            self._log_error('Sample type is not specified')
            return None

        if moh_type == MOHSampleTypes.TISSUE:
            moh_tissue_type = row[MOHHeaders.TISSUE_TYPE]
            if pd.isna(moh_tissue_type):
                # Tissue type is not specified
                self._log_error('Tissue type is not specified for tissue sample')
                return None

            fm_sample_type = TISSUE_TYPE_MAP[moh_tissue_type]
            if fm_sample_type is None:
                self._log_error(f'Unknown tissue type for tissue sample: {moh_tissue_type}')
            
            return fm_sample_type
            

            # map moh tissue type to freezeman sample type
        elif moh_type == MOHSampleTypes.NUCLEIC_ACID:
            
            moh_nucleic_type = row[MOHHeaders.NUCLEIC_ACID_TYPE]
            if pd.isna(moh_nucleic_type):
                self._log_error('Nucleic acid type not specified')
                return None

            fm_nucleic_type = NUCLEIC_ACID_TYPE_MAP[moh_nucleic_type]

            if fm_nucleic_type is None:
                self._log_error(f'Nucleic acid type not recognized: {moh_nucleic_type}')
                return None

            return fm_nucleic_type

        return None

    def _extract_container(self, row, sampleDict):
        
        container_name = self._extract_value(row, MOHHeaders.CONTAINER_NAME)
        if container_name == None:
            self._log_warning("Container name is not specified")
        
        container_barcode = self._extract_value(row, MOHHeaders.CONTAINER_BARCODE)
        if container_barcode == None:
            self._log_warning("Container barcode is not specified")

        container_type = self._extract_value(row, MOHHeaders.CONTAINER_TYPE)
        if container_type == None:
            self._log_warning("Container type is not specified")
        elif not container_type in CONTAINER_TYPES:
            self._log_error(f'Container type is not supported: {container_type}')

        well = self._extract_value(row, MOHHeaders.WELL)

        container_coord = None
        sample_coord = None
        container_kind = None

        if container_type == MOHContainerTypes.TUBE:
            # The well column contains the coord of the tube in its tube stand
            container_coord = well
            container_kind = FMSContainerKind.TUBE
        elif container_type == MOHContainerTypes.WELL_PLATE_96:
            sample_coord = well
            container_kind = FMSContainerKind.WELL_PLATE_96
        elif container_type == MOHContainerTypes.WELL_PLATE_384:
            sample_coord = well
            container_kind = FMSContainerKind.WELL_PLATE_384


        # populate the sampleDict values for containers
        # sampleDict[FMSHeaders.CONTAINER_NAME]
                
        # Freezeman:
        # container kind
        # container name
        # container barcode
        # container coord
        #
        # location barcode
        #  

        return None
           


            

