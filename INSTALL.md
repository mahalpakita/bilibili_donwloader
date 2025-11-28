Install and Build

This project can be installed locally (so you get a `bbl-dl` command) or packaged into a wheel/executable.

Prerequisites
- Python 3.7+
- pip and build tools
- (Optional) For creating an executable: `pyinstaller`

Quick local install (editable/development):

```powershell
# from project root (where pyproject.toml is located)
python -m pip install -e .
```

Quick local install (normal):

```powershell
python -m pip install .
```

After installation you will have two scripts on PATH (Windows will create .exe wrappers):
- `bbl-dl` — run in CLI mode: `bbl-dl <URL> [--output DIR] [--audio-only]`
- `bbl-dl-gui` — launch the GUI: `bbl-dl-gui`

Build a wheel (optional):

```powershell
python -m pip install build
python -m build
# the wheel will be in the 'dist' folder
```

Create a single-file Windows executable (optional)

```powershell
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed bbl_dl.py
# resulting exe in 'dist' folder
```

Notes
- The installer does not bundle FFmpeg; you must install FFmpeg separately for merging and audio extraction.
- Make sure `yt-dlp` is up-to-date:

```powershell
python -m pip install -U yt-dlp
```
