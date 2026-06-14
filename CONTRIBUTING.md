# CONTRIBUTING

First of all, thank you for your interest in contributing! 

There are quite a few things to keep in mind if you are planning to contribute to this repository. Have a look into what's cooked bellow.


---


## Automatic issue Assignment

- issue assignment in this repository is automated.
- to claim an issue, comment `I want to work on this issue`.
- once assigned, you may start working on your fork.
- if you submit a PR without having the issue assigned to you, it is upto the maintainer whether to consider the PR or not.


---


## Issue/PR Templates

These keep every issue/PR in structure and serve as guidance. 
But do keep in mind that these are not hardcoded rules to blindly follow. 
It is perfectly fine to backspace the template structure and draft your issue/PR in a blank one.


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

- Run the system to convert the sketch in the sample image to a simulation:

```bash
# <input_image_path> <output_json_path>
python -m sketchlogic temp.jpg output.iris
```


---

## Code Formatting

- Follow the existing code style in the project.
- Add docstrings to functions and comments where appropriate.
- Try to not mess up indentation when making changes.


---


## Questions

Feel free to ask questions in issues or discussions. The maintainer will always reply considering the question is appropriate and valid in common sense.

## What to do with the output file?

The last step we did in [Developer Setup](#developer-setup) gave us a `circuit.iris` file in a format that allows simulation of the circuit. This file is currently directly pluggable into [IRis](https://github.com/d-khalid/IRis) to generate a simulation. Just setup the app, load the file into it, and see the magic.
