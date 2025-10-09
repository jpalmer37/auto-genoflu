import os
from glob import glob
import subprocess
from typing import Dict
import json 
import logging

from auto_flumut._nextcloud import nc_make_folder

def load_config(config_file: str) -> Dict[str, str]:
    logging.debug(json.dumps({
        "event_type": "loading_config_file",
        "config_file": config_file
    }))
    
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
        
        logging.debug(json.dumps({
            "event_type": "config_file_loaded",
            "config_file": config_file,
            "config_keys": list(config.keys())
        }))
        
        return config
    except (IOError, json.JSONDecodeError) as e:
        logging.error(json.dumps({
            "event_type": "config_file_load_error",
            "config_file": config_file,
            "error": str(e)
        }))
        raise

def make_folder(dir_path: str) -> None:
    logging.debug(json.dumps({
        "event_type": "creating_folder",
        "dir_path": dir_path,
        "folder_type": "nextcloud" if dir_path.startswith("/data") else "local"
    }))
    
    try:
        if dir_path.startswith("/data"):
            nc_make_folder(dir_path)
        else:
            os.makedirs(dir_path, exist_ok=True)
        
        logging.debug(json.dumps({
            "event_type": "folder_created",
            "dir_path": dir_path
        }))
    except Exception as e:
        logging.error(json.dumps({
            "event_type": "folder_creation_error",
            "dir_path": dir_path,
            "error": str(e)
        }))
        raise

def get_input_name(filepath: str) -> str:
    """Extract sample name from input filename.
    Sample name is the base filename without extension.
    """
    input_name = os.path.basename(filepath).split(".")[0]
    
    logging.debug(json.dumps({
        "event_type": "extracting_input_name",
        "filepath": filepath,
        "extracted_name": input_name
    }))
    
    return input_name

def get_output_name(filepath: str) -> str:
    """Extract sample name from output filename.
    Output filename format: {sample_name}__flumut.tsv
    """
    output_name = os.path.basename(filepath).split("__")[0]
    
    logging.debug(json.dumps({
        "event_type": "extracting_output_name",
        "filepath": filepath,
        "extracted_name": output_name
    }))
    
    return output_name

def compute_hash(file_path: str) -> str:
    """Compute a SHA hash of a file."""
    if not os.path.exists(file_path):
        logging.error(json.dumps({"event_type": "compute_hash_failed_file_not_found", "file_path": file_path}))
        raise FileNotFoundError()
    return subprocess.check_output(["shasum", file_path]).decode("utf-8").split()[0]
