import json


# Load the freezeman json data file, which contains symbols for the freezeman
# template.
FM_CONFIG_FILE_PATH = 'data/FreezemanConfig.json'

try:
    with open(FM_CONFIG_FILE_PATH, 'r', encoding="utf-8") as config_file:
        FMConfig = json.load(config_file)
except(OSError) as err:
    print("Failed to load Freezeman.json file", err)
    raise err

# Create some symbols so that sub-dictionaries can be imported easily
HEADERS = FMConfig['headers']
CONTAINER_KIND = FMConfig['containerKind']
