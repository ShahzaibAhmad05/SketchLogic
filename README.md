# Sketch to Simulation System

A sketch to simulation converter for logic circuits built through a lightweight and portable model (fine-tuned from YOLO) and connection analysis algorithms.


![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![YOLO](https://img.shields.io/badge/YOLO-00FFFF?style=for-the-badge&logo=yolo&logoColor=black)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)


---


## Current Capabilities

This system is able to detect circuits made of the 7 logic gates (AND, OR, NOT, NOR, NAND, XOR, XNOR). The wiring algorithms cannot work with T-Junctions (a wire crossing over another) in wires but that too would be added soon.

An example of the system's output

<img />

<br />

*Image Credits: [IRis - Circuit Simulator](https://github.com/d-khalid/IRis)*


---


## Integration in any Circuit Simulation Engine

This project comes with `GPL-3.0 LICENSE`. See [LICENSE]() file for more details. Following that, this system can be integrated in any circuit simulation software. For setup details, refer to the [Developer Setup](#developer-setup). It mainly has two modules (explained in the sections bellow this one):

- `model/`

This can be either compiled with all the python dependencies into an executable, or used directly inside your app's technical stack (if applicable). Refer to the section bellow to checkout out the output format.

- `connector/`

Connector takes the output of `model` and converts it to a simulatable json format. This is purely python. A feasible option here is to compile it to `.exe` and run it via command-line args. OR a bitter approach would be to translate the entire system into the target app's language.


---


## ML Model for Detecting Logic Gates

Capable of detecting 7 basic logic gates (AND, OR, NAND, NOR, NOT, XOR, XNOR) and their orientation (x4 classes) in an image.

**IMPORTANT:** A debatable option is to use OBB (Oriented Bounding Box). That way we would have lesser number of input classes and easier `model.train()` configuration. But then the exact angle has to be figured out by the `connector` module which quickly becomes a pain.


### YOLOv8 nano as a Starter

YOLO is super lightweight and easy to fine-tune. The ultralytics library has the tooling to load, fine-tune, and export YOLO models which are pre-trained on the COCO dataset (80 classes). We fine-tune our logic gates detector from this checkpoint.

Configuration for the training can be found in `model/training_script.py`. 


### Farming GPUs from Kaggle 

Kaggle provides us with enough GPU support for running this script. Although there are other options available too, but [Kaggle](https://www.kaggle.com/) is currently offering more flexibility than any other GPU providers. (since we are working for free)

With that said, the [dataset](https://www.kaggle.com/datasets/shahzaibahmad05/logic-gates-data) is also uploaded to Kaggle. This will make our work significantly easier long-term.


### Dataset Collection & Annotation

The dataset consists of publicily available logic circuit images and some other datasets that had an MIT License and no requirements for citations, so it is legal.

For annotation, we have used [X-AnyLabelling](https://github.com/cvhub520/x-anylabeling) which is a free and open-source tool. Consider infering information about the dataset from `model/train/data/config.yaml`.

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

According to the confusion matrix bellow, the OR, NOR, XOR, XNOR (OR family) gates are continuously being missed by the model as background. We might want to work to fix this later on if we go with doing a dataset remake.

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

The raw image is made to go through these sub-modules where we extract the details of the logic circuit.


### Image Processing

`binarize()` - Removes rgb channels from the image, now we have a binary image with just two colors, 0 and 255. The default threshold is currently set to 127.

`bridge_gaps()` - Fills any gaps in between wires in the image. Heals wires that previous image processing might have broken. 

`skeletonize()` - Narrows the lines in the image. This significantly improves performance later on.

`color_boxes()` - Fill the gates bounding boxes as defined by the model's prediction with some color to make them invisible against wires.


### Wire Detection

`detect_wires()` - The function `color_boxes()` allows us to produce an image where only points that belong to wires remain which can be grouped together as open contours to form wires.

`generate()` - Uses the contours (lists of points) to generate wires and add it to the results. Uses a control snapping_range to determine at runtime if the wire should attach to a gate based on it's perpendicular distance to the gate's input/output side.


### Output Conversion

`remove_entries_from_gates()` - Incompatible entries such as Width and Height are removed from the json. These have to be managed by the circuit simulator at runtime.

`clear_wire_points()` - Wait, really?


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


## What to do Now?

The last step we did in [Developer Setup](#developer-setup) gave us a `circuit.json` file in a format that allows simulation of the circuit. This file is currently directly plug-able into [IRis](https://github.com/d-khalid/IRis) to generate a simulation. Just setup the app, load the file into it, and see the magic.

We are also working on making multiple converters for this format so it can be loaded into [Proteus](), [Logisim]() and other circuit simulation software.
