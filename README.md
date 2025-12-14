# Circuit Metadata Detector

<img
  src="https://drive.google.com/uc?export=view&id=1ZD5lsfOeOi-xSQmtKoMcgPF3g8Xy_MFE"
  alt="SketchLogic Banner"
  width="500"
/>

SketchLogic is a Circuit Metadata Detector that can detect logic gates, rotations, and wires from hand-drawn circuit sketches, export results as structured JSON and render a clean visualization.

It takes scanned jpg images of one (or more) Handdrawn circuits on a plain paper as input. (no lines on the paper)

**Contributions are Welcome!**

---

## Development & Testing

### System Requirements:

- Python 3.9 or Higher -> <a href="https://www.python.org/downloads/" target="_blank">Download here</a>
- Node.js version 18 or Higher (includes npm) -> <a href="https://nodejs.org/en/download/" target="_blank">Download here</a>
- MacOS, Linux, or Windows

**Note:** The term *root directory* refers to the main directory of the project. In this case, it would be the folder "*SketchLogic*".

### Backend Setup:

- Refer to [backend/README.md](https://github.com/ShahzaibAhmad05/SketchLogic/blob/main/backend/README.md) for instructions on setting up the backend.

### Usage:

For this you’ll need your terminal open in the root directory:

- In the terminal, start the backend (Flask API):

```bash
cd backend
python app.py
```

### Testing:

Open another terminal in the root directory, and enter:

````
python testRun.py
````

Feel free to edit the test run script to try out the backend api.

### Frontend Setup:

- Refer to [frontend/README.md](https://github.com/ShahzaibAhmad05/SketchLogic/blob/main/frontend/README.md) for instructions on setting up the frontend.

### Usage:

For this you’ll need your terminal open in the root directory:

- In the terminal, start the frontend (using npm):

```bash
cd frontend
npm run dev
```

### Testing:

For this, make sure the backend is already running on `localhost:5000` by using the `testRun.py` script.

Open `localhost:5173` on your browser to interact with the frontend.

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
- React Frontend

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
