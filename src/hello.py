from pandas import pandas as pd
from pathlib import PurePath
import click
import re
from enum import Enum

excelFileURL = "file:///home/ckostiw/dev/freezerman/template_convertor/data/Instruments.xlsx"
mohFileUrl = "file:///home/ckostiw/dev/freezerman/template_convertor/data/MOH.xlsx"
# csvFilePath = "/home/ckostiw/dev/freezerman/template_convertor/data/output.csv"

# Sample Name, Pool Name or Existing LIMS ID *

headerNames = [
    'mandatory fields',
    'sample type',
    'sample name, pool name or existing lims id',
    'sample set',
    'individual id',
    'cohort id',
    'container type',
    'container name',
    'well',
    'container barcode',
    'tube carrier type',
    'tube carrier name',
    'tube carrier barcode',
    'species',
    'genome size (mb)',
    'sex',
    'reference genome',
    'tissue type',
    'nucleic acid type',
    'nucleic acid size (kb)',
    'buffer',
    'volume (ul)',
    'concentration',
    'concentration units',
    'library size (bases)',
    'number in pool',
    'library type',
    'library index series',
    'library index name',
    'adapter type',
    'i7 index',
    'i5 index',
    'comments'
]


def isHeaderRow(rowTuple):
    MAX_MISMATCHED_HEADER_CELLS = 3
    mismatchedHeaders = []
    
    numMismatches = 0
    for col in rowTuple:
       
        # If a row cell contains anything other than a string then it is not a header row
        if not isinstance(col, str):
            return False

        # replace newline or tab characters with spaces, and strip * chars
        cleaned = col.replace('\n', ' ').strip(' \t\r\*')
        # replace 2 or more concurrent spaces with a single space
        cleaned = re.sub(r'\s{2,}', ' ', cleaned)
        # convert to lower case
        cleaned = cleaned.casefold()

        if not cleaned in headerNames:
            mismatchedHeaders.append(cleaned)
            numMismatches += 1
            if numMismatches > MAX_MISMATCHED_HEADER_CELLS:
                return False
    print('Mismatched headers: ', mismatchedHeaders)
    return True

def findHeaderRowIndex(dataFrame):
    MAX_ROWS_TO_CHECK = 10
    rowNumber = 0
    for row in dataFrame.itertuples(index = False, name = None):
        if isHeaderRow(row):
            return rowNumber
        rowNumber += 1
        if rowNumber > MAX_ROWS_TO_CHECK:
            break
    return -1   


def parseSheet(inputFilePath):
    dataFrame = pd.read_excel(inputFilePath)
    for row in dataFrame.itertuples(index= False, name = None):
        if isHeaderRow(row):
            print('Found header') # what is the row index?
            print(row)
            break

def convertToCSV(inputFilePath, outputFilePath):
    dataFrame = pd.read_excel(inputFilePath)
    with open(outputFilePath, 'w') as f:
        dataFrame.to_csv(outputFilePath)

@click.group()
def cli():
    pass

@click.command()
@click.argument('excelfilepath', type=click.Path(exists=True, dir_okay=False, readable=True, resolve_path=True))
def toCSV(excelfilepath):
    # Output csv file to same directory as parent, with same name, but with .csv suffix
    excelPath = PurePath(excelfilepath)
    excelStem = excelPath.stem
    csvPath = excelPath.with_name(excelStem + '.csv')
    convertToCSV(excelfilepath, csvPath)

cli.add_command(toCSV)

# def main():
#     cli()

# def main():
#     parseSheet(mohFileUrl)

# if __name__ == "__main__":
#     main()