# Dropbox Data Science

This package provides functionality for reading and writing tables from excel, csv or text files into [pandas dataframes](https://pandas.pydata.org/)

## File

Dropbox files are classified into 3 categories:
1. Csv
2. Excel
3. Text

Excel and Csv files are read using `ExcelSheetConfig` and `CsvConfig` that
define the columns and rows or sheet name in case of excel to be read
from file.
```
ExcelSheetconfig (
    sheet_name: str,
    header: int,
    cols: List[int],
    col_names: Dict[str],
    index_col_name: str
)

CsvConfig (
    header: int,
    cols: List[int]
    col_names: Dict[str],
```

## Folder

`DropboxFolder` hold list of files objects described above as state. An
`update()` call updates the state of the folder

# Monitor

A simple monitor the emits an event when the contents of a folder
are modified
