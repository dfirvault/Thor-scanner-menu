# THOR Drive Scanner

A batch script utility for running THOR (Threat Hunting and Incident Response) scans on mounted drives with automated report generation.

## Features

- Lists all mounted drives with their labels and sizes
- Validates THOR executable path (with fallback to user input)
- Creates organized output directory structure
- Generates standardized filenames with:
  - Date stamp (YYYYMMDD)
  - Case name
  - Drive identifier
- Produces three output formats:
  - CSV file with file hashes
  - HTML report
  - Text log
- Opens results folder upon completion

## Requirements

- Windows system with mounted drives
- [THOR Lite](https://www.nextron-systems.com/thor-lite/) installed (default path: `C:\Tools\Thor\thor64-lite.exe`)
- Administrative privileges recommended

## Usage

1. Run the batch file as Administrator
2. Select a drive from the displayed list by entering its number
3. Specify an output directory for reports
4. Enter a case name (used in report filenames)
5. The scan will begin automatically
6. Results folder will open when complete

## Output Files

The tool generates three files per scan with standardized naming:
YYYYMMDD-CaseName-drive(X)_files_md5s.csv
YYYYMMDD-CaseName-drive(X)_thor_scan.html
YYYYMMDD-CaseName-drive(X)_thor_log.txt


Where:
- `YYYYMMDD` = Current date
- `CaseName` = User-provided case identifier
- `X` = Drive letter being scanned

## Command Line Parameters

The script executes THOR with these recommended parameters:
-a Filescan
--intense --norescontrol --nosoft --cross-platform
--rebase-dir [output path]
--alldrives
-p [selected drive]


## Version

Current version: 0.1

## Author

Jacob Wilson  
DFIR Vault  
dfirvault@gmail.com

## Notes

- For UNC paths, the drive identifier will show as "UNC"
- The script will create the output directory if it doesn't exist
- THOR path is configurable during runtime if not found at default location
