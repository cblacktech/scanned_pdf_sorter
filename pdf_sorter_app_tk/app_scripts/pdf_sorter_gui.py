import os
import sys
import json
import shutil
import tkinter as tk
from tkinter import filedialog
from tkinter import scrolledtext
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
from send2trash import send2trash
from pdf_sorter_app_tk.app_scripts.pdf_image_viewer import PdfImageViewer
from pdf_sorter_app_tk.app_scripts.crop_box_selector import PdfCropSelector


class SorterApp:

    def __init__(self, root):
        if sys.platform.startswith('win'):
            pytesseract.pytesseract.tesseract_cmd = r'Tesseract-OCR/tesseract.exe'
            self.poppler_path = r'poppler/bin'
        elif sys.platform.startswith('linux'):
            self.poppler_path = None
            pass
        else:
            sys.exit()
        # print(os.getcwd())
        self.tab_size = 8
        self.line_string = '-' * 40
        self.root = root
        self.root.title("PDF SORTER")
        # self.root.resizable(height = 0, width = 0)
        self.root.option_add('*tearOff', False)
        self.root.minsize(width=600, height=300)

        self.root.withdraw()

        self.dark_color = '#31363b'

        self.input_file = None
        self.output_dir = None
        self.output_dict = {}
        self.crop_box = {'start': {}, 'end': {}}

        # building menu
        self.menuBar = tk.Menu(self.root)
        self.root.config(menu=self.menuBar)
        self.runMenu = tk.Menu(self.menuBar, tearoff=False)
        # self.fileMenu.add_command(label="Check", command=self.check_sorter)
        # self.fileMenu.add_command(label="Clear", command=self.clear_term)
        self.runMenu.add_command(label="Splitter", command=self.run_splitter)
        self.runMenu.add_command(label='Crop Selector', command=lambda: self.run_crop_selector(size_divisor=3))
        self.runMenu.add_command(label='Cropping', command=self.run_cropping)
        self.runMenu.add_command(label='Crop Viewer', command=self.run_crop_viewer)
        self.runMenu.add_command(label='OCR', command=self.run_ocr)
        self.runMenu.add_command(label='Main Viewer', command=self.run_main_viewer)
        self.runMenu.add_separator()
        self.runMenu.add_command(label="Quit", command=self.deactivate)
        # self.viewerMenu = tk.Menu(self.menuBar, tearoff=False)
        self.menuBar.add_cascade(label="Run", menu=self.runMenu)
        # self.menuBar.add_cascade(label="Viewer", menu=self.viewerMenu)
        self.menuBar.add_command(label="Check", command=self.run_check)
        self.menuBar.add_command(label="Clean", command=lambda: self.output_clean(self.output_dir))
        self.menuBar.add_command(label="Clear", command=self.clear_term)

        # building left frame
        self.left_frame = tk.LabelFrame(root, bg=self.dark_color)
        self.input_label = tk.Label(self.left_frame, text='Input File', bg=self.dark_color)
        self.left_spacer = tk.Label(self.left_frame, padx=8, bg=self.dark_color)
        self.input_file_btn = tk.Button(self.left_frame, text='INPUT FILE', bg=self.dark_color,
                                        command=lambda: self.select_input_file())
        self.output_dir_label = tk.Label(self.left_frame, text='Temp Out Dir', bg=self.dark_color)
        self.output_dir_btn = tk.Button(self.left_frame, text="TMP DIR", bg=self.dark_color,
                                        command=lambda: self.select_output_dir())

        # packing left frame
        self.left_frame.pack(padx=0, pady=0, side='left', fill='y')
        self.input_label.grid(row=0, column=0, sticky='w')
        self.left_spacer.grid(row=0, column=1)
        self.input_file_btn.grid(row=0, column=2, sticky='ew')

        self.output_dir_label.grid(row=1, column=0, sticky='w')
        self.output_dir_btn.grid(row=1, column=2, sticky='ew')

        # building right frame
        self.right_frame = tk.LabelFrame(root, bg=self.dark_color)
        self.terminal_output = scrolledtext.ScrolledText(self.right_frame, width=48, undo=True, bg=self.dark_color)
        self.terminal_output.configure(state='disabled')

        # packing right frame
        self.right_frame.pack(padx=0, pady=0, side='left', expand=True, fill='both')
        # self.terminal_output.grid(row=0, column=0, sticky='we')
        self.terminal_output.pack(side='left', expand=True, fill='both')

        # finds the first png file in the resources folder to use as the program icon
        icon_dir = str(os.getcwd())
        for f_name in os.listdir(icon_dir):
            if f_name.endswith('.png'):
                self.term_print('{} loaded as program icon'.format(f_name))
                self.root.iconphoto(self, tk.PhotoImage(file=icon_dir + '/' + f_name))
                break

        self.root.deiconify()

    # prints text to gui text box as well as the terminal
    def term_print(self, text=''):
        if isinstance(text, str) is False:
            text = str(text)
        if text != '':
            print(text.expandtabs(self.tab_size))
            self.terminal_output.configure(state='normal')
            self.terminal_output.insert('end', '{}\n'.format(text.expandtabs(self.tab_size)))
            self.terminal_output.see('end')
            self.terminal_output.configure(state='disabled')
        self.root.update()

    def clear_term(self):
        self.terminal_output.configure(state='normal')
        self.terminal_output.delete('1.0', 'end')
        self.terminal_output.configure(state='disabled')

    def activate(self):
        self.root.mainloop()

    def deactivate(self):
        self.root.quit()

    def select_input_file(self):
        self.input_file = filedialog.askopenfile(title='Select Input PDF File', mode='r',
                                                 filetypes=[('PDF file', '*.pdf')])
        self.term_print("[+] Selected File: {}".format(self.input_file.name))

    def select_output_dir(self):
        self.output_dir = filedialog.askdirectory(title='Select Output Directory')
        self.output_dir += '/pdf_sorter_out'
        self.term_print("[+] Selected Directory: {}".format(self.output_dir))

    def run_check(self):
        if self.input_file is not None and self.output_dir is not None:
            self.term_print("[+] Check successful")
            try:
                self.term_print("\t{}".format(self.input_file.name))
                self.term_print("\t{}".format(self.output_dir))
            except Exception as e:
                pass
            return True
        else:
            self.term_print("[-] Check failed")
            try:
                self.term_print("\tfile: {}".format(self.input_file.name))
                self.term_print("\tdir: {}".format(self.output_dir))
            except Exception as e:
                pass
            return False

    def run_ocr(self):
        if self.run_check():
            self.term_print("[+] Starting sorter")
            tmp_dir = self.create_output_dir(self.output_dir)
            self.output_dict = self.get_pdf_dict(tmp_dir)

            # with open(self.output_dir + '/dict.json', 'w') as json_file:
            #     json.dump(self.output_dict, json_file, indent=4)
            # self.term_print(f"{self.output_dir}/dict.json created")

            self.term_print("[+] Stopping sorter")
        else:
            self.term_print("[-] Unable to start sorter")

    def run_splitter(self):
        if self.run_check():
            self.term_print("[+] Starting pdf splitter")
            tmp_dir = self.create_output_dir(self.output_dir)
            self.output_clean(tmp_dir)
            self.pdf_image_splitter(self.input_file, tmp_dir)
            self.term_print("[+] Stopping pdf splitter")
        else:
            self.term_print("[-] Unable to start splitter")

    def run_crop_viewer(self):
        self.term_print(self.output_dir)
        viewer = PdfImageViewer((self.output_dir + '/crops'), only_images_boolean=True,
                                size_divisor=2)
        viewer.activate()

    def run_crop_selector(self, size_divisor=1):
        self.term_print('[+] Starting Crop Box Selector')
        crop_selector = PdfCropSelector((self.output_dir + '/images'), size_divisor=size_divisor)
        crop_selector.activate()
        self.crop_box['start']['x'] = int(crop_selector.start_x)
        self.crop_box['start']['y'] = int(crop_selector.start_y)
        self.crop_box['end']['x'] = int(crop_selector.end_x)
        self.crop_box['end']['y'] = int(crop_selector.end_y)
        self.term_print('top left ' + str(self.crop_box['start']))
        self.term_print('bottom right ' + str(self.crop_box['end']))
        del crop_selector
        self.term_print('[+] Stopping Crop Box Selector')

    def run_cropping(self):
        if self.run_check():
            self.term_print("[+] Starting image cropper")
            tmp_dir = self.create_output_dir(self.output_dir)
            for img in os.listdir(tmp_dir + '/images'):
                self.crop_image((tmp_dir + '/images/' + img), tmp_dir)
            # self.pdf_splitter(self.input_file, tmp_dir, split_boolean=False, crop_boolean=True)
            self.term_print("[+] Stopping image cropper")
        else:
            self.term_print("[-] Unable to start cropper")

    def run_main_viewer(self):
        self.term_print(self.output_dir)
        viewer = PdfImageViewer(self.output_dir, size_divisor=8)
        viewer.activate()

    # ------------------------------------------------------------------------------

    def get_pdf_dict(self, output_dir):
        # self.term_print(output_dir)
        # output_dir = self.create_new_output_dir(output_dir)
        # pdf_splitter(input_file, output_dir)
        # self.term_print(output_dir)

        # output_clean(output_dir)

        if self.run_check():
            output_dict = {}
            for image_name in os.listdir(f"{output_dir}/images"):
                image_filename = f"{output_dir}/images/{image_name}"
                crop_filename = f"{output_dir}/crops/{image_name}"
                extracted_text = self.image_extract_text(crop_filename, output_dir)
                # temp_set = set()
                temp_set = []
                if extracted_text in output_dict:
                    for item in output_dict[extracted_text]['images']:
                        # temp_set.add(item)
                        temp_set.append(item)
                    # temp_set.add(output_dict.get(output_dict[extracted_text]['pdfs']))
                    # temp_set.add(output_filename)
                    temp_set.append(image_filename)
                    output_dict[extracted_text]['images'] = temp_set
                else:
                    output_dict[extracted_text] = {}
                    # temp_set.add(output_filename)
                    temp_set.append(image_filename)
                    output_dict[extracted_text]['images'] = temp_set
                    # output_dict[extracted_text]['email'] = database.database_query(extracted_text)
        else:
            return {}

        return output_dict

    def create_output_dir(self, output_dir):
        # output_dir = output_dir + '/pdf_sorter_out'
        # self.output_clean(output_dir)
        try:
            os.mkdir(output_dir)
            # os.mkdir(output_dir + '/split')
            os.mkdir(output_dir + '/images')
            os.mkdir(output_dir + '/crops')
            os.mkdir(output_dir + '/text')
            self.term_print('output directories created')
        except Exception as e:
            self.term_print(e)
            pass
        return output_dir

    def output_clean(self, output_dir):
        try:
            send2trash(output_dir)
            # shutil.rmtree(output_dir)
            self.term_print('output_dir cleaned')
        except Exception:
            self.term_print('no output_dir to clean')
            pass

    def pdf_image_splitter(self, input_file, output_dir):
        self.create_output_dir(output_dir)
        self.term_print(input_file.name)
        self.term_print(os.path.basename(input_file.name))

        # pdf_name = os.path.basename(input_file.name).split('.')[0]
        # pdf_reader = PyPDF4.PdfFileReader(input_file)
        pdf_file = convert_from_path(input_file.name, dpi=200, poppler_path=self.poppler_path)
        self.term_print('pdf found')
        self.term_print(self.line_string)

        for num, page in enumerate(pdf_file):
            output_filename = f"{output_dir}/images/page_{num + 1}.png"
            page.save(output_filename)
            self.term_print('Created: {}'.format(output_filename.split('/')[-1]))

        self.term_print(self.line_string)

    def crop_image(self, input_file, output_dir):
        img_name = os.path.basename(input_file)
        self.term_print(f"image {img_name} found")
        file_ext = img_name.split('.')[-1]

        i = img_name.split('_')[-1].split('.')[0]
        page = Image.open(input_file)
        # page.crop(458, 724, 764, 790)
        page = page.crop((self.crop_box['start']['x'],
                          self.crop_box['start']['y'],
                          self.crop_box['end']['x'],
                          self.crop_box['end']['y']))
        page.save(f"{output_dir}/crops/page_{i}.{file_ext}")
        self.term_print(f"image page_{i}.{file_ext} saved")

    def image_extract_text(self, input_file, output_dir):
        img_name = os.path.splitext(os.path.basename(input_file))[0]
        img = Image.open(input_file)
        # self.term_print('image {}.png found'.format(img_name))
        text = pytesseract.image_to_string(img, lang='eng', config='digits')
        text_file = open(f"{output_dir}/text/{img_name}.txt", 'w')
        text_file.write(text)
        self.term_print(f"{img_name}.txt saved")
        text_file.close()
        self.term_print(f"text extracted: {text}")
        return text


if __name__ == '__main__':
    # window = tk.Tk()
    # app = SorterApp(window)
    # window.mainloop()
    app = SorterApp(tk.Tk())
    app.activate()
