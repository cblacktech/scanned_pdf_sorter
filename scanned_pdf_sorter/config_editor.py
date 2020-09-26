import configparser
import tkinter as tk
from scanned_pdf_sorter.pdf_image_config import default_config_create


class ConfigEditor:
    def __init__(self, config_file='config.ini', section=''):
        self.window = tk.Toplevel()
        self.window.title(f"Config Editor: {section}")
        # self.window.resizable(False, False)

        self.config = configparser.ConfigParser()
        self.config_file = config_file
        default_config_create(self.config_file)
        self.load_config()
        self.section = section

        self.main_frame = tk.LabelFrame(self.window)
        self.widgets = dict()
        self.build_widgets()
        # self.window.geometry(f'{self.main_frame.width}x{}')
        self.main_frame.pack(expand=True)

        self.window.protocol('WM_DELETE_WINDOW', lambda: self.deactivate())

    def build_widgets(self):
        print(f'-Starting config editor for: {self.section}')
        if self.config.has_section(self.section):
            menuBar = tk.Menu(self.window)
            self.window.config(menu=menuBar)
            menuBar.add_command(label='Save', command=self.save_config_data)
            for index, sec in enumerate(self.config[self.section]):
                self.widgets[sec] = {}
                self.widgets[sec]['label'] = tk.Label(self.main_frame, text=sec)
                self.widgets[sec]['entry'] = tk.Entry(self.main_frame)
                self.widgets[sec]['entry'].insert(-1, self.config[self.section][sec])
                self.widgets[sec]['label'].grid(row=index, column=0, sticky='w')
                self.widgets[sec]['entry'].grid(row=index, column=1, sticky='w')
        else:
            print(f'-Unable to launch config editor for: {self.section}')
            self.deactivate()

    def save_config_data(self):
        print('-Saving config')
        for sec in self.config[self.section]:
            self.config.set(self.section, sec, self.widgets[sec]['entry'].get())
        self.reload_config()
        print('-Config saved')
        self.deactivate()

    def activate(self):
        self.window.mainloop()

    def deactivate(self):
        print(f'-Stopping config editor for: {self.section}')
        self.window.destroy()
        # self.window.update()

    def load_config(self):
        self.config.read(self.config_file)

    def write_config(self):
        with open(f"{self.config_file}", 'w') as config_file:
            self.config.write(config_file)

    def reload_config(self):
        self.write_config()
        self.load_config()


if __name__ == '__main__':
    editor = ConfigEditor(section='SETTINGS')
    editor.activate()
