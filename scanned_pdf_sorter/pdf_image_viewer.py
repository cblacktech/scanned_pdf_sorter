import os
import sys
import math
import tkinter as tk
from PIL import ImageTk, Image


class PdfImageViewer:
    def __init__(self, image_dir='', size_divisor=2, only_images_boolean=False):
        self.window = tk.Toplevel()
        self.window.title("Image Viewer")
        self.window.resizable(True, True)
        self.only_images = only_images_boolean

        self.image_dir = image_dir
        self.data_dict = {}

        if os.path.isdir(image_dir):
            if self.only_images is False:
                for file in os.listdir(self.image_dir + '/images'):
                    if file.endswith(".jpg") | file.endswith(".png"):
                        index_num = int(file.split('-')[-1].split('.')[0])
                        self.data_dict[index_num] = {}
                        input_image = Image.open(os.path.join(self.image_dir + '/images', file))
                        # input_image = input_image.resize(
                        #     (math.floor(input_image.size[0] / 3), math.floor(input_image.size[1] / 3)))
                        input_image = input_image.resize(
                            (math.floor(input_image.size[0] / size_divisor), math.floor(input_image.size[1] / size_divisor)))
                        self.data_dict[index_num]['image'] = (ImageTk.PhotoImage(input_image))
                        # print(os.path.join(image_dir, file))

                for file in os.listdir(self.image_dir + '/text'):
                    if file.endswith(".txt"):
                        index_num = int(file.split('_')[-1].split('.')[0])
                        txt_file = open(os.path.join(self.image_dir + '/text', file), 'r')
                        self.data_dict[index_num]['text'] = txt_file.read()
                        # print(txt_file.read())
                        txt_file.close()

                self.text_label = tk.Label(self.window, text=self.data_dict[1]['text'])
                self.text_label.grid(row=1, column=0, columnspan=3)
            else:
                for file in os.listdir(self.image_dir):
                    if file.endswith(".jpg") | file.endswith(".png"):
                        index_num = int(file.split('-')[-1].split('.')[0])
                        self.data_dict[index_num] = {}
                        input_image = Image.open(os.path.join(self.image_dir, file))
                        # input_image = input_image.resize(
                        #     (math.floor(input_image.size[0] / 3), math.floor(input_image.size[1] / 3)))
                        input_image = input_image.resize(
                            (math.floor(input_image.size[0] / size_divisor), math.floor(input_image.size[1] / size_divisor)))
                        self.data_dict[index_num]['image'] = (ImageTk.PhotoImage(input_image))
                        # print(os.path.join(image_dir, file))
        
        self.status_label = tk.Label(self.window, text="Image 1 of {}".format(len(self.data_dict)), bd=1,
                                     relief="sunken", anchor="w")

        # print(self.image_dict[1]['image'])
        self.image_label = tk.Label(self.window, image=self.data_dict[1]['image'])

        self.image_label.grid(row=0, column=0, columnspan=3)

        self.back_btn = tk.Button(self.window, text="<<", command=self.back, state="disabled")
        self.quit_btn = tk.Button(self.window, text="Exit Program", command=lambda: self.deactivate())
        self.forward_btn = tk.Button(self.window, text=">>", command=lambda: self.forward(2))

        self.back_btn.grid(row=2, column=0)
        self.quit_btn.grid(row=2, column=1, pady=10)
        self.forward_btn.grid(row=2, column=2)
        self.status_label.grid(row=3, column=0, columnspan=3, sticky="w e")

        self.window.bind('<Left>', lambda event: [self.back, self.left_btn()])
        self.window.bind('<Right>', lambda event, n=2: [self.forward(n), self.right_btn()])
        self.window.bind('<Escape>', lambda event: [self.deactivate()])

        # self.window.mainloop()

    def activate(self):
        self.window.mainloop()

    def deactivate(self):
        self.window.quit()
        self.window.destroy()

    def forward(self, image_number):

        if image_number in self.data_dict:
            self.image_label.grid_forget()
            self.image_label = tk.Label(self.window, image=self.data_dict[image_number]['image'])
            self.forward_btn = tk.Button(self.window, text=">>", command=lambda: self.forward(image_number + 1))
            self.back_btn = tk.Button(self.window, text="<<", command=lambda: self.back(image_number - 1))

            self.window.bind('<Left>', lambda event, n=image_number - 1: [self.forward(n), self.left_btn()])
            self.window.bind('<Right>', lambda event, n=image_number + 1: [self.back(n), self.right_btn()])

            self.status_label = tk.Label(self.window, text="Image {} of {}".format(image_number, len(self.data_dict)),
                                         bd=1,
                                         relief="sunken", anchor="w")
            
            if self.only_images is False:
                # text_label.config('text') =
                self.text_label.grid_forget()
                self.text_label = tk.Label(self.window, text=self.data_dict[image_number]['text'])
                self.text_label.grid(row=1, column=0, columnspan=3)

            if image_number == len(self.data_dict):
                self.forward_btn = tk.Button(self.window, text=">>", state="disabled")
                self.window.bind('<Right>', lambda event: self.right_btn)

            self.image_label.grid(row=0, column=0, columnspan=3)
            self.back_btn.grid(row=2, column=0)
            self.forward_btn.grid(row=2, column=2)
            self.status_label.grid(row=3, column=0, columnspan=3, sticky="w e")

    def back(self, image_number):

        if image_number in self.data_dict:
            self.image_label.grid_forget()
            self.image_label = tk.Label(self.window, image=self.data_dict[image_number]['image'])
            self.forward_btn = tk.Button(self.window, text=">>", command=lambda: self.forward(image_number + 1))
            self.back_btn = tk.Button(self.window, text="<<", command=lambda: self.back(image_number - 1))

            self.window.bind('<Left>', lambda event, n=image_number - 1: [self.forward(n), self.left_btn()])
            self.window.bind('<Right>', lambda event, n=image_number + 1: [self.back(n), self.right_btn()])

            self.status_label = tk.Label(self.window, text="Image {} of {}".format(image_number, len(self.data_dict)),
                                         bd=1, relief="sunken", anchor="w")

            if self.only_images is False:
                self.text_label.grid_forget()
                self.text_label = tk.Label(self.window, text=self.data_dict[image_number]['text'])
                self.text_label.grid(row=1, column=0, columnspan=3)

            if image_number == 1:
                self.back_btn = tk.Button(self.window, text="<<", state="disabled")
                self.window.bind('<Left>', lambda event: self.left_btn())

            self.image_label.grid(row=0, column=0, columnspan=3)
            self.back_btn.grid(row=2, column=0)
            self.forward_btn.grid(row=2, column=2)
            self.status_label.grid(row=3, column=0, columnspan=3, sticky="w e")

    def left_btn(self):
        # print('left button pressed')
        print('', end='')

    def right_btn(self):
        # print('right button pressed')
        print('', end='')


if __name__ == '__main__':
    viewer = PdfImageViewer('pdf_sorter_app_tk/pdf_sorter_out')
    viewer.activate()
