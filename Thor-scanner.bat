@echo off
setlocal enabledelayedexpansion

:: ==============================================
:: INITIALIZATION
:: ==============================================
echo.
echo Developed by Jacob Wilson - Version 0.2
echo dfirvault@gmail.com
echo.

:: ==============================================
:: CHECK IF THOR IS ALREADY RUNNING
:: ==============================================
tasklist /FI "IMAGENAME eq thor64-lite.exe" 2>NUL | find /I "thor64-lite.exe" >NUL
if %ERRORLEVEL% equ 0 (
    echo.
    echo ERROR: Another THOR process is currently running.
    echo Please wait until it completes before running another scan.
    pause
    exit /b 1
)

:: ==============================================
:: THOR PATH CONFIGURATION
:: ==============================================
set "CONFIG_FILE=thor-config.txt"
set "THOR_PATH="
set "THOR_DIR="

:: Try to read path from config file
if exist "%CONFIG_FILE%" (
    for /f "usebackq delims=" %%A in ("%CONFIG_FILE%") do set "THOR_PATH=%%A"
)

:: If not found, check default locations
if not defined THOR_PATH (
    set "THOR_PATH=C:\Tools\Thor\thor64-lite.exe"
    if not exist "!THOR_PATH!" (
        if exist "thor64-lite.exe" (
            set "THOR_PATH=%CD%\thor64-lite.exe"
        ) else (
            if exist "thor-lite.exe" (
                set "THOR_PATH=%CD%\thor-lite.exe"
            )
        )
    )
)

:: ==============================================
:: VERIFY THOR EXECUTABLE
:: ==============================================
:CHECK_THOR
if not exist "!THOR_PATH!" (
    echo.
    echo ERROR: THOR executable not found.
    echo Current directory: %CD%
    dir /b thor*.exe
    set /p "THOR_PATH=Enter full path to Thor executable: "
    
    :: Check if user entered a directory path and append thor64-lite.exe if needed
    if exist "!THOR_PATH!\" (
        set "THOR_PATH=!THOR_PATH!\thor64-lite.exe"
    ) else (
        :: Check if path ends with backslash (user might have typed it)
        for /f "delims=" %%P in ("!THOR_PATH!") do (
            if "%%~pP"=="\" (
                set "THOR_PATH=!THOR_PATH!thor64-lite.exe"
            )
        )
    )
    
    if not exist "!THOR_PATH!" goto CHECK_THOR
    
    :: Save valid path
    echo !THOR_PATH! > "%CONFIG_FILE%"
)

:: Set THOR directory
for %%I in ("!THOR_PATH!") do set "THOR_DIR=%%~dpI"

:: ==============================================
:: UPDATE SIGNATURES
:: ==============================================
echo.
echo Checking THOR signatures...
if exist "!THOR_DIR!thor-lite-util.exe" (
    "!THOR_DIR!thor-lite-util.exe" upgrade
    if errorlevel 1 (
        echo WARNING: Signature update failed
    )
) else (
    echo WARNING: thor-lite-util.exe not found
)
timeout /t 2 /nobreak >nul

:: ==============================================
:: DRIVE SELECTION MENU
:: ==============================================
:DRIVE_SELECTION
cls
echo.
echo ===============================
echo    Available Drives to Scan
echo ===============================
echo.

:: Build drive list
set /a counter=0
for /f "skip=1 tokens=1,2,3*" %%A in ('wmic logicaldisk get DeviceID^,VolumeName^,Size') do (
    set "device=%%A"
    set "label=%%B"
    set "size=%%C"
    if not "!device!"=="" if not "!size!"=="" (
        set /a counter+=1
        echo [Option !counter!] Drive !device!
        set "drive!counter!=!device!"
    )
)

:: Show instructions
echo.
echo ==============================================
echo SELECTION INSTRUCTIONS:
echo    - For ONE drive: Enter its number (e.g., 2)
echo    - For MULTIPLE drives: Separate with commas (e.g., 1,3,5)
echo ==============================================
echo.

