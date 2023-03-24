from tkinter import *
from tkinter import ttk
import inspect
import os
import apod_desktop
import image_lib
from PIL import Image, ImageTk
from tkcalendar import DateEntry

image = Image.open("Logo.png")
image_size = image_lib.scale_image((1000, 500))
resize_image = image.resize(image_size)
print(resize_image)

# Determine the path and parent directory of this script
script_path = os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)
script_dir = os.path.dirname(script_path)
icon_path = os.path.join(script_dir, 'Icon.ico')

# Initialize the image cache
apod_desktop.init_apod_cache(script_dir)

# TODO: Create the GUI
root = Tk()
root.title("Astronomy Picture of the Day Viewer")
root.iconbitmap(icon_path)
root.geometry('900x500')

date_var = StringVar()
explanation_var = StringVar()
title_var = StringVar()


def get_date():
    global date_var
    date_var = calender.get_date()


def handle_combobox(e):
    global title_var
    print(title_var.get())
    set_as_desktop_btn['state'] = "active"


img = ImageTk.PhotoImage(resize_image)
show_image_label = Label(image=img)
show_image_label.image = img
show_image_label.pack()

image_explanation_label = Label(root, text="Select Image: ")
image_explanation_label.pack()

select_image_frame = LabelFrame(root, text='View Cached Image')
select_image_frame.place(x=10, y=430, width=450)

select_image_label = Label(select_image_frame, text="Select Image: ")
select_image_label.grid(row=0, column=0, pady=5, ipady=2)

image_list = apod_desktop.get_all_apod_titles()
image_list_combobox = ttk.Combobox(select_image_frame, values=image_list, state='readonly', textvariable=title_var)
image_list_combobox.set("Select an image")
image_list_combobox.grid(row=0, column=1, pady=5)
image_list_combobox.bind('<<ComboboxSelected>>', handle_combobox)

set_as_desktop_btn = Button(select_image_frame, text="Set as Desktop", state=DISABLED)
set_as_desktop_btn.grid(row=0, column=2, pady=5, ipady=1, padx=2)

# Get More Images
get_image_frame = LabelFrame(root, text='Get More Images')
get_image_frame.place(x=470, y=430, width=450)

get_image_label = Label(get_image_frame, text="Select Date: ")
get_image_label.grid(row=0, column=0, pady=5, ipady=2)

calender = DateEntry(get_image_frame, selectmode='day')
calender.grid(row=0, column=1, pady=5)

download_image_btn = Button(get_image_frame, text="Download Image", command=lambda:get_date())
download_image_btn.grid(row=0, column=2, pady=5, ipady=1, padx=2)

root.mainloop()
