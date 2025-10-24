import os
import subprocess
import time
import platform
from datetime import datetime
import re
import sys
import ctypes
import win32con  # Requires pywin32 package
from tkinter import Tk, filedialog, messagebox  # For file dialogs

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if platform.system() != 'Windows':
        print("This script requires Windows.")
        return False
        
    if not is_admin():
        print("Requesting administrator privileges...")
        script = os.path.abspath(sys.argv[0])
        params = ' '.join([script] + sys.argv[1:])
        
        try:
            # Method 1: Using shell.ShellExecuteEx
            import win32api
            import win32process
            from win32com.shell import shell, shellcon
            
            win32api.ShellExecute(
                None,
                "runas",
                sys.executable,
                params,
                None,
                win32con.SW_SHOWNORMAL
            )
        except:
            try:
                # Method 2: Using ctypes
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, params, None, 1
                )
            except Exception as e:
                print(f"Failed to elevate privileges: {str(e)}")
                return False
        return True
    return False

def select_file(title, initialdir=None, filetypes=None):
    """Open a file selection dialog and return the selected path"""
    root = Tk()
    root.withdraw()  # Hide the main window
    root.attributes('-topmost', True)  # Bring dialog to front
    
    file_path = filedialog.askopenfilename(
        title=title,
        initialdir=initialdir,
        filetypes=filetypes
    )
    
    root.destroy()
    return file_path

def select_folder(title, initialdir=None):
    """Open a folder selection dialog and return the selected path"""
    root = Tk()
    root.withdraw()  # Hide the main window
    root.attributes('-topmost', True)  # Bring dialog to front
    
    folder_path = filedialog.askdirectory(
        title=title,
        initialdir=initialdir
    )
    
    root.destroy()
    return folder_path

