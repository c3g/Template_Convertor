# from pathlib import PurePath
import pandas
import warnings

from .core import ConversionLog, ManifestError
from .freezeman import FHSSampleSubmissionTemplate
from .moh import MOHSampleManifest, MOHSampleManifestExtractor

# Disable openpyxl warnings that show up every time the freezeman template is loaded
warnings.filterwarnings("ignore", module="openpyxl", category=UserWarning)
# warnings.filterwarnings("ignore", category=UserWarning, message="Conditional Formatting extension is not supported and will be removed")
# warnings.filterwarnings("ignore", category=UserWarning, message="Data Validation extension is not supported and will be removed")
# warnings.filterwarnings("ignore", category=UserWarning, message="Unknown extension is not supported and will be removed")
# 
class MOHSampleManifestConversion:
    # Implements the conversion of one MOH sample manifest using files
    def __init__(
        self, manifest_stream, fms_template_path, fms_output_stream
    ):

        # create an error logger
        self.log = ConversionLog()

        # create the manifest sheet
        self.manifest_stream = manifest_stream

        # path to fms sample submission template file
        self.fms_template_path = fms_template_path

        # A writable file stream, to receive the output.
        self.fms_output_file_stream = fms_output_stream

    def do_conversion(self):
        # load manifest
        try:
            manifest = self.load_manifest(self.manifest_stream)
        except ManifestError as err:
            raise err
        except BaseException as err:
            self.log.add_general_message('Sample manifest could not be loaded')
            self.log.add_general_message(err)
            raise ManifestError("Unable to initialize MOH manifest") from err

        extractor = MOHSampleManifestExtractor(manifest, self.log)
        samples = extractor.extract_samples()

        # load fms sample submission template
        fms_template = FHSSampleSubmissionTemplate(self.fms_template_path)
        fms_template.append_samples(samples)
        fms_template.write_to_file(self.fms_output_file_stream)


    def load_manifest(self, manifest_filepath):
        try:
            manifest_frame = pandas.read_excel(manifest_filepath, header=None)
        except Exception as err:
            raise ManifestError("Unable to parse manifest") from err

        try:
            manifest = MOHSampleManifest(manifest_frame)
        except ManifestError as err:
            raise err
        except Exception as err:
            raise ManifestError(
                "There was a problem with the manifest contents"
            ) from err

        # print("Data rows in manifest: ", manifest.get_data_row_range())

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
