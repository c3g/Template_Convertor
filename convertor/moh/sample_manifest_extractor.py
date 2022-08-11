from datetime import date
from types import SimpleNamespace
import re
from pandas import pandas as pd
from ..core import ConversionLog
from ..freezeman import CONTAINER_KIND, HEADERS as FMS_HEADERS
from .moh_config import (
    HEADERS,
    SAMPLE_TYPES,
    CONTAINER_TYPES,
    TISSUE_TYPE_MAP,
    NUCLEIC_ACID_TYPE_MAP,
    TAXON_TYPE_MAP,
    CONCENTRATION_UNITS,
)
from .sample_manifest import MOHSampleManifest

        # "SAMPLE_TYPE"                         DONE
        # "SAMPLE_NAME"                         DONE
        # "SAMPLE_SET"                          N/A
        # "INDIVIDUAL_ID"                       DONE
        # "COHORT_ID"                           DONE
        # "CONTAINER_TYPE"                      DONE
        # "CONTAINER_NAME"                      DONE
        # "WELL"                                DONE
        # "CONTAINER_BARCODE"                   DONE
        # "TUBE_CARRIER_TYPE"                   N/A
        # "TYPE_CARRIER_NAME"                   N/A
        # "TUBE_CARRIER_BARCODE"                N/A
        # "SPECIES"                             DONE
        # "GENOME_SIZE"                         N/A
        # "SEX"                                 DONE
        # "REFERENCE_GENOME"                    N/A
        # "TISSUE_TYPE"                         DONE
        # "NUCLEIC_ACID_TYPE"                   DONE
        # "NUCLEIC_ACID_SIZE"                   N/A (?)
        # "BUFFER"                              N/A
        # "VOLUME"                              DONE
        # "CONCENTRATION"                       DONE
        # "CONCENTRATION_UNITS"                 DONE
        # "LIBRARY_SIZE"
        # "NUMBER_IN_POOL"
        # "LIBRARY_TYPE"                        DONE
        # "LIBRARY_INDEX_SIZE"
        # "LIBRARY_INDEX_NAME"
        # "ADAPTER_TYPE"
        # "I7_INDEX"
        # "I5_INDEX"
        # "COMMENTS"                            DONE


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
            # row = self.manifest.data_frame.loc[i_row]
            if not pd.isna(row[MOHHeaders.SAMPLE_NAME]):
                sample = self._extract_sample_from_row(row)
                if sample is not None:
                    samples.append(sample)

        self.log.add_general_message(f"{len(samples)} samples converted")

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

        self._extract_volume_and_concentration(row, sample_ns)

        sample_ns.COMMENT = self._extract_value(row, MOHHeaders.COMMENTS, force_string=True)

        # Populating the reception date with today's date may lead to errors.
        # It is better to leave the date empty so that the user knows they need to provide the proper date.
        # sample_ns.RECEPTION_DATE = date.today().isoformat()

        return sample_ns

    def _extract_value(self, row, header_name, force_string = False):
        """
        Extract a value from a cell. If the value is NaN return None.
        If force_string is True then the value will be converted to a string,
        unless it is None, in which case None is returned (and not 'None')
        """
        value = row[header_name]
        if pd.isna(value):
            value = None

        if force_string:
            if value is not None:
                value = str(value)
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

            if moh_tissue_type in TISSUE_TYPE_MAP:
                fm_sample_type = TISSUE_TYPE_MAP[moh_tissue_type]
            else:
                fm_sample_type = None
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

        else:
            self._log_error(f"Unsupported sample type: {moh_type}")
        return None

    def _extract_container(self, row, sample_ns):

        container_type = self._extract_value(row, MOHHeaders.CONTAINER_TYPE)
        container_name = self._extract_value(row, MOHHeaders.CONTAINER_NAME)
        container_barcode = self._extract_value(row, MOHHeaders.CONTAINER_BARCODE)
        well = self._normalize_well(self._extract_value(row, MOHHeaders.WELL))


        # Replace spaces in container name with underscore '_'
        if container_name is not None:
            container_name = container_name.strip().replace(' ', '_')

        # Emit an error if the container type is None but other container fields contain data.
        # If there is no container data in any field then just return.
        if container_type is None:
            if container_name is not None or container_name is not None or well is not None:
                self._log_error("Container type must be specified")
            else:
                return

        if container_type is not None:
            # make sure the container type is one of the expected types
            if not container_type in CONTAINER_TYPES.values():
                self._log_error(f"Container type is not supported: {container_type}")
            else:
                if container_type == MOHContainerTypes.TUBE:
                    # The well column contains the coord of the tube in its tube stand
                    # sample_ns.CONTAINER_COORD = well
                    sample_ns.CONTAINER_KIND = FMSContainerKind.TUBE
                    sample_ns.CONTAINER_NAME = container_name
                    
                    # If no tube barcode is specified, default to the sample name as the barcode
                    if container_barcode is None:
                        sample_ns.CONTAINER_BARCODE = self._extract_value(row, MOHHeaders.SAMPLE_NAME)
                    else:
                        sample_ns.CONTAINER_BARCODE = container_barcode

                    # Tube carrier
                    # If the tube is shipped in a tube carrier set the fms location barcode to the
                    # tube carrier barcode, and the fms container coord to the well.
                    tube_carrier_barcode = self._extract_value(row, MOHHeaders.TUBE_CARRIER_BARCODE)
                    if tube_carrier_barcode is not None:
                        sample_ns.LOCATION_BARCODE = tube_carrier_barcode
                        sample_ns.CONTAINER_COORD = well
                    
                elif container_type == MOHContainerTypes.WELL_PLATE_96 or container_type == MOHContainerTypes.WELL_PLATE_384:
                    if container_type == MOHContainerTypes.WELL_PLATE_96:
                        sample_ns.CONTAINER_KIND = FMSContainerKind.WELL_PLATE_96
                    else:
                        sample_ns.CONTAINER_KIND = FMSContainerKind.WELL_PLATE_384

                    sample_ns.SAMPLE_COORD = well
                    sample_ns.CONTAINER_BARCODE = container_barcode
                    sample_ns.CONTAINER_NAME = container_name
                else:
                    self._log_error(f"Container type is unexpected: {container_type}")


    def _extract_individual(self, row, sample_ns):
        # Individual ID
        # Cohort ID
        # Species
        # Sex
        sample_ns.INDIVIDUAL_ID = self._extract_value(row, MOHHeaders.INDIVIDUAL_ID, force_string=True)
        
        sample_ns.COHORT = self._extract_value(row, MOHHeaders.COHORT_ID, force_string=True)

        sample_ns.SEX = self._extract_value(row, MOHHeaders.SEX)

        # For species, freezeman only supports a limited set of taxon id's
        # Should we copy the taxon anyway and let the user decide what they want to do?
        taxon = self._extract_value(row, MOHHeaders.SPECIES)
        if taxon is not None:
            if taxon in TAXON_TYPE_MAP:
                sample_ns.TAXON = TAXON_TYPE_MAP[taxon]
            else:
                self._log_warning(f"Unsupported taxon type: {taxon}")

        # If cohort, sex, or taxon are specified then freezeman also requires
        # an indvidual ID
        if sample_ns.COHORT is not None or sample_ns.SEX is not None or sample_ns.TAXON is not None:
            if sample_ns.INDIVIDUAL_ID is None:
                # For MOH, the individual id is part of the sample name.
                # If the sample name conforms to the MoH naming convention then extract the
                # individual id and cohort.
                sample_name = self._extract_value(row, MOHHeaders.SAMPLE_NAME)
                if self._is_moh_sample_name(sample_name):
                    self._extract_moh_individual_and_cohort(self._extract_value(row, MOHHeaders.SAMPLE_NAME), sample_ns)
                else:
                    self._log_error("Individual ID must be specified if cohort, sex or taxon is specified.")
                
    def _extract_volume_and_concentration(self, row, sample_ns):
        # "VOLUME"
        # "CONCENTRATION"
        # "CONCENTRATION_UNITS"
        sample_ns.VOLUME = self._extract_value(row, MOHHeaders.VOLUME)

        concentration = self._extract_value(row, MOHHeaders.CONCENTRATION)
        concentration_units = self._extract_value(row, MOHHeaders.CONCENTRATION_UNITS)

        if concentration_units is not None:
            # freezeman only allows ng/uL. If the concentration is in any other units
            # then ignore the concentration.
            if concentration_units == CONCENTRATION_UNITS["NG_UL"]:
                sample_ns.CONCENTRATION = concentration
            else:
                sample_ns.concentration = None
                self._log_error(f"Concentration must be specified in ng/uL. {concentration_units} is not supported.")

        
    def _extract_library(self, row, sample_ns):
        # libraries are not supported by this tool
        pass

    def _is_moh_sample_name(self, sample_name):
        if sample_name is not None:
            return sample_name.startswith('MoH')
        else:
            return False

    def _extract_moh_individual_and_cohort(self, sample_name, sample_ns):
        # Regular expression for matching MoH sample name format.
        # MOH sample names have six segments, separated by '-' dashes.
        # Example: MoHQ-MU-8-16-FF1-1DT
        #
        # Segment 1:  must begin with "MoH" followed by a letter indicating the region (Q for Quebec)
        # Segment 2: Institution code (MU, JG, CM, GC, MR)
        # Segment 3: Cohort id
        # Segment 4: Patient id in cohort
        # Segment 5: Sample id
        # Segment 6: Sample info (extraction, DNA/RNA, normal/tumour)
        # 
        # We use the first four segments for the freezeman individual id (eg. MoHQ-MU-8-16)
        # and we extract the cohort id.

        moh_sample_name_reg_exp = r'(MoH.-\w+-(\w+)-\w+)-\w+-\w+'

        match = re.match(moh_sample_name_reg_exp, sample_name)
        if match is None:
            self._log_warning(f'MoH sample name does not match expected format "{sample_name}". Individual ID and cohort cannot be extracted.')
        else:
            # match[1] is the individual id
            if sample_ns.INDIVIDUAL_ID is None:
                sample_ns.INDIVIDUAL_ID = match[1]
            # match[2] is the cohort id segment
            if sample_ns.COHORT is None:
                sample_ns.COHORT = match[2]

                
    def _normalize_well(self, well):
        """
        Freezeman expects well coordinates to contain a letter followed by two
        digits, with a zero to pad the digit if necessary, eg "A01". 
        
        MOH doesn't use the padding, so we have to add it.

        eg. A1 is converted to A01
        """
        if well:
            if len(well) == 2:  
                match = re.match(r'[A-P][1-9]', well)
                if match:
                    well = f'{well[0]}0{well[1]}'
        return well

