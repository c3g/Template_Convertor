from pathlib import PurePath
from moh.sample_manifest_conversion import MOHSampleManifestConversion


def main():
    fms_template_file_path = PurePath("data/Sample_submission_v3_8_0.xlsx")
    moh_file_url = (
        "file:///home/ckostiw/dev/freezerman/template_convertor/data/MOH-TEST.xlsx"
    )
    output_file_path = PurePath("data/output.xlsx")

    log_file_path = PurePath("data/output.log")

    conversion = MOHSampleManifestConversion(
        moh_file_url, fms_template_file_path, output_file_path, log_file_path
    )
    conversion.do_conversion()

    print("DONE")


if __name__ == "__main__":
    main()
