import argparse
import re
import subprocess
import json
import os
import hashlib
import sys

import yaml

REGISTRY_FILE = "model_registry.json"

def run_command(command):
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        sys.exit(f"Command failed: {command}")

def load_registry():
    if not os.path.exists(REGISTRY_FILE):
        return {}
    with open(REGISTRY_FILE, "r") as f:
        return json.load(f)

def save_registry(registry):
    with open(REGISTRY_FILE, "w") as f:
        json.dump(registry, f, indent=4)

def get_md5_from_dvc(dvc_file_path):
    with open(dvc_file_path, "r") as f:
        dvc_content = yaml.safe_load(f)
    return dvc_content['outs'][0]['md5']

def add_and_push(path, version, model, description, is_model=False):
    semver_pattern = r"^v\d+\.\d+\.\d+$"
    if not re.match(semver_pattern, version):
        sys.exit("Invalid version format. Use 'vX.Y.Z' (e.g., v1.0.0).")

    registry = load_registry()

    # Check for existing versions
    if model in registry:
        latest_version = registry[model][-1]["version"]
        if version < latest_version:
            print(f"Latest version of {model} is {latest_version}")
            proceed = input("You are adding changes to an older version. This may disrupt the model. Proceed? (y/n): ")
            if proceed.lower() != 'y':
                sys.exit("Operation cancelled by user.")

    # DVC and Git operations
    run_command(f"dvc add {path}")

    md5 = get_md5_from_dvc(f"{model}.dvc")
    # Update registry
    entry = {
        "md5": md5,
        "description": description,
        "version": version
    }
    registry.setdefault(model, []).append(entry)
    save_registry(registry)
    print(f"{'Model' if is_model else 'File/Folder'} '{model}' added with version {version}.")

    run_command(f"git add {model}.dvc model_registry.json")
    run_command(f"git commit -m '{description}'")
    run_command(f"dvc push {path}")
    run_command(f"git push")

def switch_version(name, version, pull=False):
    registry = load_registry()
    if name not in registry:
        sys.exit(f"No entries found for {name} in registry.")

    versions = registry[name]
    target_entry = next((entry for entry in versions if entry["version"] == version), None)
    if not target_entry:
        sys.exit(f"Version {version} for {name} not found in registry.")

    dvc_file = f"{name}.dvc"
    if not os.path.exists(dvc_file):
        sys.exit(f"{dvc_file} does not exist.")

    # Load and modify the .dvc file
    with open(dvc_file, "r") as f:
        dvc_content = yaml.safe_load(f)

    dvc_content['outs'][0]['md5'] = target_entry["md5"]

    with open(dvc_file, "w") as f:
        yaml.dump(dvc_content, f)

    print(f"Updated {dvc_file} to version {version} with MD5 {target_entry['md5']}.")

    if pull:
        run_command(f"dvc pull {name}")
        print(f"Pulled data for {name} version {version}.")

def pull_specific_file(file_path, model):
    run_command(f"dvc pull {model}/{file_path}")
    print(f"Pulled {file_path} successfully.")

def pull_specific_model(model):
    run_command(f"dvc pull {model}")
    print(f"Pulled {model} successfully.")

def main():
    parser = argparse.ArgumentParser(description="DVC Automation CLI Tool")
    subparsers = parser.add_subparsers(dest="command")

    add_parser = subparsers.add_parser("add-data", help="Add and push a file/folder")
    add_parser.add_argument("path", help="Path to the file or folder")
    add_parser.add_argument("version", help="Version identifier (e.g., v1.0)")
    add_parser.add_argument("model", help="Model name (used for .dvc file)")
    add_parser.add_argument("description", help="Description of the change")

    model_parser = subparsers.add_parser("add-model", help="Add and push an entire model")
    model_parser.add_argument("path", help="Path to the model directory")
    model_parser.add_argument("version", help="Version identifier (e.g., v1.0)")
    model_parser.add_argument("model", help="Model name (used for .dvc file)")
    model_parser.add_argument("description", help="Description of the model change")

    switch_parser = subparsers.add_parser("switch", help="Switch to a specific model version")
    switch_parser.add_argument("name", help="Name of the model")
    switch_parser.add_argument("version", help="Version to switch to")
    switch_parser.add_argument("--pull", action="store_true", help="Pull data after switching")

    pull_file_parser = subparsers.add_parser("pull-file", help="Pull a specific file or folder from the DVC remote")
    pull_file_parser.add_argument("file_path", help="Path to the file or folder to pull")
    pull_file_parser.add_argument("model", help="Model from where the file should be pulled")

    pull_file_parser = subparsers.add_parser("pull-model", help="Pull a specific model from the DVC remote")
    pull_file_parser.add_argument("model", help="Model that should be pulled")

    args = parser.parse_args()

    if args.command == "add-data":
        add_and_push(args.path, args.version, args.model, args.description)
    elif args.command == "add-model":
        add_and_push(args.path, args.version, args.model, args.description, is_model=True)
    elif args.command == "switch":
        switch_version(args.name, args.version, args.pull)
    elif args.command == "pull-file":
        pull_specific_file(args.file_path, args.model)
    elif args.command == "pull-model":
        pull_specific_model(args.model)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()