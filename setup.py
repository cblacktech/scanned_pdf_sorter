from setuptools import setup

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='scanned_pdf_sorter',
    version='1.0.4',
    packages=['scanned_pdf_sorter'],
    url='https://gitlab.com/cblacktech/scanned_pdf_sorter',
    license='',
    author='Caleb Black',
    author_email='cblacktech@gmail.com',
    description='Extracts data from the pages of a pdf file and groups the pages by the data extracted',
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='~=3.0',
    install_requires=[
        'Pillow',
        'pdf2image',
        'easyocr'
    ],
    zip_safe=False,
)
