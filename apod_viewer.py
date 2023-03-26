from tkinter import *
from tkinter import ttk
import inspect
import os
import apod_desktop
import image_lib
from PIL import Image, ImageTk
from tkcalendar import DateEntry
from datetime import date


# Determine the path and parent directory of this script
script_path = os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)
script_dir = os.path.dirname(script_path)
icon_path = os.path.join(script_dir, 'Icon.ico')
database_file = 'APOD/image_cache.db'

# Initialize the image cache
apod_desktop.init_apod_cache(script_dir)

# TODO: Create the GUI
root = Tk()
root.title("Astronomy Picture of the Day Viewer")
root.iconbitmap(icon_path)
root.geometry('900x600')

date_var = StringVar()
explanation_var = StringVar()
title_var = StringVar()
image_frame = Frame(root)
image_frame.pack(fill=BOTH, expand=True)


image = Image.open('Logo.png')
image_size = image_lib.scale_image((1000, 500))
resize_image = image.resize(image_size)

img = ImageTk.PhotoImage(resize_image)
show_image_label = Label(image_frame, image=img)
show_image_label.image = img
show_image_label.pack()


def setting_image(image_path):
    image1 = Image.open(image_path)
    image_size1 = image_lib.scale_image((1000, 500))
    resize_image1 = image1.resize(image_size1)

    new_img = ImageTk.PhotoImage(resize_image1)
    show_image_label.configure(image=new_img)
    show_image_label.image = new_img


def get_data():
    global date_var
    date_var = calender.get_date()
    record_id = apod_desktop.add_apod_to_cache(date_var)
    print(f"RECORD ID: {record_id}")
    apod_information = apod_desktop.get_apod_info(record_id)
    print(apod_information)
    image_lib.set_desktop_background_image(apod_information['file_path'])
    setting_image(apod_information['file_path'])
    image_explanation_label['text'] = apod_information['explanation']
    print(f"Combobox Current ID: {image_list_combobox.current()}")


def get_data_from_db():
    record_id = image_list_combobox.current() + 1
    print(f"RECORD ID: {record_id}")
    apod_information = apod_desktop.get_apod_info(record_id)
    print(apod_information)
    image_lib.set_desktop_background_image(apod_information['file_path'])
    setting_image(apod_information['file_path'])
    image_explanation_label['text'] = apod_information['explanation']
    print(f"Combobox Current ID: {image_list_combobox.current()}")


def download_image():
    global date_var
    date_var = calender.get_date()


def handle_combobox(e):
    set_as_desktop_btn['state'] = "active"


image_explanation_label = Label(image_frame, text="", justify=LEFT)
image_explanation_label.pack(fill=X, padx=5, pady=5)
image_explanation_label.bind('<Configure>', lambda e: image_explanation_label.config(wraplength=image_explanation_label.winfo_width()))

select_image_frame = LabelFrame(image_frame, text='View Cached Image')
select_image_frame.pack(side=LEFT, expand=True, fill=X, anchor=S, padx=5)

select_image_label = Label(select_image_frame, text="Select Image: ")
select_image_label.pack(side=LEFT, padx=5, pady=5)

image_list = apod_desktop.get_all_apod_titles()
image_list_combobox = ttk.Combobox(select_image_frame, values=image_list, state='readonly', textvariable=title_var)
image_list_combobox.set("Select an image")
image_list_combobox.pack(side=LEFT, padx=5, pady=5)
image_list_combobox.bind('<<ComboboxSelected>>', handle_combobox)

set_as_desktop_btn = Button(select_image_frame, text="Set as Desktop", state=DISABLED, command=lambda: get_data_from_db())
set_as_desktop_btn.pack(side=LEFT, padx=5, pady=5)

# Get More Images
get_image_frame = LabelFrame(image_frame, text='Get More Images')
get_image_frame.pack(side=RIGHT, expand=True, fill=X, anchor=S, padx=5)

get_image_label = Label(get_image_frame, text="Select Date: ")
get_image_label.pack(side=LEFT, padx=5, pady=5)

min_date = date(1995, 6, 16)
max_date = date.today()
calender = DateEntry(get_image_frame, selectmode='day', mindate=min_date, maxdate=max_date)
calender.pack(side=LEFT, padx=5, pady=5)

download_image_btn = Button(get_image_frame, text="Download Image", command=lambda: get_data())
download_image_btn.pack(side=LEFT, padx=5, pady=5)

root.mainloop()
