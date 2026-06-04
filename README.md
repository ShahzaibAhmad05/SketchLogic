# Image to Simulation Converter for Basic Logic Circuits

A sketch to simulation converter for logic circuits built through a lightweight and portable YOLO model and connection analysis algorithms.

It takes scanned jpg images of one (or more) Handdrawn circuits on a plain paper as input.


---


## ML Model for Detecting Logic Gates

The scripts in `models/` can be used to train a computer vision model that is capable of detecting 7 basic logic gates (AND, OR, NAND, NOR, NOT, XOR, XNOR) and their orientation in an image. (using OBB)


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
