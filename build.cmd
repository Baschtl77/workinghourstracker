@echo off
pip install -r requirements.txt
python -O -m PyInstaller --onefile --add-data "images;images" --icon "images\icon.ico" timetracker.py
copy logging_config.ini dist\