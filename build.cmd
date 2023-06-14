@echo off
pyinstaller --onefile --add-data "images;images" --icon "images\icon.ico" timetracker.py