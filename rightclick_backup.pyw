import sys
import os
import shutil
import configparser
import re
import tkinter as tk
from tkinter import ttk

# CONFIG ---------------------------------------------------
config = configparser.ConfigParser()
appdata_path = os.getenv('LOCALAPPDATA')
app_config_path = os.path.join(appdata_path, 'Rightclick Backup')
config_file = 'settings.ini'
config_file_path = os.path.join(app_config_path, config_file)

# create or load config file
if not os.path.exists(app_config_path):
    os.makedirs(app_config_path)
if not os.path.isfile(config_file_path):
    config['Settings'] = {
        'Subfolders': False,
        'Filecap': False,
        'Filecapsize': 1000
    }
    with open(config_file_path, 'w') as configfile:
        config.write(configfile)
else:
    config.read(config_file_path)

# GET SETTINGS
config_subfolders = config.getboolean('Settings', 'Subfolders')
config_filecap = config.getboolean('Settings', 'Filecap')
config_filecapsize = config.getint('Settings', 'Filecapsize')

# OPEN SETTINGS ---------------------------------------------------

if len(sys.argv) < 2:
    window = tk.Tk()
    window.title("Rightclick Backup settings")
    width = 420
    height = 180
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2) 
    window.geometry('%dx%d+%d+%d' % (width, height, x, y))

    # VARIABLES
    checkbox_subfolders_var = tk.BooleanVar(value=config_subfolders)
    checkbox_filecap_var = tk.BooleanVar(value=config_filecap)
    input_filecapsize_var = tk.StringVar(value=config_filecapsize)

    # FUNCTIONS
    def toggle_filecapsize():
        input_filecapsize.config(state='normal' if checkbox_filecap_var.get() else 'disabled')

    def save_config():
        config['Settings'] = {
            'Subfolders': checkbox_subfolders_var.get(),
            'Filecap': checkbox_filecap_var.get(),
            'Filecapsize': input_filecapsize_var.get()
        }
        with open(config_file_path, 'w') as configfile:
            config.write(configfile)

    def validate_filecapsize():
        input_value = int(input_filecapsize.get())

        if input_value < 1:
            return False
        elif input_value > 10000:
            return False
        else:
            return True
        
    def invalid_filecapsize():
        input_value = int(input_filecapsize_var.get())
        clamped_value = min(max(input_value,1), 10000)
        input_filecapsize.delete(0, tk.END)
        input_filecapsize.insert(0, str(clamped_value))

    def quit_program():
        window.quit()
        window.destroy()

    # UI ELEMENTS
    wrapper_frame = ttk.Frame(window)
    wrapper_frame.pack(anchor="center", expand=True)

    checkbox_subfolders = ttk.Checkbutton(wrapper_frame, text="Create subfolders for each file", variable=checkbox_subfolders_var)
    checkbox_subfolders.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)

    checkbox_filecap = ttk.Checkbutton(wrapper_frame, text="Backup file cap", variable=checkbox_filecap_var, command=toggle_filecapsize)
    checkbox_filecap.grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)

    input_filecapsize = ttk.Entry(wrapper_frame, textvariable=input_filecapsize_var, validate='focusout', validatecommand=validate_filecapsize, invalidcommand=invalid_filecapsize, state='normal' if checkbox_filecap_var.get() else 'disabled')
    input_filecapsize.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

    buttons_frame = ttk.Frame(wrapper_frame)
    buttons_frame.grid(row=3, column=1, pady=20)

    save_button = ttk.Button(buttons_frame, text="Save", command=save_config)
    save_button.pack(side="left", padx="5", anchor="se")

    exit_button = ttk.Button(buttons_frame, text="Exit", command=quit_program)
    exit_button.pack(side="left", padx="5", anchor="se")

    window.mainloop()



# MAKE BACKUP ---------------------------------------------------
if len(sys.argv) >= 2:
    # FILE TO BACKUP
    file_path = sys.argv[1]
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    file_extension = os.path.splitext(file_path)[1]
    backup_dir = os.path.join(os.path.dirname(file_path), "backup")

    if not os.path.isdir(backup_dir):
        os.makedirs(backup_dir)

    if config_subfolders is True:
        sub_dir = os.path.join(backup_dir, file_name)
        if not os.path.isdir(sub_dir):
            os.makedirs(sub_dir)
        backup_dir = sub_dir

    # REGEX MATCHING
    pattern = re.compile(file_name + "_(\d{3})\\" + file_extension)

    backup_files = [f for f in os.listdir(backup_dir) if re.match(pattern, f)]
    next_suffix = str(len(backup_files)).zfill(3)

    if backup_files:
        most_recent_file = max(backup_files, key=lambda x: int(re.match(pattern, x).group(1)))
        last_suffix = int(pattern.match(most_recent_file).group(1))
        next_suffix = str(last_suffix + 1).zfill(3)
    else:
        next_suffix = str(0).zfill(3)

    # DELETE FILES EXCEEDING THE CAP
    if config_filecap is True:
        if len(backup_files) >= config_filecapsize:
            backup_files.sort(key=lambda x: int(re.match(pattern, x).group(1)))
            config_filecapsize -= 1
            for file_to_delete in backup_files[:-config_filecapsize]:
                file_path_to_delete = os.path.join(backup_dir, file_to_delete)
                os.remove(file_path_to_delete)

    
    new_file_path = os.path.join(backup_dir, file_name + "_" + str(next_suffix) + file_extension)
    shutil.copy(file_path, new_file_path)


