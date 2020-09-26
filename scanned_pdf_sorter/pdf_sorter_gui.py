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
from pathlib import Path
from scanned_pdf_sorter.pdf_sorter_tools import SorterTools
from scanned_pdf_sorter.pdf_image_viewer import PdfImageViewer
from scanned_pdf_sorter.crop_box_selector import PdfCropSelector
from scanned_pdf_sorter.config_editor import ConfigEditor


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


class SorterApp(SorterTools):
    """Scanned PDF Sorter App

    This program allows the user to take a pdf file and run Optical Character Recognition (OCR) on a selected region for
    each page of the pdf file. This program will then group together the pages that have the same information produced
    by the OCR scan.

    Warning: Currently the stacktrace for any errors that occur will only be visible via the terminal
    """

    def __init__(self, root, config_file='config.ini'):
        super().__init__()
        self.root = root
        self.root.title("PDF SORTER")
        self.root.option_add('*tearOff', False)
        self.root.minsize(width=600, height=300)
        self.root.withdraw()

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

        self.optionMenu = tk.Menu(self.menuBar, tearoff=False)
        self.optionMenu.add_command(label='Settings', command=lambda: self.run_config_editor(section='SETTINGS'))
        self.optionMenu.add_command(label='Crop Box', command=lambda: self.run_config_editor(section='CROP_BOX'))
        self.optionMenu.add_command(label='SQL Server', command=lambda: self.run_config_editor(section='SQL_SERVER'))

        self.menuBar.add_cascade(label="Run", menu=self.runMenu)
        self.menuBar.add_cascade(label="Viewers", menu=self.viewMenu)
        self.menuBar.add_cascade(label="Options", menu=self.optionMenu)
        self.menuBar.add_command(label="Check", command=self.run_check)
        self.menuBar.add_command(label="Clear", command=self.clear_term)

        # building left frame
        self.left_frame = tk.LabelFrame(self.root)
        self.input_label = tk.Label(self.left_frame, text='Input File')
        self.left_spacer = tk.Label(self.left_frame, padx=8)
        self.input_file_btn = tk.Button(self.left_frame, text='INPUT FILE', command=self.select_input_file)

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

        self.root.protocol('WM_DELETE_WINDOW', lambda: self.deactivate(confirmation_box=True))
        self.root.deiconify()

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

    def run_config_editor(self, section=''):
        config_editor = ConfigEditor(config_file=self.config_file, section=section)
        config_editor.activate()
        self.write_config()
        self.load_config()

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

    def run_crop_viewer(self):
        """Opens a tkinter window to check and see if the crop box selection is what is desired"""
        viewer = PdfImageViewer((self.output_dir + '/crops'), only_images_boolean=True,
                                size_divisor=self.config.getint('SETTINGS', 'crop_display_divisor', fallback=2))
        viewer.activate()


def main(config_file='config.ini'):
    app = SorterApp(tk.Tk(), config_file)
    app.activate()


if __name__ == '__main__':
    main(config_file='config.ini')
