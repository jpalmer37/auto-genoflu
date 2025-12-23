import os, sys
from glob import glob
import subprocess
from typing import List, Set, Tuple, Dict
import json 
import logging
import pandas as pd
from datetime import datetime
from auto_genoflu.operations import make_folder, move_file

def prelim_checks(config: dict) -> None:
    """Perform preliminary checks on the configuration."""
    if not os.path.exists(config['input_dir']):
        raise FileNotFoundError(f"Input directory does not exist: {config['input_dir']}")
    
    use_nextcloud = config.get('use_nextcloud', False)
    dirs_to_create = [ 'output_dir', 'provenance_dir', 'summary_dir']
    for dir_key in dirs_to_create:
        if not os.path.exists(config[dir_key]):
            logging.info(json.dumps({"event_type": f"{dir_key}_not_found", dir_key: config[dir_key]}))
            make_folder(config[dir_key], use_nextcloud=use_nextcloud)


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

def add_confidence_column(df: pd.DataFrame) -> pd.DataFrame:
    """Add a Confidence column based on Genotype Percent Match List values.
    
    Args:
        df: DataFrame containing the 'Genotype Percent Match List' column
        
    Returns:
        DataFrame with added 'Confidence' column
    """
    logging.debug(json.dumps({"event_type": "add_confidence_column_start"}))
    
    def process(string):
        if not isinstance(string, str):
            return None
        fields = [float(x.strip("% ")) for x in string.split(",")]
        return min(fields)
    df['Min Percent Match'] = df['Genotype Percent Match List'].apply(process)
    df['Confidence Level'] = pd.cut(df['Min Percent Match'], bins=[0, 90, 95, 98, 100], labels=['sub90','90','95','98'])
    
    logging.info(json.dumps({"event_type": "add_confidence_column_complete"}))
    
    return df


def collect_df(input_files: List[str]) -> pd.DataFrame:
    """Combine multiple TSV files into a single file and return the combined dataframe.
    
    Args:
        output_file: Path to the output TSV file
        input_files: List of input TSV file paths
        
    Returns:
        Combined DataFrame from all input files
    """
    # Check argument count
    if len(input_files) < 1:
        logging.warning(json.dumps({"event_type": "collect_df_no_input_files", "input_files": input_files}))
        return pd.DataFrame()
    
    # Read all TSV files and concatenate
    dataframes = [pd.read_csv(file, sep='\t') for file in input_files]
    combined_df = pd.concat(dataframes, ignore_index=True)
    
    logging.info(json.dumps({"event_type": "collect_df_complete",  "input_files": input_files}))
    
    return combined_df

def make_summary_file(config: dict) -> None:
    logging.info(json.dumps({"event_type": "make_summary_file_start"}))

    timestamp = datetime.now().strftime('%y-%m-%d_%H-%M-%S')

    output_filename = f"GenoFLU_summary_{timestamp}.tsv"

    tmp_file = os.path.join(config['work_dir'], output_filename)
    output_file = os.path.join(config['summary_dir'], output_filename)  
    input_files = glob(os.path.join(config['output_dir'], "*genoflu.tsv"))

    try:
        output_df = collect_df(input_files)

        output_df = add_confidence_column(output_df)

        output_df.to_csv(tmp_file, sep='\t', index=False)

        move_file(tmp_file, output_file, use_nextcloud=config.get('use_nextcloud', False))

        os.remove(tmp_file)

        logging.info(json.dumps({"event_type": "make_summary_file_complete", "output_file": output_file}))
    except ValueError:
        logging.info(json.dumps({"event_type": "no_input_files", "input_files_count": len(input_files)}))
        pass
    except FileExistsError:
        logging.info(json.dumps({"event_type": "output_file_exists", "output_file": output_file}))
        pass


def delete_files(glob_expr: str) -> None:
    """Delete files matching the given glob expression."""

    for file_path in glob(glob_expr):
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                logging.debug(json.dumps({
                    "event_type": "file_deleted",
                    "file_path": str(file_path)
                }))
            except Exception as e:
                logging.error(json.dumps({
                    "event_type": "file_deletion_error",
                    "file_path": str(file_path),
                    "error": str(e)
                }))
        