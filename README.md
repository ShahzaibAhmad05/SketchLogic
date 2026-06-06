# Sketch to Simulation Converter for Logic Circuits

A sketch to simulation converter for logic circuits built through a lightweight and portable YOLO model and connection analysis algorithms.

It takes scanned jpg images of Handdrawn circuits on a plain paper as input.


---


## Open-Source usage of this project

This project comes with `MIT LICENSE`. See [LICENSE]() file for more details.

This system can be integrated in any circuit simulation software. For setup details, refer to the [Developer Setup](#developer-setup). It mainly has two parts:

- ML Model

This can be either compiled with all the python dependencies into an executable, or used directly inside your app's technical stack (if applicable). Refer to the inference script to figure out what this model outputs.

- Connector System

This is purely python. A feasible option here is to compile it to `.exe` and run it via command-line args. OR a bitter approach would be to translate the entire system into your app's language.


---


## ML Model for Detecting Logic Gates

The scripts in `models/` can be used to train a computer vision model that is capable of detecting 7 basic logic gates (AND, OR, NAND, NOR, NOT, XOR, XNOR) and their orientation in an image. (using OBB)

**IMPORTANT:** One critical limitation with OBB (Oriented Bounding Box) is that it is only able to detect if the gate is horizontal or vertical. The exact angle has to be figured out by the `connector` module.


### YOLOv8 nano as a Starter

YOLO is super lightweight and easy to fine-tune. The ultralytics library provides us with tooling to load, fine-tune, and export YOLO models which are pre-trained on the COCO dataset (80 classes). We fine-tune from this checkpoint to our logic gates detector in this script.

Configuration for the model can be found in `model/training_script.py`. 


### Farming GPUs from Kaggle 

Kaggle provides us with enough GPU support for running this script. Although there are other options available too, but [Kaggle](https://www.kaggle.com/) is currently offering more flexibility than any other GPU providers. (since we are working for free)

With that said, the dataset is also uploaded to Kaggle. This will make our work significantly easier long-term.


### Dataset Collection & Annotation

The dataset consists of publicily available logic circuit images and some other datasets that had an MIT License, and no requirements for citations, so it is legal.

For annotation, we have used [X-AnyLabelling]() which is a free and open-source tool. The dataset can be downloaded from [here](). Consider infering information about the dataset from `config.yaml`.

IMPORTANT CITATION here as requested by X-AnyLabelling [here](https://github.com/CVHub520/X-AnyLabeling#citing):

```js
@misc{X-AnyLabeling,
  year = {2023},
  author = {Wei Wang},
  publisher = {Github},
  organization = {CVHub},
  journal = {Github repository},
  title = {Advanced Auto Labeling Solution with Added Features},
  howpublished = {\url{https://github.com/CVHub520/X-AnyLabeling}}
}
```


### Last Training Session

The model was last trained 05/06/2026 for approximately 6.35 hours on Kaggle. The Jupyter notebook can be viewed [here](https://www.kaggle.com/code/shahzaibahmad05/sketchlogic-training-notebook). 


| epoch | time | train/box_loss | train/cls_loss | train/dfl_loss | train/angle_loss | precision | recall | mAP50 | mAP50-95 | val/box_loss | val/cls_loss | val/dfl_loss | val/angle_loss |
|-------|------|----------------|----------------|----------------|------------------|-----------|--------|-------|----------|--------------|--------------|--------------|----------------|
| 100 | 19931.4s | 0.394 | 0.299 | 1.047 | 0.004 | 0.993 | 0.988 | 0.995 | 0.892 | 0.510 | 0.428 | 0.677 | 0.002 |


<img src="https://drive.google.com/uc?export=view&id=1StQvNYJ5S1Dl0IWmfrYiu6ashUvirEdj" />
<br />
<img src="https://drive.google.com/uc?export=view&id=1WCEGoeG9l2GPmJ9VMFqHr0pfoJkYgEgk" />


### Model (module) Output format

`model/` module in the repository as run by `python -m module` has this output format:

```json
{
    "$id": 1,
    "$type": "AndGate",
    "CenterX": 626,
    "CenterY": 405,
    "Width": 176,
    "Height": 148,
    "Rotation": 0,
}
```

---


## Connector for Circuit Connections




---


## Developer Setup

- Clone the repository:

```bash
git clone https://github.com/ShahzaibAhmad05/SketchLogic.git
```

- Download a [sample image](https://drive.google.com/file/d/1oM1hXelDe4CP7UINKykob-5esfnC-Yg9/view?usp=sharing) and the [model weights](https://drive.google.com/file/d/1JoGrqKjKqVrckpMn2kMGk8Dhp9zJWugv/view?usp=sharing). Put them in these paths:

```bash
./Sketchlogic/model/SketchLogic.pt
./Sketchlogic/temp.jpg
```

- Install requirements for python (make sure you have 3.11 or just configure it in venv):

```bash
pip install -r requirements.txt
```

- Run the model to generate inference for the image:

```bash
# <input_image_path> <output_json_path>
python -m model temp.jpg output.json
```

- Run the connector to generate wires and output the circuit:

```bash
# <input_image_path> <previous_output_path> <output_json_path>
python -m connector temp.jpg output.json circuit.json
```


---


## What to do with the output json file?

The last step we did in [Developer Setup]() gave us a circuit.json file in a format that allows simulation of the circuit. This file is currently directly plug-able into [IRis](https://github.com/d-khalid/IRis) to generate a simulation. Just setup the app, load the file into it, and see the magic.

We are also working on making multiple converters for this format so it can be loaded into [proteus], [Logisim] and other circuit simulation software.
