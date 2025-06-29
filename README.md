# THOR Drive Scanner 

A batch script utility for running THOR scans on single or multiple drives with automated reporting.

![image](https://github.com/user-attachments/assets/27333594-27f8-4c74-9cda-a9cebc11695e)

## ✨ New in Version 2.0
- **Multi-drive scanning**: Select multiple drives (e.g., `1,3,5`)
- **Signature updates**: Auto-updates THOR signatures before scanning
- **Per-drive case names**: Unique identifiers for each scanned drive
- **Performance mode**: Optional `--threads 0` for max CPU utilization
- **Improved input handling**: Supports spaced or compact formats (`1,2` or `1, 2`)
- **Create and automatically maintain a config file that points to the Thor location and is validated on each execution

## Features

- Lists mounted drives with labels/sizes  
- Validates THOR executable path (with fallback prompt)  
- **New**: Sequential multi-drive scanning  
- Creates organized output directory  
- Generates standardized filenames with:
  - Date stamp (YYYYMMDD)  
  - Custom case name  
  - Drive identifier  
- Produces three output formats:
  - CSV (file hashes)  
  - HTML report  
  - Text log  
- Opens results folder upon completion  

## Requirements

- Windows 10/11 with mounted drives  
- [THOR Lite](https://www.nextron-systems.com/thor-lite/) (tested with v10.7+)  
- Administrative privileges  

## Usage

1. Run as Administrator  
2. Select drives (single number or comma-separated list)  
3. Specify output directory  
4. **New**: Enter unique case name for each drive  
5. Choose performance mode (optional)  
6. Scans run sequentially  
7. Results folder opens automatically  

## Output Files
YYYYMMDD-CaseName-drive(X)_files_md5s.csv
YYYYMMDD-CaseName-drive(X)_thor_scan.html
YYYYMMDD-CaseName-drive(X)_thor_log.txt

Where:  
- `YYYYMMDD` = Scan date  
- `CaseName` = User-provided identifier  
- `X` = Drive letter  

## Command Parameters

THOR executes with these optimized settings:  
  -a Filescan  
  --intense --norescontrol --nosoft --cross-platform  
  --rebase-dir [output path]  
  --alldrives  
  -p [selected drive]  
  [--threads 0 if performance mode enabled]  

## Version

Current version: 0.2

## 👤 Author

**Jacob Wilson**  
📧 dfirvault@gmail.com
[https://www.linkedin.com/in/jacob--wilson/](https://www.linkedin.com/in/jacob--wilson/)

**More information:**
[https://dfirvault.com](https://dfirvault.com)

** Key improvements in latest version **
1. Added multi threaded support (Thank you Florian for the suggestion)
2. Simplified usage instructions
3. Added multi-drive selection
4. Added automated local config file managment
