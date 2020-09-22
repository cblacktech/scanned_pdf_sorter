# scanned\_pdf\_sorter

-   [Introduction](#introduction)
-   [Prerequisites](#prerequisites)
    -   [Programs / Libraries](#programs-libraries)
    -   [Pip Packages](#pip-packages)
-   [Installation & Running](#installation-running)
    -   [Linux](#linux)
    -   [Windows](#windows)
-   [Building](#building)
-   [Config.ini](#configini)
-   [Notes](#notes)
-   [Authors](#authors)

## Introduction

The purpose of this project is to sort and group pages of a scanned pdf
file by the selected information that was extracted from each page.

Project Links

-   [Gitlab](https://www.gitlab.com/cblacktech/scanned_pdf_sorter)
-   [GitKraken Board](https://app.gitkraken.com/glo/board/Xy8D66sO6gARqmUg)

## Prerequisites

### Programs / Libraries

-   [Poppler](https://poppler.freedesktop.org) is required for the
    reading and writing of pdf files.
    -   [Poppler](https://poppler.freedesktop.org) is included in most Linux Distributions.
    -   Poppler for Windows: [7z Archive Download](https://blog.alivate.com.au/poppler-windows/)

-   [Tesseract](https://tesseract-ocr.github.io/) is required for
    OCR functionality (Optical Character Recognition)
    -   Install [Tesseract](https://tesseract-ocr.github.io/) via your package manager
    -   Tesseract building instructions for Windows are located in the [Notes](#notes) section

### Pip Packages

-   All necessary pip packages are listed in setup.py

-   In general, here are the packages that are
    needed for this program to run
    -   matplotlib
    -   Pillow
    -   pdf2image
    -   pytesseract
    -   pyodbc


## Installation & Running

### Linux

-   Create and activate a virtual environment:
    -   `python -m venv venv`
    -   `source ./venv/bin/activate`

-   pip install via the git repo, replace `BRANCH` with the
    desired git repo branch that you want to install
    
    ```
    pip install git+https://www.gitlab.com/cblacktech/scanned_pdf_sorter@BRANCH
    ```
    
-   To run the program, run this entry_point command in the terminal

    ```
    pdf_sorter_app_run
    ```

### Windows

-   Create and navigate into a directory for this program

-   Create and activate a virtual environment:
    -   `python -m venv venv`
    -   `.\env\Scripts\activate`

-   pip install via the git repo, replace `BRANCH` with the
    desired git repo branch that you want to install (omit `@BRANCH` for default branch)
    
    ```
    pip install git+https://www.gitlab.com/cblacktech/scanned_pdf_sorter@BRANCH
    ```

-   Download `wintools.zip` from repo and move the zip file to the program directory (Do one of the following):

    -   ```
        curl -LJO https://gitlab.com/cblacktech/scanned_pdf_sorter/-/raw/BRANCH/wintools.zip
        ```
    
    -   Download the zip file from this the [repo](https://www.gitlab.com/cblacktech/scanned_pdf_sorter).
            By clicking the `wintools.zip` file in the repo, then clicking the download button.
    
-   To run the program, run this entry_point command in the terminal

    ```
    pdf_sorter_app_run
    ```

## Building

-   Follow the [Installation & Running](#installation-running) section until the pip installation part

-   Pip install the packages needed for development / building purposes

    ```
    pip install .[dev]
    ```
    
    or
    
    ```
    pip install git+https://www.gitlab.com/cblacktech/scanned_pdf_sorter@BRANCH[dev]
    ```
    
    *(where you replace `BRANCH` with the desired git repo branch that you want to install)*

-   Run pyinstaller using the spec file
    
    ```
    pyinstaller pdf_sorter_app.spec
    ```

-   The finished program will be located inside the `dist` folder
    -   Run the executable to start the program after you navigate
        into the program directory inside of `dist`
        -   Linux: `./pdf_sorter_app`
        -   Windows: `pdf_sorter_app.exe`

## Config.ini

-   `image_type` determines the image file type that is used (currently
    supports the values *png* and *jpeg*).

-   `file_initial_search_dir` determines where the pdf file selector
    will first open upo at.

-   The `CROP_BOX` stores the top-left coordinates and the bottom-right
    coordinates what the images will be cropped to.

-   **Currently all of the other options are for testing and development
    purposes (it is not recommended for any of these values to be changed
    at this time)**

## Notes

-   If you want a custom window icon, have a `.png` file in the same
    directory that you are launching your application from.

-   To reinstall poppler download it from [here](https://blog.alivate.com.au/poppler-windows/)
    and extract it into a folder called `wintools`.

-   `tesseract.exe` was build from source using the build instructions in the tesseract
    [docs](https://tesseract-ocr.github.io/tessdoc/Compiling.html#static-linking),
    and then was moved inside the `wintools` folder.

-   The `tessdata` folder contains the data for recognizing english characters and numbers,
    `eng.traindata`. The traindata was downloaded from their git
    [repo](https://github.com/tesseract-ocr/tessdata/blob/master/eng.traineddata).

-   Due to not having access to Mac hardware for testing purposes therefore, Mac
    OS is not supported.

## Authors

-   **Caleb Black** - [cblacktech](https://gitlab.com/cblacktech)
