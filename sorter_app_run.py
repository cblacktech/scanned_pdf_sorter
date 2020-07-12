import tkinter as tk
from app_scripts.pdf_sorter_gui import SorterApp

if __name__ == '__main__':
    app = SorterApp(tk.Tk())
    app.root.mainloop()

    # crop_app = PdfCropSelector('pdf_sorter_app_tk/pdf_sorter_out/images')
    # crop_app.activate()
