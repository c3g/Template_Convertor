

from pathlib import PurePath

import pandas

from MOH.MOHSampleManifest import MOHSampleManifest
from MOH.MOHSampleManifestExtractor import MOHSampleManifestExtractor
from core.ConversionLog import ConversionLog
from core.ManifestError import ManifestError


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
        samples = extractor.extractSamples()

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

        print("Data rows in manifest: ", manifest.getDataRowRange())

        return manifest



        
