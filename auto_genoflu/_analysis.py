import os 
from glob import glob 
from typing import List, Tuple
import subprocess
import datetime
import json
import logging

from auto_genoflu._tools import get_input_name, get_output_name, make_symlink, compute_hash, load_config, glob_single
from auto_genoflu.operations import move_file, make_folder
from auto_genoflu._rename import rename_fasta_headers

def get_genoflu_env_path():
    try:
        logging.debug(json.dumps({"event_type": "locating_genoflu_env_path"}))
        genoflu_bin_path = subprocess.check_output(['which', 'genoflu.py']).decode('utf-8').strip()
        genoflu_env_path = os.path.dirname(os.path.dirname(genoflu_bin_path))

    except subprocess.CalledProcessError:
        logging.error(json.dumps({"event_type": "genoflu_not_found", "error": "genoflu.py not found in PATH"}))
        raise FileNotFoundError("genoflu.py not found in PATH")

    logging.debug(json.dumps({"event_type": "genoflu_env_path_found", "genoflu_env_path": genoflu_env_path}))

    return genoflu_env_path

def prelim_checks(config: dict) -> None:
    """Perform preliminary checks on the configuration."""
    use_nextcloud = config.get('use_nextcloud', False)
    
    # Derive rename_dir from work_dir
    rename_dir = os.path.join(config['work_dir'], 'rename')
    config['rename_dir'] = rename_dir
    
    for dir_name in ['input_dir', 'work_dir', 'rename_dir', 'output_dir', 'provenance_dir']:
        if not os.path.exists(config[dir_name]):
            logging.info(json.dumps({"event_type": f"{dir_name}_not_found", "dir_path": config[dir_name]}))
            make_folder(config[dir_name], use_nextcloud)

def find_genoflu_files_to_process(config: dict) -> Tuple[List[str], List[str], List[str]]:
    """Find FASTA files in input_dir that haven't been processed in output_dir."""
    logging.debug(json.dumps({"event_type": "find_genoflu_files_to_process_start", "input_dir": config['input_dir'], "output_dir": config['output_dir']}))
    
    # Get all FASTA files from input directory

    input_files = []
    for expr in config['glob_expressions']:
        input_files += glob(os.path.join(config['input_dir'], expr))

    
    # Get all TSV output files from output directory
    output_files = glob(os.path.join(config['output_dir'], "*.tsv"))
    
    logging.debug(json.dumps({"event_type": "file_discovery", "input_files_count": len(input_files), "output_files_count": len(output_files)}))
    
    # Extract sample names
    inputs_dict = {get_input_name(f): f for f in input_files}
    outputs_dict = {get_output_name(f): f for f in output_files}

    existing_samples = set(inputs_dict.keys()) & set(outputs_dict.keys())
    
    logging.debug(json.dumps({"event_type": "existing_samples", "existing_samples_count": len(existing_samples)}))

    # Find samples that need to be processed
    samples_to_process = set()

    for name in existing_samples:
        # Check if provenance file exists
        provenance_path = os.path.join(config['provenance_dir'], f"{name}__genoflu_complete.json")
        if not os.path.exists(provenance_path):
            logging.warning(json.dumps({"event_type": "provenance_file_missing", "provenance_file": provenance_path}))
            samples_to_process.add(name)
            continue
        
        # Load provenance
        provenance = load_config(provenance_path)

        # Check if input or output files have changed
        if provenance['input_hash'] != compute_hash(inputs_dict[name]):
            logging.warning(json.dumps({"event_type": "input_file_changed_hash_mismatch", "provenance_file": provenance['input_file'], "provenance_hash": provenance['input_hash'], "input_file": inputs_dict[name], "input_hash": compute_hash(inputs_dict[name])}))
            samples_to_process.add(name)
        elif provenance['output_hash'] != compute_hash(outputs_dict[name]):
            logging.warning(json.dumps({"event_type": "output_file_changed_hash_mismatch", "provenance_file": provenance['output_file'], "provenance_hash": provenance['output_hash'], "output_file": outputs_dict[name], "output_hash": compute_hash(outputs_dict[name])}))
            samples_to_process.add(name)

    # Find samples that haven't been processed
    samples_to_process |= set(inputs_dict.keys()) - set(outputs_dict.keys())
    
    # Get the full file paths of the input files to process
    files_to_process = [inputs_dict[sample] for sample in samples_to_process]
    
    return input_files, output_files, files_to_process

