# Frontend Packages

This repository contains the frontend GUI application written with tkinter. It is compatible with both Linux and Windows, but it is intended to be run on a Windows computer.

## Installation Instructions

Clone the git repository into whichever directory you would like it to be installed. It is designed to be a relatively portable application, so all files will be contained within the git repository. It also requires anaconda or miniconda to be installed. Use `git submodule init` and `git submodule update` to pull the eln_packages_frontend module.

```
git clone https://github.com/ddomlab/eln_packages_frontend.git
git submodule init
git submodule update
```

Before running, make sure you create a conda environment from the provided environment.yml

```
# in the eln_packages_frontend directory:
conda env create -f environment.yml
conda activate ddomlabfrontend
python main.py
```

After installation, you can create a batch file to run this application quickly and easily on Windows

```
@echo off
conda activate your_environment_name

C:\Path\To\Conda\env\python.exe main.py
```