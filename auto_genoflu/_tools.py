import os, sys
from glob import glob
import subprocess
from typing import List, Set, Tuple, Dict
import json 
import logging
from datetime import datetime

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

    if not os.path.exists(config['summary_dir']):
        logging.info(json.dumps({"event_type": "summary_dir_not_found", "summary_dir": config['summary_dir']}))
        os.makedirs(config['summary_dir'])

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

def make_symlink(src: str, dst: str) -> None:
    logging.debug(json.dumps({
        "event_type": "creating_symlink",
        "src": src,
        "dst": dst
    }))
    
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

def collectfile(output_file, input_files):
    # Check argument count
    if len(input_files) < 1:
        print("ERROR: No input files provided.")
        raise ValueError
    
    # Check if output file already exists
    if os.path.exists(output_file):
        print("ERROR: Output file already exists.")
        raise FileExistsError
    
    # Open output file in write mode
    with open(output_file, 'w') as outfile:
        # Read and write header from first file
        with open(input_files[0], 'r') as first_file:
            header = first_file.readline()
            outfile.write(header)
        
        # Append non-header lines from all files
        for file in input_files:
            with open(file, 'r') as infile:
                # Skip header for subsequent files
                next(infile, None)
                # Write remaining lines
                outfile.writelines(infile)


def make_summary_file(config: dict) -> None:
    timestamp = datetime.now().strftime('%y-%m-%d_%H-%M')

    output_file = os.path.join(config['summary_dir'], f"genoflu_summary_{timestamp}")  # output filename with timestamp
    input_files = glob(os.path.join(config['output_dir'], "*genoflu.tsv"))

    try:
        collectfile(output_file, input_files)
    
    except ValueError:
        logging.info(json.dumps({"event_type": "no_input_files", "input_files_count": len(input_files)}))
        pass
    except FileExistsError:
        logging.info(json.dumps({"event_type": "output_file_exists", "output_file": output_file}))
        pass
