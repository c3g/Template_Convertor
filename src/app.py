from pathlib import PurePath
from moh.sample_manifest_conversion import MOHSampleManifestConversion


def main():
    fms_template_file_path = PurePath("config/fms_sample_submission_template.xlsx")
    moh_file_path = PurePath("data/MGC_Sample_Submission_QA.xlsx")
    output_file_path = PurePath("data/output.xlsx")

    log_file_path = PurePath("data/output.log")

    conversion = MOHSampleManifestConversion(
        moh_file_path, fms_template_file_path, output_file_path, log_file_path
    )
    conversion.do_conversion()

    print("DONE")


if __name__ == "__main__":
    main()
