
import sys
from moh.sample_manifest_conversion import MOHSampleManifestConversion

print(sys.path)

def main():
    excel_file_url = "file:///home/ckostiw/dev/freezerman/template_convertor/data/Instruments.xlsx"
    moh_file_url = "file:///home/ckostiw/dev/freezerman/template_convertor/data/MOH-TEST.xlsx"

    conversion = MOHSampleManifestConversion(moh_file_url, excel_file_url)
    conversion.doConversion()

    print('DONE')

if __name__ == "__main__":
    main()
