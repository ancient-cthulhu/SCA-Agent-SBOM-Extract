# Veracode SCA SBOM Extraction Tool

A Python script to extract Software Bill of Materials (SBOM) files for all Veracode SCA (Software Composition Analysis) projects across all workspaces in your organization.

## Overview

This tool automates the extraction of SBOM data from Veracode SCA projects using the Veracode REST API. It supports multiple SBOM formats and can optionally include vulnerability information in the exported files.

## Prerequisites

### Required Software
- Python 3.7 or higher
- pip (Python package manager)

### Required Python Packages

Install the required dependencies:

```bash
pip install requests veracode-api-signing
```

### Veracode Platform Requirements

**Required API Permissions:**
- Results API - Read access to SCA workspaces, projects, and SBOM data

**Minimum Role:**
- Submitter role or higher with access to SCA workspaces

Note: The authenticated user must have access to the workspaces and projects you wish to export. Users will only be able to export SBOMs for projects they have permission to view.

## Authentication Setup

The script uses the Veracode API credentials for authentication. You can configure credentials using either a credentials file or environment variables.

### Option 1: Credentials File (Recommended)

Create a credentials file at the following location:

**Windows:**
```
C:\Users\{username}\.veracode\credentials
```

**Mac/Linux:**
```
~/.veracode/credentials
```

**File format:**
```ini
[default]
veracode_api_key_id = YOUR_API_KEY_ID
veracode_api_key_secret = YOUR_API_KEY_SECRET
```

### Option 2: Environment Variables

Set the following environment variables:

**Windows (Command Prompt):**
```cmd
set VERACODE_API_KEY_ID=YOUR_API_KEY_ID
set VERACODE_API_KEY_SECRET=YOUR_API_KEY_SECRET
```

**Windows (PowerShell):**
```powershell
$env:VERACODE_API_KEY_ID="YOUR_API_KEY_ID"
$env:VERACODE_API_KEY_SECRET="YOUR_API_KEY_SECRET"
```

**Mac/Linux (Bash/Zsh):**
```bash
export VERACODE_API_KEY_ID=YOUR_API_KEY_ID
export VERACODE_API_KEY_SECRET=YOUR_API_KEY_SECRET
```

### Generating API Credentials

1. Log in to the Veracode Platform
2. Navigate to your profile settings
3. Go to "API Credentials"
4. Generate a new API key pair
5. Save the API Key ID and API Key Secret securely

## Usage

### Basic Command

Run the script with default settings (CycloneDX format, no vulnerabilities):

```bash
python script.py
```

### Command-Line Options

| Option | Description | Default | Choices |
|--------|-------------|---------|---------|
| `--output-dir` | Directory where SBOMs will be saved | `sboms` | Any valid path |
| `--format` | SBOM format type | `cyclonedx` | `cyclonedx`, `spdx` |
| `--vulns` | Include vulnerability data in SBOMs | `false` | flag (no value) |

### Examples

**Export SBOMs in CycloneDX format:**
```bash
python script.py
```

**Export SBOMs in SPDX format:**
```bash
python script.py --format spdx
```

**Include vulnerability information:**
```bash
python script.py --vulns
```

**Export to a custom directory:**
```bash
python script.py --output-dir /path/to/exports
```

**Export SPDX format with vulnerabilities to a custom directory:**
```bash
python script.py --format spdx --vulns --output-dir ./sca-sboms
```

**View all available options:**
```bash
python script.py --help
```

## Output Structure

The script creates a hierarchical directory structure organized by workspace and project:

```
sboms/
├── Workspace_Name_1/
│   ├── Project_Name_1/
│   │   └── sbom_cyclonedx.json
│   ├── Project_Name_2/
│   │   └── sbom_cyclonedx.json
│   └── Project_Name_3/
│       └── error.txt
├── Workspace_Name_2/
│   ├── Project_Name_A/
│   │   └── sbom_cyclonedx.json
│   └── Project_Name_B/
│       └── sbom_cyclonedx.json
└── Workspace_Name_3/
    └── Project_Name_X/
        └── sbom_cyclonedx.json
```

**File naming:**
- CycloneDX format: `sbom_cyclonedx.json`
- SPDX format: `sbom_spdx.json`
- Errors: `error.txt` (created in project directory if SBOM export fails)

## SBOM Formats

### CycloneDX
CycloneDX is a lightweight SBOM standard designed for use in application security contexts and supply chain component analysis. It is maintained by OWASP and provides a comprehensive inventory of components, dependencies, and vulnerabilities.

### SPDX
SPDX (Software Package Data Exchange) is an open standard for communicating software bill of materials information, including components, licenses, copyrights, and security references. It is maintained by the Linux Foundation and is an ISO/IEC standard (ISO/IEC 5962:2021).

## Script Behavior

### Processing Flow
1. Authenticates with the Veracode API
2. Retrieves all workspaces accessible to the authenticated user
3. For each workspace:
   - Retrieves all projects
   - Creates a directory for the workspace
4. For each project:
   - Creates a directory for the project
   - Attempts to retrieve the SBOM in the specified format
   - Saves the SBOM to a JSON file
   - If an error occurs, writes the error message to `error.txt`

### Error Handling
- **No SBOM found**: Projects without recent agent-based scans will not have SBOM data available. The script will log this and continue.
- **API errors**: Network issues or API rate limiting will be logged to `error.txt` in the project directory.
- **Authentication errors**: Invalid credentials will cause the script to fail with an authentication error.

### Special Cases
- Workspace and project names with special characters (/, \) are automatically sanitized for filesystem compatibility
- Workspaces with zero projects are processed but will have empty directories
- Projects are only included if agent-based scans have been performed

## Troubleshooting

### Authentication Failures
**Symptom:** 401 Unauthorized errors

**Solutions:**
- Verify your API credentials are correct
- Ensure the credentials file is in the correct location
- Check that environment variables are set correctly
- Verify your API credentials have not expired
- Confirm your user has the required permissions

### No SBOMs Found
**Symptom:** "No SBOM found (likely no recent agent scan)" messages

**Solutions:**
- Ensure the project has been scanned using the Veracode SCA Agent
- Verify the scan completed successfully in the Veracode Platform
- Note: Upload scans and IDE scans do not generate agent-based SBOMs

### Permission Errors
**Symptom:** 403 Forbidden errors or missing projects

**Solutions:**
- Verify your user has access to the workspace/project
- Confirm your user has the Submitter role or higher
- Check that your team membership includes the relevant workspaces

## Performance Considerations

- Large organizations with many workspaces and projects may take considerable time to process
- The script processes projects sequentially to avoid API rate limiting
- Progress is displayed in real-time showing the current workspace and project being processed
- Consider running the script during off-peak hours for large exports

## Limitations

- Only exports SBOMs for agent-based scans (not upload or IDE scans)
- Requires network connectivity to api.veracode.com
- Subject to Veracode API rate limits
- Does not support proxy configurations (would require code modification)

## Disclaimer

This tool is not officially maintained or supported by Veracode.
