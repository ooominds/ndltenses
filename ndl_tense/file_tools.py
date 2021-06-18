from os import path, mkdir, sep
import pandas as pd

def check_folder_exist(filepath):
    if path.isdir(filepath):
        return
    else:
        mkdir(filepath)

def create_directories(dir_path, sep_file_path, folder_depth):
    for i in range(folder_depth):
        dir_path = sep.join([dir_path, sep_file_path[i + 1]])
        check_folder_exist(dir_path)

def manage_directories(dir_list, FILE_DIREC):
    for filepath in dir_list:
        sep_file_path = filepath.split(sep)
        dir_path = sep_file_path[0]
        if FILE_DIREC:  
            create_directories(dir_path, sep_file_path, (len(sep_file_path) - 2))
        else:
            create_directories(dir_path, sep_file_path, (len(sep_file_path) - 1))