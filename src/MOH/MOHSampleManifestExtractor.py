
import json
from re import M
from types import SimpleNamespace
from pandas import pandas as pd
from Freezeman.sample import FreezemanSample
from MOH.MOHConfig import HEADERS, SAMPLE_TYPES
from MOH.MOHSampleManifest import MOHSampleManifest
from core.ConversionLog import ConversionLog
from MOH.MOHConfig import TISSUE_TYPE_MAP, NUCLEIC_ACID_TYPE_MAP

# Use a simple namespace for dot notation
MOHSampleTypes = SimpleNamespace(**SAMPLE_TYPES)
MOHHeaders = SimpleNamespace(**HEADERS)

class MOHSampleManifestExtractor:
    # Implements the sample extraction logic
    def __init__(self, manifest:MOHSampleManifest, conversionLog: ConversionLog):
        self.manifest = manifest
        self.log = conversionLog


    def extractSamples(self):
        samples = []
        rowRange = self.manifest.getDataRowRange()
        for iRow in rowRange:
            row = self.manifest.getRow(iRow)
            sample = self._extractSampleFromRow(row, iRow)
            if sample != None:
                samples.append(sample)

        return samples


    def _extractSampleFromRow(self, row, rowNumber):
        type = self._extractSampleType(row, rowNumber)
        if type == None:
            return None

        sample = FreezemanSample()

        sample.alias = row[MOHHeaders.SAMPLE_NAME]
        sample.name = row[MOHHeaders.SAMPLE_NAME]
        sample.kind = type
        sample.volume = self._extractValue(row, rowNumber, MOHHeaders.VOLUME)

        return sample

    def _extractValue(self, row, rowNumber, headerName):
        value = row[headerName]
        if pd.isna(value):
            value = None
        return value

    def _extractSampleType(self, row, rowNumber):
        mohType = row[MOHHeaders.SAMPLE_TYPE]

        if pd.isna(mohType):
            # sample type is missing
            self.log.sampleSkipped("Sample type is not specified", rowNumber)
            return None

        if mohType == MOHSampleTypes.TISSUE:
            mohTissueType = row[MOHHeaders.TISSUE_TYPE]
            if pd.isna(mohTissueType):
                # Tissue type is not specified
                self.log.sampleSkipped("Tissue type not specified", rowNumber)
                return None

            fmSampleType = TISSUE_TYPE_MAP[mohTissueType]
            if fmSampleType == None:
                self.log.sampleSkipped(f"Sample has unknown tissue type: {mohTissueType}", rowNumber)
            
            return fmSampleType
            

            # map moh tissue type to freezeman sample type
        elif mohType == MOHSampleTypes.NUCLEIC_ACID:
            
            mohNucleicType = row[MOHHeaders.NUCLEIC_ACID_TYPE]
            if pd.isna(mohNucleicType):
                self.log.sampleSkipped("Nucleic acid type not specified", rowNumber)
                return None

            fmNucleicType = NUCLEIC_ACID_TYPE_MAP[mohNucleicType]

            if fmNucleicType == None:
                self.log.sampleSkipped(f"Nucleic acid type not recognized: {mohNucleicType}")
                return None

            return fmNucleicType

        self.log.sampleSkipped(f"Sample type is not supported: {mohType}")

        return None
           
    def extractVolume(self, row, rowNumber):
        volume = row[MOHHeaders.VOLUME]
        if pd.isna(volume):
            return ""
        return volume

            

