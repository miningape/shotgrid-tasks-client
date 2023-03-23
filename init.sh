#!/bin/bash

# Set up env and install deps
python -m venv env
source env/bin/activate
pip install -r requirements.txt

# Run code
python main.py