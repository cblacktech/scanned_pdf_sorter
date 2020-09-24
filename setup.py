from os import path
from setuptools import setup, find_packages

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='scanned-pdf-sorter',
    version='0.4.20dev',
    packages=find_packages(
        include=[
            'scanned_pdf_sorter'
        ],
        exclude=[
            'wintools'
        ]
    ),
    url='https://gitlab.com/cblacktech/scanned_pdf_sorter',
    author='Caleb Black',
    author_email='cblacktech@gmail.com',
    description='A program that splits and groups pages of a PDF via the data that is extracted using OCR,'
                'over a specified area.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='~=3.0',
    include_package_data=True,
    install_requires=[
        'matplotlib==3.2.2',
        'Pillow',
        'pdf2image',
        'pytesseract',
        'pyodbc',
    ],
    extras_require={
        'dev': [
            'wheel',
            'pyinstaller',
            'pylint',
            'pytest',
        ],
    },
    zip_safe=False,
    entry_points={'console_scripts': [
        'pdf_sorter_app_run = scanned_pdf_sorter.pdf_sorter_gui:main'
    ]},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows :: Windows 10",
    ],
)