def main():
    # ==============================================
    # CHECK ADMIN PRIVILEGES
    # ==============================================
    if platform.system() == 'Windows' and not is_admin():
        if run_as_admin():
            sys.exit(0)  # Exit the non-elevated instance
        else:
            print("This script must be run as administrator.")
            input("Press Enter to exit...")
            sys.exit(1)

    # Rest of your existing code...
    print("\nRunning with administrator privileges...\n")
    
    # ==============================================
    # INITIALIZATION
    # ==============================================
    print("\nDeveloped by Jacob Wilson - Version 0.4")
    print("dfirvault@gmail.com\n")

    # ==============================================
    # CHECK IF THOR IS ALREADY RUNNING
    # ==============================================
    if is_process_running("thor64-lite.exe"):
        print("\nERROR: Another THOR process is currently running.")
        print("Please wait until it completes before running another scan.")
        input("Press Enter to exit...")
        return 1

    # ==============================================
    # THOR PATH CONFIGURATION
    # ==============================================
    config_file = "thor-config.txt"
    thor_path = ""
    thor_dir = ""

    # Try to read path from config file
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            thor_path = f.readline().strip()

    # If not found, check default locations
    if not thor_path:
        thor_path = r"C:\Tools\Thor\thor64-lite.exe"
        if not os.path.exists(thor_path):
            if os.path.exists("thor64-lite.exe"):
                thor_path = os.path.join(os.getcwd(), "thor64-lite.exe")
            elif os.path.exists("thor-lite.exe"):
                thor_path = os.path.join(os.getcwd(), "thor-lite.exe")

    # ==============================================
    # VERIFY THOR EXECUTABLE (WITH FILE SELECTOR)
    # ==============================================
    while not os.path.exists(thor_path):
        print("\nERROR: THOR executable not found.")
        print(f"Current directory: {os.getcwd()}")
        
        # List thor*.exe files in current directory
        for f in os.listdir():
            if f.lower().startswith("thor") and f.lower().endswith(".exe"):
                print(f)
        
        print("\nPlease select the THOR executable:")
        try:
            # Show file selection dialog
            thor_path = select_file(
                "Select THOR executable (thor64-lite.exe or thor-lite.exe)",
                initialdir=os.getcwd(),
                filetypes=[("THOR Executable", "thor*.exe"), ("All files", "*.*")]
            )
            
            if not thor_path:  # User cancelled
                print("File selection cancelled. Exiting...")
                sys.exit(1)
                
        except Exception as e:
            print(f"Error showing file dialog: {e}")
            thor_path = input("Enter full path to Thor executable: ").strip()
        
        # Check if user entered a directory path and append thor64-lite.exe if needed
        if thor_path and os.path.isdir(thor_path):
            thor_path = os.path.join(thor_path, "thor64-lite.exe")
        elif thor_path and thor_path.endswith("\\"):
            thor_path = os.path.join(thor_path, "thor64-lite.exe")
    
    # Save valid path
    with open(config_file, 'w') as f:
        f.write(thor_path)
    
    thor_dir = os.path.dirname(thor_path)

    # ==============================================
    # UPDATE SIGNATURES
    # ==============================================
    print("\nChecking THOR signatures...")
    thor_util = os.path.join(thor_dir, "thor-lite-util.exe")
    if os.path.exists(thor_util):
        try:
            result = subprocess.run([thor_util, "upgrade"], check=True)
        except subprocess.CalledProcessError:
            print("WARNING: Signature update failed")
    else:
        print("WARNING: thor-lite-util.exe not found")
    
    time.sleep(2)

    # ==============================================
    # DRIVE SELECTION MENU
    # ==============================================
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n===============================")
        print("    Available Drives to Scan")
        print("===============================\n")

        # Build drive list - NOW INCLUDES EMULATED/REMOVABLE DRIVES
        drives = get_available_drives()
        if not drives:
            print("No available drives found!")
            input("Press Enter to exit...")
            return 1

        for i, (drive, label, size, drive_type) in enumerate(drives, 1):
            type_desc = get_drive_type_description(drive_type)
            print(f"[Option {i}] Drive {drive} - {type_desc}")

        print("\n==============================================")
        print("SELECTION INSTRUCTIONS:")
        print("   - For ONE drive: Enter its number (e.g., 2)")
        print("   - For MULTIPLE drives: Separate with commas (e.g., 1,3,5)")
        print("==============================================\n")

        # Get and process user input
        choices = input("Enter your drive selection(s): ").strip()
        selected_drives = []
        invalid_selection = False

        # Process input
        for part in choices.split(','):
            part = part.strip()
            if part.isdigit():
                idx = int(part) - 1
                if 0 <= idx < len(drives):
                    selected_drives.append(drives[idx][0])
                else:
                    print(f"ERROR: {part} is not a valid option")
                    invalid_selection = True
            elif part:
                print(f"ERROR: Invalid character '{part}' detected")
                invalid_selection = True

        if not invalid_selection and selected_drives:
            break
        elif not selected_drives:
            print("ERROR: No valid drives selected")
        
        input("Press Enter to try again...")

    # ==============================================
    # REPORT LOCATION (WITH FOLDER SELECTOR)
    # ==============================================
    print()
    report_path = ""
    while True:
        try:
            print("Please select the folder to save reports:")
            report_path = select_folder(
                "Select folder to save reports",
                initialdir=os.path.expanduser("~\\Documents")
            )
            
            if not report_path:  # User cancelled
                print("Folder selection cancelled. Exiting...")
                sys.exit(1)
                
            os.makedirs(report_path, exist_ok=True)
            if os.path.isdir(report_path):
                break
            else:
                print("ERROR: Could not create directory")
        except Exception as e:
            print(f"Error showing folder dialog: {e}")
            report_path = input("Enter folder to save reports (e.g., C:\\Reports): ").strip()
            if not report_path:
                continue
                
            try:
                os.makedirs(report_path, exist_ok=True)
                if os.path.isdir(report_path):
                    break
                else:
                    print("ERROR: Could not create directory")
            except Exception as e:
                print(f"ERROR: Could not create directory - {str(e)}")

    # ==============================================
    # CASE NAMES
    # ==============================================
    case_names = []
    for drive in selected_drives:
        while True:
            print()
            case_name = input(f"Enter Case Name for drive {drive} (e.g., MAL2024-001): ").strip()
            if case_name:
                case_names.append(case_name)
                break
            else:
                print("ERROR: Case Name cannot be empty")

    # ==============================================
    # PERFORMANCE OPTION
    # ==============================================
    print()
    performance_mode = input("Use all threads for maximum performance? (y/n): ").strip().lower()
    thread_option = "--threads 0" if performance_mode == 'y' else ""

    # ==============================================
    # RUN SCANS
    # ==============================================
    print("\nStarting THOR scans...\n")

    for i, drive in enumerate(selected_drives):
        print(f"===== Scanning {drive} [Case: {case_names[i]}] =====")
        
        # Generate filenames
        now = datetime.now()
        date = now.strftime("%Y%m%d")
        drive_letter = drive[0]
        
        csv_file = f"{date}-{case_names[i]}-drive({drive_letter})_files_md5s.csv"
        html_file = f"{date}-{case_names[i]}-drive({drive_letter})_thor_scan.html"
        log_file = f"{date}-{case_names[i]}-drive({drive_letter})_thor_log.txt"

        # Run THOR
        print(f"Starting scan of {drive}...")
        
        cmd = [
            thor_path,
            "-a", "Filescan",
            "--intense", "--norescontrol", "--nosoft", "--cross-platform",
            "--rebase-dir", report_path,
            "--alldrives",
            "-p", drive,
            "--csvfile", os.path.join(report_path, csv_file),
            "--htmlfile", os.path.join(report_path, html_file),
            "--logfile", os.path.join(report_path, log_file)
        ]
        
        # Add thread option if selected (corrected format)
        if performance_mode == 'y':
            cmd.extend(["--threads", "0"])
        
        try:
            subprocess.run(cmd, check=True)
            print(f"Completed scan of {drive}")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while scanning {drive}: {str(e)}")
        
        print()

    # ==============================================
    # COMPLETION
    # ==============================================
    if platform.system() == 'Windows':
        os.startfile(report_path)
    else:
        subprocess.run(['xdg-open', report_path])
    
    print("All scans completed. Reports saved to:")
    print(f"{report_path}\\")
    
    if len(selected_drives) == 1:
        input("Press Enter to exit...")