:: Get and process user input
:GET_INPUT
set "choices="
set /p "choices=Enter your drive selection(s): "

:: Initialize variables
set "scanCount=0"
set "invalidSelection="

:: Process each character in input
set "currentNumber="
for /f "delims=" %%C in ('cmd /u /c echo !choices!^| find /v ""') do (
    if "%%C"=="," (
        if defined currentNumber (
            call :PROCESS_NUMBER !currentNumber!
            set "currentNumber="
        )
    ) else if "%%C" geq "0" if "%%C" leq "9" (
        set "currentNumber=!currentNumber!%%C"
    ) else if "%%C" neq " " (
        set "invalidSelection=1"
    )
)

:: Process last number if present
if defined currentNumber call :PROCESS_NUMBER !currentNumber!

:: Check for any errors
if defined invalidSelection (
    echo ERROR: Invalid characters detected
    goto GET_INPUT
)

if !scanCount! equ 0 (
    echo ERROR: No valid drives selected
    goto GET_INPUT
)

:: Continue with rest of script
goto AFTER_DRIVE_SELECTION

:: Subroutine to process each number
:PROCESS_NUMBER
if defined drive%1 (
    set /a scanCount+=1
    set "selectedDrives!scanCount!=!drive%1!"
) else (
    echo ERROR: %1 is not a valid option
    set "invalidSelection=1"
)
goto :eof

:AFTER_DRIVE_SELECTION
:: ==============================================
:: REPORT LOCATION
:: ==============================================
echo.
set /p "reportPath=Enter folder to save reports (e.g., C:\Reports): "
if not exist "!reportPath!\" mkdir "!reportPath!"
if not exist "!reportPath!\" (
    echo ERROR: Could not create directory
    exit /b 1
)

:: ==============================================
:: CASE NAMES
:: ==============================================
for /l %%i in (1,1,!scanCount!) do (
    echo.
    :GET_CASENAME
    set "caseName%%i="
    set /p "caseName%%i=Enter Case Name for drive !selectedDrives%%i! (e.g., MAL2024-001): "
    if "!caseName%%i!"=="" (
        echo ERROR: Case Name cannot be empty
        goto GET_CASENAME
    )
)

:: ==============================================
:: PERFORMANCE OPTION
:: ==============================================
echo.
set /p "performanceMode=Use all threads for maximum performance? (y/n): "
set "threadOption="
if /i "!performanceMode!"=="y" set "threadOption=--threads 0"

:: ==============================================
:: RUN SCANS
:: ==============================================
echo.
echo Starting THOR scans...
echo.

for /l %%i in (1,1,!scanCount!) do (
    echo ===== Scanning !selectedDrives%%i! [Case: !caseName%%i!] =====
    
    :: Generate filenames
    for /f "tokens=2 delims==" %%a in ('wmic os get LocalDateTime /value') do set "datetime=%%a"
    set "date=!datetime:~0,8!"
    set "driveLetter=!selectedDrives%%i:~0,1!"
    
    set "csvFile=!date!-!caseName%%i!-drive(!driveLetter!)_files_md5s.csv"
    set "htmlFile=!date!-!caseName%%i!-drive(!driveLetter!)_thor_scan.html"
    set "logFile=!date!-!caseName%%i!-drive(!driveLetter!)_thor_log.txt"

    :: Run THOR
    echo Starting scan of !selectedDrives%%i!...
    start "" /wait "!THOR_PATH!" ^
      -a Filescan ^
      --intense --norescontrol --nosoft --cross-platform ^
      --rebase-dir "!reportPath!" ^
      --alldrives ^
      -p !selectedDrives%%i! ^
      --csvfile "!reportPath!\!csvFile!" ^
      --htmlfile "!reportPath!\!htmlFile!" ^
      --logfile "!reportPath!\!logFile!" ^
      !threadOption!

    echo Completed scan of !selectedDrives%%i!
    echo.
)

:: ==============================================
:: COMPLETION
:: ==============================================
start explorer "!reportPath!"
echo All scans completed. Reports saved to:
echo !reportPath!\
if !scanCount! equ 1 pause
