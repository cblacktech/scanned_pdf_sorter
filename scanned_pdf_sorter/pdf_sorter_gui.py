import os
import sys
import json
import shutil
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import scrolledtext
from tkinter import messagebox
import configparser
import re
from zipfile import ZipFile
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
from scanned_pdf_sorter.pdf_image_viewer import PdfImageViewer
from scanned_pdf_sorter.crop_box_selector import PdfCropSelector
from scanned_pdf_sorter.pdf_image_config import default_config_create
from scanned_pdf_sorter.mssql_query import MsSqlQuery


class StdoutRedirector:
    def __init__(self, text_widget, root_widget, tab_size=4, text_color=None, secondary_output=sys.__stdout__):
        self.text_area = text_widget
        self.tab_size = tab_size
        self.root_widget = root_widget
        self.text_color = text_color
        self.secondary_output = secondary_output

    def write(self, string):
        if isinstance(string, str) is False:
            string = str(string)
        self.text_area.configure(state='normal')
        try:
            self.text_area.configure(fg=self.text_color)
        except Exception:
            self.text_area.configure(fg=None)
        self.text_area.insert('end', f"{string.expandtabs(self.tab_size)}")
        print(string.expandtabs(self.tab_size), file=self.secondary_output, end='')
        self.text_area.see('end')
        self.text_area.configure(state='disabled')
        self.root_widget.update()

    def flush(self):
        self.text_area.configure(state='normal')
        self.text_area.delete('1.0', 'end')
        self.text_area.configure(state='disabled')
        self.root_widget.update()


