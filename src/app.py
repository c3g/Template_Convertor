from pathlib import PurePath
from moh.sample_manifest_conversion import MOHSampleManifestConversion


def main():
    fms_template_file_path = PurePath("data/Sample_submission_v3_8_0.xlsx")
    moh_file_url = (
        "file:///home/ckostiw/dev/freezerman/template_convertor/data/MOH-TEST.xlsx"
    )

    conversion = MOHSampleManifestConversion(moh_file_url, fms_template_file_path)
    conversion.doConversion()

    print("DONE")


if __name__ == "__main__":
    main()
