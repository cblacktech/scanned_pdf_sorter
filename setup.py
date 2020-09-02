from os import path
from setuptools import setup, find_packages

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='scanned-pdf-sorter',
    version='0.4.8dev',
    packages=find_packages(
        include=[
            'scanned_pdf_sorter'
        ],
        exclude=[
            'wintools'
        ]
    ),
    url='https://gitlab.com/cblacktech/scanned_pdf_sorter',
    license='',
    author='Caleb Black',
    author_email='cblacktech@gmail.com',
    description='Extracts data from the pages of a pdf file and groups the pages by the data extracted',
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
    zip_safe=False,
    entry_points={'console_scripts': [
        'pdf_sorter_app_run = scanned_pdf_sorter.pdf_sorter_gui:main'
    ]},
)
