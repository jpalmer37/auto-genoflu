# auto_flumut Workflow Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          auto_flumut                            │
│                      (Python Application)                       │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Main Loop (__main__.py)               │  │
│  │                                                          │  │
│  │  1. Load configuration (JSON)                           │  │
│  │  2. Run preliminary checks                              │  │
│  │  3. Execute analysis cycle                              │  │
│  │  4. Sleep for scan_interval_seconds                     │  │
│  │  5. Repeat                                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Analysis Cycle (_analysis.py)               │  │
│  │                                                          │  │
│  │  ┌────────────────────────────────────────────────┐     │  │
│  │  │  1. Scan input_dir for FASTA files            │     │  │
│  │  └────────────────────────────────────────────────┘     │  │
│  │                         ↓                               │  │
│  │  ┌────────────────────────────────────────────────┐     │  │
│  │  │  2. Check existing outputs & provenance        │     │  │
│  │  │     - Compare file hashes                      │     │  │
│  │  │     - Identify new/changed files               │     │  │
│  │  └────────────────────────────────────────────────┘     │  │
│  │                         ↓                               │  │
│  │  ┌────────────────────────────────────────────────┐     │  │
│  │  │  3. For each file to process:                  │     │  │
│  │  │     a. Run flumut -M output.tsv input.fasta   │     │  │
│  │  │     b. Compute input & output hashes          │     │  │
│  │  │     c. Create provenance JSON                 │     │  │
│  │  │     d. Upload files (output + provenance)     │     │  │
│  │  │     e. Clean up temp files                    │     │  │
│  │  └────────────────────────────────────────────────┘     │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
┌──────────────┐
│ Input FASTA  │
│   Files      │
└──────┬───────┘
       │
       ↓
┌──────────────────────┐
│   input_dir/         │
│  *.fasta, *.fa       │
└──────┬───────────────┘
       │
       ↓ (scan)
┌──────────────────────┐
│  File Discovery      │
│  - Find new files    │
│  - Check hashes      │
│  - Detect changes    │
└──────┬───────────────┘
       │
       ↓ (process)
┌──────────────────────────────────┐
│  Run flumut                      │
│                                  │
│  flumut -M mutations.tsv file   │
│                                  │
│  Input:  sample.fasta            │
│  Output: sample_mutations.tsv    │
└──────┬───────────────────────────┘
       │
       ↓ (hash & track)
┌──────────────────────────────────┐
│  Compute Hashes                  │
│                                  │
│  input_hash  = SHA(input.fasta)  │
│  output_hash = SHA(output.tsv)   │
└──────┬───────────────────────────┘
       │
       ↓ (create provenance)
┌──────────────────────────────────┐
│  Generate Provenance JSON        │
│  {                               │
│    "timestamp": "...",           │
│    "input_file": "...",          │
│    "input_hash": "...",          │
│    "output_file": "...",         │
│    "output_hash": "..."          │
│  }                               │
└──────┬───────────────────────────┘
       │
       ↓ (upload)
┌──────────────────────────────────┐
│  Upload to Destinations          │
│                                  │
│  1. output_dir/sample__flumut.tsv│
│  2. provenance_dir/sample__*.json│
│                                  │
│  (Optional: Nextcloud upload)    │
└──────┬───────────────────────────┘
       │
       ↓ (cleanup)
┌──────────────────────────────────┐
│  Remove Temporary Files          │
│  - Local mutation.tsv            │
│  - Local provenance.json         │
└──────────────────────────────────┘
```

## File Naming Convention

```
Input:      sample_name.fasta
            ↓
Output:     sample_name__flumut.tsv
Provenance: sample_name__flumut_complete.json
```

## Module Responsibilities

```
┌─────────────────────────────────────────────────────┐
│ __main__.py                                         │
│ - Argument parsing                                  │
│ - Logging setup                                     │
│ - Main loop coordination                            │
│ - Config loading                                    │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ _analysis.py                                        │
│ - File discovery (find_files_to_process)           │
│ - flumut execution (run_flumut)                    │
│ - Provenance creation                              │
│ - Directory validation (prelim_checks)             │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ _tools.py                                           │
│ - Configuration loading (load_config)               │
│ - File hashing (compute_hash)                       │
│ - Name extraction (get_input_name, get_output_name) │
│ - Directory creation (make_folder)                  │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ _nextcloud.py                                       │
│ - Credential loading (load_credentials)             │
│ - File upload (nc_upload_file)                      │
│ - Folder creation (nc_make_folder)                  │
└─────────────────────────────────────────────────────┘
```

## Deployment Options

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  Local Install  │      │     Docker      │      │   AWS Fargate   │
├─────────────────┤      ├─────────────────┤      ├─────────────────┤
│ pip install -e .│      │ docker build    │      │ ECR + ECS       │
│ auto_flumut -c  │      │ docker run      │      │ Task Definition │
│   config.json   │      │   -v volumes    │      │ Fargate Service │
└─────────────────┘      └─────────────────┘      └─────────────────┘
        │                        │                        │
        └────────────────────────┴────────────────────────┘
                                 ↓
                    ┌────────────────────────┐
                    │  Storage Options       │
                    ├────────────────────────┤
                    │ - Local filesystem     │
                    │ - Nextcloud (WebDAV)   │
                    │ - EFS (AWS)            │
                    │ - NFS mount            │
                    └────────────────────────┘
```

## Comparison: auto-genoflu vs auto-flumut

```
auto-genoflu:                    auto-flumut:
─────────────                    ────────────

Input FASTA                      Input FASTA
    ↓                               ↓
Rename Headers                   [SKIP - Not needed]
    ↓                               ↓
Copy to rename_dir               [SKIP - Not needed]
    ↓                               ↓
Create Symlink                   [SKIP - Not needed]
    ↓                               ↓
Find genoflu env                 [SKIP - Not needed]
    ↓                               ↓
Run genoflu.py                   Run flumut
 (5 arguments)                    (2 arguments)
    ↓                               ↓
Find TSV + XLSX                  Find TSV only
    ↓                               ↓
Upload both files                Upload TSV
    ↓                               ↓
Compute hashes                   Compute hashes
    ↓                               ↓
Create provenance                Create provenance
    ↓                               ↓
Upload provenance                Upload provenance
    ↓                               ↓
Cleanup 4 temp files             Cleanup 2 temp files

Steps: ~12                       Steps: ~6
Complexity: High                 Complexity: Low
```

## Logging Flow

```
JSON Structured Logs:
───────────────────

Every operation logs:
{
  "timestamp": "2024-01-15T14:30:45.123",
  "level": "INFO|DEBUG|WARNING|ERROR",
  "module": "module_name",
  "function_name": "function_name",
  "message": {
    "event_type": "specific_event",
    "key1": "value1",
    "key2": "value2"
  }
}

Event Types:
- config_loaded
- scan_complete
- file_discovery
- analysis_complete
- file_hashes_computed
- upload_success
- etc.
```

## Error Handling

```
Error Detection → Logging → Continue Processing
     ↓               ↓              ↓
 Exception      JSON Log        Next File
  Caught         Error Event     (if applicable)
     
Examples:
- File not found → Log + Skip
- flumut fails   → Log + Continue
- Hash mismatch  → Log + Reprocess
- Upload fails   → Log + Report
```
