from datetime import date
from types import SimpleNamespace
import re
from pandas import pandas as pd
from core.conversion_log import ConversionLog
from freezeman.freezeman_config import CONTAINER_KIND, HEADERS as FMS_HEADERS
from .moh_config import (
    HEADERS,
    SAMPLE_TYPES,
    CONTAINER_TYPES,
    TISSUE_TYPE_MAP,
    NUCLEIC_ACID_TYPE_MAP,
    TAXON_TYPE_MAP,
)
from .sample_manifest import MOHSampleManifest


# Use a simple namespace for dot notation
MOHSampleTypes = SimpleNamespace(**SAMPLE_TYPES)
MOHHeaders = SimpleNamespace(**HEADERS)
MOHContainerTypes = SimpleNamespace(**CONTAINER_TYPES)
MOHTaxonTypes = SimpleNamespace(**TAXON_TYPE_MAP)

FMSHeaders = SimpleNamespace(**FMS_HEADERS)
FMSContainerKind = SimpleNamespace(**CONTAINER_KIND)


def normalize_name(name):
    """
    Replace illegal characters by underscores.
    Legal characters are a-z, A-Z, 0-9, _ (underscore), - (dash), . (period)
    """

    reg_ex = "[^a-z|A-Z|0-9|_.-]"
    return re.sub(reg_ex, "_", name)


class MOHSampleManifestExtractor:
    # Implements the sample extraction logic
    def __init__(self, manifest: MOHSampleManifest, conversion_log: ConversionLog):
        self.manifest = manifest
        self.log = conversion_log
        self.current_row_number = -1

    def _log_error(self, error_message):
        self.log.add_error(self.current_row_number, error_message)

    def _log_warning(self, warning_message):
        self.log.add_warning(self.current_row_number, warning_message)

    def extract_samples(self):
        samples = []
        row_range = self.manifest.get_data_row_range()
        for i_row in row_range:
            self.current_row_number = i_row
            row = self.manifest.get_row(i_row)
            sample = self._extract_sample_from_row(row)
            if sample is not None:
                samples.append(sample)

        return samples

    def _create_fms_sample(self):
        """A sample is modeled as a dictionary with keys matching the keys in the fms header
        definitions, wrapped in a SimpleNamespace to allow dot addressing of sample fields
        """
        sample = {}

        for key in FMS_HEADERS.keys():
            sample[key] = None

        return SimpleNamespace(**sample)

    def _extract_sample_from_row(self, row):

        row_type = self._extract_sample_type(row)
        if row_type is None:
            return None

        sample_ns = self._create_fms_sample()

        sample_ns.SAMPLE_KIND = row_type

        sample_ns.SAMPLE_NAME = normalize_name(row[MOHHeaders.SAMPLE_NAME])
        sample_ns.ALIAS = row[MOHHeaders.SAMPLE_NAME]

        sample_ns.VOLUME = self._extract_value(row, MOHHeaders.VOLUME)

        self._extract_container(row, sample_ns)

        self._extract_individual(row, sample_ns)

        sample_ns.COMMENT = self._extract_value(row, MOHHeaders.COMMENTS)

        sample_ns.RECEPTION_DATE = date.today().isoformat()

        return sample_ns

    def _extract_value(self, row, header_name):
        value = row[header_name]
        if pd.isna(value):
            value = None
        return value

    def _extract_sample_type(self, row):
        moh_type = row[MOHHeaders.SAMPLE_TYPE]

        if pd.isna(moh_type):
            # sample type is missing
            self._log_error("Sample type is not specified")
            return None

        if moh_type == MOHSampleTypes.TISSUE:
            moh_tissue_type = row[MOHHeaders.TISSUE_TYPE]
            if pd.isna(moh_tissue_type):
                # Tissue type is not specified
                self._log_error("Tissue type is not specified for tissue sample")
                return None

            fm_sample_type = TISSUE_TYPE_MAP[moh_tissue_type]
            if fm_sample_type is None:
                self._log_error(
                    f"Unknown tissue type for tissue sample: {moh_tissue_type}"
                )

            return fm_sample_type

            # map moh tissue type to freezeman sample type
        elif moh_type == MOHSampleTypes.NUCLEIC_ACID:

            moh_nucleic_type = row[MOHHeaders.NUCLEIC_ACID_TYPE]
            if pd.isna(moh_nucleic_type):
                self._log_error("Nucleic acid type not specified")
                return None

            fm_nucleic_type = NUCLEIC_ACID_TYPE_MAP[moh_nucleic_type]

            if fm_nucleic_type is None:
                self._log_error(f"Nucleic acid type not recognized: {moh_nucleic_type}")
                return None

            return fm_nucleic_type

        return None

    def _extract_container(self, row, sample_ns):

        container_type = self._extract_value(row, MOHHeaders.CONTAINER_TYPE)
        if container_type is None:
            self._log_warning("Container type is not specified")
        elif not container_type in CONTAINER_TYPES.values():
            self._log_error(f"Container type is not supported: {container_type}")

        if container_type == MOHContainerTypes.TUBE:
            # The well column contains the coord of the tube in its tube stand
            sample_ns.CONTAINER_COORD = self._extract_value(row, MOHHeaders.WELL)
            sample_ns.CONTAINER_KIND = FMSContainerKind.TUBE
        elif container_type == MOHContainerTypes.WELL_PLATE_96:
            sample_ns.SAMPLE_COORD = self._extract_value(row, MOHHeaders.WELL)
            sample_ns.CONTAINER_KIND = FMSContainerKind.WELL_PLATE_96
        elif container_type == MOHContainerTypes.WELL_PLATE_384:
            sample_ns.SAMPLE_COORD = self._extract_value(row, MOHHeaders.WELL)
            sample_ns.CONTAINER_KIND = FMSContainerKind.WELL_PLATE_384
        else:
            self._log_error(f"Container type is not supported: {container_type}")

        sample_ns.CONTAINER_NAME = self._extract_value(row, MOHHeaders.CONTAINER_NAME)
        sample_ns.CONTAINER_BARCODE = self._extract_value(
            row, MOHHeaders.CONTAINER_BARCODE
        )

        # TODO Which warning/error messages would be useful here, and which would just be noise?

    def _extract_individual(self, row, sample_ns):
        # Individual ID
        # Cohort ID
        # Species
        # Sex
        sample_ns.INDIVIDUAL_ID = self._extract_value(row, MOHHeaders.INDIVIDUAL_ID)
        if sample_ns.INDIVIDUAL_ID is None:
            # The individual ID must be specified if any of the other individual fields
            # are used.
            return

        sample_ns.COHORT = self._extract_value(row, MOHHeaders.COHORT_ID)

        sample_ns.SEX = self._extract_value(row, MOHHeaders.SEX)

        # For species, freezeman only supports a limited set of taxon id's
        # Should we copy the taxon anyway and let the user decide what they want to do?
        taxon = self._extract_value(row, MOHHeaders.SPECIES)
        if taxon is not None:
            sample_ns.TAXON = TAXON_TYPE_MAP[taxon]
            if sample_ns.TAXON is None:
                self._log_warning(f"Unsupported taxon type: {taxon}")