def is_process_running(process_name):
    try:
        if platform.system() == 'Windows':
            output = subprocess.check_output(['tasklist', '/FI', f'IMAGENAME eq {process_name}'], 
                                            stderr=subprocess.DEVNULL, 
                                            universal_newlines=True)
            return process_name.lower() in output.lower()
        else:
            # For non-Windows systems (though THOR is Windows-only)
            output = subprocess.check_output(['ps', 'aux'], universal_newlines=True)
            return process_name in output
    except:
        return False

def get_drive_type_description(drive_type):
    """Convert drive type number to descriptive string"""
    drive_types = {
        0: "Unknown",
        1: "No Root Directory",
        2: "Removable",  # USB drives, floppy disks
        3: "Fixed",      # Hard drives
        4: "Remote",     # Network drives
        5: "CD-ROM",
        6: "RAM disk"
    }
    return drive_types.get(drive_type, f"Type {drive_type}")

def get_available_drives():
    """Get all available drives including emulated/removable drives"""
    drives = []
    if platform.system() == 'Windows':
        try:
            # Method 1: Using WMIC (most comprehensive for drive types)
            try:
                output = subprocess.check_output(
                    'wmic logicaldisk get DeviceID,VolumeName,Size,DriveType /format:csv',
                    stderr=subprocess.DEVNULL,
                    universal_newlines=True,
                    shell=True
                )
                
                # Parse CSV output - we want ALL drive types including removable (2)
                for line in output.splitlines()[1:]:  # Skip header
                    parts = line.strip().split(',')
                    if len(parts) >= 5:
                        device = parts[1]  # DeviceID is in second column
                        label = parts[2] if len(parts) > 2 else ""
                        size = parts[3] if len(parts) > 3 else "0"
                        drive_type = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else 0
                        
                        # Include ALL drive types including removable (2), fixed (3), etc.
                        if device and device.endswith(':'):
                            drives.append((device, label, size, drive_type))
                
                if drives:
                    return drives
            except Exception as e:
                print(f"WMIC method failed: {e}")
                pass  # WMIC failed, fall back to next method

            # Method 2: Using psutil (alternative method)
            try:
                import psutil
                for partition in psutil.disk_partitions():
                    if partition.device:
                        drive = partition.device.split('\\')[0]
                        try:
                            usage = psutil.disk_usage(partition.mountpoint)
                            size = str(usage.total)
                        except:
                            size = "0"
                        
                        # Determine drive type from options
                        opts = partition.opts.lower()
                        if 'removable' in opts:
                            drive_type = 2
                        elif 'fixed' in opts:
                            drive_type = 3
                        elif 'remote' in opts:
                            drive_type = 4
                        elif 'cdrom' in opts:
                            drive_type = 5
                        else:
                            drive_type = 0
                            
                        drives.append((drive, partition.mountpoint, size, drive_type))
                if drives:
                    return drives
            except ImportError:
                pass  # psutil not available
            except Exception as e:
                print(f"psutil method failed: {e}")
                pass

            # Method 3: Direct drive letter checking (fallback)
            import string
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    try:
                        # Get volume label
                        label_output = subprocess.check_output(
                            ['vol', drive],
                            stderr=subprocess.DEVNULL,
                            universal_newlines=True,
                            shell=True
                        )
                        label = label_output.split('\n')[0].split()[-1]
                    except:
                        label = ""
                    
                    # Get size (approximate)
                    try:
                        total_bytes = 0
                        for root, dirs, files in os.walk(drive):
                            for f in files:
                                fp = os.path.join(root, f)
                                try:
                                    total_bytes += os.path.getsize(fp)
                                except:
                                    pass
                        size = str(total_bytes)
                    except:
                        size = "0"
                    
                    # Try to determine drive type
                    try:
                        # Use powershell to get drive type
                        ps_cmd = f"(Get-PSDrive -Name {letter}).Provider.Name"
                        output = subprocess.check_output(
                            ['powershell', '-Command', ps_cmd],
                            stderr=subprocess.DEVNULL,
                            universal_newlines=True
                        )
                        if 'FileSystem' in output:
                            # For FileSystem drives, we can't easily distinguish fixed vs removable
                            # without admin rights, so we'll default to showing them
                            drive_type = 0  # Unknown but accessible
                        else:
                            drive_type = 0
                    except:
                        drive_type = 0
                    
                    drives.append((f"{letter}:", label, size, drive_type))
            
        except Exception as e:
            print(f"Error detecting drives: {str(e)}")
    
    return drives

if __name__ == "__main__":
    main()
