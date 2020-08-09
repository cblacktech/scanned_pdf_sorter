''''''''''''''''''
scanned_pdf_sorter
''''''''''''''''''

.. contents:: Overview
    :depth: 3

============
Introduction
============

The purpose of this project is to sort and group pages of a scanned pdf file by the selected information that was extracted from each page.

=============
Prerequisites
=============

--------------------
Programs / Libraries
--------------------

- `Poppler <https://poppler.freedesktop.org>`_ is required for the reading and writing of pdf files

------------
Pip Packages
------------

- Pillow
- pdf2image
- easyocr

-----
Linux
-----

- `Poppler <https://poppler.freedesktop.org>`_ is included in most Linux Distributions.

-------
Windows
-------

- Poppler: `7z Archive Download <https://blog.alivate.com.au/poppler-windows/>`_ *(Download the lasted archive)*

======================
Installation & Running
======================

------------------------------
Setup & Run via python scripts
------------------------------

- Download and extract project zip file
- Navigate to project directory
- Create and activate a virtual environment:
    * python -m venv venv
    * source ./venv/bin/activate
- Install nessesary packages via pip
    * ex: pip install Pillow pdf2image etc...

- To run the program run this command via the terminal:

.. code-block:: python

    python scanned_pdf_sorter/pdf_sorter_gui.py

---------------
Install via pip
---------------

- Download and extract project zip file
- Navigate to project directory
- Create and activate a virtual environment:
    * python -m venv venv
    * source ./venv/bin/activate
- Install package
    * python setup.py install

-------
Windows
-------

- Extract poppler archive to project directory
- In the config.ini file set the poppler path to the bin directory of poppler (ex: poppler_path = r'./poppler/bin')

========
Building
========

--------
setup.py
--------

- Navigate to project directory
- Install project via pip

.. code-block::

    pip install .


- How to run the program after pip install

.. code-block::

    python

    from scanned_pdf_sorter import pdf_image_config, pdf_sorter_gui

    pdf_image_config.default_config_create(filname='config.ini')

    pdf_sorter_gui.main(config_file='config.ini')


While still in the python console you may this command to remove the config file, after the gui is closed

.. code-block::

    import os; os.remove('config.ini')

-----------
PyInstaller
-----------

- Install PyInstaller

.. code-block::

    pip install pyinstaller

- PyInstaller: terminal command

.. code-block::

    pyinstaller scanned_pdf_sorter/pdf_sorter_gui.py  -n pdf_sorter_app --hidden-import PIL._tkinter_finderclear --onefile

==========
Config.ini
==========

- ``tmp_dir_select`` determines if the user want to select a custom folder for the file produced by the program

- ``image_type`` determines the image file type that is used (currently supports the values *png* and *jpeg*)

- ``file_initial_search_dir`` determines where the pdf file selector will first open upo at

- The ``CROP_BOX`` stores the top-left coordinates and the bottom-right coordinates of the crop_box for the images

- The ``poppler_path`` is for Windows users to specify the path to the binaries for poppler

- **Currently all of the other options are for testing and development purposes (it is not recommended for these other values to be changed at this time)**

=====
Notes
=====

- Complete Windows installation instructions is a work in progress
- Due to not having access to a Mac computer for testing purposes, Mac OS is not supported

=======
Authors
=======

- **Caleb Black** - `cblacktech <https://gitlab.com/cblacktech>`_
