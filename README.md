# Circuit Metadata Detector

<img
  src="https://drive.google.com/uc?export=view&id=1ZD5lsfOeOi-xSQmtKoMcgPF3g8Xy_MFE"
  alt="SketchLogic Banner"
  width="500"
/>

SketchLogic is a Circuit Metadata Detector that can detect logic gates, rotations, and wires from hand-drawn circuit sketches, export results as structured JSON and render a clean visualization.

It takes scanned jpg images of one (or more) Handdrawn circuits on a plain paper as input. (no lines on the paper)

**Project Status:** _Development phase._

**Contributions are Welcome!**

---

## Development & Testing

### System Requirements:

- Python 3.9 or Higher -> <a href="https://www.python.org/downloads/" target="_blank">Download here</a>
- Node.js version 18 or Higher (includes npm) -> <a href="https://nodejs.org/en/download/" target="_blank">Download here</a>
- MacOS, Linux, or Windows

### Installation:

Bellow is the recommended installation process for testing of this project. Please feel free to use any other approaches you prefer.

Clone the repository:

```bash
git clone https://github.com/ShahzaibAhmad05/SketchLogic.git
cd SketchLogic
```

Run the following script to automatically install all missing dependencies
(Python packages, Node.js modules) and download the featured SKELO model:

```bash
python prerequisites.py
```

### Usage:

For this you’ll need your terminal open in the project root (the folder where you cloned the repository):

- In the terminal, start the backend (Flask API):

```bash
python backend/app.py
```

### Manual Development Setup (backend only)

If you’d rather perform the backend setup manually (without the script), follow these steps. These mirror what `setup.py` does.

Prerequisites

- Python 3.9 or higher

From the project root, run the following in Windows PowerShell:

```powershell
# 1) (Optional) Create and activate a virtual environment
py -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2) Install Python dependencies
pip install -r requirements.txt
```

```powershell
# 3) Download the custom YOLO model (SKELO) to skelo/SKELOv1.pt
python -m gdown "https://drive.google.com/uc?id=18T0X30kh4I2EVv0G93hwnP3h4O2i5tqb" -O "skelo/SKELOv1.pt"

# 4) Download example asset image to project root (example.jpg)
python -m gdown "https://drive.google.com/uc?id=1J14cpmGsXOk9QjlC6kARyNqDHXQr5FAV" -O "example.jpg"

# 5) Run the backend API (this repository)
python .\app.py
```

#### Without gdown (manual download)

If you cannot or prefer not to use `gdown`, download the files via your browser and place them in the correct locations:

1. Download the SKELO model (YOLO) file to your Downloads folder. Model URL: <https://drive.google.com/uc?id=18T0X30kh4I2EVv0G93hwnP3h4O2i5tqb>. Rename the downloaded file to `SKELOv1.pt` if needed, then move it into the project at `skelo/SKELOv1.pt`.

Ensure the `skelo` folder exists in the project root (create it if it doesn't), then move the file into `skelo/SKELOv1.pt`.

2. Download the example asset image to your Downloads folder. Asset URL: <https://drive.google.com/uc?id=1J14cpmGsXOk9QjlC6kARyNqDHXQr5FAV>. Rename it to `example.jpg`, then move it into the project root as `example.jpg`.

3. Then run the backend API as described in the Usage section.

Notes

- The model file must be located at `skelo/SKELOv1.pt` (this is the path used by the app).
- The example asset downloads to `example.jpg` in the project root.
- After the server starts, check health at: <http://localhost:5000/api/health>

---

**\*NOTE:** This project is currently under development. Installation is meant for development and/or testing purposes only.\*

---

## Key Features

- Detect **logic gates** from sketches  
  _Supported:_ AND, OR, NOT, NAND, NOR, XOR, XNOR
- Detect **gate rotation** (0°, 90°, 180°, 270°)
- Detect **wires** and return them as ordered XY polylines
- Export **all components with coordinates** in structured JSON
- Visualize the **reconstructed circuit**
- Accuracy: **>80% accuracy** on the above criteria

---

## Components

- Custom YOLO model named **SKELO** used for gates detection
- Wire Detection Algorithms for detecting wires
- Backend API

---

## Contributing

- Bug reports, suggestions, and PRs are absolutely WELCOME!

- See `CONTRIBUTING.md` for more details.

- If you would like to collaborate, please contact the owner using the information provided in the [Contact](#contact) section.

- For security issues, see `SECURITY.md`.

---

## License

Distributed under the MIT License. See `LICENSE` for more information.

---

## Contact

- **LinkedIn:** [ShahzaibAhmad05](https://www.linkedin.com/in/shahzaibahmad05)
- **Email:** [shahzaibahmad6789@gmail.com](mailto:shahzaibahmad6789@gmail.com)
