import os
from glob import glob
import subprocess
from typing import List, Set, Tuple, Dict
import json 

def load_config(config_file: str) -> Dict[str, str]:
    with open(config_file, "r") as f:
        config = json.load(f)
    return config

def make_symlink(src: str, dst: str) -> None:
    if os.path.exists(dst):
        os.remove(dst)
    os.symlink(src, dst)

def get_input_name(filepath: str) -> str:
    """Extract sample names from a list of filenames.
    Sample name is everything before the first underscore.
    """
    return os.path.basename(filepath).split(".")[0]

def get_output_name(filepath: str) -> str:
    return os.path.basename(filepath).split("__")[0]


def compute_hash(file_path: str) -> str:
    """Compute a hash of a file."""
    return subprocess.check_output(["shasum", file_path]).decode("utf-8").split()[0]


def glob_single(pattern: str):
    file_list = glob(pattern)
        
    if len(file_list) > 1:
        print("ERROR: Multiple files found for pattern:", pattern)
        raise ValueError
    elif len(file_list) == 0:
        print("ERROR: No files found for pattern:", pattern)
        return None
    
    return file_list[0]

