from pathlib import PurePath
import pandas

from core.conversion_log import ConversionLog
from core.manifest_error import ManifestError
from freezeman.freezeman_template import FMSSampleSubmissionTemplate
from .sample_manifest import MOHSampleManifest
from .sample_manifest_extractor import MOHSampleManifestExtractor


class MOHSampleManifestConversion:
    # Implements the conversion of one MOH sample manifest using files
    def __init__(self, manifest_path, fms_template_path):

        # create an error logger
        self.log = ConversionLog()

        # create the manifest sheet
        self.manifest_path = manifest_path

        # create the freezeman sheet
        self.fms_template_path = fms_template_path

    def doConversion(self):
        # load manifest
        try:
            manifest = self.loadManifest(self.manifest_path)
        except BaseException as err:
            raise ManifestError("Unable to initialize manifest") from err

        extractor = MOHSampleManifestExtractor(manifest, self.log)
        samples = extractor.extract_samples()

        # load fms sample submission template
        fms_template = self.load_sample_submission_template(self.fms_template_path)
        fms_template.append_samples(samples)
        self.save_sample_submission_template(
            fms_template.sheet.data_frame, PurePath("data/output.xlsx")
        )

        # For now, just print errors and warnings to console
        self.log.output_messages()

        print()

        # TODO remove print code
        # for sample in samples:
        #     print(sample)

    def loadManifest(self, manifestFilePath):
        try:
            manifestFrame = pandas.read_excel(manifestFilePath)
        except Exception as err:
            raise ManifestError("Unable to parse manifest") from err

        try:
            manifest = MOHSampleManifest(manifestFrame)
        except Exception as err:
            raise ManifestError(
                "There was a problem with the manifest contents"
            ) from err

        print("Data rows in manifest: ", manifest.get_data_row_range())

        return manifest

    def load_sample_submission_template(self, template_path):
        try:
            data_frame = pandas.read_excel(template_path)
        except Exception as err:
            raise ManifestError(
                "Unable to parse fms sample submission template"
            ) from err
        return FMSSampleSubmissionTemplate(data_frame)

    def save_sample_submission_template(self, data_frame, template_output_path):
        try:
            data_frame.to_excel(template_output_path, header=False, index=False)
        except Exception as err:
            raise ManifestError("Unable to write sample submission file") from err
