import os
import sys
import threading
import time
import tkinter as tk

from ImageDisplay import ImageDisplay
from FileCrawler import FileCrawler
from ButtonManager import ButtonManager

from PIL import ImageTk, Image
from send2trash import send2trash

__all__ = ["ImageBrowser"]

class ImageBrowser:

    def __init__(self, passed=None):
        """ImageBrowser([passed=None])

        :param passed: Default=None, filepath that runs the program. Default runs os.getcwd()
        """

        self.open_file = ""
        self.entered = False
        self.file_list = []
        self.rotate_qty = 0

        # ------Program Window-----#

        self.window = tk.Tk()
        self.window.title("Image Viewer")

        self.dimY = self.window.winfo_screenheight()
        self.dimX = self.window.winfo_screenwidth()

        self._resize_program()

        image = tk.PhotoImage(file="toolbar/iv_logo.png")
        self.window.iconphoto(False, image)

        self.window.geometry(f"{self.programX}x{self.programY}+100+0")
        self.window.resizable(width=False, height=False)
        self.window.config(background="gray75")

        self.window.bind("<Left>", lambda x: self._back_image())
        self.window.bind("<Right>", lambda x: self._next_image())
        self.window.bind("<BackSpace>", lambda x: self._chg_dir)

        self.file_bar_frame = tk.Frame(self.window, height=35, padx=5, background="gray30")
        self.file_bar_frame.pack(side="top", fill="x")
        self.file_bar_frame.pack_propagate(0)

        load = Image.open("toolbar/up_arrow.png")
        load = load.resize((20, 20))
        self.up_render = ImageTk.PhotoImage(load)

        self.up_dir = tk.Button(self.file_bar_frame, image=self.up_render, background="gray75", borderwidth=0,
                                command=self._chg_dir)
        self.up_dir.pack(side="left")

        self.file_bar = tk.Entry(self.file_bar_frame, width=95, font=("Ariel", 12))
        self.file_bar.pack(side="left")

        self.file_bar.bind("<FocusIn>", lambda x: self.window.unbind("<BackSpace>"))
        self.file_bar.bind("<FocusOut>", lambda x: self.window.bind("<BackSpace>", self._chg_dir))

        self.go_button = tk.Button(self.file_bar_frame, text="Go!", font=("Ariel", 10), borderwidth=0, background="gray75",
                                   command=lambda: self._go_click(self.file_bar.get()), activebackground="gray45")
        self.go_button.pack(side="left")
        self.file_bar.bind("<Return>", lambda x: self.go_button.invoke())

        self.image_container_c = tk.Label(self.file_bar_frame, background="gray30", pady=5)
        self.image_container_c.pack(side="left")

        tk.Label(self.image_container_c, width=8, background="gray30").pack(side="left")

        self.image_container = tk.Label(self.image_container_c, background="gray30", pady=5)
        self.image_container.pack(side="left")

        load = Image.open("toolbar/trash.png")
        load = load.resize((25, 25))
        trash_render = ImageTk.PhotoImage(load)
        self.file_option_trash = tk.Button(self.image_container, image=trash_render, width=25, height=25,
                                           borderwidth=0, background="gray75", activebackground="gray45",
                                           command=self._del_image)
        self.file_option_trash.pack(side="left")

        load = Image.open("toolbar/flip_trans.png")
        load = load.resize((25, 25))
        f_h_render = ImageTk.PhotoImage(load)
        self.flip_horizontal = tk.Button(self.image_container, image=f_h_render, height=25, width=25, borderwidth=0,
                                         background="gray75", activebackground="gray45",
                                         command=lambda: self.ID.flip("horizontal"))
        self.flip_horizontal.pack(side="left", anchor="center")

        load = load.rotate(90, Image.NEAREST, expand=1)
        f_v_render = ImageTk.PhotoImage(load)
        self.flip_vertical = tk.Button(self.image_container, image=f_v_render, height=25, width=25, borderwidth=0,
                                       background="gray75", activebackground="gray45",
                                       command=lambda: self.ID.flip("vertical"))
        self.flip_vertical.pack(side="left", anchor="center")

        load = Image.open("toolbar/rotate_trans.png")
        load = load.resize((25, 25))
        rotate_render = ImageTk.PhotoImage(load)
        self.file_option_rotate = tk.Button(self.image_container, image=rotate_render, width=25, height=25,
                                            borderwidth=0, background="gray75", activebackground="gray45",
                                            command=lambda: self.ID.rotate("ccw"))
        self.file_option_rotate.pack(side="left")

        load = load.transpose(Image.FLIP_LEFT_RIGHT)
        rotate_r_render = ImageTk.PhotoImage(load)
        self.file_option_rotate_r = tk.Button(self.image_container, image=rotate_r_render, width=25, height=25,
                                              borderwidth=0, background="gray75", activebackground="gray45",
                                              command=lambda: self.ID.rotate("cw"))
        self.file_option_rotate_r.pack(side="left")

        tk.Label(self.image_container_c, width=8, background="gray30").pack(side="left")

        self.zoom_container = tk.Label(self.image_container_c, background="gray30")
        self.zoom_container.pack(side="left")

        self.zoom_amount = tk.Entry(self.zoom_container, width=4, font=("Ariel", 14))
        self.zoom_amount.pack(side="left")

        self.zoom_amount.bind("<FocusIn>", lambda x: self.window.unbind("<BackSpace>"))
        self.zoom_amount.bind("<FocusOut>", lambda x: self.window.bind("<BackSpace>", self._chg_dir))

        load = Image.open("toolbar/zoom_trans.png")
        load = load.resize((25, 25))
        zoom_render = ImageTk.PhotoImage(load)
        self.file_option_zoom = tk.Button(self.zoom_container, image=zoom_render, width=25, height=25,
                                          borderwidth=0, background="gray75", activebackground="gray45",
                                          command=self._zoom, justify=tk.CENTER)
        self.file_option_zoom.pack(side="left")
        self.zoom_amount.bind("<Return>", lambda x: self.file_option_zoom.invoke())

        self.slideshow_container = tk.Label(self.file_bar_frame, width=25, background="gray75")
        self.slideshow_container.pack(side="right")

        self.slideshow_play = tk.Button(self.slideshow_container, text="Start Slideshow!", font=("Ariel", 10),
                                        background="gray75", command=lambda: self._slideshow_click(self.open_file),
                                        activebackground="gray45", borderwidth=0)
        self.slideshow_play.pack()

        self.slideshow_stop = tk.Button(self.slideshow_container, text="Stop Slideshow!", font=("Ariel", 10),
                                        background="gray75", command=lambda: self._slideshow_click(self.open_file),
                                        activebackground="gray45", borderwidth=0)

        self.top_frame = tk.Frame(self.window, background="gray75")
        self.top_frame.pack(side="top")

        self.folder_frame = tk.Frame(self.top_frame, width=300, height=self.height+4, borderwidth=2, relief="flat",
                                     background="gray30")
        self.folder_frame.pack(side="left", anchor="nw")
        self.folder_frame.pack_propagate(0)

        self.folder_text = tk.Text(self.folder_frame, background="gray75", relief="flat", wrap="none")
        self.folder_text.pack(expand=True, fill="both")

        self.folder_text.tag_config("blank", background="gray30", foreground="#A4541D", justify=tk.LEFT,
                                    font=("Ariel", 12, "bold"), spacing1="4", spacing2="4", spacing3="4", lmargin1="5")

        self.folder_text.tag_config("spacer", font=("Ariel", 1), background="gray30")

        self.folder_buttons = ButtonManager(self.folder_text)

        self.folder_scroll = tk.Scrollbar(self.folder_text)
        self.folder_scroll.pack(side="right", fill="y")

        self.folder_text.config(yscrollcommand=self.folder_scroll.set)
        self.folder_scroll.config(command=self.folder_text.yview)

        self.image_frame = tk.Frame(self.top_frame, height=self.height+4, width=self.width+4, borderwidth=2, relief="flat",
                                    background="gray10")
        self.image_frame.pack(side="left", expand=True, anchor=tk.CENTER)
        self.image_frame.pack_propagate(0)

        self.image_frame.bind("<Enter>", lambda x: self.file_options_enter())
        self.image_frame.bind("<Leave>", lambda x: self.file_options_exit())

        load = Image.open("toolbar/default_img.png")
        render = ImageTk.PhotoImage(load)

        """
        self.image_label = tk.Label(self.image_frame, image=render, height=946, width=1146, anchor="center",
                                    background="gray10", borderwidth=2, relief="flat")
        self.image_label.pack(fill="both", expand=True)
        """
        self.image_canvas = tk.Canvas(self.image_frame, height=self.height, width=self.width, background="gray10", borderwidth=2,
                                      relief="flat")
        self.image_canvas.pack(anchor=tk.CENTER, fill="both")
        self.image_canvas.create_image(self.width/2, self.height/2, image=render, anchor="center")

        self.ID = ImageDisplay(self.image_canvas, self.width, self.height)

        self.text_var = tk.StringVar()
        self.text_var.set("")
        self.file_count = tk.StringVar()
        self.file_count.set("")
        self.folder_count = tk.StringVar()
        self.folder_count.set("")
        self.file_name = tk.Frame(self.window, background="gray60")
        self.file_name.pack(side="bottom", fill="x")
        self.file_size = tk.StringVar()
        self.file_size.set("  0.00 MB")

        self.file_count_disp = tk.Label(self.file_name, textvariable=self.file_count, background="gray60", padx=4,
                                        justify=tk.LEFT, anchor="w", borderwidth=2, relief="sunken")
        self.file_count_disp.pack(side="left")

        self.folder_count_disp = tk.Label(self.file_name, textvariable=self.folder_count, background="gray60", padx=4,
                                          justify=tk.LEFT, anchor="w", borderwidth=2, relief="sunken")
        self.folder_count_disp.pack(side="left")

        self.file_link = tk.Label(self.file_name, textvariable=self.text_var, background="gray60", padx=4,
                                  justify=tk.LEFT, anchor="w", borderwidth=2, relief="sunken")
        self.file_link.pack(side="left", expand=True, fill="both")

        self.file_size_disp = tk.Label(self.file_name, textvariable=self.file_size, background="gray60", padx=4,
                                       justify=tk.LEFT, anchor="w", borderwidth=2, relief="sunken")
        self.file_size_disp.pack(side="right")

        if passed is None:
            self.link = os.getcwd()
            self.crawler = FileCrawler()
        else:
            self.link = passed
            self.crawler = FileCrawler(self.link)

        self.open_folder(self.link)
        self.file_bar.delete(0, tk.END)
        self.file_bar.insert(tk.INSERT, self.link)

        self.window.mainloop()

    def file_options_enter(self):
        # self.window.bind("<MouseWheel>", self._scroll)
        # self.window.bind("<Button-4>", self._scroll)
        # self.window.bind("<Button-5>", self._scroll)
        self.entered = True

        load = Image.open("toolbar/file_options.png")
        load = load.resize((120, 50))
        self.options_render = ImageTk.PhotoImage(load)
        self.file_option_bar = tk.Label(self.image_frame, image=self.options_render, width=120, height=50)
        self.file_option_bar.place(x=(self.image_frame.winfo_width()-120)/2, y=850)

        load = Image.open("toolbar/back.png")
        self.back_render = ImageTk.PhotoImage(load)
        self.file_option_back = tk.Button(self.file_option_bar, image=self.back_render, width=50, height=50,
                                          borderwidth=0, background="white", command=self._back_image)
        self.file_option_back.place(x=9, y=0)

        load = Image.open("toolbar/next.png")
        self.next_render = ImageTk.PhotoImage(load)
        self.file_option_next = tk.Button(self.file_option_bar, image=self.next_render, width=50, height=50,
                                          borderwidth=0, background="white", command=self._next_image)
        self.file_option_next.place(x=59, y=0)

    def _resize_program(self):
        self.width = self.dimX - 774
        self.height = self.dimY - 134 - 25

        self.programX = self.dimX - 470
        self.programY = self.dimY - 72 - 25

    def _zoom(self):
        amount = int(self.zoom_amount.get())
        self.ID.zoom(amount/100)

    def _scroll(self, event):
        count = 0
        if event.num == 5 or event.delta < 0:
            count += 1
        else:
            count -= 1

        if count > 0:
            self._next_image()
        else:
            self._back_image()

    def _chg_dir(self):
        direct = os.path.split(self.file_bar.get())[0]
        self.file_bar.delete(0, tk.END)
        self.file_bar.insert(tk.INSERT, direct)
        self.go_button.invoke()
        self.open_image()

    def _next_image(self):
        try:
            index = self.file_list.index(self.open_file)
            if index < len(self.file_list)-1:
                index += 1
                self.open_image(self.file_list[index])
                self.folder_buttons.scroll(self.file_list[index])
        except (AttributeError, ValueError):
            pass

    def _del_image(self):
        try:
            index = self.file_list.index(self.open_file)
            send2trash(self.file_list[index])
            self._next_image()
            self.crawler = FileCrawler(self.link)
            self.open_folder(self.link)
        except (AttributeError, ValueError):
            pass

    def _back_image(self):
        try:
            index = self.file_list.index(self.open_file)
            if index > 0:
                index -= 1
                self.open_image(self.file_list[index])
                self.folder_buttons.scroll(self.file_list[index])
        except (AttributeError, ValueError):
            pass

    def file_options_exit(self):
        self.entered = False
        self.file_option_bar.place_forget()
        # self.window.unbind("<MouseWheel>")
        # self.window.unbind("<Button-4>")
        # self.window.unbind("<Button-5>")

    def _go_click(self, link):
        thread = threading.Thread(target=self._go_click_thread, args=(link,))
        thread.daemon = True
        thread.start()

    def _go_click_thread(self, link):
        if link.endswith(".jpg") or link.endswith(".png") or link.endswith(".jpeg") or link.endswith(".gif") \
                or link.endswith(".tiff") or link.endswith(".bmp") or link.endswith(".tif"):
            string = os.path.split(link)
            self.open_image(link)
            link = string[0]

        self.folder_text.config(state=tk.NORMAL)
        self.folder_text.delete(1.0, tk.END)
        self.folder_text.insert(tk.END, f"Loading...\n", "blank")
        self.folder_text.config(state=tk.DISABLED)
        self.crawler = FileCrawler(link)
        self.open_folder(link)

    def _slideshow_click(self, link):
        if link == "":
            return
        if len(threading.enumerate()) >= 2:
            self.SLIDESHOW_RUNNING = False
            self.slideshow_play.pack()
            self.slideshow_stop.pack_forget()
        else:
            if len(self.file_list) > 0:
                self.SLIDESHOW_RUNNING = True
                self.slideshow_play.pack_forget()
                self.slideshow_stop.pack()
                cmd_thread = threading.Thread(target=self._slideshow_start, args=())
                cmd_thread.daemon = True
                cmd_thread.start()

    def _slideshow_start(self):
        # link = link.replace(" ", "%")
        # os.system(f"py slideshow.py {link}")
        for _ in self.file_list:
            time.sleep(2)
            if not self.SLIDESHOW_RUNNING:
                break
            self._next_image()

    def folder_fill(self, link):
        try:
            self.link = link
            self.folder_text.config(state=tk.NORMAL)
            self.folder_text.delete(1.0, tk.END)
            self.folder_text.insert(tk.END, f"..\\{os.path.split(link)[-1]}\\\n", "blank")
            folders = self.crawler.pull_folders(link)
            self.folder_count.set(f"{len(folders)} folder(s)")
            for folder in folders:
                dir_path = os.path.join(link, folder)
                self.folder_text.insert(tk.END, "\n", "spacer")
                self.folder_text.insert(tk.END, "> " + folder + "\n", self.folder_buttons.add(self.open_folder, dir_path))
                self.folder_text.insert(tk.END, "\n", "spacer")
            self.folder_text.config(state=tk.DISABLED)
        except (KeyError, TypeError):
            self.folder_count.set(f"0 folder(s)")
            pass

    def open_folder(self, link):
        self.folder_fill(link)
        self.file_bar.delete(0, tk.END)
        self.file_bar.insert(tk.INSERT, link)
        folder = os.path.split(link)[-1]
        self.window.title(f"Image Viewer - {folder}")
        try:
            self.folder_text.config(state=tk.NORMAL)
            self.file_list.clear()
            for file in self.crawler.file_list(link):
                self.file_list.append(file)
                self.folder_text.insert(tk.END, "\n", "spacer")
                self.folder_text.insert(tk.END, "- " + os.path.split(file)[-1] + "\n", self.folder_buttons.addFile(self.open_image, file))
                self.folder_text.insert(tk.END, "\n", "spacer")
            self.file_count.set(f"{len(self.file_list)} file(s)")
        except (TypeError, KeyError):
            self.file_count.set(f"0 file(s)")
            pass
        self.folder_text.config(state=tk.DISABLED)

    def open_image(self, file="toolbar/default_img.png"):
        """open_image(self, [file="toolbar/default_img.png"])
        :param file: the link to the file
        :return: Displays image
        """
        self.open_file = file
        self.ID.open_image(file)
        self.zoom_amount.delete(0, tk.END)
        self.zoom_amount.insert(tk.END, int(self.ID.zoom_percentage()))

        try:
            file_size = os.path.getsize(self.open_file)/1048576
        except FileNotFoundError:
            return
        self.text_var.set(self.open_file)
        if file_size < 10:
            self.file_size.set("  %.2f MB" % file_size)
        else:
            self.file_size.set("%.2f MB" % file_size)
        if self.entered:
            self.file_option_bar.place_forget()
            self.file_options_enter()


if len(sys.argv) > 1:
    arg = sys.argv[-1].replace("%", " ")
    ImageBrowser(arg)
else:
    ImageBrowser()
