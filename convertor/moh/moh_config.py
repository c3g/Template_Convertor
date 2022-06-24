from .moh_config_data import MOHConfig

# Create some symbols so that sub-dictionaries can be imported easily
HEADERS = MOHConfig["headers"]
TISSUE_TYPE_MAP = MOHConfig["tissueTypeMap"]
NUCLEIC_ACID_TYPE_MAP = MOHConfig["nucleicAcidTypeMap"]
SAMPLE_TYPES = MOHConfig["sampleTypes"]
CONTAINER_TYPES = MOHConfig["containerTypes"]
TAXON_TYPE_MAP = MOHConfig["taxonTypeMap"]
CONCENTRATION_UNITS = MOHConfig["concentration_units"]
LIBRARY_TYPES = MOHConfig["library_types"]
