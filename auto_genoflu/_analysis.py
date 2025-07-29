import os 
from glob import glob 
from typing import List
import subprocess
import datetime
import json
import logging

from auto_genoflu._tools import get_input_name, get_output_name, make_symlink, compute_hash, load_config, glob_single
from auto_genoflu._rename import rename_fasta_headers


def find_files_to_process(config: dict) -> List[str]:
    """Find FASTA files in input_dir that haven't been processed in output_dir."""
    # Get all FASTA files from input directory
    input_files = glob(os.path.join(config['input_dir'], "*.fa")) + \
                 glob(os.path.join(config['input_dir'], "*.fasta"))
    
    # Get all CSV files from output directory
    output_files = glob(os.path.join(config['output_dir'], "*.tsv"))
    
    # Extract sample names
    inputs_dict = {get_input_name(f): f for f in input_files}
    outputs_dict = {get_output_name(f): f for f in output_files}

    existing_samples = set(inputs_dict.keys()) & set(outputs_dict.keys())

    # Find samples that need to be processed
    samples_to_process = set()

    for name in existing_samples:
        # Check if provenance file exists
        provenance_path = os.path.join(config['provenance_dir'], f"{name}__genoflu_complete.json")
        if not os.path.exists(provenance_path):
            logging.warning(json.dumps({"event_type": "provenance_file_missing", "provenance_file": os.path.join(config['provenance_dir'], f"{name}__genoflu_complete.json")}))
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
    
    return files_to_process

def run_genoflu(fasta_file: str, config: dict) -> None:
    """Run the analysis on a FASTA file and save result to results_dir."""
    # Extract sample name
    sample_name = get_input_name(fasta_file)
    
    # Construct output filename
    output_file = os.path.join(config['output_dir'], f"{sample_name}__genoflu.tsv")
    renamed_filepath = os.path.join(config['rename_dir'], f"{sample_name}__input.fasta")
    input_filepath = f'./{sample_name}__input.fasta'
    # Build and run the command
    try:
        # need this because genoflu is stupid 
        rename_fasta_headers(fasta_file, renamed_filepath)
        make_symlink(renamed_filepath, input_filepath)

        # Replace this with your actual command
        cmd = [ "conda", "run", "-n", "genoflu", "genoflu.py",
            "-i", config['genoflu_env'] + "/dependencies/fastas/",
            "-c", config['genoflu_env'] + "/dependencies/genotype_key.xlsx",
            "-f", input_filepath,
            "-n", sample_name
        ]
        
        # Run the subprocess
        result = subprocess.run(cmd, check=True, capture_output=True)

        tsv_file = glob_single(f'./{sample_name}*stats.tsv')
        xlsx_file = glob_single(f'./{sample_name}*stats.xlsx')

        os.rename(tsv_file, output_file)

        input_hash = compute_hash(fasta_file)
        output_hash = compute_hash(output_file)

        genoflu_complete = {
            "timestamp_analysis_complete": datetime.datetime.now().isoformat(),
            "input_file": fasta_file,
            "input_hash": input_hash,
            "output_file": output_file,
            "output_hash": output_hash
        }

        with open(os.path.join(config['provenance_dir'], f"{sample_name}__genoflu_complete.json"), "w") as f:
            json.dump(genoflu_complete, f)

        # Remove the temporary files
        os.remove(xlsx_file)
        os.remove(input_filepath)

        print(f"Successfully processed {fasta_file}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error processing {fasta_file}: {e}")
        print(f"STDERR: {e.stderr}")
