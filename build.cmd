@echo off
pip install -r requirements.txt
pyinstaller --onefile --add-data "images;images" --icon "images\icon.ico" timetracker.py