# Circuit Metadata Detector

<img
  src="https://drive.google.com/uc?export=view&id=1ZD5lsfOeOi-xSQmtKoMcgPF3g8Xy_MFE"
  alt="SketchLogic Banner"
  width="500"
/>


SketchLogic is a Circuit Metadata Detector that can detect logic gates, rotations, and wires from hand-drawn circuit sketches, export results as structured JSON and render a clean visualization.

It takes scanned jpg images of one (or more) Handdrawn circuits on a plain paper as input. (no lines on the paper) 

**Project Status:** *Development phase.* 

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
````

Run the following script to automatically install all missing dependencies 
(Python packages, Node.js modules) and download the featured SKELO model:

```bash
python prerequisites.py
````

### Usage:

For this you’ll need **two terminal windows** open, both in the project root (the folder where you cloned the repository):

- In the **first terminal**, start the backend (Flask API):

```bash
python backend/app.py
````

- In the second terminal, start the frontend (React app)

```bash
cd frontend
npm run dev
````

The frontend will run on port 5173. Open <a href="http://localhost:5173/" target="_blank">localhost:5173</a> in your browser to view the app.

---

***NOTE:** This project is currently under development. Installation is meant for development and/or testing purposes only.*

---

## Key Features
- Detect **logic gates** from sketches  
  *Supported:* AND, OR, NOT, NAND, NOR, XOR, XNOR
- Detect **gate rotation** (0°, 90°, 180°, 270°)
- Detect **wires** and return them as ordered XY polylines
- Export **all components with coordinates** in structured JSON
- Visualize the **reconstructed circuit**
- Accuracy: **>80% accuracy** on the above criteria

---

## Components
- Custom YOLO model named **SKELO** used for gates detection
- Wire Detection Algorithms for detecting wires
- Frontend
- Backend API

---

## Contributing

- Early-stage project. Bug reports, suggestions, and small PRs are welcome anytime.

- If you would like to collaborate, please contact the owner using the information provided in the [Contact](#contact) section.

- For security issues, please use **private email** (see `SECURITY.md`).

---

## License

Distributed under the MIT License. See `LICENSE` for more information.


---

## Contact

* **LinkedIn:** [ShahzaibAhmad05](https://www.linkedin.com/in/shahzaibahmad05)
* **Email:** [shahzaibahmad6789@gmail.com](mailto:shahzaibahmad6789@gmail.com)