class SorterApp:
    """Scanned PDF Sorter App

    This program allows the user to take a pdf file and run Optical Character Recognition (OCR) on a selected region for
    each page of the pdf file. This program will then group together the pages that have the same information produced
    by the OCR scan.

    This program needs the following packages installed within a python environment for proper functionality:
        -Pillow, pdf2image, easyocr

    Warning: Currently the stacktrace for any errors that occur will only be visible via the terminal
    """

    def __init__(self, root, config_file='config.ini'):
        self.root = root
        self.tab_size = 8
        self.line_string = '-' * 40
        self.root.title("PDF SORTER")
        self.root.option_add('*tearOff', False)
        self.root.minsize(width=600, height=300)
        self.root.withdraw()

        self.input_file = None
        self.output_dir = None
        self.output_dict = {}
        self.crop_box = {'start': {}, 'end': {}}

        # building right frame
        self.right_frame = tk.LabelFrame(self.root)
        self.tab_manager = ttk.Notebook(self.right_frame)
        self.terminal_output = scrolledtext.ScrolledText(self.tab_manager, undo=True)
        self.tab_manager.add(self.terminal_output, text='Log')
        self.terminal_output.configure(state='disabled')
        # self.error_output = scrolledtext.ScrolledText(self.tab_manager, undo=True)
        # self.tab_manager.add(self.error_output, text='Error')
        # self.error_output.configure(state='disabled')

        # redirecting terminal and error output
        sys.stdout = StdoutRedirector(self.terminal_output, self.root, self.tab_size, None, sys.__stdout__)
        # sys.stderr = StdoutRedirector(self.error_output, self.root, self.tab_size, 'Red', sys.__stderr__)

        # loading config file contents
        self.config = configparser.ConfigParser()
        self.config_file = config_file
        # if the config file does not exist, a new one with default values will be created
        default_config_create(self.config_file)
        self.load_box_config()
        print(f"-Loading crop box coordinates from {self.config_file}")

        # test_database = MsSqlQuery(driver=self.config.get('SQL_SERVER', 'driver'),
        #                            server_ip=self.config.get('SQL_SERVER', 'server_ip'),
        #                            database_name=self.config.get('SQL_SERVER', 'database'),
        #                            table_name=self.config.get('SQL_SERVER', 'table'),
        #                            id_column=self.config.get('SQL_SERVER', 'id_column'),
        #                            email_column=self.config.get('SQL_SERVER', 'email_column'),
        #                            sql_login=self.config.getboolean('SQL_SERVER', 'sql_login'),
        #                            username=self.config.get('SQL_SERVER', 'username'),
        #                            password=self.config.get('SQL_SERVER', 'password'))

        # building menu
        self.menuBar = tk.Menu(self.root)
        self.root.config(menu=self.menuBar)

        self.runMenu = tk.Menu(self.menuBar, tearoff=False)
        self.runMenu.add_command(label="Quick", command=lambda: [self.load_config(), self.run_quick()])
        self.runMenu.add_command(label="Clean", command=lambda: self.output_clean(confirmation_box=True))
        self.runMenu.add_separator()
        self.runMenu.add_command(label="Splitter", command=lambda: [self.load_config(), self.run_splitter()])
        self.runMenu.add_command(label='Crop Images', command=lambda: [self.load_config(), self.run_cropping()])
        self.runMenu.add_command(label='OCR', command=lambda: [self.load_config(), self.run_ocr()])
        self.runMenu.add_command(label='Merge', command=lambda: [self.load_config(), self.run_merge()])
        self.runMenu.add_separator()
        self.runMenu.add_command(label='JSON', command=lambda: self.save_pdf_dict())
        self.runMenu.add_separator()
        self.runMenu.add_command(label="Quit", command=lambda: self.deactivate(confirmation_box=True))

        self.viewMenu = tk.Menu(self.menuBar, tearoff=False)
        self.viewMenu.add_command(label='Crop Selector', command=lambda: [self.load_config(), self.run_crop_selector()])
        self.viewMenu.add_command(label='Crop Viewer', command=lambda: [self.load_config(), self.run_crop_viewer()])
        self.viewMenu.add_command(label='Image+Text Viewer', command=lambda: self.run_main_viewer())

        self.menuBar.add_cascade(label="Run", menu=self.runMenu)
        self.menuBar.add_cascade(label="Viewers", menu=self.viewMenu)
        self.menuBar.add_command(label="Check", command=self.run_check)
        self.menuBar.add_command(label="Clear", command=self.clear_term)

        # building left frame
        self.left_frame = tk.LabelFrame(self.root)
        self.input_label = tk.Label(self.left_frame, text='Input File')
        self.left_spacer = tk.Label(self.left_frame, padx=8)
        self.input_file_btn = tk.Button(self.left_frame, text='INPUT FILE', command=self.select_input_file)
        self.output_dir = f"{os.getcwd()}/pdf_sorter_out"
        print(f"-Selected Directory: {self.output_dir}")

        # packing left frame
        self.left_frame.pack(padx=0, pady=0, side='left', fill='y')
        self.input_label.grid(row=0, column=0, sticky='w')
        self.left_spacer.grid(row=0, column=1)
        self.input_file_btn.grid(row=0, column=2, sticky='ew')

        # packing right frame
        self.right_frame.pack(padx=0, pady=0, side='left', expand=True, fill='both')
        self.tab_manager.pack(side='left', expand=True, fill='both')

        # finds a png file and uses it as the program icon
        for f_name in os.listdir(os.getcwd()):
            if f_name.endswith('.png'):
                print(f"-{f_name} loaded as program icon")
                self.root.iconphoto(self, tk.PhotoImage(file=f"{os.getcwd()}/{f_name}"))
                break

        if sys.platform.startswith('win'):
            if os.path.isdir('wintools') is False:
                with ZipFile('wintools.zip', 'r') as zipfile:
                    zipfile.extractall()
            if os.path.isfile('wintools.zip') and os.path.isdir('wintools'):
                shutil.rmtree('wintools')
                with ZipFile('wintools.zip', 'r') as zipfile:
                    zipfile.extractall()
            self.poppler_path = r'wintools/poppler/bin'
            pytesseract.pytesseract.tesseract_cmd = r'wintools/tesseract.exe'
        elif sys.platform.startswith('linux'):
            self.poppler_path = None
        else:
            sys.exit()

        self.root.protocol('WM_DELETE_WINDOW', lambda: self.deactivate(confirmation_box=True))
        self.root.deiconify()

    def load_config(self):
        self.config.read(self.config_file)

    def write_config(self):
        with open(f"{self.config_file}", 'w') as config_file:
            self.config.write(config_file)

    def load_box_config(self):
        if self.config.has_section('CROP_BOX'):
            self.load_config()
            self.crop_box['start']['x'] = self.config.getint('CROP_BOX', 'start_x')
            self.crop_box['start']['y'] = self.config.getint('CROP_BOX', 'start_y')
            self.crop_box['end']['x'] = self.config.getint('CROP_BOX', 'end_x')
            self.crop_box['end']['y'] = self.config.getint('CROP_BOX', 'end_y')
        else:
            print(f"-Unable to load crop box coordinates {self.config_file}")

    def clear_term(self):
        """deletes all text from the text box"""
        self.terminal_output.configure(state='normal')
        self.terminal_output.delete('1.0', 'end')
        self.terminal_output.configure(state='disabled')

    def activate(self):
        """Starts the mainloop for the tk main window"""
        self.root.mainloop()

    def deactivate(self, confirmation_box=False):
        """Destroys the tk main window"""
        if confirmation_box:
            quit_message = messagebox.askquestion('Exit Application',
                                                  'Are you sure that you want to quit this application?',
                                                  icon='warning')
            if quit_message == 'yes':
                self.root.withdraw()
                self.root.quit()
                sys.exit()
        else:
            self.root.withdraw()
            self.root.quit()
            sys.exit()

    def select_input_file(self):
        """Opens a file selection tkinter window for the user to select a pdf file"""
        self.input_file = filedialog.askopenfile(initialdir=self.config.get('SETTINGS', 'file_initial_search_dir',
                                                                            fallback=''),
                                                 title='Select Input PDF File', mode='r',
                                                 filetypes=[('PDF file', '*.pdf')])
        if self.input_file:
            print(f"-Selected File: {self.input_file.name}")
        else:
            print("-Selected File: no pdf file selected")

    def select_output_dir(self):
        """Opens a folder selection tkinter window for the user to select the location of the files that are produced
        by this program"""
        self.output_dir = filedialog.askdirectory(title='Select Output Directory')
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
            self.run_merge()
            print("-Stopping quick")
        else:
            print("-Unable to run quick")

    def run_ocr(self):
        if self.run_check():
            print("-Starting OCR")
            self.create_output_dir()

            crop_list = os.listdir(f"{self.output_dir}/crops")
            crop_list.sort(key=lambda x: x.split('-')[-1].split('.')[0])
            for index, image_file in enumerate(crop_list):
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
        crop_selector = PdfCropSelector((self.output_dir + '/images'),
                                        size_divisor=self.config.getint('SETTINGS', 'crop_select_divisor', fallback=3),
                                        box_coords=[self.config.getint('CROP_BOX', 'start_x'),
                                                    self.config.getint('CROP_BOX', 'start_y'),
                                                    self.config.getint('CROP_BOX', 'end_x'),
                                                    self.config.getint('CROP_BOX', 'end_y')])
        crop_selector.activate()

        try:
            self.config.add_section('CROP_BOX')
        except configparser.DuplicateSectionError:
            pass
        self.config.set('CROP_BOX', 'start_x', str(crop_selector.start_x))
        self.config.set('CROP_BOX', 'start_y', str(crop_selector.start_y))
        self.config.set('CROP_BOX', 'end_x', str(crop_selector.end_x))
        self.config.set('CROP_BOX', 'end_y', str(crop_selector.end_y))
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

    def run_crop_viewer(self):
        """Opens a tkinter window to check and see if the crop box selection is what is desired"""
        viewer = PdfImageViewer((self.output_dir + '/crops'), only_images_boolean=True,
                                size_divisor=self.config.getint('SETTINGS', 'crop_display_divisor', fallback=2))
        viewer.activate()

    def run_main_viewer(self):
        """Displays the extracted images from the pdf as well as the information that was extracted from the OCR scan"""
        print("-Starting main viewer")
        viewer = PdfImageViewer(self.output_dir,
                                size_divisor=self.config.getint('SETTINGS', 'main_display_divisor', fallback=8))
        viewer.activate()
        print("-Stopping main viewer")

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
            clean_message = messagebox.askquestion('Clean TEMP Folder',
                                                   'Are you sure you want to clean the TEMP Folder?',
                                                   icon='warning')
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


def main(config_file='config.ini'):
    app = SorterApp(tk.Tk(), config_file)
    app.activate()


if __name__ == '__main__':
    main(config_file='config.ini')
