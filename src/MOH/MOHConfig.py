import json
from types import SimpleNamespace


# Load the MOH_DATA json data file, which contains tables for mapping MOH
# values to freezeman values.
MOH_CONFIG_FILE_PATH = 'data/MOHConfig.json'


try:
    with open(MOH_CONFIG_FILE_PATH, 'r') as config_file:
        MOHConfig = json.load(config_file)
except(OSError) as err:
    print("Failed to load MOHConfig.json file", err)
    raise err

# Create some symbols so that sub-dictionaries can be imported easily
HEADERS = MOHConfig['headers']
TISSUE_TYPE_MAP = MOHConfig['tissueTypeMap']
NUCLEIC_ACID_TYPE_MAP = MOHConfig['nucleicAcidTypeMap']
SAMPLE_TYPES = MOHConfig['sampleTypes']