#!/bin/sh

# Set up env and install deps
python -m venv env
source env/bin/activate
pip install PySide6
pip install git+https://github.com/shotgunsoftware/python-api.git

# Run code
python main.py