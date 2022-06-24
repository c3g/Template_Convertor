import json
from pathlib import PurePath
import sys

from moh.moh_config import LIBRARY_TYPES
from .freezeman_config_data import FMConfig


# # Load the freezeman json data file, which contains symbols for the freezeman
# # template.
# FM_CONFIG_FILE_PATH = "config/FreezemanConfig.json"

# try:
#     executable_path = PurePath(sys.executable)
#     config_path = executable_path.parent / FM_CONFIG_FILE_PATH


#     with open(config_path, "r", encoding="utf-8") as config_file:
#         FMConfig = json.load(config_file)
# except (OSError) as err:
#     print("Failed to load Freezeman.json file", err)
#     raise err

# Create some symbols so that sub-dictionaries can be imported easily
HEADERS = FMConfig["headers"]
CONTAINER_KIND = FMConfig["containerKind"]
LIBRARY_TYPES = FMConfig["library_types"]
