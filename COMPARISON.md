# Comparison: auto-genoflu vs auto-flumut

## Overview

Both tools follow the same architecture pattern but automate different bioinformatics tools with different requirements.

## Key Differences

| Feature | auto-genoflu | auto-flumut |
|---------|--------------|-------------|
| **Tool** | GenoFLU (genotyping) | flumut (mutation detection) |
| **Command** | `genoflu.py -i <deps> -c <key> -f <file> -n <name>` | `flumut -M <output.tsv> <input.fasta>` |
| **Output Files** | TSV + XLSX | TSV only |
| **Header Renaming** | Required (CFIA/GISAID formats) | Not needed |
| **Symlinks** | Required (genoflu quirk) | Not needed |
| **Rename Directory** | Yes | No |
| **Env Path Discovery** | Yes (complex setup) | No |

## Architectural Improvements in auto-flumut

### 1. Simplified Workflow
- **auto-genoflu**: Input → Rename headers → Create symlink → Run tool → Find outputs → Upload
- **auto-flumut**: Input → Run tool → Upload

### 2. Cleaner Code Structure
- Removed `_rename.py` module (not needed)
- Simplified `_analysis.py` (no env path discovery)
- Direct file processing without intermediate steps

### 3. Configuration
```json
// auto-genoflu needs 4 directories
{
  "input_dir": "...",
  "rename_dir": "...",    // auto-flumut doesn't need this
  "output_dir": "...",
  "provenance_dir": "..."
}

// auto-flumut needs only 3 directories
{
  "input_dir": "...",
  "output_dir": "...",
  "provenance_dir": "..."
}
```

### 4. Docker Setup
```dockerfile
# auto-genoflu
RUN mkdir -p /home/ubuntu/genoflu/{rename,outputs,logs}

# auto-flumut (simpler)
RUN mkdir -p /home/ubuntu/flumut/{outputs,logs}
```

## Shared Features

Both tools share:
- ✅ JSON-based structured logging
- ✅ SHA hash-based provenance tracking
- ✅ Nextcloud integration for file uploads
- ✅ Automatic file change detection
- ✅ Continuous monitoring with configurable scan intervals
- ✅ Docker containerization for AWS Fargate
- ✅ Same error handling patterns

## File Naming Conventions

### auto-genoflu
- Input: `sample_name.fasta`
- Renamed: `sample_name__input.fasta`
- Output: `sample_name__genoflu.tsv`, `sample_name__genoflu.xlsx`
- Provenance: `sample_name__genoflu_complete.json`

### auto-flumut
- Input: `sample_name.fasta`
- Output: `sample_name__flumut.tsv`
- Provenance: `sample_name__flumut_complete.json`

## Code Metrics

| Metric | auto-genoflu | auto-flumut |
|--------|--------------|-------------|
| Python modules | 5 | 4 |
| Lines in _analysis.py | ~180 | ~200 |
| Config parameters | 5 | 4 |
| Docker directories | 4 | 3 |

## When to Use Which

### Use auto-genoflu when:
- You need influenza genotyping
- You have CFIA or GISAID formatted sequences
- You need both TSV and XLSX outputs

### Use auto-flumut when:
- You need mutation detection
- You have standard FASTA files
- You only need mutation TSV output
- You want a simpler, more maintainable solution

## Migration Path

To migrate from auto-genoflu to auto-flumut style:

1. Remove header renaming logic (if tool doesn't need it)
2. Simplify command execution (no symlinks)
3. Remove intermediate directories
4. Update output file handling
5. Simplify Docker setup

## Common Patterns (Reusable)

Both tools demonstrate patterns that can be reused for other tools:

```python
# File discovery pattern
inputs_dict = {get_input_name(f): f for f in input_files}
outputs_dict = {get_output_name(f): f for f in output_files}

# Provenance pattern
provenance = {
    "timestamp_analysis_complete": datetime.datetime.now().isoformat(),
    "input_file": input_path,
    "input_hash": compute_hash(input_path),
    "output_file": output_path,
    "output_hash": compute_hash(output_path)
}

# Main loop pattern
while True:
    config = load_config(args.config)
    prelim_checks(config)
    run_auto_analysis(config)
    time.sleep(scan_interval)
```
