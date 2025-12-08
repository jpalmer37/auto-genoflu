
import json 
import logging
import submitit
import time

def init_slurm_executor(config: dict = None) -> submitit.AutoExecutor:
    if config is None:
        config = {}
    if 'slurm_params' not in config:
        config['slurm_params'] = {}
    executor = submitit.AutoExecutor(folder=config['slurm_params'].get("log_dir", "slurm_logs"))
    executor.update_parameters(
        slurm_job_name=config['slurm_params'].get("job_name", "auto-genoflu_batch"),
        slurm_partition=config['slurm_params'].get("partition", "prod"),
        slurm_time=config['slurm_params'].get("time", "01:00:00"),
        slurm_mem=config['slurm_params'].get("mem", "4G"),
        slurm_cpus_per_task=config['slurm_params'].get("cpus_per_task", 1),
        slurm_array_parallelism=config['slurm_params'].get("array_parallelism", 4)
    )
    return executor

def run_slurm_array(executor: submitit.AutoExecutor, function: callable, *function_args) -> None:
    job_list = executor.map_array(
        function,
        *function_args
    )

    # wait on all jobs to complete
    failed_jobs = []
    for job in job_list:
        job.wait()

        if job.state not in ['COMPLETED', 'FAILED']:
            time.sleep(10)

        if job.state == "FAILED":
            failed_jobs.append(job)
    
    for job in failed_jobs:
        logging.error(json.dumps({"event_type": "slurm_job_failed", "job_id": job.job_id, "exception": str(job.exception()), "stderr": job.stderr}))
    
    return job_list
