#!/usr/bin/env python3
import os
import ast
import sys
import subprocess

# Known mappings for packages where the pip install name differs from the import name
IMPORT_TO_PKG_MAP = {
    "cv2": "opencv-python",
    "yaml": "pyyaml",
    "bs4": "beautifulsoup4",
    "PIL": "Pillow",
    "dotenv": "python-dotenv",
    "jwt": "PyJWT",
    "sklearn": "scikit-learn",
    "crypto": "pycryptodome",
    "telegram": "python-telegram-bot",
}

def is_virtual_environment():
    """Returns True if the script is running inside a virtual environment."""
    return (hasattr(sys, 'real_prefix') or 
            (getattr(sys, 'base_prefix', sys.prefix) != sys.prefix))

def get_installed_packages():
    """Gets a list of all packages installed in the current environment."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=freeze"],
            capture_output=True, text=True, check=True
        )
        packages = []
        for line in result.stdout.strip().split("\n"):
            if "==" in line:
                # Extract package name before '==' and strip whitespace cleanly
                pkg_name = line.split("==")[0].strip()
                packages.append(pkg_name.lower())
        return packages
    except subprocess.CalledProcessError:
        print("\033[91mError: Could not execute 'pip list'. Make sure pip is installed.\033[0m")
        sys.exit(1)

def extract_imports_from_project():
    """Scans all .py files in the current folder tree to find top-level imported libraries."""
    imported_libs = set()
    
    for root, _, files in os.walk("."):
        if any(ignored in root for ignored in [".venv", "venv", "env", ".git", "__pycache__", "build", "dist", "test_env"]):
            continue
            
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read(), filename=file_path)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                # FIXED: Extract index 0 from split list before lowering string
                                base_mod = alias.name.split('.')[0].strip().lower()
                                imported_libs.add(base_mod)
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                # FIXED: Extract index 0 from split list before lowering string
                                base_mod = node.module.split('.')[0].strip().lower()
                                imported_libs.add(base_mod)
                except Exception:
                    continue
    return imported_libs

def extract_packages_from_requirements():
    """Extracts explicit top-level declarations from requirements.txt safely."""
    req_packages = set()
    if os.path.exists("requirements.txt"):
        try:
            with open("requirements.txt", "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        pkg = line
                        # FIXED: Properly extract name segment using loop substitution safely
                        for operator in ["==", ">=", "<=", ">", "<", "@"]:
                            if operator in pkg:
                                pkg = pkg.split(operator)[0]
                        req_packages.add(pkg.strip().lower())
        except Exception as e:
            print(f"\033[93m⚠️ Warning parsing requirements.txt: {e}\033[0m")
    return req_packages

def main():
    if not is_virtual_environment():
        print("\033[91m❌ ERROR: Global Environment Protected!\033[0m")
        print("\033[93mpip-clean is designed to safely run ONLY inside a virtual environment (.venv).\033[0m")
        print("Running this globally could break your core system dependencies.")
        print("\nPlease activate your virtual environment first:")
        print(" > test_env\\Scripts\\activate\n")
        sys.exit(1)

    print("\033[94m🔍 Running pip-clean: Scanning codebase for ghost dependencies...\033[0m\n")
    
    installed = get_installed_packages()
    actual_imports = extract_imports_from_project()
    requirements_pkgs = extract_packages_from_requirements()
    
    mapped_imports = set()
    for lib in actual_imports:
        mapped_imports.add(lib)
        if lib in IMPORT_TO_PKG_MAP:
            mapped_imports.add(IMPORT_TO_PKG_MAP[lib].lower())

    sub_dependency_protections = {
        "urllib3", "idna", "certifi", "charset-normalizer",
        "six", "numpy", "python-dateutil", "typing-extensions"
    }

    critical_baselines = {"pip", "setuptools", "wheel", "twine", "black", "flake8", "pytest", "uv"}
    
    ghost_packages = []
    for pkg in installed:
        if (pkg not in mapped_imports and 
            pkg not in requirements_pkgs and 
            pkg not in sub_dependency_protections and
            pkg not in critical_baselines):
            ghost_packages.append(pkg)
            
    if not ghost_packages:
        print("\033[92m✨ Perfect! Your environment is perfectly clean. No unused dependencies found.\033[0m")
        return

    print(f"\033[93m⚠️ Found {len(ghost_packages)} unused packages occupying space:\033[0m")
    for pkg in ghost_packages:
        print(f"  - {pkg}")
    
    print("\n" + "="*50)
    try:
        choice = input("\033[1mDo you want to safely uninstall ALL of these packages? (y/N): \033[0m").strip().lower()
    except (KeyboardInterrupt, EOFError):
        print("\n\033[90mOperation canceled.\033[0m")
        return
    
    if choice in ['y', 'yes']:
        print("\n\033[94m🧹 Cleaning up packages...\033[0m")
        for pkg in ghost_packages:
            print(f"Uninstalling {pkg}...")
            subprocess.run([sys.executable, "-m", "pip", "uninstall", pkg, "-y"], capture_output=True)
        print("\n\033[92m🎉 Environment successfully cleaned up!\033[0m")
    else:
        print("\n\033[90mOperation canceled. No files or packages were modified.\033[0m")

if __name__ == "__main__":
    main()
