# auto_flumut - Documentation Index

## 📚 Quick Navigation

### Getting Started (Start Here!)
1. **[QUICKSTART.md](QUICKSTART.md)** - Get up and running in 5 minutes
   - Local installation
   - Docker deployment
   - Basic usage examples

2. **[setup-flumut.sh](setup-flumut.sh)** - Interactive setup script
   - Automated directory creation
   - Configuration file generation
   - Sample data creation

### Complete Documentation
3. **[README-flumut.md](README-flumut.md)** - Full documentation
   - Features overview
   - Installation methods
   - Configuration reference
   - Usage examples
   - Nextcloud integration
   - Deployment guide

### Building & Testing
4. **[BUILD_TEST.md](BUILD_TEST.md)** - Development guide
   - Development setup
   - Testing procedures
   - Docker build process
   - Linting and quality checks
   - Troubleshooting

### Understanding the Project
5. **[SUMMARY.md](SUMMARY.md)** - Project overview
   - Architecture details
   - File flow diagram
   - Production readiness checklist
   - Future enhancements

6. **[COMPARISON.md](COMPARISON.md)** - Compare with auto-genoflu
   - Key differences
   - Architectural improvements
   - When to use which tool
   - Migration path

## 📂 File Structure

### Python Package (`auto_flumut/`)
```
auto_flumut/
├── __init__.py          # Package initialization, version info
├── __main__.py          # Entry point, CLI, main loop
├── _analysis.py         # File discovery, flumut execution, provenance
├── _tools.py            # Utilities: config, hashing, naming
└── _nextcloud.py        # Cloud storage integration
```

### Configuration Files
- **config-flumut.json** - Local development config example
- **aws-config-flumut.json** - AWS/production config example
- **environment-flumut.yml** - Conda environment specification
- **pyproject.toml** - Python package metadata (includes both tools)

### Docker & Deployment
- **Dockerfile-flumut** - Container definition for auto_flumut
- **docker-compose-flumut.yml** - Docker Compose configuration
- **.github/workflows/build-flumut.yml** - CI/CD pipeline for Docker builds

### Original Tool (Unchanged)
```
auto_genoflu/            # Original GenoFLU automation
├── __init__.py
├── __main__.py
├── _analysis.py
├── _tools.py
├── _nextcloud.py
└── _rename.py
```

## 🎯 Use Case Guide

### I want to...

#### Run flumut automatically on my FASTA files
→ Start with [QUICKSTART.md](QUICKSTART.md) or run [setup-flumut.sh](setup-flumut.sh)

#### Deploy in Docker/AWS Fargate
→ See [README-flumut.md](README-flumut.md#aws-fargate-deployment) or [QUICKSTART.md](QUICKSTART.md#option-2-docker-production)

#### Understand how it works
→ Read [SUMMARY.md](SUMMARY.md) for architecture and [COMPARISON.md](COMPARISON.md) for design decisions

#### Build and test the code
→ Follow [BUILD_TEST.md](BUILD_TEST.md)

#### Compare with auto-genoflu
→ Check [COMPARISON.md](COMPARISON.md)

#### Integrate with Nextcloud
→ See [README-flumut.md](README-flumut.md#nextcloud-integration)

#### Troubleshoot issues
→ See [BUILD_TEST.md](BUILD_TEST.md#common-issues) and [QUICKSTART.md](QUICKSTART.md#-troubleshooting)

## 📖 Reading Order for Different Users

### For End Users
1. [QUICKSTART.md](QUICKSTART.md) - Quick deployment
2. [README-flumut.md](README-flumut.md) - Full usage guide
3. [BUILD_TEST.md](BUILD_TEST.md#common-issues) - Troubleshooting

### For Developers
1. [SUMMARY.md](SUMMARY.md) - Architecture overview
2. [COMPARISON.md](COMPARISON.md) - Design decisions
3. [BUILD_TEST.md](BUILD_TEST.md) - Development setup
4. Browse `auto_flumut/` source code

### For DevOps/Deployment
1. [QUICKSTART.md](QUICKSTART.md#-aws-fargate-deployment) - AWS deployment
2. [README-flumut.md](README-flumut.md#docker-support) - Docker details
3. [BUILD_TEST.md](BUILD_TEST.md#deployment-checklist) - Deployment checklist

### For Researchers
1. [README-flumut.md](README-flumut.md#provenance-json-file) - Provenance tracking
2. [SUMMARY.md](SUMMARY.md#output-files) - Output format details
3. [COMPARISON.md](COMPARISON.md) - Methodology comparison

## 🔗 External Resources

- **flumut tool**: https://github.com/flu-crew/flumut
- **auto-genoflu** (original): See `auto_genoflu/` directory
- **Bioconda**: https://bioconda.github.io/

## 📝 Configuration Examples

All configuration files follow the same pattern:

```json
{
  "input_dir": "/path/to/inputs/",
  "output_dir": "/path/to/outputs/",
  "provenance_dir": "/path/to/logs/",
  "scan_interval_seconds": 60
}
```

See specific examples:
- Local: [config-flumut.json](config-flumut.json)
- AWS: [aws-config-flumut.json](aws-config-flumut.json)

## 🚀 Quick Commands

```bash
# Setup
./setup-flumut.sh

# Run locally
auto_flumut -c config-flumut.json --log-level INFO

# Build Docker
docker build -f Dockerfile-flumut -t auto-flumut:latest .

# Run Docker
docker run auto-flumut:latest -c /app/config.json

# Install for development
pip install -e .

# Test
python -m pytest  # (if tests added)
```

## 📊 Metrics

- **Total Lines of Code**: ~400 (Python)
- **Documentation Pages**: 6
- **Config Files**: 4
- **Python Modules**: 5
- **Dependencies**: 3 (Python, flumut, requests)

## ✨ Key Features

- ✅ Automated FASTA processing
- ✅ SHA hash-based provenance
- ✅ JSON structured logging
- ✅ Nextcloud integration
- ✅ Docker/Fargate ready
- ✅ Change detection
- ✅ Configurable scanning

## 🆘 Support

For issues or questions:
1. Check [BUILD_TEST.md](BUILD_TEST.md#common-issues) for common problems
2. Review [QUICKSTART.md](QUICKSTART.md#-troubleshooting) for troubleshooting
3. Open an issue on GitHub
4. Check flumut documentation

---

**Last Updated**: 2024-01-15  
**Version**: 0.1.0  
**Status**: Production Ready ✅
