import os
import sys
import math
import tkinter as tk
from PIL import ImageTk, Image


class PdfCropSelector:
    def __init__(self, image_dir, size_divisor=1):
        self.window = tk.Toplevel()
        self.window.title("Bounding Box Selector")
        self.window.resizable(True, True)

        self.image_dir = image_dir
        self.image_dict = dict()
        self.options_dict = dict()
        self.size_divisor = size_divisor
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0
        try:
            for file in os.listdir(self.image_dir):
                if file.endswith(".jpg") | file.endswith(".png"):
                    index_num = int(file.split('-')[-1].split('.')[0])
                    self.image_dict[index_num] = dict()
                    input_image = Image.open(os.path.join(self.image_dir, file))
                    input_image = input_image.resize((math.floor(input_image.size[0] / self.size_divisor),
                                                      math.floor(input_image.size[1] / self.size_divisor)))
                    input_image = input_image.crop((0, 0, input_image.size[0],
                                                    math.floor(input_image.size[1] / self.size_divisor)))
                    self.image_dict[index_num]['image'] = (ImageTk.PhotoImage(input_image))
                    del index_num
        except FileNotFoundError:
            self.window.destroy()

        self.create_canvas(index=1)
        self.status_label = tk.Label(self.window, text="Image 1 of {}".format(len(self.image_dict)), bd=1,
                                     relief="sunken", anchor="w")

        self.back_btn = tk.Button(self.window, text="<<", command=self.back, state="disabled")
        self.quit_btn = tk.Button(self.window, text="Save Box Coordinates", command=lambda: self.deactivate())
        self.forward_btn = tk.Button(self.window, text=">>", command=lambda: self.forward(2))

        self.back_btn.grid(row=2, column=0)
        self.quit_btn.grid(row=2, column=1, pady=10)
        self.forward_btn.grid(row=2, column=2)
        self.status_label.grid(row=3, column=0, columnspan=3, sticky="w e")

        self.window.bind('<Left>', lambda event: [self.back, self.left_btn()])
        self.window.bind('<Right>', lambda event, n=2: [self.forward(n), self.right_btn()])
        self.window.bind('<Escape>', lambda event: [self.deactivate()])
        self.image_canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.image_canvas.bind("<B1-Motion>", self.on_move_press)
        self.image_canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.rect = None

    def create_canvas(self, index):
        try:
            self.image_canvas.grid_forget()
        except Exception:
            pass
        image = self.image_dict[index]['image']
        self.image_canvas = tk.Canvas(self.window, cursor='cross', height=image.height(), width=image.width())
        self.image_canvas.create_image((image.width() / 2, image.height() / 2), image=image)
        self.image_canvas.grid(row=0, column=0, columnspan=3)

    def on_button_press(self, event):
        # print("[+] Mouse click")
        # save mouse drag start position
        self.start_x = self.image_canvas.canvasx(event.x)
        self.start_y = self.image_canvas.canvasy(event.y)

        # create rectangle if not yet exist
        if not self.rect:
            self.rect = self.image_canvas.create_rectangle(self.start_x, self.start_y, 1, 1, outline='red')

    def on_move_press(self, event):
        cursor_x = self.image_canvas.canvasx(event.x)
        cursor_y = self.image_canvas.canvasy(event.y)

        # expand rectangle as you drag the mouse
        self.image_canvas.coords(self.rect, self.start_x, self.start_y, cursor_x, cursor_y)

    def on_button_release(self, event):
        # print("[+] Mouse release")
        self.end_x = self.image_canvas.canvasx(event.x)
        self.end_y = self.image_canvas.canvasy(event.y)
        print('start: ' + str(self.start_x) + ', ' + str(self.start_y))
        print('end: ' + str(self.end_x) + ', ' + str(self.end_y))
        pass

    def activate(self):
        self.window.mainloop()

    def deactivate(self):
        # try:
        self.start_x = math.floor(self.start_x * self.size_divisor)
        self.start_y = math.floor(self.start_y * self.size_divisor)
        self.end_x = math.floor(self.end_x * self.size_divisor)
        self.end_y = math.floor(self.end_y * self.size_divisor)
        # except Exception:
        #     pass
        self.window.destroy()
        self.window.quit()

    def forward(self, image_number):

        if image_number in self.image_dict:
            # self.image_canvas.grid_forget()
            # self.image_canvas = tk.Label(self.window)
            # self.image_canvas.create_image(image=self.image_dict[image_number]['image'])
            self.create_canvas(index=image_number)
            self.forward_btn = tk.Button(self.window, text=">>", command=lambda: self.forward(image_number + 1))
            self.back_btn = tk.Button(self.window, text="<<", command=lambda: self.back(image_number - 1))

            self.window.bind('<Left>', lambda event, n=image_number - 1: [self.forward(n), self.left_btn()])
            self.window.bind('<Right>', lambda event, n=image_number + 1: [self.back(n), self.right_btn()])
            self.image_canvas.bind("<ButtonPress-1>", self.on_button_press)
            self.image_canvas.bind("<B1-Motion>", self.on_move_press)
            self.image_canvas.bind("<ButtonRelease-1>", self.on_button_release)

            try:
                self.image_canvas.create_rectangle(self.start_x, self.start_y, self.end_x, self.end_y, outline='red')
            except Exception:
                pass
            self.status_label = tk.Label(self.window, text="Image {} of {}".format(image_number, len(self.image_dict)), bd=1, relief="sunken", anchor="w")

            if image_number == len(self.image_dict):
                self.forward_btn = tk.Button(self.window, text=">>", state="disabled")
                self.window.bind('<Right>', lambda event: self.right_btn)

            # self.image_label.grid(row=0, column=0, columnspan=3)
            self.back_btn.grid(row=2, column=0)
            self.forward_btn.grid(row=2, column=2)
            self.status_label.grid(row=3, column=0, columnspan=3, sticky="w e")

    def back(self, image_number):

        if image_number in self.image_dict:
            # self.image_canvas.grid_forget()
            # self.image_canvas = tk.Label(self.window)
            # self.image_canvas.create_image(image=self.image_dict[image_number]['image'])
            self.create_canvas(index=image_number)
            self.forward_btn = tk.Button(self.window, text=">>", command=lambda: self.forward(image_number + 1))
            self.back_btn = tk.Button(self.window, text="<<", command=lambda: self.back(image_number - 1))

            self.window.bind('<Left>', lambda event, n=image_number - 1: [self.forward(n), self.left_btn()])
            self.window.bind('<Right>', lambda event, n=image_number + 1: [self.back(n), self.right_btn()])
            self.image_canvas.bind("<ButtonPress-1>", self.on_button_press)
            self.image_canvas.bind("<B1-Motion>", self.on_move_press)
            self.image_canvas.bind("<ButtonRelease-1>", self.on_button_release)

            try:
                self.image_canvas.create_rectangle(self.start_x, self.start_y, self.end_x, self.end_y, outline='red')
            except Exception:
                pass

            self.status_label = tk.Label(self.window, text="Image {} of {}".format(image_number, len(self.image_dict)),
                                         bd=1, relief="sunken", anchor="w")

            if image_number == 1:
                self.back_btn = tk.Button(self.window, text="<<", state="disabled")
                self.window.bind('<Left>', lambda event: self.left_btn())

            # self.image_label.grid(row=0, column=0, columnspan=3)
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
    viewer = PdfCropSelector('pdf_sorter_out/images', size_divisor=3)
    viewer.activate()
