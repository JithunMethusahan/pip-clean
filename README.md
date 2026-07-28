# 🧹 pip-clean

A zero-dependency, single-file Python micro-utility that scans your codebase, identifies "ghost" dependencies that are installed but never imported, and cleans them up interactively.

### The Problem
Running `pip freeze` often reveals a massive list of third-party modules. Over time, you stop using libraries, but they remain permanently cached inside your local `.venv`, quietly eating up disk space and introducing compliance or security bloat.

### How it Works
`pip-clean` scans your local workspace using Python's built-in Abstract Syntax Tree (`ast`) parser. It maps actual import footprints against `pip list`, filters out essential dev tooling, and cleanly removes the anomalies.

### Quick Start 

Ensure your local virtual environment is active, then install the utility natively straight from GitHub via pip:

```bash
 pip install git+https://github.com/JithunMethusahan/pip-clean/
```

### 🚀 Usage

Execute the package analyzer loop instantly from absolutely anywhere inside your project workspace:

```bash
pip-clean
```


### Key Advantages
- **Zero Configuration**: No dependencies, works instantly out of the box on standard python runtimes.
- **Interactive Check**: Never touches a package without asking you for validation first.
- **Fast Parsing**: Uses syntax tree walking rather than regex, preventing false-positive flags inside strings or comment blocks.
