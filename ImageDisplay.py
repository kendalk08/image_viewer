import tkinter as tk
from PIL import Image, ImageTk

__all__ = ["ImageDisplay"]

class ImageDisplay:
    """
    Image Display class to rotate, flip, zoom images before deploying them in your tkinter program. Supports
    tkinter.Label and tkinter.Canvas.
    """

    HORIZONTAL = "-horizontal"
    VERTICAL = "-vertical"
    CCW = "-ccw"
    CW = "-cw"

    def __init__(self, image, width, height):
        """__init__(image, width, height)

        :param image: background image widget
        :param width: base widgets width
        :param height: base widgets height
        """

        self.image = image
        self.width = width
        self.height = height
        self.load = None
        self.render = None
        self.zoom_width = None
        self.zoom_height = None
        self._width = None
        self._height = None

    def open_image(self, file="toolbar/default_img.png", preloaded=False, _zoom=False):
        """open_image(self[, file="toolbar/default_img.png"][, preloaded=False][, _zoom=False])
        Supported objects currently are label and canvas.

        :param file: the link to the file
        :param preloaded: True/False
        :param _zoom: class controlled
        :return: None
        """

        if not preloaded:
            self._load_image(file)

        if not _zoom:
            self._width, self._height = self.load.size

            if self._width < self.width and self._height < self.height:
                h = self._height
                w = self._width
            else:
                _zoom_h = round((self._height + (self.height - self._height)) / self.true_height, 2)
                _zoom_w = round((self._width + (self.width - self._width)) / self.true_width, 2)

                if _zoom_h > _zoom_w:
                    self.zoom(_zoom_w-.01)
                    return
                else:
                    self.zoom(_zoom_h-.01)
                    return
        else:
            h = self.zoom_height
            w = self.zoom_width

        self.load = self.load.resize((w, h))

        if not _zoom:
            _check = self.zoom_percentage()
            if _check > 100:
                self.zoom(1)
                return

        self.render = ImageTk.PhotoImage(self.load)

        if self.image.winfo_class() == "Label":
            self.image.configure(image=self.render)
        elif self.image.winfo_class() == "Canvas":
            self.image.delete("all")
            self._reset_widget((w-1, h-1))
            self.image.create_image(self.width / 2, self.height / 2, image=self.render, anchor=tk.CENTER)
        else:
            raise TypeError(f"TypeError: {self.image.winfo_class()} not supported!")

        self._scrollbars()
        self.image.focus()

    def _load_image(self, file):
        """_load_image(self, file)

        :param file: file location
        :return: None
        """
        self.open_file = file
        self.load = Image.open(self.open_file)
        self.true_width, self.true_height = self.load.size

    def rotate(self, direction):
        """rotate(self, direction)

        :param direction: -cw/-ccw
        :return: None
        """
        if not direction.startswith("-"):
            direction = "-{}".format(direction)

        if direction == self.CW:
            self.load = self.load.rotate(-90, Image.NEAREST, expand=1)
        elif direction == self.CCW:
            self.load = self.load.rotate(90, Image.NEAREST, expand=1)
        else:
            raise TypeError("Wrong direction input")

        self.open_image(preloaded=True)

    def flip(self, f_direction):
        """flip(self, f_direction)

        :param f_direction: -horizontal/-vertical
        :return: None
        """
        if not f_direction.startswith("-"):
            f_direction = "-{}".format(f_direction)

        if f_direction == self.HORIZONTAL:
            self.load = self.load.transpose(Image.FLIP_LEFT_RIGHT)
        elif f_direction == self.VERTICAL:
            self.load = self.load.transpose(Image.FLIP_TOP_BOTTOM)
        else:
            raise TypeError("Wrong direction input")

        self.open_image(preloaded=True)

    def zoom(self, amount):
        """zoom(self, amount)

        :param amount: zoom amount as a decimal
        :return: None
        """
        load = Image.open(self.open_file)
        _width, _height = load.size
        self.zoom_width = int(_width*amount)
        self.zoom_height = int(_height*amount)

        self.open_image(preloaded=True, _zoom=True)

    def zoom_percentage(self):
        """zoom_percentage(self)

        :return: Percentage of image Zoom
        """
        _width, _height = self.load.size
        _width_float = _width/self.true_width
        _height_float = _height/self.true_height

        if _width_float == _height_float:
            return _width_float*100
        else:
            return _height_float*100

    def _scrollbars(self):
        """_scrollbars(self)
        Adds scrollbars to canvas if needed because image is to large to fully display

        :return: None
        """
        if self.image.winfo_class() == "Canvas":
            _width, _height = self.load.size

            try:
                self.verticalScroll.pack_forget()
            except AttributeError:
                pass
            try:
                self.horizontalScroll.pack_forget()
            except AttributeError:
                pass

            if _height > self.height:
                self.verticalScroll = tk.Scrollbar(self.image, command=self.image.yview, orient=tk.VERTICAL)
                self.verticalScroll.pack(side="right", fill="y")
                self.image.config(yscrollcommand=self.verticalScroll.set, scrollregion=self.image.bbox("all"))
            else:
                self.image.config(yscrollcommand=None, scrollregion=self.image.bbox("all"))

            if _width > self.width:
                self.horizontalScroll = tk.Scrollbar(self.image, command=self.image.xview, orient=tk.HORIZONTAL)
                self.horizontalScroll.pack(side="bottom", fill="x")
                self.image.config(xscrollcommand=self.horizontalScroll.set, scrollregion=self.image.bbox("all"))
            else:
                self.image.config(xscrollcommand=None, scrollregion=self.image.bbox("all"))

    def _reset_widget(self, size):
        if size[0] >= self.width or size[1] >= self.height:
            self.image.configure(height=self.height, width=self.width)
            self.image.pack_forget()
            self.image.pack(fill="both", expand=True)
        else:
            self.image.configure(height=size[1], width=size[0])
            self.image.pack_forget()
            self.image.pack(anchor=tk.CENTER, expand=True)
