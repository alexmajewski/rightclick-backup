import sys
import os
import shutil
import ctypes

def Mbox(title, text, style):
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)

if len(sys.argv) < 2:
    Mbox("Rightclick Backup", "Use this program by right-clicking a file and choosing the 'Backup' option.", 0)
    sys.exit(1) 

file_path = sys.argv[1]

file_name = os.path.splitext(os.path.basename(file_path))[0]
file_extension = os.path.splitext(file_path)[1]

backup_dir = os.path.join(os.path.dirname(file_path), "backup")

if not os.path.isdir(backup_dir):
    os.makedirs(backup_dir)
    
backup_files = [f for f in os.listdir(backup_dir) if f.startswith(file_name)]
next_suffix = str(len(backup_files)).zfill(3)

new_file_path = os.path.join(backup_dir, file_name + "_" + str(next_suffix) + file_extension)
shutil.copy(file_path, new_file_path)