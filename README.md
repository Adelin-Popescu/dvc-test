# DVC Automation CLI Tool

Streamline data and model versioning using **DVC** and **Git**, with **AWS S3** as remote storage.  
This CLI tool provides commands to add data/models, switch between versions, and pull specific files or models.

---

## Prerequisites

- Python ~25
- Git
- AWS CLI (configured with your credentials)
- DVC with S3 support

---

## Project Structure

```bash
project/
├── data/                   # Your data directory
├── models/                 # Your models directory
├── model_registry.json     # Registry tracking model versions
├── dvcCLI.py       # The CLI tool script
├── .dvc/                   # DVC configuration directory
├── .git/                   # Git repository directory
└── .env                    # Environment variables for AWS credentials
```

---

## Initialization

Create a script named `init_dvc_project.sh` to set up your environment:

```bash
#!/bin/bash

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip and install required packages
pip install --upgrade pip
pip install 'dvc[s3]' boto3 pyyaml

# Initialize Git and DVC
git init
dvc init

# Configure AWS CLI
aws configure

# Add S3 remote to DVC
dvc remote add -d myremote s3://your-bucket-name/path
dvc remote modify myremote access_key_id $AWS_ACCESS_KEY_ID
dvc remote modify myremote secret_access_key $AWS_SECRET_ACCESS_KEY
dvc remote modify myremote region your-region

# Create .env file
cat <<EOL > .env
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_DEFAULT_REGION=your-region
EOL

echo "Initialization complete. Remember to 'source venv/bin/activate'."
```

Make the script executable:

```bash
chmod +x init_dvc_project.sh
```

Run it:

```bash
./init_dvc_project.sh
```

> **Important:** Replace placeholders like `your-bucket-name`, `your-access-key-id`, etc., with your real AWS S3 and credentials.

---

## CLI Tool Usage

Assuming your CLI tool is saved as `dvcCLI.py`, here are the available commands:

### 1. Add Data

```bash
python dvcCLI.py add-data <path> <version> <model> <description>
```
- **path**: Path to the data file or folder.
- **version**: Version identifier (e.g., `v1.0.0`).
- **model**: Model name (used for .dvc file).
- **description**: Description of the change.

---

### 2. Add Model

```bash
python dvcCLI.py add-model <path> <version> <model> <description>
```
- **path**: Path to the model directory.
- **version**: Version identifier.
- **model**: Model name.
- **description**: Model description.

---

### 3. Switch Version

```bash
python dvcCLI.py switch <name> <version> [--pull]
```
- **name**: Model name.
- **version**: Target version.
- **--pull** (optional): Pull after switching.

---

### 4. Pull Specific File

```bash
python dvcCLI.py pull-file <file_path> <model>
```
- **file_path**: Path to the file/folder.
- **model**: Model name.

---

### 5. Pull Model

```bash
python dvcCLI.py pull-model <model>
```
- **model**: Model name.

---

## Notes

- **Version Format**: Use semantic versioning like `v1.0.0`.
- **Model Registry**: `model_registry.json` keeps track of versions and hashes.
- **Environment Variables**: Load AWS credentials easily:

```bash
export $(cat .env | xargs)
```

- **Git Integration**: The tool automatically stages and commits changes.

---

## Security Considerations

- **.env File**: Add `.env` to `.gitignore` to avoid leaking credentials.
- **AWS Credentials**: Use IAM roles and policies to minimize security risks.

---

## Additional Resources

- [DVC Documentation](https://dvc.org/doc)
- [AWS CLI Quickstart](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html)
- [DVC S3 Remote Setup Guide](https://dvc.org/doc/user-guide/setup-remote-storage/s3)

---

