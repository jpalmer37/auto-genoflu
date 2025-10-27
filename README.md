# auto-genoflu

Automated analysis tools for influenza genomics.

## Projects

This repository contains two automated analysis tools:

### auto-genoflu
Automated GenoFLU analysis tool for influenza genotyping. See original implementation in `auto_genoflu/` directory.

### auto-flumut ✨ NEW
Automated flumut analysis tool for influenza mutation detection. 

**Quick Links:**
- 📖 [Full Documentation](README-flumut.md)
- 🚀 [Quick Start Guide](QUICKSTART.md)
- 📋 [Documentation Index](INDEX.md)
- 🔄 [Workflow Diagrams](WORKFLOW.md)
- 📊 [Comparison with auto-genoflu](COMPARISON.md)

## Quick Start

### auto-genoflu
```bash
# Install and run
mamba install -c bioconda genoflu
pip install -e .
auto_genoflu -c config.json
```

### auto-flumut
```bash
# Easy setup with interactive script
./setup-flumut.sh

# Or manually:
mamba install -c bioconda flumut
pip install -e .
auto_flumut -c config-flumut.json
```

## Features

Both tools provide:
- ✅ Automated file monitoring and processing
- ✅ SHA hash-based provenance tracking
- ✅ JSON structured logging
- ✅ Nextcloud integration (optional)
- ✅ Docker containerization
- ✅ AWS Fargate ready

## Key Differences

| Feature | auto-genoflu | auto-flumut |
|---------|--------------|-------------|
| Purpose | Genotyping | Mutation detection |
| Command | Complex (5 args) | Simple (2 args) |
| Processing | 6 steps | 3 steps |
| Outputs | TSV + XLSX | TSV only |

See [COMPARISON.md](COMPARISON.md) for detailed comparison.

## Documentation

### For auto-flumut:
- **[QUICKSTART.md](QUICKSTART.md)** - Get running in 5 minutes
- **[README-flumut.md](README-flumut.md)** - Complete documentation
- **[BUILD_TEST.md](BUILD_TEST.md)** - Build and test guide
- **[INDEX.md](INDEX.md)** - Navigation index
- **[WORKFLOW.md](WORKFLOW.md)** - Architecture diagrams

### For auto-genoflu:
See `auto_genoflu/` directory for implementation.

## Installation

### Using pip (local development)
```bash
pip install -e .
```

### Using Docker
```bash
# auto-genoflu
docker build -f Dockerfile -t auto-genoflu:latest .

# auto-flumut
docker build -f Dockerfile-flumut -t auto-flumut:latest .
```

### Using conda
```bash
# auto-genoflu
mamba env create -f environment.yml

# auto-flumut
mamba env create -f environment-flumut.yml
```

## Repository Structure

```
auto-genoflu/  (repository root)
│
├── auto_genoflu/              # Original GenoFLU tool
├── auto_flumut/               # NEW: Flumut automation tool
│
├── Documentation (auto-flumut)
│   ├── README-flumut.md
│   ├── QUICKSTART.md
│   ├── BUILD_TEST.md
│   ├── COMPARISON.md
│   ├── SUMMARY.md
│   ├── INDEX.md
│   └── WORKFLOW.md
│
├── Configuration
│   ├── config.json            # auto-genoflu config
│   ├── config-flumut.json     # auto-flumut config
│   └── environment*.yml       # Conda environments
│
└── Docker
    ├── Dockerfile             # auto-genoflu
    └── Dockerfile-flumut      # auto-flumut
```

## License

See LICENSE file for details.

## Contributing

Issues and pull requests welcome!

See individual documentation for detailed usage instructions.