import os
from glob import glob
import argparse
import subprocess
import json
import datetime 
import time
import logging 

DEFAULT_SCAN_INTERVAL_SECONDS = 300

from auto_genoflu._analysis import find_genoflu_files_to_process, run_genoflu, prelim_checks
from auto_genoflu._tools import load_config, make_summary_file

def run_auto_analysis(config: dict) -> None:
    # Ensure output directory exists
    os.makedirs(config['rename_dir'], exist_ok=True)
    os.makedirs(config['output_dir'], exist_ok=True)
    os.makedirs(config['provenance_dir'], exist_ok=True)
    
    # Find files that need to be processed
    scan_start_timestamp = datetime.datetime.now()

    input_files, output_files, files_to_process = find_genoflu_files_to_process(config)

    scan_complete_timestamp = datetime.datetime.now()
    scan_duration_delta = scan_complete_timestamp - scan_start_timestamp
    scan_duration_seconds = scan_duration_delta.total_seconds()

    logging.info(json.dumps({"event_type": "scan_complete", "scan_duration_seconds": scan_duration_seconds, \
                             "files_to_process": len(files_to_process), "inputs_detected": len(input_files), \
                             "outputs_detected": len(output_files)}))


    # Process each file
    for fasta_file in files_to_process:
        run_genoflu(fasta_file, config)
        logging.info(json.dumps({"event_type": "analysis_complete",  "fasta_file": fasta_file }))    

    if len(files_to_process) > 0:
        make_summary_file(config)

def main() -> None:
    """Main function to parse arguments and process files."""
    args = get_args()

    logging.basicConfig(
        format='{"timestamp": "%(asctime)s.%(msecs)03d", "level": "%(levelname)s", "module": "%(module)s", "function_name": "%(funcName)s", "message": %(message)s}',
        datefmt='%Y-%m-%dT%H:%M:%S',
        level=args.log_level,
    )
    logging.debug(json.dumps({"event_type": "debug_logging_enabled"}))
    

    while(True):
        try:
            config = load_config(args.config)
            logging.info(json.dumps({"event_type": "config_loaded", "config_file": os.path.abspath(args.config)}))
        except json.decoder.JSONDecodeError as e:
            # If we fail to load the config file, we continue on with the
            # last valid config that was loaded.
            logging.error(json.dumps({"event_type": "load_config_failed", "config_file": os.path.abspath(args.config)}))

        # Add use_nextcloud flag to config
        config['use_nextcloud'] = args.use_nextcloud

        prelim_checks(config)

        run_auto_analysis(config)

        if "scan_interval_seconds" in config:
            try:
                scan_interval = float(str(config['scan_interval_seconds']))
            except ValueError as e:
                scan_interval = DEFAULT_SCAN_INTERVAL_SECONDS
        time.sleep(scan_interval)

def get_args():
    """Main function to parse arguments and process files."""
    parser = argparse.ArgumentParser(description="Process FASTA files and run analysis")
    parser.add_argument('-c', "--config", required=True, help="JSON config file")
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], type=str.upper, default='info')
    parser.add_argument('--use-nextcloud', action='store_true', help="Use Nextcloud for file uploads instead of local file system operations")
    return parser.parse_args()    


if __name__ == "__main__":
    main()