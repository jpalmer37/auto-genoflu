# Quick Start Guide - auto_flumut

## 🚀 Quick Start (5 minutes)

### Option 1: Local Installation (without Docker)

```bash
# 1. Install flumut via conda/mamba
mamba install -c bioconda flumut

# 2. Clone and install auto_flumut
cd auto-genoflu
pip install -e .

# 3. Create directories
mkdir -p ~/flumut/{inputs,outputs,logs}

# 4. Create config file
cat > ~/flumut/config.json << EOF
{
  "input_dir": "$HOME/flumut/inputs/",
  "output_dir": "$HOME/flumut/outputs/",
  "provenance_dir": "$HOME/flumut/logs/",
  "scan_interval_seconds": 60
}
EOF

# 5. Run
auto_flumut -c ~/flumut/config.json --log-level INFO
```

### Option 2: Docker (Production)

```bash
# 1. Build image
docker build -f Dockerfile-flumut -t auto-flumut:latest .

# 2. Create directories and config
mkdir -p ~/flumut-docker/{inputs,outputs,logs}

cat > ~/flumut-docker/config.json << EOF
{
  "input_dir": "/data/inputs/",
  "output_dir": "/data/outputs/",
  "provenance_dir": "/data/logs/",
  "scan_interval_seconds": 60
}
EOF

# 3. Run container
docker run -d \
  --name auto-flumut \
  -v ~/flumut-docker/inputs:/data/inputs \
  -v ~/flumut-docker/outputs:/data/outputs \
  -v ~/flumut-docker/logs:/data/logs \
  -v ~/flumut-docker/config.json:/app/config.json \
  auto-flumut:latest -c /app/config.json --log-level INFO
```

## 📁 Directory Structure

```
auto-genoflu/
├── auto_flumut/              # Main package
│   ├── __init__.py
│   ├── __main__.py          # Entry point
│   ├── _analysis.py         # Core logic
│   ├── _tools.py            # Utilities
│   └── _nextcloud.py        # Cloud integration
├── Dockerfile-flumut         # Container definition
├── environment-flumut.yml    # Conda environment
├── config-flumut.json       # Example config
├── aws-config-flumut.json   # AWS example
└── docker-compose-flumut.yml
```

## 🔄 How It Works

```
┌─────────────────────────────────────────────────────────┐
│                    auto_flumut                          │
│                                                         │
│  1. SCAN input_dir for *.fasta files                   │
│  2. CHECK against outputs & provenance                 │
│  3. PROCESS new/changed files:                         │
│     flumut -M sample__flumut.tsv sample.fasta          │
│  4. HASH input & output files (SHA)                    │
│  5. CREATE provenance JSON with timestamp & hashes     │
│  6. UPLOAD to output_dir & provenance_dir              │
│  7. WAIT scan_interval_seconds                         │
│  8. REPEAT                                             │
└─────────────────────────────────────────────────────────┘
```

## 📝 Example Usage

### Add a file to process

```bash
# Copy FASTA file to input directory
cp my_sample.fasta ~/flumut/inputs/

# Check logs (if running in background)
tail -f ~/flumut/logs/*.log

# View output
cat ~/flumut/outputs/my_sample__flumut.tsv
```

### Check provenance

```bash
# View provenance JSON
cat ~/flumut/logs/my_sample__flumut_complete.json

# Example output:
{
  "timestamp_analysis_complete": "2024-01-15T14:30:45.123456",
  "input_file": "/home/user/flumut/inputs/my_sample.fasta",
  "input_hash": "abc123def456...",
  "output_file": "/home/user/flumut/outputs/my_sample__flumut.tsv",
  "output_hash": "789xyz012..."
}
```

## 🔧 Configuration Reference

### Minimal Config
```json
{
  "input_dir": "/path/to/inputs/",
  "output_dir": "/path/to/outputs/",
  "provenance_dir": "/path/to/logs/",
  "scan_interval_seconds": 60
}
```

### AWS/Production Config
```json
{
  "input_dir": "/data/service-user/files/analysis/auto_flumut/inputs/",
  "output_dir": "/data/service-user/files/analysis/auto_flumut/outputs/",
  "provenance_dir": "/data/service-user/files/analysis/auto_flumut/logs/",
  "scan_interval_seconds": 30
}
```

## 🌐 Nextcloud Setup (Optional)

```bash
# Set environment variables
export NEXTCLOUD_API_URL="https://your-nextcloud.com/remote.php/dav/files"
export NEXTCLOUD_API_USERNAME="your-username"
export NEXTCLOUD_API_PASSWORD="your-app-password"

# Run with Nextcloud enabled
auto_flumut -c config.json
```

## ☁️ AWS Fargate Deployment

### 1. Push to ECR
```bash
# Build and tag
docker build -f Dockerfile-flumut -t auto-flumut:latest .
docker tag auto-flumut:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/auto-flumut:latest

# Login and push
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/auto-flumut:latest
```

### 2. Create Task Definition
```json
{
  "family": "auto-flumut",
  "containerDefinitions": [{
    "name": "auto-flumut",
    "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/auto-flumut:latest",
    "command": ["-c", "/data/config.json", "--log-level", "INFO"],
    "environment": [
      {"name": "NEXTCLOUD_API_URL", "value": "https://..."},
      {"name": "NEXTCLOUD_API_USERNAME", "value": "..."},
      {"name": "NEXTCLOUD_API_PASSWORD", "value": "..."}
    ],
    "mountPoints": [{
      "sourceVolume": "efs-storage",
      "containerPath": "/data"
    }]
  }]
}
```

### 3. Deploy
```bash
aws ecs create-service \
  --cluster your-cluster \
  --service-name auto-flumut \
  --task-definition auto-flumut:1 \
  --desired-count 1 \
  --launch-type FARGATE
```

## 🐛 Troubleshooting

### Issue: No files processed
```bash
# Check if files are in input_dir
ls -la ~/flumut/inputs/

# Check logs for errors
auto_flumut -c config.json --log-level DEBUG
```

### Issue: flumut command not found
```bash
# Install flumut
mamba install -c bioconda flumut

# Verify installation
which flumut
flumut --help
```

### Issue: Permission errors
```bash
# Fix permissions
chmod -R 755 ~/flumut
```

## 📊 Monitoring

### View JSON logs
```bash
# Real-time monitoring
tail -f logs.json | jq .

# Filter by event type
cat logs.json | jq 'select(.message.event_type == "scan_complete")'

# Count processed files
cat logs.json | jq 'select(.message.event_type == "analysis_complete")' | wc -l
```

## 🔄 Comparison with auto-genoflu

| Feature | auto-genoflu | auto-flumut |
|---------|--------------|-------------|
| Command | Complex (5 args) | Simple (2 args) |
| Header rename | Required | Not needed |
| Symlinks | Required | Not needed |
| Directories | 4 | 3 |
| Output files | 2 (TSV+XLSX) | 1 (TSV) |

## 📚 Additional Resources

- [Full Documentation](README-flumut.md)
- [Build & Test Guide](BUILD_TEST.md)
- [Detailed Comparison](COMPARISON.md)
- [flumut GitHub](https://github.com/flu-crew/flumut)
