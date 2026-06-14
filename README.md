# Sketch to Simulation System

A Sketch to Simulation Converter for logic circuits that uses a fine-tuned YOLO model to detect components and image analysis to make circuit connections through wires.


![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![YOLO](https://img.shields.io/badge/YOLO-00FFFF?style=for-the-badge&logo=yolo&logoColor=black)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)


---


## Current Capabilities

### Input

Handdraw a simple logic circuit on blank paper consisting of gates (AND, OR, NOT, NAND, NOR, XOR, XNOR). A few things to keep in mind when drawing a circuit on paper:

- Make sure the paper is truly blank and has no guidelines on it.
- Make sure the drawing is spacious enough. Sketches/images being too compact drop the accuracy significantly.
- Cutting/overwriting on the sketch reduces performance.
- No wires should cross-over. Wire extensions are currently not supported.

If you have ensured all of the points mentioned above, then the output should have around 90% accuracy. Slight imperfections can be dealt with by doing edits to the design in the target circuit simulation software.


### Output

The system will output the detected circuit(s) in a simulation software compatible format. Currently, only `.iris` format is supported (which is compatible with [IRis](https://github.com/d-khalid/IRis). But we plan to add support for [Logisim Evolution](https://github.com/logisim-evolution/logisim-evolution) soon.

Examples:

<img height="300" alt="sketch" src="https://github.com/user-attachments/assets/d9fcfb4a-60a5-41da-a6ab-6697400d0876" />
<img height="300" alt="simulation" src="https://github.com/user-attachments/assets/eb3b09d5-6d5f-4507-b6d4-d6940265cd4c" />

<img height="240" alt="sketch" src="https://github.com/user-attachments/assets/c9310d11-d471-4b0b-97f1-89addbb17a0b" />
<img height="240" alt="simulation" src="https://github.com/user-attachments/assets/63a9c119-e507-4737-92f2-1f0ec9370b03" />

<br />
<br />

> *Images Credit: [IRis](https://github.com/d-khalid/IRis)*


---


## Integration with any Circuit Simulation Software

This project comes with a `GPL-3.0 LICENSE`. See the [LICENSE](https://github.com/ShahzaibAhmad05/SketchLogic?tab=GPL-3.0-1-ov-file) file for more details. Following that, this system can be integrated in a circuit simulation software with just a few steps.

The whole system is defined as a module named `sketchlogic`, and can be compiled using [pyinstaller](https://github.com/pyinstaller/pyinstaller) or similar tools. The compiled version can then be shipped with the software as an optional or required feature.

The compiled size for an exe may go upto a few hundred MBs due to our usage of `ultralytics`. We are currently working to make this process easier by shifting to `onnxruntime` instead of `ultralytics` for the inference. But that will take quite a bit of time as it needs a lot of manual work which ultralytics is doing for us currently.


---


## System Workflow

### Model

Capable of detecting 7 basic logic gates (AND, OR, NAND, NOR, NOT, XOR, XNOR) and their orientation (x4 classes, totalling 28) in an image. The configuration for fine-tuning YOLO is simple and can be found in `./sketchlogic/model/train/training.py`.

The dataset used for fine-tuning was compiled using publicly available images of logic circuits. We collected a dataset of 2,500 such images, annotated it using a custom-annotation tool, involving a lot of manual work. Any further annotation is preferred to be done by `X-AnyLabelling` on dataset updates.

There is one issue here, that is the plots for the last training session have been lost. They may be added here if training is run again. The dataset can be downloaded from [here](https://drive.google.com/file/d/1H22YKo60RVP0wAn1gruZzJOcp0HdeSIo/view?usp=sharing) for anyone interested.

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


### Connector

This is responsible for wire detection, input/output pins detection, and attaching IO components (toggles, probes, etc) with wires whose one end is connected to gates. 

We start in this module by image processing using `image_handler`, applying binarization, skeletonization, gap healing, contour detection, wire generation from those contours, connecting wires with gates, and generating IO components. 

Basically, this is the core of the system. But it's accuracy relies heavily on whether the `Model` module was able to draw the bounding boxes around components properly.


### Converter

This sub-module contains logic for conversion of the results from the `Connector` into a simulatable format. It applies advanced scaling, translation and key-value conversion. This is the sub-module we work on when we want to add support for a new format.


---


## What to do with the output file?

The last step we did in [Developer Setup](#developer-setup) gave us a `circuit.iris` file in a format that allows simulation of the circuit. This file is currently directly pluggable into [IRis](https://github.com/d-khalid/IRis) to generate a simulation. Just setup the app, load the file into it, and see the magic.
