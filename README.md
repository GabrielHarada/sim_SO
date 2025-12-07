pyinstaller:

windows:
pyinstaller --onefile --windowed main.py

ubuntu:
pyinstaller --onefile main.py --hidden-import='PIL._tkinter_finder'