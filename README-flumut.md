# auto-flumut

Automated flumut analysis tool for influenza mutation detection. This tool monitors an input directory for FASTA files, runs the flumut analysis tool on them, and saves the results with provenance tracking.

## Overview

`auto-flumut` is a Python application that automates the use of the [flumut](https://github.com/flu-crew/flumut) bioinformatics tool. It continuously monitors an input directory for FASTA files, processes them through flumut, and tracks file changes using hash-based provenance.

## Features

- **Automated Processing**: Continuously monitors input directory for new FASTA files
- **Provenance Tracking**: Uses SHA hashing to track input/output file changes
- **JSON Logging**: Structured JSON logs for easy parsing and monitoring
- **Nextcloud Integration**: Optional upload of results to Nextcloud storage
- **Docker Support**: Ready-to-deploy Docker container for AWS Fargate
- **Change Detection**: Automatically reprocesses files if inputs change

## Installation

### Using Conda/Mamba

```bash
# Create conda environment
mamba env create -f environment-flumut.yml

# Activate environment
conda activate auto-flumut

# Install the package
pip install -e .
```

### Using Docker

```bash
# Build the Docker image
docker build -f Dockerfile-flumut -t auto-flumut:latest .

# Run with docker-compose
docker-compose -f docker-compose-flumut.yml up
```

## Configuration

Create a JSON configuration file with the following structure:

```json
{
  "input_dir": "/path/to/flumut/inputs/",
  "output_dir": "/path/to/flumut/outputs/",
  "provenance_dir": "/path/to/flumut/logs/",
  "scan_interval_seconds": 180
}
```

### Configuration Parameters

- **input_dir**: Directory to monitor for input FASTA files (.fa, .fasta, .fna)
- **output_dir**: Directory where output TSV files will be saved
- **provenance_dir**: Directory for JSON provenance files
- **scan_interval_seconds**: Time (in seconds) between directory scans

## Usage

### Command Line

```bash
# Run with a config file
auto_flumut -c config-flumut.json

# Run with debug logging
auto_flumut -c config-flumut.json --log-level DEBUG
```

### Docker

```bash
# Using docker run
docker run -v /path/to/config.json:/app/config.json auto-flumut:latest -c /app/config.json

# Using docker-compose
docker-compose -f docker-compose-flumut.yml up
```

## How It Works

1. **Scan**: The tool scans the input directory for FASTA files
2. **Check**: Compares against existing outputs and provenance files
3. **Process**: Runs `flumut -M mutations_output.tsv input.fasta` for new/changed files
4. **Hash**: Computes SHA hashes of input and output files
5. **Provenance**: Creates JSON file tracking analysis completion time and file hashes
6. **Upload**: Optionally uploads results to Nextcloud (if configured)
7. **Repeat**: Waits for the configured interval and repeats

## Output Format

### Mutations TSV File
Named as: `{sample_name}__flumut.tsv`

Contains mutation analysis results from flumut.

### Provenance JSON File
Named as: `{sample_name}__flumut_complete.json`

Example:
```json
{
  "timestamp_analysis_complete": "2024-01-15T14:30:45.123456",
  "input_file": "/path/to/input/sample.fasta",
  "input_hash": "abc123...",
  "output_file": "/path/to/output/sample__flumut.tsv",
  "output_hash": "def456..."
}
```

## Nextcloud Integration

To enable Nextcloud uploads, set these environment variables:

```bash
export NEXTCLOUD_API_URL="https://your-nextcloud.com/remote.php/dav/files"
export NEXTCLOUD_API_USERNAME="your-username"
export NEXTCLOUD_API_PASSWORD="your-password"
```

## Logging

All logs are output in JSON format for easy parsing:

```json
{
  "timestamp": "2024-01-15T14:30:45.123",
  "level": "INFO",
  "module": "__main__",
  "function_name": "run_auto_analysis",
  "message": {
    "event_type": "scan_complete",
    "scan_duration_seconds": 0.5,
    "files_to_process": 3,
    "inputs_detected": 10,
    "outputs_detected": 7
  }
}
```

### Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages (e.g., missing provenance files)
- **ERROR**: Error messages (e.g., failed analyses)

## AWS Fargate Deployment

The tool is designed to run as a long-running service on AWS Fargate:

1. Build and push Docker image to ECR
2. Create Fargate task definition using the image
3. Mount EFS or use S3 for persistent storage
4. Configure environment variables for Nextcloud (if needed)
5. Deploy as a Fargate service

## Differences from auto-genoflu

- **Simpler command**: flumut uses a straightforward CLI (`flumut -M output.tsv input.fasta`)
- **No header renaming**: flumut doesn't require FASTA header preprocessing
- **No symlinks**: Direct file processing without symlink workarounds
- **Single output**: Only TSV output (no XLSX files)
- **No rename_dir**: Removed unnecessary intermediate directory

## Development

### Project Structure

```
auto_flumut/
├── __init__.py          # Package initialization
├── __main__.py          # Entry point and main loop
├── _analysis.py         # Core analysis logic
├── _tools.py            # Utility functions
└── _nextcloud.py        # Nextcloud integration
```

### Testing

```bash
# Run with a test config
auto_flumut -c config-flumut.json --log-level DEBUG
```

## License

See LICENSE file for details.

## Related Projects

- [flumut](https://github.com/flu-crew/flumut) - Influenza mutation detection tool
- [auto-genoflu](https://github.com/jpalmer37/auto-genoflu) - Automated GenoFLU analysis
