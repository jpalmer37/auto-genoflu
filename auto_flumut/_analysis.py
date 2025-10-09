import os 
from glob import glob 
from typing import List, Tuple
import subprocess
import datetime
import json
import logging

from auto_flumut._tools import get_input_name, get_output_name, compute_hash, load_config, make_folder
from auto_flumut._nextcloud import nc_upload_file

def prelim_checks(config: dict) -> None:
    """Perform preliminary checks on the configuration."""
    for dir_name in ['input_dir', 'output_dir', 'provenance_dir']:
        if not os.path.exists(config[dir_name]):
            logging.info(json.dumps({"event_type": f"{dir_name}_not_found", "dir_path": config[dir_name]}))
            make_folder(config[dir_name])

def find_files_to_process(config: dict) -> Tuple[List[str], List[str], List[str]]:
    """Find FASTA files in input_dir that haven't been processed in output_dir."""
    logging.debug(json.dumps({
        "event_type": "find_files_to_process_start", 
        "input_dir": config['input_dir'], 
        "output_dir": config['output_dir']
    }))
    
    # Get all FASTA files from input directory
    input_files = glob(os.path.join(config['input_dir'], "*.fa")) + \
                 glob(os.path.join(config['input_dir'], "*.fasta")) + \
                 glob(os.path.join(config['input_dir'], "*.fna"))
    
    # Get all TSV output files from output directory
    output_files = glob(os.path.join(config['output_dir'], "*.tsv"))
    
    logging.debug(json.dumps({
        "event_type": "file_discovery", 
        "input_files_count": len(input_files), 
        "output_files_count": len(output_files)
    }))
    
    # Extract sample names
    inputs_dict = {get_input_name(f): f for f in input_files}
    outputs_dict = {get_output_name(f): f for f in output_files}

    existing_samples = set(inputs_dict.keys()) & set(outputs_dict.keys())
    
    logging.debug(json.dumps({
        "event_type": "existing_samples", 
        "existing_samples_count": len(existing_samples)
    }))

    # Find samples that need to be processed
    samples_to_process = set()

    for name in existing_samples:
        # Check if provenance file exists
        provenance_path = os.path.join(config['provenance_dir'], f"{name}__flumut_complete.json")
        if not os.path.exists(provenance_path):
            logging.warning(json.dumps({
                "event_type": "provenance_file_missing", 
                "provenance_file": provenance_path
            }))
            samples_to_process.add(name)
            continue
        
        # Load provenance
        provenance = load_config(provenance_path)

        # Check if input or output files have changed
        if provenance['input_hash'] != compute_hash(inputs_dict[name]):
            logging.warning(json.dumps({
                "event_type": "input_file_changed_hash_mismatch", 
                "provenance_file": provenance['input_file'], 
                "provenance_hash": provenance['input_hash'], 
                "input_file": inputs_dict[name], 
                "input_hash": compute_hash(inputs_dict[name])
            }))
            samples_to_process.add(name)
        elif provenance['output_hash'] != compute_hash(outputs_dict[name]):
            logging.warning(json.dumps({
                "event_type": "output_file_changed_hash_mismatch", 
                "provenance_file": provenance['output_file'], 
                "provenance_hash": provenance['output_hash'], 
                "output_file": outputs_dict[name], 
                "output_hash": compute_hash(outputs_dict[name])
            }))
            samples_to_process.add(name)

    # Find samples that haven't been processed
    samples_to_process |= set(inputs_dict.keys()) - set(outputs_dict.keys())
    
    # Get the full file paths of the input files to process
    files_to_process = [inputs_dict[sample] for sample in samples_to_process]
    
    return input_files, output_files, files_to_process

def run_flumut(fasta_file: str, config: dict) -> None:
    """Run the flumut analysis on a FASTA file and save result to output_dir."""
    # Extract sample name
    sample_name = get_input_name(fasta_file)
    
    # Construct output filename
    output_tsv_path = os.path.join(config['output_dir'], f"{sample_name}__flumut.tsv")
    temp_output = f"{sample_name}_mutations.tsv"
    
    try:
        # Run flumut command: flumut -M mutations_output.tsv input.fasta
        cmd = [
            "flumut",
            "-M", temp_output,
            fasta_file
        ]
        
        logging.debug(json.dumps({
            "event_type": "running_flumut_command",
            "sample_name": sample_name,
            "command": " ".join(cmd)
        }))
        
        # Run the subprocess
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        logging.debug(json.dumps({
            "event_type": "subprocess_output",
            "sample_name": sample_name,
            "stdout": result.stdout[:500] if result.stdout else "",
            "stderr": result.stderr[:500] if result.stderr else ""
        }))

        # Upload the output file to the final location
        if not os.path.exists(temp_output):
            raise FileNotFoundError(f"Expected output file {temp_output} not found")
            
        nc_upload_file(temp_output, output_tsv_path)

        # Compute file hashes
        input_hash = compute_hash(fasta_file)
        output_hash = compute_hash(output_tsv_path)
        
        logging.debug(json.dumps({
            "event_type": "file_hashes_computed",
            "sample_name": sample_name,
            "input_hash": input_hash,
            "output_hash": output_hash
        }))

        # Create provenance JSON
        flumut_complete = {
            "timestamp_analysis_complete": datetime.datetime.now().isoformat(),
            "input_file": fasta_file,
            "input_hash": input_hash,
            "output_file": output_tsv_path,
            "output_hash": output_hash
        }

        provenance_filename = f"{sample_name}__flumut_complete.json"
        with open(provenance_filename, "w") as f:
            json.dump(flumut_complete, f, indent=2)

        provenance_path = os.path.join(config['provenance_dir'], provenance_filename)

        logging.debug(json.dumps({
            "event_type": "uploading_provenance", 
            "sample_name": sample_name, 
            "provenance_filename": provenance_filename
        }))
        
        nc_upload_file(provenance_filename, provenance_path)

        # Remove temporary files
        logging.debug(json.dumps({
            "event_type": "removing_temporary_files", 
            "sample_name": sample_name, 
            "files": [temp_output, provenance_filename]
        }))
        
        for f in [temp_output, provenance_filename]:
            if os.path.exists(f):
                os.remove(f)
        
        logging.debug(json.dumps({
            "event_type": "run_flumut_complete", 
            "sample_name": sample_name
        }))
        
    except subprocess.CalledProcessError as e:
        logging.error(json.dumps({
            "event_name": "flumut_failed", 
            "sample_name": sample_name, 
            "error": str(e), 
            "command": " ".join(cmd), 
            "stderr": e.stderr if e.stderr else ""
        }))

    except (IOError, FileNotFoundError) as e:
        logging.error(json.dumps({
            "event_name": "flumut_failed_file_error", 
            "sample_name": sample_name, 
            "error": str(e), 
            "files": [fasta_file, temp_output, output_tsv_path]
        }))

    except KeyError as e:
        logging.error(json.dumps({
            "event_name": "flumut_failed_key_error", 
            "sample_name": sample_name, 
            "error": str(e)
        }))
