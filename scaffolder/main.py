from pathlib import Path
import json
import datetime
import questionary
import subprocess
import sys
import os

# Robust template loader for both installed package and local development
def load_templates():
    try:
        # Modern way to load bundled data when installed as a package
        import importlib.resources as pkg_resources
        try:
            # Python 3.9+ syntax
            json_str = pkg_resources.files('scaffolder').joinpath('templates.json').read_text(encoding='utf-8')
            return json.loads(json_str)
        except AttributeError:
            # Fallback syntax for older importlib variants
            with pkg_resources.open_text('scaffolder', 'templates.json', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        # Fallback to local path relative to this script file
        base_path = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_path, "templates.json")
        try:
            with open(json_path, "r", encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Error: 'templates.json' not found at {json_path}")
            return None

def create_scaffolder():
    templates = load_templates()
    if not templates:
        return

    project_name = questionary.text("Enter your new project name:").ask()
    if not project_name:
        print("Project name cannot be empty.")
        return
    project_name = project_name.strip()

    target_path = questionary.text("Enter destination path (leave blank for current folder):").ask().strip()
    
    project_type = questionary.select(
        "Choose your project type:",
        choices=list(templates.keys())
    ).ask()

    include_license = questionary.confirm("Would you like to include an MIT License?").ask()
    
    author_name = ""
    if include_license:
        author_name = questionary.text("Enter your name/organization for the license:").ask().strip()

    if target_path:
        root_dir = Path(target_path) / project_name
    else:
        root_dir = Path(project_name)
    
    if root_dir.exists():
        print(f"[ERROR]: Directory '{root_dir}' already exists.")
        return

    print(f"Scaffolding {project_type} workspace at '{root_dir}'...")

    root_dir.mkdir(parents=True, exist_ok=True)
    
    (root_dir / "README.md").write_text(f"# {project_name}\n\nA {project_type} project.\n")
    (root_dir / ".gitignore").write_text(".env\n__pycache__/\nbuild/\n.DS_Store\n")
    
    template_data = templates[project_type]

    # Create folders specified in JSON
    for folder in template_data["folders"]:
        folder_path = root_dir / folder
        folder_path.mkdir(parents=True, exist_ok=True)

    # Create files specified in JSON and write their default content
    for file_path_str, file_content in template_data["files"].items():
        file_path = root_dir / file_path_str
        file_path.parent.mkdir(parents=True, exist_ok=True) # Ensure nested file folders exist
        file_path.write_text(file_content)

    if project_type == "python":
        print("Setting up virtual environment (venv)...")
        try:
            # sys.executable ensures it uses the exact Python interpreter currently running the script
            venv_path = root_dir / "venv"
            subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
            print("Virtual environment 'venv' created successfully.")

            requirements_file = root_dir / "requirements.txt"
            if requirements_file.exists():
                print("Installing dependencies from requirements.txt...")
                
                # Determine correct pip path based on OS (Windows vs Mac/Linux)
                if os.name == "nt":
                    pip_executable = venv_path / "Scripts" / "pip.exe"
                else:
                    pip_executable = venv_path / "bin" / "pip"

                if pip_executable.exists():
                    subprocess.run([str(pip_executable), "install", "-r", str(requirements_file)], check=True)
                    print("Dependencies installed successfully.")
                else:
                    print("[WARNING]: Pip executable not found in virtual environment.")

        except subprocess.CalledProcessError:
            print("[WARNING]: Failed to create virtual environment or install dependencies automatically.")

    if include_license:
        current_year = datetime.datetime.now().year
        mit_license_text = f"""MIT License

Copyright (c) {current_year} {author_name}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
        (root_dir / "LICENSE").write_text(mit_license_text)
        print("Generated MIT license.")

    print("Initializing Git repository...")
    try:
        # Run 'git init' inside the new project root directory
        subprocess.run(["git", "init"], cwd=str(root_dir), check=True, capture_output=True)
        
        # Optional: Stage all generated files and make an initial commit
        subprocess.run(["git", "add", "."], cwd=str(root_dir), check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit via the-scaffolder"], cwd=str(root_dir), check=True, capture_output=True)
        
        print("Git repository initialized and initial commit created successfully.")
    except FileNotFoundError:
        print("[WARNING]: Git is not installed or not found in your system's PATH.")
    except subprocess.CalledProcessError:
        print("[WARNING]: Failed to initialize Git repository.")

    print(f" Successfully generated workspace at '{root_dir}'.")

if __name__ == "__main__":
    create_scaffolder()