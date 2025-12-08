# auto-genoflu

An automated analysis workflow for running GenoFLU and managing outputs.

## Usage

```bash
auto_genoflu -c <config_file> [--log-level {DEBUG,INFO,WARNING,ERROR}]
```

### Arguments

- `-c, --config`: Path to JSON configuration file (required)
- `--log-level`: Set logging level (optional, default: INFO)

### Operating Modes

#### Local Processing Mode (Default)

By default, the package operates in local processing mode:

```bash
auto_genoflu -c config.json
```

In this mode:
- Analysis is run locally on the machine
- No SLURM required

#### SLURM Processing Mode

To use SLURM for parallel processing, set `"use_slurm": true` in the config file:

```bash
auto_genoflu -c config.json
```

In this mode:
- Jobs are submitted to SLURM cluster
- Requires SLURM configuration in `slurm_params`

#### Nextcloud Integration

To use Nextcloud for file uploads, set `"use_nextcloud": true` in the config file:

In this mode:
- Files are uploaded via Nextcloud WebDAV API
- Directories are created via Nextcloud API
- Requires environment variables:
  - `NEXTCLOUD_API_USERNAME`
  - `NEXTCLOUD_API_PASSWORD`
  - `NEXTCLOUD_API_URL`

### Configuration File

The configuration file should be a JSON file with the following structure:

```json
{
    "id_threshold": 98.0,
    "input_dir": "/path/to/genoflu/inputs/",
    "output_dir": "/path/to/genoflu/outputs/",
    "provenance_dir": "/path/to/genoflu/logs/",
    "work_dir": "/path/to/working/dir",
    "summary_dir": "/path/to/genoflu/summary/",
    "glob_expressions": ["*.fa", "*.fasta", "*.fna"],
    "scan_interval_seconds": 180,
    "use_nextcloud": false,
    "use_slurm": false,
    "slurm_params": {
        "log_dir": "/path/to/slurm/logs",
        "partition": "prod",
        "cpus_per_task": 2,
        "mem": "4G",
        "time": "00:20:00",
        "job_name": "auto-genoflu_batch",
        "array_parallelism": 8
    }
}
```

#### Configuration Parameters

- **`id_threshold`** (optional): Identity threshold for GenoFLU analysis (default: 98.0)
- **`input_dir`** (required): Directory containing input FASTA files
- **`output_dir`** (required): Directory for output TSV files
- **`provenance_dir`** (required): Directory for provenance/log files
- **`work_dir`** (required): Directory where genoflu will execute and create temporary files
- **`summary_dir`** (required): Directory for summary files
- **`glob_expressions`** (optional): List of glob patterns for input files (default: ["*.fa", "*.fasta", "*.fna"])
- **`scan_interval_seconds`** (optional): Time in seconds between scans for new files (default: 300)
- **`use_nextcloud`** (optional): Enable Nextcloud integration (default: false)
- **`use_slurm`** (optional): Enable SLURM processing (default: false)
- **`slurm_params`** (required if use_slurm is true): SLURM job parameters
  - `log_dir`: Directory for SLURM logs
  - `partition`: SLURM partition
  - `cpus_per_task`: CPUs per task
  - `mem`: Memory per task
  - `time`: Time limit
  - `job_name`: Job name
  - `array_parallelism`: Number of parallel tasks