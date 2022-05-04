
from MOH.MOHSampleManifestConversion import MOHSampleManifestConversion


def main():
    excelFileURL = "file:///home/ckostiw/dev/freezerman/template_convertor/data/Instruments.xlsx"
    mohFileUrl = "file:///home/ckostiw/dev/freezerman/template_convertor/data/MOH-TEST.xlsx"

    conversion = MOHSampleManifestConversion(mohFileUrl, excelFileURL)
    conversion.doConversion()

    print('DONE')

if __name__ == "__main__":
    main()