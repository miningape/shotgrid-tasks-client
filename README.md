# Shotgrid tasks manager

## Installing & Running

If you are on Mac / Linux you can use the `run.sh` script to set up the environment, download dependencies (PySide6) and run the application.

Otherwise you will need to install dependencies using `pip install -r requirements.txt` (or pip install the dependecies as shown below) and run the application using `python main.py`. Optionally: use `python -m venv ...` to create a virtual environment.

## Requirements

- Python 3.7.16

## Dependencies

- PySide6
- Shotgrid's Python API (git+https://github.com/shotgunsoftware/python-api.git)

```bash
pip install PySide6
pip install git+https://github.com/shotgunsoftware/python-api.git
```

## Usage

This application allows you to download / upload files to / from Shotgrid tasks.

- On the first time running this application you will first need to input your Shotgrid url (e.g. https://<name>.shotgrid.autodesk.com/), then after clicking the button in the upper-righthand corder, you can input your credentials and log in.
- After a successful login, your credentials (and URL) are then saved to `.config.json` in the current working directory so you will not have to input them again.
- From the tasks list, you can download all the files from all the versions of that task, or you can upload a file on your disk to Shotgrid (this creates a new version of the task).
