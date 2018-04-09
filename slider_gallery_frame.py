import tkinter as tk

class SliderGalleryFrame(tk.Frame):
    def __init__(self, root, imagesList, final_img_size):
        super(SliderGalleryFrame, self).__init__(root)
        self.master.minsize(width=100, height=100)
        self.master.config()

        self.master.bind('<Left>', self.left_key)
        self.master.bind('<Right>', self.right_key)

        self.main_frame = tk.Frame()
        self.main_frame.pack(fill='both', expand=True)

        self.imagesList = imagesList

        self.panel = tk.Label(root, image=self.imagesList[0])
        self.panel.pack(side="bottom", fill="both", expand="yes")

        self.var = tk.IntVar()
        self.scale = tk.Scale(root, from_=0, to=len(imagesList) - 1, variable=self.var, orient=tk.HORIZONTAL,
                         command=self.sel, width=20, length=final_img_size)
        self.scale.pack(anchor=tk.N)

        self.pack()

    def left_key(self, event):
        self.scale.set(self.scale.get() - 1)

    def right_key(self, event):
        self.scale.set(self.scale.get() + 1)

    def sel(self, event):
        self.panel.config(image=self.imagesList[int(event)])