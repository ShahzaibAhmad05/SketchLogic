"""
Pre-requisites installation script

"""

try:    # Will be imported later anyways
    from pathlib import Path
except: pass

def install_if_missing(module_name, install_key) -> bool:
    """ Returns True if a module was missing """
    try:
        __import__(module_name)
        return False
    except ImportError:
        print(f"{module_name} is not installed.")
        print(f"Installing {module_name}...")
        try:
            import subprocess
            subprocess.check_call(['pip', 'install', install_key])
            print("Installation complete.")
            return True
        except Exception as e:
            print("An unexpected error occured while installing dependencies: ", e)
            print()
            sys.exit(1)

def check_modules(modules: dict) -> None:
    print("Checking Missing Dependencies...")

    # INSTALL MISSING MODULES
    new_modules_installed = False
    new_modules = []
    for name, key in modules.items(): 
        new_modules_installed = install_if_missing(name, key)
        if new_modules_installed:
            new_modules.append(name)
    # LOG RESULTS
    if new_modules_installed:
        print("The following modules were installed: ")
        for module in new_modules:
            print(module)
    else: print("No Missing Dependencies.")

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

if __name__ == "__main__":
    print()
    print("________ PREREQUISITES INSTALLER ________")
    print()
    modules = {
        "flask": "Flask",
        "flask_cors": "Flask-Cors",
        "PIL": "Pillow",
        "torch": "torch",
        "cv2": "opencv-python",
        "numpy": "numpy",
        "scipy": "scipy",
        "skimage": "scikit-image",
        "ultralytics": "ultralytics",
        "gdown": "gdown",
        "pathlib": "pathlib"
    }
    check_modules(modules)
    print()
    # NOW SAFELY IMPORT
    from pathlib import Path
    import gdown
    import sys
    import os
    
    # FETCH THE MODEL
    print("Checking Model Installation...")
    model_path = Path("skelo_ai/SKELOv1.pt")
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
        OUTPUT_DIR = Path("skelo_ai")
        MODEL_URL = "https://drive.google.com/uc?id=18T0X30kh4I2EVv0G93hwnP3h4O2i5tqb"
        fetch_model(MODEL_URL, OUTPUT_DIR)
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

    print("✨ Prerequisites installed.")
    print()

    print("Root Directory: ")
    print(os.getcwd())
    print()