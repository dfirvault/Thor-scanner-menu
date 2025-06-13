@echo off
setlocal enabledelayedexpansion
echo.
echo Developed by Jacob Wilson - Version 0.1
echo dfirvault@gmail.com
echo.
:: ==============================================
:: DRIVE SELECTION MENU
:: ==============================================
cls
echo.
echo ===============================
echo Mounted Drives on This System
echo ===============================

:: Initialize counter
set /a counter=1
:: ==============================================
:: INITIAL SETUP
:: ==============================================
:: INITIAL SETUP
:: ==============================================
set "THOR_PATH=C:\Tools\Thor\thor64-lite.exe"

:: ==============================================
:: CHECK FOR THOR EXECUTABLE
:: ==============================================
:CHECK_THOR
if exist "%THOR_PATH%" (
    echo THOR found at: "%THOR_PATH%"
) else (
    echo.
    echo WARNING: THOR not found at "%THOR_PATH%".
    set /p "THOR_PATH=Enter full path to Thor64-lite.exe (e.g., C:\Tools\Thor\Thor64-lite.exe): "
    if not exist "%THOR_PATH%" (
        echo Error: THOR executable not found at "%THOR_PATH%".
        goto CHECK_THOR
    )
)
:: Use WMIC to get drive info
:: Use WMIC to get drive info and filter out empty lines
for /f "skip=1 tokens=1,2,3*" %%A in ('wmic logicaldisk get DeviceID^,VolumeName^,Size') do (
    set "device=%%A"
    set "label=%%B"
    set "size=%%C"

    :: Skip lines with no device ID or size
    if not "!device!"=="" if not "!size!"=="" (
        :: Convert size in bytes to GB (rounded)
        echo !counter! [!device!]
        set "drive!counter!=!device!"
        set /a counter+=1
    )
)

:: ==============================================
:: USER INPUT
:: ==============================================
echo.
set /p "choice=Enter the number of the drive to scan: "
set "scanDrive=!drive%choice%!"
if not defined scanDrive (
    echo Invalid selection. Exiting.
    exit /b 1
)

:: Prompt for report path
echo.
set /p "reportPath=Enter full path (e.g., C:\Reports) to save the THOR report: "

:: Ensure directory exists
if not exist "!reportPath!\" (
    mkdir "!reportPath!"
    if !errorlevel! neq 0 (
        echo Error: Could not create "!reportPath!". Exiting.
        exit /b 1
    )
)

:: Prompt for case name
echo.
set /p "CaseName=Enter Case Name (e.g., MAL2024-001): "
if "!CaseName!"=="" (
    echo Error: Case Name cannot be empty.
    exit /b 1
)

:: ==============================================
:: FILENAME FORMATTING (YYYYMMDD-CaseName-Drive(X)_...)
:: ==============================================
:: Get date in YYYYMMDD format (locale-independent)
for /f "tokens=2 delims==" %%a in ('wmic os get LocalDateTime /value') do set "DateTime=%%a"
set "FormattedDate=!DateTime:~0,8!"

:: Extract drive letter (e.g., "D" from "D:\")
set "drive=!scanDrive:~0,1!"
if "!drive!"=="\" set "drive=UNC"  :: Handle UNC paths (\\server\share)

:: Generate filenames
set "csvFile=!FormattedDate!-!CaseName!-drive(!drive!)_files_md5s.csv"
set "htmlFile=!FormattedDate!-!CaseName!-drive(!drive!)_thor_scan.html"
set "logFile=!FormattedDate!-!CaseName!-drive(!drive!)_thor_log.txt"

:: ==============================================
:: RUN THOR SCAN
:: ==============================================
echo.
echo Running THOR on !scanDrive!...
echo Output will be saved to: !reportPath!\
echo.

Start "" !THOR_PATH! ^
  -a Filescan ^
  --intense --norescontrol --nosoft --cross-platform ^
  --rebase-dir "!reportPath!" ^
  --alldrives ^
  -p !scanDrive! ^
  --csvfile "!reportPath!\!csvFile!" ^
  --htmlfile "!reportPath!\!htmlFile!" ^
  --logfile "!reportPath!\!logFile!"

:: Open results folder when done
start explorer "!reportPath!"
echo THOR scan started. Report will be saved to:
echo !reportPath!\
pause
