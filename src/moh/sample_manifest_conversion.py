import pandas

from core.conversion_log import ConversionLog
from core.manifest_error import ManifestError
from .sample_manifest import MOHSampleManifest
from .sample_manifest_extractor import MOHSampleManifestExtractor



class MOHSampleManifestConversion:
# Implements the conversion of one MOH sample manifest using files
    def __init__(self, manifestFilePath, freezemanTemplatePath):

        # create an error logger
        self.log = ConversionLog()

        # create the manifest sheet
        self.manifestFilePath = manifestFilePath

        # create the freezeman sheet
        self.freezemanTemplatePath = freezemanTemplatePath


    def doConversion(self):
         # load manifest
        try:
            manifest = self.loadManifest(self.manifestFilePath)
        except BaseException as err:
           raise ManifestError('Unable to initialize manifest') from err

        extractor = MOHSampleManifestExtractor(manifest, self.log)
        samples = extractor.extract_samples()

        # For now, just print errors and warnings to console
        self.log.output_messages()

        print()
        
        # TODO remove print code
        for sample in samples:
            print(sample)



    def loadManifest(self, manifestFilePath):
        try:
            manifestFrame = pandas.read_excel(manifestFilePath)
        except Exception as err:
            raise ManifestError('Unable to parse manifest') from err

        try:
            manifest = MOHSampleManifest(manifestFrame)
        except Exception as err:
            raise ManifestError('There was a problem with the manifest contents') from err

        print("Data rows in manifest: ", manifest.get_data_row_range())

        return manifest



        