def run_genoflu(fasta_file: str, config: dict) -> None:
    """Run the analysis on a FASTA file and save result to results_dir."""
    # Extract sample name
    sample_name = get_input_name(fasta_file)
    
    # Construct output filename
    input_filename = f'{sample_name}__input.fasta'
    rename_fasta_path = os.path.join(config['rename_dir'], input_filename)
    output_tsv_path = os.path.join(config['output_dir'], f"{sample_name}__genoflu.tsv")
    
    # Get working directory from config, default to current directory
    working_dir = config.get('work_dir', os.getcwd())
    
    # Save the original working directory to restore later
    original_dir = os.getcwd()
    
    # Build and run the command
    try:
        # Change to working directory if specified
        if working_dir != original_dir:
            make_folder(working_dir, use_nextcloud=False)  # work directory is not allowed to be on nextcloud
            os.chdir(working_dir)
            logging.debug(json.dumps({
                "event_type": "working_directory_changed",
                "from": original_dir,
                "to": working_dir
            }))

        genoflu_env_path = get_genoflu_env_path()

        # need this because genoflu is stupid 
        rename_fasta_headers(fasta_file, rename_fasta_path)
        symlink_path = f"./{input_filename}"
        make_symlink(rename_fasta_path, symlink_path)

        # Replace this with your actual command
        cmd = [ f"genoflu.py",
            "-i", f"{genoflu_env_path}/dependencies/fastas/",
            "-c", f"{genoflu_env_path}/dependencies/genotype_key.xlsx",
            "-f", input_filename,
            "-n", sample_name
        ]
        
        # Run the subprocess
        result = subprocess.run(cmd, check=True, capture_output=True)
        
        logging.debug(json.dumps({
            "event_type": "subprocess_output",
            "sample_name": sample_name,
            "stdout": result.stdout.decode('utf-8')[:500],  # First 500 chars to avoid overwhelming logs
            "stderr": result.stderr.decode('utf-8')[:500] if result.stderr else ""
        }))

        tsv_filename = glob_single(f'./{sample_name}*stats.tsv')
        xlsx_filename = glob_single(f'./{sample_name}*stats.xlsx')
        
        logging.debug(json.dumps({
            "event_type": "output_files_discovered",
            "sample_name": sample_name,
            "tsv_filename": tsv_filename,
            "xlsx_filename": xlsx_filename
        }))

        # Upload or move the TSV file based on configuration
        use_nextcloud = config.get('use_nextcloud', False)
        move_file(tsv_filename, output_tsv_path, use_nextcloud=use_nextcloud)

        input_hash = compute_hash(fasta_file)
        output_hash = compute_hash(output_tsv_path)
        
        logging.debug(json.dumps({
            "event_type": "file_hashes_computed",
            "sample_name": sample_name,
            "input_hash": input_hash,
            "output_hash": output_hash
        }))

        genoflu_complete = {
            "timestamp_analysis_complete": datetime.datetime.now().isoformat(),
            "input_file": fasta_file,
            "input_hash": input_hash,
            "output_file": output_tsv_path,
            "output_hash": output_hash
        }

        with open(f"{sample_name}__genoflu_complete.json", "w") as f:
            json.dump(genoflu_complete, f)

        provenance_filename = f"{sample_name}__genoflu_complete.json"
        provenance_path = os.path.join(config['provenance_dir'], provenance_filename)

        logging.debug(json.dumps({"event_type": "uploading_files", "sample_name": sample_name, "tsv_filename": tsv_filename, "provenance_filename": provenance_filename}))
        
        # Upload or move the provenance file based on configuration
        move_file(provenance_filename, provenance_path, use_nextcloud=use_nextcloud)

        # Remove the temporary files
        logging.debug(json.dumps({"event_type": "removing_temporary_files", "sample_name": sample_name, "files": [rename_fasta_path, tsv_filename, xlsx_filename, provenance_filename, symlink_path]}))
        for f in [rename_fasta_path, tsv_filename, xlsx_filename, provenance_filename, symlink_path]:
            os.remove(f)
        
        logging.debug(json.dumps({"event_type": "run_genoflu_complete", "sample_name": sample_name}))

        
    except subprocess.CalledProcessError as e:
        logging.error(json.dumps({"event_name": "genoflu_failed", "sample_name": sample_name, "error": str(e), "command": " ".join(cmd), "stderr": e.stderr.decode('utf-8') if e.stderr else ""}))

    except (IOError, FileNotFoundError) as e:
        logging.error(json.dumps({"event_name": "genoflu_failed_file_error", "sample_name": sample_name, "error": str(e), "files": [rename_fasta_path, input_filename, output_tsv_path]}))

    except (KeyError) as e:
        logging.error(json.dumps({"event_name": "genoflu_failed_key_error", "sample_name": sample_name, "error": str(e)}))
    
    finally:
        # Always restore the original working directory
        if os.getcwd() != original_dir:
            os.chdir(original_dir)
            logging.debug(json.dumps({
                "event_type": "working_directory_restored",
                "to": original_dir
            }))
