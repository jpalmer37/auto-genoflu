import os
from glob import glob
import subprocess
from typing import List, Set, Tuple, Dict
import json 
import logging

def prelim_checks(config: dict) -> None:
    """Perform preliminary checks on the configuration."""
    if not os.path.exists(config['input_dir']):
        raise FileNotFoundError(f"Input directory does not exist: {config['input_dir']}")
    
    if not os.path.exists(config['rename_dir']):
        logging.info(json.dumps({"event_type": "rename_dir_not_found", "rename_dir": config['rename_dir']}))
        os.makedirs(config['rename_dir'])
    
    if not os.path.exists(config['output_dir']):
        logging.info(json.dumps({"event_type": "output_dir_not_found", "output_dir": config['output_dir']}))
        os.makedirs(config['output_dir'])
    
    if not os.path.exists(config['provenance_dir']):
        logging.info(json.dumps({"event_type": "provenance_dir_not_found", "provenance_dir": config['provenance_dir']}))
        os.makedirs(config['provenance_dir'])

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

