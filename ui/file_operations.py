from tkinter import filedialog
import os

def load_xpr_folder(app):
    app.xpr_folder_path = filedialog.askdirectory()
    if app.xpr_folder_path:
        app.xpr_folder_label.config(text=app.xpr_folder_path)

def load_xpn_folder(app):
    app.xpn_folder_path = filedialog.askdirectory()
    if app.xpn_folder_path:
        app.xpn_folder_label.config(text=app.xpn_folder_path)

def find_file_in_dir(directory, extension):
    for item in os.listdir(directory):
        if item.upper().endswith(extension.upper()):
            return os.path.join(directory, item)
    return None
