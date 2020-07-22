import os
import sys
import json
import shutil
import tkinter as tk
from tkinter import filedialog
from tkinter import scrolledtext
from tkinter import messagebox
import configparser
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
from scanned_pdf_sorter.pdf_image_viewer import PdfImageViewer
from scanned_pdf_sorter.crop_box_selector import PdfCropSelector
from scanned_pdf_sorter.pdf_image_config import default_config_create


class SorterApp:
    """Scanned PDF Sorter App

    This program allows the user to take a pdf file and run Optical Character Recognition (OCR) on a selected region for
    each page of the pdf file. This program will then group together the pages that have the same information produced
    by the OCR scan.

    This program needs the following packages installed within a python environment for proper functionality:
        -Pillow, pytesseract, pdf2image

    The python packages 'pytesseract' and 'pdf2image' require the installation of the programs Tesseract-OCR and Poppler
    to function properly.

    Warning: Currently the stacktrace for any errors that occur will only be visible via the terminal
    """

    def __init__(self, root, config_file='config.ini'):
        self.config = configparser.ConfigParser()
        self.config_file = config_file
        # if the config file does not exist, a new one with default values will be created
        default_config_create(self.config_file)
        self.load_config()

        if sys.platform.startswith('win'):
            pytesseract.pytesseract.tesseract_cmd = self.config.get('SETTINGS', 'tesseract_cmd',
                                                                    fallback='tesseract')
            self.poppler_path = self.config.get('SETTINGS', 'poppler_path', fallback=None)
        elif sys.platform.startswith('linux'):
            self.poppler_path = None
        else:
            sys.exit()

        self.tab_size = 8
        self.line_string = '-' * 40
        self.root = root
        self.root.title("PDF SORTER")
        self.root.option_add('*tearOff', False)
        self.root.minsize(width=600, height=300)

        self.root.withdraw()

        self.input_file = None
        self.output_dir = None
        self.output_dict = {}
        self.crop_box = {'start': {}, 'end': {}}

        # building menu
        self.menuBar = tk.Menu(self.root)
        self.root.config(menu=self.menuBar)
        self.runMenu = tk.Menu(self.menuBar, tearoff=False)
        self.runMenu.add_command(label="Splitter", command=self.run_splitter)
        self.runMenu.add_command(label='Crop Selector', command=self.run_crop_selector)
        self.runMenu.add_command(label='Crop Images', command=self.run_cropping)
        self.runMenu.add_command(label='Crop Viewer', command=self.run_crop_viewer)
        self.runMenu.add_command(label='OCR', command=self.run_ocr)
        self.runMenu.add_command(label='Image+Text Viewer', command=self.run_main_viewer)
        self.runMenu.add_separator()
        self.runMenu.add_command(label="Quit", command=lambda: self.deactivate(confirmation_box=True))
        self.menuBar.add_cascade(label="Run", menu=self.runMenu)
        self.menuBar.add_command(label="Check", command=self.run_check)
        self.menuBar.add_command(label="Clean", command=lambda: self.output_clean(confirmation_box=True))
        self.menuBar.add_command(label="Clear", command=self.clear_term)

        # building right frame
        self.right_frame = tk.LabelFrame(root)
        self.terminal_output = scrolledtext.ScrolledText(self.right_frame, width=48, undo=True)
        self.terminal_output.configure(state='disabled')

        # building left frame
        self.left_frame = tk.LabelFrame(root)
        self.input_label = tk.Label(self.left_frame, text='Input File')
        self.left_spacer = tk.Label(self.left_frame, padx=8)
        self.input_file_btn = tk.Button(self.left_frame, text='INPUT FILE', command=self.select_input_file)
        if self.config.getboolean('SETTINGS', 'tmp_dir_select'):
            self.output_dir_label = tk.Label(self.left_frame, text='Temp Out Dir')
            self.output_dir_btn = tk.Button(self.left_frame, text="TMP DIR", command=self.select_output_dir)
            self.output_dir_label.grid(row=1, column=0, sticky='w')
            self.output_dir_btn.grid(row=1, column=2, sticky='ew')
        else:
            self.output_dir = f"{os.getcwd()}/pdf_sorter_out"
            self.term_print("Selected Directory: {}".format(self.output_dir))

        # packing left frame
        self.left_frame.pack(padx=0, pady=0, side='left', fill='y')
        self.input_label.grid(row=0, column=0, sticky='w')
        self.left_spacer.grid(row=0, column=1)
        self.input_file_btn.grid(row=0, column=2, sticky='ew')

        # packing right frame
        self.right_frame.pack(padx=0, pady=0, side='left', expand=True, fill='both')
        self.terminal_output.pack(side='left', expand=True, fill='both')

        # finds a png file and uses it as the program icon
        for f_name in os.listdir(os.getcwd()):
            if f_name.endswith('.png'):
                self.term_print('{} loaded as program icon'.format(f_name))
                self.root.iconphoto(self, tk.PhotoImage(file=f"{os.getcwd()}/{f_name}"))
                break
        self.load_box_config()
        self.root.deiconify()

    def load_config(self):
        self.config.read(self.config_file)

    def write_config(self):
        with open(f"{self.config_file}", 'w') as config_file:
            self.config.write(config_file)

    def load_box_config(self):
        if self.config.has_section('CROP_BOX'):
            self.load_config()
            self.term_print(f"Loading crop box coordinates from {self.config_file}")
            self.crop_box['start']['x'] = self.config.getint('CROP_BOX', 'start_x')
            self.crop_box['start']['y'] = self.config.getint('CROP_BOX', 'start_y')
            self.crop_box['end']['x'] = self.config.getint('CROP_BOX', 'end_x')
            self.crop_box['end']['y'] = self.config.getint('CROP_BOX', 'end_y')
        else:
            self.term_print(f"Unable to load crop box coordinates {self.config_file}")

    def term_print(self, text=''):
        """prints the given text to gui text box as well as the terminal"""
        if isinstance(text, str) is False:
            text = str(text)
        if text != '':
            print('-' + text.expandtabs(self.tab_size))
            self.terminal_output.configure(state='normal')
            self.terminal_output.insert('end', f"{'-' + text.expandtabs(self.tab_size)}\n")
            self.terminal_output.see('end')
            self.terminal_output.configure(state='disabled')
        self.root.update()

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
            quit_message = tk.messagebox.askquestion('Exit Application',
                                                     'Are you sure that you want to quit this application?',
                                                     icon='warning')
            if quit_message == 'yes':
                self.root.quit()
        else:
            self.root.quit()

    def select_input_file(self):
        """Opens a file selection tkinter window for the user to select a pdf file"""
        self.input_file = filedialog.askopenfile(initialdir=self.config.get('SETTINGS', 'file_initial_search_dir',
                                                                            fallback=''),
                                                 title='Select Input PDF File', mode='r',
                                                 filetypes=[('PDF file', '*.pdf')])
        self.term_print("Selected File: {}".format(self.input_file.name))

    def select_output_dir(self):
        """Opens a folder selection tkinter window for the user to select the location of the files that are produced
        by this program"""
        self.output_dir = filedialog.askdirectory(title='Select Output Directory')
        self.output_dir += '/pdf_sorter_out'
        self.term_print("Selected Directory: {}".format(self.output_dir))

    def run_check(self):
        """Checks to see if an input file is selected and valid"""
        self.term_print("Running Check...")
        self.term_print(self.line_string)
        self.load_box_config()
        if self.input_file is not None and self.input_file.name:
            self.term_print("Check successful")
            self.term_print(f"{self.input_file.name}")
            self.term_print(f"{self.output_dir}")
            self.term_print('top left ' + str(self.crop_box['start']))
            self.term_print('bottom right ' + str(self.crop_box['end']))
            self.term_print(self.line_string)
            return True
        else:
            self.term_print("Check failed")
            self.term_print("file: 'no pdf file selected'")
            self.term_print(f"dir: {self.output_dir}")
            self.term_print('top left ' + str(self.crop_box['start']))
            self.term_print('bottom right ' + str(self.crop_box['end']))
            self.term_print(self.line_string)
            return False

    def run_ocr(self):
        if self.run_check():
            self.term_print("Starting OCR")
            self.create_output_dir()
            self.output_dict = self.get_pdf_dict()

            if self.config.getboolean('SETTINGS', 'create_dict_json', fallback=False):
                with open(self.output_dir + '/dict.json', 'w') as json_file:
                    json.dump(self.output_dict, json_file, indent=4)
                self.term_print(f"{self.output_dir}/dict.json created")

            self.term_print("Stopping OCR")
        else:
            self.term_print("Unable to start OCR")

    def run_splitter(self):
        if self.run_check():
            self.term_print("Starting pdf splitter")
            self.create_output_dir()
            self.output_clean()
            self.pdf_image_splitter(self.input_file)
            self.term_print("Stopping pdf splitter")
        else:
            self.term_print("Unable to start splitter")

    def run_crop_selector(self):
        """Opens a tkinter window and allows the user to select which area all of the images should be cropped to"""
        self.term_print('Starting Crop Box Selector')
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

        self.term_print('top left ' + str(self.crop_box['start']))
        self.term_print('bottom right ' + str(self.crop_box['end']))
        del crop_selector
        self.term_print('Stopping Crop Box Selector')

    def run_cropping(self):
        """Crops all of the pdf page images and saves them"""
        if self.run_check():
            self.term_print("Starting image cropper")
            self.create_output_dir()
            for img in os.listdir(f"{self.output_dir}/images"):
                self.crop_image(f"{self.output_dir}/images/{img}")
            self.term_print("Stopping image cropper")
        else:
            self.term_print("Unable to start cropper")

    def run_crop_viewer(self):
        """Opens a tkinter window to check and see if the crop box selection is what is desired"""
        self.term_print(self.output_dir)
        viewer = PdfImageViewer((self.output_dir + '/crops'), only_images_boolean=True,
                                size_divisor=self.config.getint('SETTINGS', 'crop_display_divisor', fallback=2))
        viewer.activate()

    def run_main_viewer(self):
        """Displays the extracted images from the pdf as well as the information that was extracted from the OCR scan"""
        self.term_print(self.output_dir)
        viewer = PdfImageViewer(self.output_dir,
                                size_divisor=self.config.getint('SETTINGS', 'main_display_divisor', fallback=8))
        viewer.activate()

    def get_pdf_dict(self) -> dict:
        """Scans the folder structure and groups the pdf images by matching extracted information from the OCR scan"""
        self.term_print(self.output_dir)

        if self.run_check():
            output_dict = {}
            image_list = os.listdir(f"{self.output_dir}/images")
            image_list.sort(key=lambda x: x.split('-')[-1].split('.')[0])
            crop_list = os.listdir(f"{self.output_dir}/crops")
            crop_list.sort(key=lambda x: x.split('-')[-1].split('.')[0])
            for index, image_file in enumerate(image_list):
                image_filename = f"{self.output_dir}/images/{image_file}"
                crop_filename = f"{self.output_dir}/crops/{crop_list[index - 1]}"
                extracted_text = self.image_extract_text(crop_filename)
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
        else:
            return {}

        return output_dict

    def create_output_dir(self):
        """Creates the folder structure to hold the files that are produced by this program"""
        try:
            os.mkdir(self.output_dir)
            os.mkdir(self.output_dir + '/images')
            os.mkdir(self.output_dir + '/crops')
            os.mkdir(self.output_dir + '/text')
            self.term_print('output directories created')
        except FileExistsError:
            pass

    def output_clean(self, confirmation_box=False):
        """Deletes the folder holding the files that are produced by this program"""
        if confirmation_box:
            clean_message = tk.messagebox.askquestion('Clean TEMP Folder',
                                                      'Are you sure you want to clean the TEMP Folder?',
                                                      icon='warning')
            if clean_message == 'yes':
                try:
                    shutil.rmtree(self.output_dir)
                    self.term_print(f'{self.output_dir} has been deleted')
                except Exception:
                    self.term_print(f'Error in cleaning {self.output_dir}')
        else:
            try:
                shutil.rmtree(self.output_dir)
                self.term_print(f'{self.output_dir} has been deleted')
            except Exception:
                self.term_print(f'Error in cleaning {self.output_dir}')

    def pdf_image_splitter(self, input_file):
        """Splits the pdf file into pages and saves the contents as images"""
        self.create_output_dir()
        self.term_print(input_file.name)
        self.term_print(f"file {os.path.basename(input_file.name)} found")

        self.term_print(f"Extracting images from the pages of {os.path.basename(input_file.name)}...")
        pdf_file_images = convert_from_path(input_file.name, dpi=self.config.getint('SETTINGS', 'dpi', fallback=200),
                                            poppler_path=self.poppler_path, paths_only=True, fmt="png", thread_count=4,
                                            output_folder=f"{self.output_dir}/images")
        self.term_print(f"Extracted {len(pdf_file_images)} images from {os.path.basename(input_file.name)}")

        # for num, page in enumerate(pdf_file):
        #     output_filename = f"{self.output_dir}/images/page_{num + 1}." \
        #                       f"{self.config.get('SETTINGS', 'image_type', fallback='png')}"
        #     page.save(output_filename)
        #     self.term_print(f"Created: {output_filename.split('/')[-1]}")

    def crop_image(self, input_file):
        """Crops the given image to the crop box that was selected"""
        img_name = os.path.basename(input_file)
        self.term_print(f"image {img_name} found")
        file_ext = img_name.split('.')[-1]

        i = img_name.split('-')[-1].split('.')[0]
        page = Image.open(input_file)
        page = page.crop((self.crop_box['start']['x'],
                          self.crop_box['start']['y'],
                          self.crop_box['end']['x'],
                          self.crop_box['end']['y']))
        page.save(f"{self.output_dir}/crops/{i}.{file_ext}")
        self.term_print(f"image {i}.{file_ext} saved")

    def image_extract_text(self, input_file):
        """Runs Tesseract-OCR using pytesseract to extract number from the given image and saves the extracted text"""
        img_name = os.path.splitext(os.path.basename(input_file))[0]
        img = Image.open(input_file)
        # self.term_print('image {}.png found'.format(img_name))
        text = pytesseract.image_to_string(img, lang='eng', config='digits')
        text_file = open(f"{self.output_dir}/text/{img_name}.txt", 'w')
        text_file.write(text)
        self.term_print(f"{img_name}.txt saved")
        text_file.close()
        self.term_print(f"text extracted: {text}")
        return text


def main():
    app = SorterApp(tk.Tk())
    app.activate()


if __name__ == '__main__':
    main()
