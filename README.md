# scanned_pdf_sorter

The purpose of this project is to sort and group pages of a scanned pdf file by the selected information that was extracted from each page.

## Introduction

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

* [Poppler](https://poppler.freedesktop.org "https://poppler.freedesktop.org") is required for the reading and writing of pdf files

#### Pip Packages
* Pillow
* pdf2image
* easyocr

#### Linux

* [Poppler](https://poppler.freedesktop.org "https://poppler.freedesktop.org")
is included in most Linux Distributions.

#### Windows

* Poppler: [7z Archive Download](https://blog.alivate.com.au/poppler-windows/) *(Download the lasted archive)*

### Installing

#### Install & Run Python Scripts

```
* Download and extract project zip file

* Navigate to project directory

* Run these commands via the terminal:

python -m venv venv

source ./venv/bin/activate

* install nessesary packages via pip
ex: pip install Pillow pdf2image ...

* To run the program run this command via the terminal:

python scanned_pdf_sorter/pdf_sorter_gui.py
```

#### Install via pip
```
* Download and extract project zip file

* Navigate to project directory

* Run these commands via the terminal:

python -m venv venv

source ./venv/bin/activate

python setup.py install
```

#### Windows:
```
* extract poppler archive to project directory
* In the config.ini file set the poppler path to the bin directory of poppler (ex: poppler_path = r'./poppler/bin')
```

## Building

Install PyInstaller
```
pip install pyinstaller
```

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

* The **poppler_path** is for Windows users to specify
the path to the binaries for poppler

* **Currently all of the other options are for testing and development purposes *(it is not recommend for these values to be changed)*** 


## Notes

* Complete Windows installation instructions is a work in progress
* Due to not having access to a Mac computer for testing purposes, Mac OS is not supported

## Authors

* **Caleb Black** - [cblacktech](https://gitlab.com/cblacktech)
