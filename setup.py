"""
Pre-requisites installation script

"""

try:    # Will be imported later anyways
    from pathlib import Path
except: pass

def is_python_compatible(min_major=3, min_minor=9) -> bool:
    """Return True if Python version >= 3.9 (default)."""
    import sys
    major, minor = sys.version_info.major, sys.version_info.minor
    return (major, minor) >= (min_major, min_minor)

def fetch_model(model_url: str, out_dir: str | Path) -> Path:
    output_path = str(out_dir / "SKELOv1.pt")  # directory target; gdown will put the file here
    try:
        print("Fetching model...")
        gdown.download(url=model_url, output=output_path)
    except Exception as e:
        print("An error occured: ", e)

def install_python_packages() -> None:
    """
    Installs dependencies from a requirements.txt file.
    Returns only if installation succeeds, fails otherwise.

    """
    import subprocess
    import sys
    
    requirements_file = "requirements.txt"
    try:
        print(f"Installing Python dependencies from {requirements_file}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
        print("Requirements installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to install requirements: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error while installing requirements: {e}")
        sys.exit(1)

def check_system_requirements() -> None:
    print("Checking system requirements...")
    if not is_python_compatible():
        print("[ERROR] Python version >= 3.9 is required.")
        print("Please download the latest from: https://www.python.org/downloads/")
        print()
        sys.exit(1)
    print("System requirements met.")

def printIntro() -> None:
    """ Prints the introduction for the prerequisites installer """

    print("- This script will install dependencies for the backend (on your permission only)")
    print("- Please make sure you have an active internet connection.")
    print()

if __name__ == "__main__":
    import os, sys
    os.system("cls")
    print("________ SETUP FOR IRIS BACKEND ________")
    print()
    printIntro()
    print()

    if input("Continue? (y): ") not in ['y', 'Y']:
        print("Operation cancelled by the user.")
        print()
        sys.exit(0)

    # CHECK SYSTEM REQUIREMENTS
    check_system_requirements()     # Blocks immediately if required versions are not installed
    print()

    # INSTALL PYTHON PACKAGES
    if input("Install missing python packages? (y): ") in ['y', 'Y']:
        install_python_packages()
    else:
        print("Python packages were not installed.")
    print()

    # NOW IMPORT (MAY STILL BE NOT SAFE)
    try:
        from pathlib import Path
        import gdown
        import sys
        import os
    except:
        print("[ERROR] Cannot import some python packages")
        print("Please enter (y) next time to install python packages properly.")
        print()
        sys.exit(1)
    
    # FETCH THE MODEL
    print("Checking SKELO Model Installation...")
    model_path = Path("backend/skelo/SKELOv1.pt")
    model_install_cancelled = False
    if model_path.exists():
        if (input("WARNING: SKELO Model is already installed. Reinstall? (y) ")).strip() in ['y', 'Y']:
            print(f"Removing {str(model_path)}...")
            os.remove(str(model_path))
        else:
            print("Model Installation cancelled by user.")
            model_install_cancelled = True
            
    # DOWNLOAD FROM GOOGLE DRIVE
    if not model_install_cancelled:
        OUTPUT_DIR = Path("backend/skelo")
        MODEL_URL = "https://drive.google.com/uc?id=18T0X30kh4I2EVv0G93hwnP3h4O2i5tqb"
        try:
            fetch_model(MODEL_URL, OUTPUT_DIR)
        except:
            print("[ERROR] Could not download SKELO model")
            print("please check your internet and try again.")
            print()
            sys.exit(1)
    print()

    # DOWNLOAD ASSETS
    xmp_img_url = "https://drive.google.com/uc?id=1J14cpmGsXOk9QjlC6kARyNqDHXQr5FAV"
    print("Downloading assets...")
    try:
        gdown.download(xmp_img_url, output=str(Path("example.jpg")))
    except:
        print("[ERROR] Could not download project assets")
        print("Please check your internet and try again.")
        print()
        sys.exit(1)

    print("Assets downloaded.")
    print()

    print("Setup finished successfully.")
    print()
