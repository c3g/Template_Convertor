# from pathlib import PurePath
import pandas

from core.conversion_log import ConversionLog
from core.manifest_error import ManifestError
from freezeman.freezeman_template import FHSSampleSubmissionTemplate
from .sample_manifest import MOHSampleManifest
from .sample_manifest_extractor import MOHSampleManifestExtractor


class MOHSampleManifestConversion:
    # Implements the conversion of one MOH sample manifest using files
    def __init__(
        self, manifest_path, fms_template_path, fms_output_file_path, log_file_path
    ):

        # create an error logger
        self.log = ConversionLog()

        # create the manifest sheet
        self.manifest_path = manifest_path

        # path to fms sample submission template file
        self.fms_template_path = fms_template_path

        # path where sample file will be written
        self.fms_output_file_path = fms_output_file_path

        # path where log will be written
        self.log_file_path = log_file_path

    def do_conversion(self):
        # load manifest
        try:
            manifest = self.load_manifest(self.manifest_path)
        except BaseException as err:
            raise ManifestError("Unable to initialize manifest") from err

        extractor = MOHSampleManifestExtractor(manifest, self.log)
        samples = extractor.extract_samples()

        # load fms sample submission template
        fms_template = FHSSampleSubmissionTemplate(self.fms_template_path)
        fms_template.append_samples(samples)
        fms_template.write_to_file(self.fms_output_file_path)

        # For now, just print errors and warnings to console
        self.log.output_messages()
        self.log.write_log(self.log_file_path)

    def load_manifest(self, manifest_filepath):
        try:
            manifest_frame = pandas.read_excel(manifest_filepath, header=None)

            # for row in manifest_frame.iterrows():
            #     print(row)

        except Exception as err:
            raise ManifestError("Unable to parse manifest") from err

        try:
            manifest = MOHSampleManifest(manifest_frame)
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
        return FHSSampleSubmissionTemplate(data_frame)

    def save_sample_submission_template(self, data_frame, template_output_path):
        try:
            data_frame.to_excel(template_output_path, header=False, index=False)
        except Exception as err:
            raise ManifestError("Unable to write sample submission file") from err
