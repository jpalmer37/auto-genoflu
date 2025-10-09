# Build and Test Guide for auto-flumut

## Prerequisites

- Python 3.8+
- conda/mamba (for full installation with flumut)
- Docker (for containerized deployment)

## Local Development Setup

### 1. Install in Development Mode

```bash
# Clone the repository
cd /path/to/auto-genoflu

# Install in editable mode (without flumut - for development)
pip install -e .

# Or create conda environment with flumut
mamba env create -f environment-flumut.yml
conda activate auto-flumut
pip install -e .
```

### 2. Verify Installation

```bash
# Check if command is available
which auto_flumut

# View help
auto_flumut --help

# Test import
python -c "import auto_flumut; print('Import successful')"
```

## Testing

### Unit Tests (Core Functionality)

```bash
# Test configuration loading
python -c "
from auto_flumut._tools import load_config
config = load_config('config-flumut.json')
print('Config loaded:', list(config.keys()))
"

# Test file discovery
python -c "
from auto_flumut._analysis import find_files_to_process, prelim_checks
from auto_flumut._tools import load_config

config = load_config('config-flumut.json')
prelim_checks(config)
input_files, output_files, files_to_process = find_files_to_process(config)
print(f'Inputs: {len(input_files)}, Outputs: {len(output_files)}, To process: {len(files_to_process)}')
"
```

### Integration Test (with flumut installed)

```bash
# Create test directories
mkdir -p /tmp/flumut-test/{inputs,outputs,logs}

# Create test config
cat > /tmp/flumut-test/config.json << EOF
{
  "input_dir": "/tmp/flumut-test/inputs/",
  "output_dir": "/tmp/flumut-test/outputs/",
  "provenance_dir": "/tmp/flumut-test/logs/",
  "scan_interval_seconds": 5
}
EOF

# Create test FASTA file
cat > /tmp/flumut-test/inputs/test.fasta << EOF
>test_sequence_1
ATCGATCGATCGATCG
>test_sequence_2
GCTAGCTAGCTAGCTA
EOF

# Run auto_flumut (will process once and wait)
# Press Ctrl+C after first scan completes
auto_flumut -c /tmp/flumut-test/config.json --log-level DEBUG
```

## Docker Build and Test

### Build Docker Image

```bash
# Build the image
docker build -f Dockerfile-flumut -t auto-flumut:latest .

# Verify image
docker images | grep auto-flumut
```

### Test Docker Container

```bash
# Create local test directories
mkdir -p /tmp/docker-test/{inputs,outputs,logs}

# Create config
cat > /tmp/docker-test/config.json << EOF
{
  "input_dir": "/data/inputs/",
  "output_dir": "/data/outputs/",
  "provenance_dir": "/data/logs/",
  "scan_interval_seconds": 10
}
EOF

# Run container
docker run -v /tmp/docker-test:/data auto-flumut:latest -c /data/config.json --log-level DEBUG
```

### Using docker-compose

```bash
# Update docker-compose-flumut.yml with correct paths
# Then run:
docker-compose -f docker-compose-flumut.yml up
```

## Linting and Code Quality

```bash
# Check for syntax errors
python -m py_compile auto_flumut/*.py

# Run flake8 (if installed)
flake8 auto_flumut/ --max-line-length=120

# Run pylint (if installed)
pylint auto_flumut/ --max-line-length=120
```

## Common Issues

### Issue: "flumut command not found"
**Solution**: Install flumut via conda:
```bash
mamba install -c bioconda flumut
```

### Issue: "Nextcloud upload fails"
**Solution**: Set environment variables:
```bash
export NEXTCLOUD_API_URL="https://your-nextcloud.com/remote.php/dav/files"
export NEXTCLOUD_API_USERNAME="your-username"
export NEXTCLOUD_API_PASSWORD="your-password"
```

### Issue: "Permission denied" errors
**Solution**: Ensure directories have correct permissions:
```bash
chmod -R 755 /path/to/{inputs,outputs,logs}
```

## Deployment Checklist

- [ ] Test locally with sample FASTA files
- [ ] Verify configuration file paths are correct
- [ ] Test Nextcloud uploads (if using)
- [ ] Build Docker image and test in container
- [ ] Push image to container registry (ECR, Docker Hub, etc.)
- [ ] Configure AWS Fargate task definition
- [ ] Set up persistent storage (EFS or S3)
- [ ] Configure environment variables
- [ ] Deploy and monitor logs

## Performance Notes

- **Scan Interval**: Default is 300 seconds (5 minutes). Adjust based on expected file arrival rate.
- **File Size**: Tested with files up to 100MB. Larger files may require increased container resources.
- **Concurrent Processing**: Currently processes files sequentially. For parallel processing, run multiple instances with different input directories.
