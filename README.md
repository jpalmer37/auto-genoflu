# auto-genoflu

An automated analysis workflow for running GenoFLU and managing outputs.

## Usage

```bash
auto_genoflu -c <config_file> [--use-nextcloud] [--log-level {DEBUG,INFO,WARNING,ERROR}]
```

### Arguments

- `-c, --config`: Path to JSON configuration file (required)
- `--use-nextcloud`: Enable Nextcloud API for file uploads (optional, default: disabled)
- `--log-level`: Set logging level (optional, default: INFO)

### Operating Modes

#### Local File System Mode (Default)

By default, the package operates in local file system mode using standard file operations:

```bash
auto_genoflu -c config.json
```

In this mode:
- Files are copied to output directories using `shutil.copy2`
- Directories are created using `os.makedirs`
- No Nextcloud credentials required

#### Nextcloud Mode

To use Nextcloud for file uploads, add the `--use-nextcloud` flag:

```bash
auto_genoflu -c config.json --use-nextcloud
```

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
    "input_dir": "/path/to/genoflu/inputs/",
    "rename_dir": "/path/to/genoflu/rename/",
    "output_dir": "/path/to/genoflu/outputs/",
    "provenance_dir": "/path/to/genoflu/logs/",
    "scan_interval_seconds": 180
}
```