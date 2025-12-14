"""
Pre-requisites installation script.

Please install the requirements file before opting to run this file.

"""


from pathlib import Path
import os, sys

# Check if this is run from the correct dir
if not os.getcwd().endswith("backend"):
    print("Please run this script from backend dir.")
    sys.exit(1)

# This package might not be present
try: import gdown
except Exception: 
    print("Requirements not installed.")
    print("Run pip install gdown before running this script again.")


def fetch_from_gdrive(url: str, out_dir: Path, out_file_name: str) -> Path:
    output_path = os.path.join(str(out_dir), out_file_name)  # directory target; gdown will put the file here
    try:
        print(f"Fetching {out_file_name}...")
        gdown.download(url=url, output=output_path)
    except Exception as e:
        print("An error occured: ", e)


def printIntro() -> None:
    """ Prints the introduction for this script """

    print()
    print("________ SETUP FOR BACKEND ________")
    print()
    print("- Please make sure you have an active internet connection.")
    print("- This script will download files for the backend.")
    print("- Each file will be download on your permission (unless --noconfirm is used)")
    print()


if __name__ == "__main__":

    # Modes for this script (controlled using CLI)
    noconfirm = False
    printIntro()


    # toggle Modes based on input
    if len(sys.argv) == 2:
        if sys.argv[1] == "--noconfirm":
            print("- noconfirm Enabled")
            noconfirm = True
        else:
            print("Invalid CLI option.")
            print("Usage: ")
            print("\t--noconfirm\n")
            sys.exit(0)
        print()

    if not noconfirm and input("Continue? (y): ") not in ['y', 'Y']:
        print("Operation cancelled by the user.")
        print()
        sys.exit(0)
    

    # FETCH THE MODEL
    print("Checking SKELO Model Installation...")
    model_path = Path("skelo/SKELOv1.pt")
    model_install_cancelled = False

    if not noconfirm and model_path.exists():
        if (input("WARNING: SKELO Model is already installed. Reinstall? (y) ")).strip() in ['y', 'Y']:
            print(f"Removing {str(model_path)}...")
            os.remove(str(model_path))
        else:
            print("Model Installation cancelled by user.")
            model_install_cancelled = True
            
    # DOWNLOAD FROM GOOGLE DRIVE
    if not model_install_cancelled:
        # If noconfirm is there or user says yes
        if noconfirm or input("Download SKELOv1 model? (y) ") in ["y", "Y"]:

            OUTPUT_DIR = Path("skelo")
            MODEL_URL = "https://drive.google.com/uc?id=18T0X30kh4I2EVv0G93hwnP3h4O2i5tqb"
            MODEL_FILE_NAME = "SKELOv1.pt"
            try:
                fetch_from_gdrive(MODEL_URL, OUTPUT_DIR, MODEL_FILE_NAME)
            except:
                print("[ERROR] Could not download SKELO model")
                print("please check your internet and try again.")
                print()
                sys.exit(1)
    print()


    # DOWNLOAD ASSETS
    print("Downloading assets...")
    assets = {
        "example.jpg": "https://drive.google.com/uc?id=1J14cpmGsXOk9QjlC6kARyNqDHXQr5FAV"
    }       # Keys are file names and values are urls
    for key, val in assets.items():
        try:
            if noconfirm or input(f"Download {key}? (y) ") in ["y", "Y"]:
                fetch_from_gdrive(url=val, out_dir=".", out_file_name=key)
        except:
            print("[ERROR] Could not download project assets")
            print("Please check your internet and try again.")
            print()
            sys.exit(1)


    print("Assets downloaded.")
    print()

    print("Setup finished successfully.")
    print()
