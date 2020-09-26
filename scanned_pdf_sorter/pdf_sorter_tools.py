import os
import sys
import json
import shutil
import configparser
import re
from pathlib import Path
from zipfile import ZipFile
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
from scanned_pdf_sorter.pdf_image_config import default_config_create
from scanned_pdf_sorter.pdf_image_viewer import PdfImageViewer
from scanned_pdf_sorter.mssql_query import MsSqlQuery


class SorterTools:

    def __init__(self, config_file='config.ini'):
        self.tab_size = 8
        self.line_string = '-' * 40

        self.input_file = None
        self.output_dir = None
        self.output_dict = {}
        self.crop_box = {'start': {}, 'end': {}}

        # loading config file contents
        self.config = configparser.ConfigParser()
        self.config_file = config_file
        # if the config file does not exist, a new one with default values will be created
        default_config_create(self.config_file)
        self.load_box_config()
        print(f"-Loading crop box coordinates from {self.config_file}")

        # try:
        #     test_database = MsSqlQuery(driver=self.config.get('SQL_SERVER', 'driver'),
        #                                server_ip=self.config.get('SQL_SERVER', 'server_ip'),
        #                                database_name=self.config.get('SQL_SERVER', 'database'),
        #                                table_name=self.config.get('SQL_SERVER', 'table'),
        #                                id_column=self.config.get('SQL_SERVER', 'id_column'),
        #                                email_column=self.config.get('SQL_SERVER', 'email_column'),
        #                                sql_login=self.config.getboolean('SQL_SERVER', 'sql_login'),
        #                                username=self.config.get('SQL_SERVER', 'username'),
        #                                password=self.config.get('SQL_SERVER', 'password'))
        # except Exception as e:
        #     print(e)

        self.output_dir = f"{os.getcwd()}/pdf_sorter_out"
        print(f"-Selected Directory: {self.output_dir}")

        if sys.platform.startswith('win'):
            if os.path.isdir('wintools') is False:
                with ZipFile('wintools.zip', 'r') as zipfile:
                    zipfile.extractall()
            if os.path.isfile('wintools.zip') and os.path.isdir('wintools'):
                shutil.rmtree('wintools')
                with ZipFile('wintools.zip', 'r') as zipfile:
                    zipfile.extractall()
            for f_name in os.listdir(Path.joinpath(Path(os.getcwd()), Path('wintools'))):
                if 'poppler' in f_name:
                    self.poppler_path = Path.joinpath(Path(os.getcwd()), Path('wintools'), Path(f_name), Path('bin'))
            pytesseract.pytesseract.tesseract_cmd = r'wintools/tesseract.exe'
        elif sys.platform.startswith('linux'):
            self.poppler_path = None
        else:
            sys.exit()

    def load_config(self):
        self.config.read(self.config_file)

    def write_config(self):
        with open(f"{self.config_file}", 'w') as config_file:
            self.config.write(config_file)

    def load_box_config(self):
        self.load_config()
        if self.config.has_section('CROP_BOX'):
            self.crop_box['start']['x'] = self.config.getint('CROP_BOX', 'start_x')
            self.crop_box['start']['y'] = self.config.getint('CROP_BOX', 'start_y')
            self.crop_box['end']['x'] = self.config.getint('CROP_BOX', 'end_x')
            self.crop_box['end']['y'] = self.config.getint('CROP_BOX', 'end_y')
        else:
            print(f"-Unable to load crop box coordinates {self.config_file}")

    def select_input_file(self):
        self.input_file = Path(input('Input PDf File Name: '))
        if self.input_file:
            print(f"-Selected File: {self.input_file.name}")
        else:
            print("-Selected File: no pdf file selected")

    def select_output_dir(self):
        self.output_dir = Path(input('Select Output Directory: '))
        self.output_dir += '/pdf_sorter_out'
        print(f"-Selected Directory: {self.output_dir}")

    def run_check(self):
        """Checks to see if an input file is selected and valid"""
        print(self.line_string)
        print("-Running Check...")
        self.load_box_config()
        if self.input_file:
            print(f"-file: {self.input_file.name}")
            print(f"-dir: {self.output_dir}")
            print(f"-top left {str(self.crop_box['start'])}")
            print(f"-bottom right {str(self.crop_box['end'])}")
            print("-Check successful")
            print(self.line_string)
            return True
        else:
            print("-file: 'no pdf file selected'")
            print(f"-dir: {self.output_dir}")
            print(f"-top left {str(self.crop_box['start'])}")
            print(f"-bottom right {str(self.crop_box['end'])}")
            print("-Check failed")
            print(self.line_string)
            return False

    def run_quick(self):
        """Function to run the functions for: splitter, cropper, and ocr in quick succession"""
        if self.run_check():
            print("-Starting quick")
            self.run_splitter()
            self.run_crop_selector()
            self.run_cropping()
            self.run_ocr()
            self.run_main_viewer()
            self.run_merge()
            print("-Stopping quick")
        else:
            print("-Unable to run quick")

    def run_main_viewer(self):
        """Displays the extracted images from the pdf as well as the information that was extracted from the OCR scan"""
        print("-Starting main viewer")
        viewer = PdfImageViewer(self.output_dir,
                                size_divisor=self.config.getint('SETTINGS', 'main_display_divisor', fallback=8))
        viewer.activate()
        print("-Stopping main viewer")

    def run_ocr(self):
        if self.run_check():
            print("-Starting OCR")
            self.create_output_dir()

            crop_list = os.listdir(f"{self.output_dir}/crops")
            crop_list.sort(key=lambda x: x.split('-')[-1].split('.')[0])
            for image_file in crop_list:
                crop_filename = f"{self.output_dir}/crops/{image_file}"
                self.image_extract_text(crop_filename)

            print("-Stopping OCR")
        else:
            print("-Unable to start OCR")

    def run_merge(self):
        pdf_dict = self.get_pdf_dict()
        for num, key in enumerate(pdf_dict.keys()):
            pdf_images = pdf_dict[key]['images']
            img_list = []
            for img in pdf_images:
                img_data = Image.open(img)
                img_data = img_data.convert('RGB')
                img_list.append(img_data)
            im1 = img_list.pop(0)
            im1.save(f"{self.output_dir}/pdfs/pdf-{str(num)}.pdf", save_all=True, append_images=img_list)
            print(f"-file pdf-{str(num)}.pdf saved")

    def save_pdf_dict(self):
        if os.path.isfile(os.path.join(self.output_dir, 'pdf_dict.json')):
            shutil.rmtree(os.path.join(self.output_dir, 'pdf_dict.json'))
        self.output_dict = self.get_pdf_dict()
        with open(self.output_dir + '/pdf_dict.json', 'w') as json_file:
            json.dump(self.output_dict, json_file, indent=4)
        print(f"-{self.output_dir}/pdf_dict.json created")

    def run_splitter(self):
        if self.run_check():
            print("-Starting pdf splitter")
            self.create_output_dir()
            self.output_clean()
            self.pdf_image_splitter(self.input_file)
            print("-Stopping pdf splitter")
        else:
            print("-Unable to start splitter")

    def run_crop_selector(self):
        """Opens a tkinter window and allows the user to select which area all of the images should be cropped to"""
        print('-Starting Crop Box Selector')
        crop_selector = dict()
        crop_selector['start_x'] = input('Select start_x: ')
        crop_selector['start_y'] = input('Select start_y: ')
        crop_selector['end_x'] = input('Select end_x: ')
        crop_selector['end_y'] = input('Select end_y: ')

        try:
            self.config.add_section('CROP_BOX')
        except configparser.DuplicateSectionError:
            pass
        self.config.set('CROP_BOX', 'start_x', str(crop_selector['start_x']))
        self.config.set('CROP_BOX', 'start_y', str(crop_selector['start_y']))
        self.config.set('CROP_BOX', 'end_x', str(crop_selector['end_x']))
        self.config.set('CROP_BOX', 'end_y', str(crop_selector['end_y']))
        self.write_config()
        self.load_config()
        self.load_box_config()

        print('-top left ' + str(self.crop_box['start']))
        print('-bottom right ' + str(self.crop_box['end']))
        del crop_selector
        print('-Stopping Crop Box Selector')

    def run_cropping(self):
        """Crops all of the pdf page images and saves them"""
        if self.run_check():
            print("-Starting image cropper")
            self.create_output_dir()
            for img in os.listdir(f"{self.output_dir}/images"):
                self.crop_image(f"{self.output_dir}/images/{img}")
            print("-Stopping image cropper")
        else:
            print("-Unable to start cropper")

    def get_pdf_dict(self) -> dict:
        """Scans the folder structure and groups the pdf images by matching extracted information from the OCR scan"""
        self.create_output_dir()

        if self.run_check():
            output_dict = {}
            image_list = os.listdir(f"{self.output_dir}/images")
            image_list.sort(key=lambda x: x.split('-')[-1].split('.')[0])
            text_list = os.listdir(f"{self.output_dir}/text")
            text_list.sort(key=lambda x: x.split('-')[-1].split('.')[0])

            for image_file in image_list:
                image_filename = f"{self.output_dir}/images/{image_file}"
                image_num = image_filename.split('-')[-1].split('.')[0].zfill(
                    len(str(len(text_list))))
                with open(f"{self.output_dir}/text/{image_num}.txt") as text_file:
                    extracted_text = text_file.read()

                temp_set = []
                if extracted_text in output_dict:
                    for item in output_dict[extracted_text]['images']:
                        temp_set.append(item)
                    temp_set.append(image_filename)
                    output_dict[extracted_text]['images'] = temp_set
                else:
                    output_dict[extracted_text] = {}
                    temp_set.append(image_filename)
                    output_dict[extracted_text]['images'] = temp_set
                    # output_dict[extracted_text]['email'] = database.database_query(extracted_text)
            return output_dict
        else:
            return {'null': 'null'}

    def create_output_dir(self):
        """Creates the folder structure to hold the files that are produced by this program"""
        try:
            os.mkdir(self.output_dir)
            print(f"-{self.output_dir} created")
        except FileExistsError:
            pass
        try:
            os.mkdir(self.output_dir + '/images')
            print(f"-{self.output_dir}/images created")
        except FileExistsError:
            pass
        try:
            os.mkdir(self.output_dir + '/crops')
            print(f"-{self.output_dir}/crops created")
        except FileExistsError:
            pass
        try:
            os.mkdir(self.output_dir + '/text')
            print(f"-{self.output_dir}/text created")
        except FileExistsError:
            pass
        try:
            os.mkdir(self.output_dir + '/pdfs')
            print(f"-{self.output_dir}/pdfs created")
        except FileExistsError:
            pass

    def output_clean(self, confirmation_box=False):
        """Deletes the folder holding the files that are produced by this program"""
        if confirmation_box:
            clean_message = input('Are you sure you want to clean the TEMP Folder? (yes/no): ')
            if clean_message == 'yes':
                try:
                    shutil.rmtree(self.output_dir)
                    print(f'-{self.output_dir} has been deleted')
                except Exception:
                    print(f'-Error in cleaning {self.output_dir}')
        else:
            try:
                shutil.rmtree(self.output_dir)
                print(f'-{self.output_dir} has been deleted')
            except Exception:
                print(f'-Error in cleaning {self.output_dir}')

    def pdf_image_splitter(self, input_file):
        """Splits the pdf file into pages and saves the contents as images"""
        self.create_output_dir()
        print(f"-{input_file.name}")
        print(f"-file {os.path.basename(input_file.name)} found")

        print(f"-Extracting images from the pages of {os.path.basename(input_file.name)}...")
        pdf_file_images = convert_from_path(input_file.name, dpi=self.config.getint('SETTINGS', 'dpi', fallback=200),
                                            poppler_path=self.poppler_path, paths_only=True, fmt="png", thread_count=4,
                                            output_folder=f"{self.output_dir}/images")
        print(f"-Extracted {len(pdf_file_images)} images from {os.path.basename(input_file.name)}")

    def crop_image(self, input_file):
        """Crops the given image to the crop box that was selected"""
        img_name = os.path.basename(input_file)
        print(f"-image {img_name} found")
        file_ext = img_name.split('.')[-1]

        i = img_name.split('-')[-1].split('.')[0]
        page = Image.open(input_file)
        page = page.crop((self.crop_box['start']['x'],
                          self.crop_box['start']['y'],
                          self.crop_box['end']['x'],
                          self.crop_box['end']['y']))
        page.save(f"{self.output_dir}/crops/{i}.{file_ext}")
        print(f"-image {i}.{file_ext} saved")

    def image_extract_text(self, input_file):
        """Runs an OCR scan to extract number from the given image and saves the extracted text"""
        img_name = os.path.splitext(os.path.basename(input_file))[0]
        text_data = pytesseract.image_to_string(Image.open(input_file), lang='eng')
        text = self.replace_chars(text_data)

        with open(f"{self.output_dir}/text/{img_name}.txt", 'w') as text_file:
            if text.isdigit() is False:
                text = '0'
            text_file.write(text)
            print(f"-{img_name}.txt saved")
            print(f"-text extracted: {text}")
        return text

    def replace_chars(self, text):
        list_of_numbers = re.findall(r'\d+', text)
        result_number = ''.join(list_of_numbers)
        return result_number

