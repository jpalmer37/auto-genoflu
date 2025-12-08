import os
from glob import glob
import argparse
import json
import datetime 
import time
import logging 


DEFAULT_SCAN_INTERVAL_SECONDS = 300

from auto_genoflu._analysis import find_genoflu_files_to_process, run_genoflu, prelim_checks
from auto_genoflu._tools import load_config, make_summary_file, delete_files
from auto_genoflu.operations import make_folder
from auto_genoflu.slurm import init_slurm_executor, run_slurm_array

def run_auto_analysis(config: dict) -> None:
    # Ensure output directory exists
    use_nextcloud = config.get('use_nextcloud', False)
    make_folder(config['output_dir'], use_nextcloud=use_nextcloud)
    make_folder(config['provenance_dir'], use_nextcloud=use_nextcloud)
    
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
    if len(files_to_process) > 0:
        if config.get('use_slurm', False):

            logging.info(json.dumps({"event_type": "initializing_slurm_executor"}))
            executor = init_slurm_executor(config)
            logging.info(json.dumps({"event_type": "submitting_slurm_array", "n_tasks": len(files_to_process)}))
            job_list = run_slurm_array(
                executor,
                run_genoflu,
                files_to_process,
                [config]*len(files_to_process)
            )
            logging.info(json.dumps({"event_type": "slurm_analysis_completed", "n_tasks": len(files_to_process)}))

            completed_jobs = [job for job in job_list if job.state == "COMPLETED"]

            for job in completed_jobs:
                delete_files(os.path.join(config['slurm_params'].get("log_dir", "slurm_logs"), f"{job.job_id}*"))
            logging.info(json.dumps({"event_type": "slurm_logs_deleted", "deleted_jobs": [job.job_id for job in completed_jobs]}))
        else:
            logging.info(json.dumps({"event_type": "using_local_processing_for_analysis"}))
            for fasta_file in files_to_process:
                run_genoflu(fasta_file, config)
                logging.info(json.dumps({"event_type": "analysis_complete",  "fasta_file": fasta_file }))    

        
        make_summary_file(config)

def main() -> None:
    """Main function to parse arguments and process files."""
    args = get_args()

    logging.basicConfig(
        format='{"timestamp": "%(asctime)s.%(msecs)03d", "level": "%(levelname)s", "module": "%(module)s", "function_name": "%(funcName)s", "message": %(message)s}',
        datefmt='%Y-%m-%dT%H:%M:%S',
        level=args.log_level,
    )
    logging.getLogger().addHandler(logging.StreamHandler())
    logging.debug(json.dumps({"event_type": "debug_logging_enabled"}))
    

    while(True):
        try:
            config = load_config(args.config)
            logging.info(json.dumps({"event_type": "config_loaded", "config_file": os.path.abspath(args.config)}))
        except json.decoder.JSONDecodeError as e:
            # If we fail to load the config file, we continue on with the
            # last valid config that was loaded.
            logging.error(json.dumps({"event_type": "load_config_failed", "config_file": os.path.abspath(args.config)}))

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
    return parser.parse_args()    


if __name__ == "__main__":
    main()