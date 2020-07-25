# scanned_pdf_sorter

The purpose of this project is to sort and group pages of a scanned pdf file by the selected information that was extracted from each page.

## Introduction

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

The following programs are needed for the scripts to run

* [Tesseract-OCR](https://github.com/tesseract-ocr/tessdoc/blob/master/Downloads.md "https://github.com/tesseract-ocr")
* [Poppler](https://poppler.freedesktop.org "https://poppler.freedesktop.org")

#### Linux

[Tesseract](https://tesseract-ocr.github.io/tessdoc/Home.html "https://tesseract-ocr.github.io") and
[Poppler](https://poppler.freedesktop.org "https://poppler.freedesktop.org")
are included in most Linux Distributions.

#### Windows

*(**WARNING**: Windows installation instructions are still a work in progress)*

* Tesseract: [Conda-Forge Download](https://anaconda.org/conda-forge/tesseract/files)

* Poppler: [Conda-Forge Download](https://anaconda.org/conda-forge/poppler/files)

### Installing

A step by step series of examples that tell you how to get a development env running

Say what the step will be

```
* Download and extract project zip file

* Navigate to project directory

* Run these commands via the terminal:

python -m venv venv

source ./venv/bin/activate

pip install Pillow, pyinstaller, pdf2image

* To run the program run this command via the terminal:

python scanned_pdf_sorter/pdf_sorter_gui.py
```

## Building

PyInstaller: terminal command

```
pyinstaller sorter_app_run.py scanned_pdf_sorter --hidden-import PIL._tkinter_finder
```

Pip setup.py: terminal command

```
python setup.py sdisk
python -m pip install dist/*
```

Example of running after pip install

```
python

from scanned_pdf_sorter import *

pdf_image_config.default_config_create()

pdf_sorter_gui.main()
```

After you are done with the program use this command to remove the config file,
while still in the python console:

```
import os; os.remove('config.ini')
exit()
```

## Config.ini file
* **tmp_dir_select** determines if the user want to select a custom folder for the file
produced by the program

* **image_type** determines the image file type that is used
(currently supports the values *png* and *jpeg*)

* **file_initial_search_dir** determines where the pdf file selector will first open upo at

* The **CROP_BOX** stores the top-left coordinates and the bottom-right coordinates
of the crop_box for the images

* The **poppler_path** and the **tesseract_cmd** are for Windows users to specify
the path to the binaries of those programs

* **Currently all of the other options are for testing and development purposes** 


## Notes

* Complete Windows installation instructions and support are not available right now
* Due to not having access to a Mac computer for testing purposes, Mac OS is not supported

## Authors

* **Caleb Black** - [cblacktech](https://gitlab.com/cblacktech)
