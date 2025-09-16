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

def is_node_compatible(min_major=18) -> bool:
    """Return True if Node.js version >= 18 is installed."""
    try:
        import subprocess
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        version_str = result.stdout.strip().lstrip("v")  # e.g., "v18.16.0" → "18.16.0"
        major = int(version_str.split(".")[0])
        return major >= min_major
    except Exception:
        return False

def fetch_model(model_url: str, out_dir: str | Path) -> Path:
    output_path = str(out_dir / "SKELOv1.pt")  # directory target; gdown will put the file here
    try:
        print("Fetching model...")
        gdown.download(url=model_url, output=output_path)
    except Exception as e:
        print("An error occured: ", e)

def install_deps() -> None:
    print("Installing dependencies...")
    frontend_dir = Path("frontend")
    try:
        import subprocess
        import shutil
        npm = shutil.which("npm") or shutil.which("npm.cmd")    # Works Cross-platform
        subprocess.check_call([npm, "ci", "--include=dev"], cwd=frontend_dir)
    except Exception as e:
        print("An unexpected error occured while installing deps dependencies: ", e)
        print()
        sys.exit(1)

def create_api_base() -> None:
    api_url = "http://localhost:5000/api"
    with open("frontend/.env.development", "w") as f:
        f.write(f"VITE_API_BASE={api_url}\n")
    print(f"API base created for {api_url}")

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
        sys.exit(1)
    if not is_node_compatible():
        print("[ERROR] Node.js version >= 18 is required.")
        print("Please download the latest from: https://nodejs.org/en/download/")
        sys.exit(1)
    print("System requirements met.")

if __name__ == "__main__":
    print()
    print("________ PREREQUISITES INSTALLER ________")
    print()

    # CHECK SYSTEM REQUIREMENTS
    check_system_requirements()     # Blocks immediately if required versions are not installed
    print()

    # INSTALL PYTHON PACKAGES
    install_python_packages()
    print()
    # NOW SAFELY IMPORT
    from pathlib import Path
    import gdown
    import sys
    import os
    
    # FETCH THE MODEL
    print("Checking Model Installation...")
    model_path = Path("backend/skelo_ai/SKELOv1.pt")
    cancelled = False
    if model_path.exists():
        if (input("WARNING: SKELO Model is already installed. Reinstall? (y) ")).strip() in ['y', 'Y']:
            print(f"Removing {str(model_path)}...")
            os.remove(str(model_path))
        else:
            print("Model Installation cancelled by user.")
            cancelled = True
            
    # DOWNLOAD FROM GOOGLE DRIVE
    if not cancelled:
        OUTPUT_DIR = Path("backend/skelo_ai")
        MODEL_URL = "https://drive.google.com/uc?id=18T0X30kh4I2EVv0G93hwnP3h4O2i5tqb"
        fetch_model(MODEL_URL, OUTPUT_DIR)
    print()

    # DOWNLOAD ASSETS
    xmp_img_url = "https://drive.google.com/uc?id=1J14cpmGsXOk9QjlC6kARyNqDHXQr5FAV"
    logo_url = "https://drive.google.com/uc?id=13ZXEp4fvuKEZadgTTMT4NYT6ScylOe-k"
    banner_url = "https://drive.google.com/uc?id=1ZD5lsfOeOi-xSQmtKoMcgPF3g8Xy_MFE"
    print("Downloading assets...")
    gdown.download(banner_url, output=str(Path("frontend/src/assets/banner.jpg")))
    gdown.download(logo_url, output=str(Path("frontend/public/logo.jpg")))
    gdown.download(logo_url, output=str(Path("backend/example.jpg")))
    print("Assets downloaded.")
    print()

    # INSTALL DEPS
    print("Checking Node Modules Installation...")
    cancelled = False
    if Path("frontend/node_modules").exists():
        if input("WARNING: Node modules are already installed. Reinstall? (y) ").strip() not in ['y', 'Y']:
            print("deps Installation cancelled by user.")
            cancelled = True
    if not cancelled:
        install_deps()
    print()

    # CREATE .env file for development
    print("Creating API base...")
    create_api_base()
    print()

    print("Prerequisites installed.")
    print()

    print(f"Project Directory: {os.getcwd()}")
    print()
