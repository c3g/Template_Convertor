import json
import os
from pathlib import Path, PurePath
import sys
from .moh_config_data import MOHConfig

# # Load the MOH_DATA json data file, which contains tables for mapping MOH
# # values to freezeman values.
# MOH_CONFIG_FILE_PATH = "config/MOHConfig.json"


# try:
#     executable_path = PurePath(sys.executable)
#     config_path = executable_path.parent / MOH_CONFIG_FILE_PATH

#     print(f"MOHConfig path: {config_path}")

#     with open(config_path, "r", encoding="utf-8") as config_file:
#         MOHConfig = json.load(config_file)

# except (OSError) as err:
#     print("Failed to load MOHConfig.json file", err)
#     raise err

# Create some symbols so that sub-dictionaries can be imported easily
HEADERS = MOHConfig["headers"]
TISSUE_TYPE_MAP = MOHConfig["tissueTypeMap"]
NUCLEIC_ACID_TYPE_MAP = MOHConfig["nucleicAcidTypeMap"]
SAMPLE_TYPES = MOHConfig["sampleTypes"]
CONTAINER_TYPES = MOHConfig["containerTypes"]
TAXON_TYPE_MAP = MOHConfig["taxonTypeMap"]
CONCENTRATION_UNITS = MOHConfig["concentration_units"]
LIBRARY_TYPES = MOHConfig["library_types"]
