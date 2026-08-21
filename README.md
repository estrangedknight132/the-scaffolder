# The Scaffolder

A simple CLI tool I built to instantly set up project workspaces, make directories, handle templates, spin up virtual environments, install dependencies, and init Git all in one go.

## Features

* **Interactive prompts** using `questionary` so you don't have to pass a million arguments.
* **JSON templates** so folder and file structures are totally customizable.
* **Auto-venv** that provisions a Python virtual environment automatically.
* **Auto-install** that looks for a `requirements.txt` and runs pip install for you.
* **Git integration** that runs init, stages files, and makes an initial commit out of the box.
* **Optional MIT license** generation.

## Installation

Install it straight from GitHub via pip:

```
pip install "git+https://github.com/estrangedknight132/the-scaffolder.git"
```
Or clone it locally and install it in editable mode:
```
git clone [https://github.com/estrangedknight132/the-scaffolder.git](https://github.com/estrangedknight132/the-scaffolder.git)
cd the-scaffolder
pip install -e .
```
## Usage

Just open your terminal and run:
```
scaffold
```
Follow the prompts to name your project, pick a path, choose a template type, and you're good to go.
