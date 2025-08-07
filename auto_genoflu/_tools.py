import os
from glob import glob
import subprocess
from typing import List, Set, Tuple, Dict
import json 
import logging
import shutil 

from auto_genoflu._nextcloud import nc_make_folder, nc_upload_file, load_credentials, convert_nextcloud_path_to_local

def load_config(config_file: str) -> Dict[str, str]:
    logging.debug(json.dumps({"event_type": "loading_config_file", "config_file": config_file}))

    try:
        with open(config_file, "r") as f:
            config = json.load(f)
        
        logging.debug(json.dumps({"event_type": "config_file_loaded", "config_file": config_file, "config": config}))
        
        for path in ['input_dir', 'output_dir', 'provenance_dir']:
            config[path + "_local"] = convert_nextcloud_path_to_local(config[path], config['nc_data_mount_dir'])

        logging.debug(json.dumps({"event_type": "config_paths_converted", "config_file": config_file, "config": config}))

        return config
    except (IOError, json.JSONDecodeError) as e:
        logging.error(json.dumps({"event_type": "config_file_load_error", "config_file": config_file, "error": str(e)}))
        raise

def copy_file(src, dst):
    if dst.startswith("nc://"):
        logging.debug(json.dumps({"event_type": "copying_file_to_nextcloud", "src": src, "remote_path": dst}))
        nc_upload_file(src, dst)
    
    else:
        # Handle local destination
        logging.debug(json.dumps({"event_type": "copying_file_locally", "src": src, "dst": dst}))
        shutil.copy2(src, dst)
    
    logging.debug(json.dumps({"event_type": "file_copied", "src": src, "dst": dst}))


def make_folder(dir_path: str) -> None:
    logging.debug(json.dumps({
        "event_type": "creating_folder",
        "dir_path": dir_path,
        "folder_type": "nextcloud" if dir_path.startswith("nc://") else "local"
    }))
    
    try:
        if dir_path.startswith("nc://"):
            nc_make_folder(dir_path)
        else:
            os.makedirs(dir_path, exist_ok=True)
        
        logging.debug(json.dumps({
            "event_type": "folder_created",
            "dir_path": dir_path
        }))
    except Exception as e:
        logging.error(json.dumps({"event_type": "folder_creation_error", "dir_path": dir_path, "error": str(e)}))
        raise

def make_symlink(src: str, dst: str) -> None:
    logging.debug(json.dumps({"event_type": "creating_symlink", "src": src, "dst": dst}))
    
    try:
        if os.path.exists(dst):
            logging.debug(json.dumps({
                "event_type": "removing_existing_symlink",
                "dst": dst
            }))
            os.remove(dst)
        
        os.symlink(src, dst)
        
        logging.debug(json.dumps({
            "event_type": "symlink_created",
            "src": src,
            "dst": dst
        }))
    except Exception as e:
        logging.error(json.dumps({
            "event_type": "symlink_creation_error",
            "src": src,
            "dst": dst,
            "error": str(e)
        }))
        raise

def get_input_name(filepath: str) -> str:
    """Extract sample names from a list of filenames.
    Sample name is everything before the first underscore.
    """
    input_name = os.path.basename(filepath).split(".")[0]
    
    logging.debug(json.dumps({
        "event_type": "extracting_input_name",
        "filepath": filepath,
        "extracted_name": input_name
    }))
    
    return input_name

def get_output_name(filepath: str) -> str:
    output_name = os.path.basename(filepath).split("__")[0]
    
    logging.debug(json.dumps({
        "event_type": "extracting_output_name",
        "filepath": filepath,
        "extracted_name": output_name
    }))
    
    return output_name


def compute_hash(file_path: str) -> str:
    """Compute a hash of a file."""
    if not os.path.exists(file_path):
        logging.error(json.dumps({"event_type": "compute_hash_failed_file_not_found", "file_path": file_path}))
        raise FileNotFoundError()
    return subprocess.check_output(["shasum", file_path]).decode("utf-8").split()[0]


def glob_single(pattern: str):
    logging.debug(json.dumps({
        "event_type": "glob_single_search",
        "pattern": pattern
    }))
    
    file_list = glob(pattern)
        
    if len(file_list) > 1:
        logging.error(json.dumps({
            "event_type": "multiple_files_found",
            "pattern": pattern,
            "files_found": file_list
        }))
        raise ValueError(f"Multiple files found for pattern: {pattern}")
    elif len(file_list) == 0:
        logging.warning(json.dumps({
            "event_type": "no_files_found",
            "pattern": pattern
        }))
        return None
    
    logging.debug(json.dumps({
        "event_type": "glob_single_result",
        "pattern": pattern,
        "file_found": file_list[0]
    }))
    
    return file_list[0]

