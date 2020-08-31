# scanned\_pdf\_sorter

-   [Introduction](#introduction)
-   [Prerequisites](#prerequisites)
    -   [Programs / Libraries](#programs-libraries)
    -   [Pip Packages](#pip-packages)
    -   [Linux](#linux)
    -   [Windows](#windows)
-   [Installation & Running](#installation-running)
    -   [Setup & Run via python scripts](#setup-run-via-python-scripts)
    -   [Install via pip](#install-via-pip)
    -   [Windows](#windows-1)
-   [Building](#building)
    -   [setup.py](#setuppy)
    -   [PyInstaller](#pyinstaller)
-   [Config.ini](#configini)
-   [Notes](#notes)
-   [Authors](#authors)

## Introduction

The purpose of this project is to sort and group pages of a scanned pdf
file by the selected information that was extracted from each page.

Project Links

-   https://www.gitlab.com/cblacktech/scanned_pdf_sorter

-   [GitKraken Board](https://app.gitkraken.com/glo/board/Xy8D66sO6gARqmUg)

## Prerequisites

### Programs / Libraries

-   [Poppler](https://poppler.freedesktop.org) is required for the
    reading and writing of pdf files

### Pip Packages

-   Pillow
-   pdf2image
-   easyocr
-   torch & torchvision (Run command from the [pytorch website](https://pytorch.org/))

### Linux

-   [Poppler](https://poppler.freedesktop.org) is included in most Linux Distributions.

### Windows

-   Poppler: [7z Archive Download](https://blog.alivate.com.au/poppler-windows/)
    *(Download the lasted archive)*

## Installation & Running

### Setup & Run via python scripts

-   Download and extract project zip file

-   Navigate to project directory

-   Create and activate a virtual environment:

    -   `python -m venv venv`
    
    -   `source ./venv/bin/activate`

-   Install necessary packages via pip

    -   pip install using requirements.txt or by listing all of the
        packages after `pip install`

    ```
    pip install -r requirements.txt -f https://download.pytorch.org/whl/torch_stable.html
    ```

-   To run the program run this command via the terminal

    ```
    python scanned_pdf_sorter/pdf_sorter_gui.py
    ```

### Install via pip

-   Download and extract project zip file

-   Navigate to project directory

-   Create and activate a virtual environment:

    1.   `python -m venv venv`
    
    2.   `source ./venv/bin/activate`

-   Install package
    -   `python setup.py install`

-   Run command
    -   `pdf_sorter_app_run`

### Windows

-   Extract poppler archive to project directory

-   In the config.ini file set the poppler path to the bin directory of
    poppler (ex: poppler\_path = r'./poppler/bin')

## Building

### setup.py

-   Navigate to project directory

-   Install project via pip
    -   `python setup.py install`

-   How to run the program after pip install

    1.   `python`
    
    2.   `from scanned_pdf_sorter import pdf_image_config, pdf_sorter_gui`
    
    3.   `pdf_image_config.default_config_create(filname='config.ini')`
    
    4.   `pdf_sorter_gui.main(config_file='config.ini')`


-   While still in the python console you may this command to remove the
    config file, after the gui is closed
    
    ```
    import os; os.remove('config.ini')
    ```

### PyInstaller

-   Install PyInstaller

    ```
    pip install pyinstaller
    ```

-   PyInstaller: terminal command
    
    ```
    pyinstaller scanned_pdf_sorter/pdf_sorter_gui.py  -n pdf_sorter_app --hidden-import PIL._tkinter_finderclear --onefile
    ```

## Config.ini

-   `tmp_dir_select` determines if the user want to select a custom
    folder for the file produced by the program
-   `image_type` determines the image file type that is used (currently
    supports the values *png* and *jpeg*)
-   `file_initial_search_dir` determines where the pdf file selector
    will first open upo at
-   The `CROP_BOX` stores the top-left coordinates and the bottom-right
    coordinates of the crop\_box for the images
-   The `poppler_path` is for Windows users to specify the path to the
    binaries for poppler
-   **Currently all of the other options are for testing and development
    purposes (it is not recommended for these other values to be changed
    at this time)**

## Notes

-   If you want a custom window icon, have a `.png` file in the same
    directory that you are launching your application from
-   Due to not having access to Mac hardware for testing purposes, Mac
    OS is not supported
-   ***Complete Windows installation instructions is a work in progress***

## Authors

-   **Caleb Black** - [cblacktech](https://gitlab.com/cblacktech)

