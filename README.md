# Blueprint Lens

Blueprint Lens is a Windows desktop app that captures screenshots and turns them into step-by-step AI guidance. It is a student project, and the simplest way to use it is to download the `.exe` and run it.

## What it does

- Opens a prompt window on launch
- Analyzes a full-screen screenshot from your typed prompt
- Lets you choose a specific area before analysis
- Supports quick screenshot-based follow-up with `Ctrl+Shift+Q`
- Saves guide history locally in `saved_history.json`
- Lets you view, import, export, and continue guides

## Requirements

- Windows
- Internet access
- Permission to capture screenshots and listen for global hotkeys

## Quick Start

1. Download the app executable.
2. Run the `.exe` on Windows.
3. The main prompt opens right away so you can start asking questions.

If Windows Defender or another antivirus warns about the executable, make sure the file really came from this project and only proceed if you trust it. The app is a student-built project and does not include intentional malicious code.

## Install

You only need the Python setup below if you want to run or rebuild the source version.

### Using VS Code

1. Install VS Code from https://code.visualstudio.com/
2. Open the folder that contains `contextual_ai_app.py`
3. Open the terminal in VS Code
4. Create a virtual environment:

```powershell
python -m venv .venv
```

5. Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If Windows blocks script execution, run this once in the same terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

6. Install the required packages:

```powershell
python -m pip install --upgrade pip
pip install keyboard pyautogui requests pillow
```

### Without VS Code

Open a terminal in the project folder and run the same commands above.

## Run

Start the app with:

```powershell
python contextual_ai_app.py
```

The prompt window should appear immediately after launch. If you are using the `.exe`, just double-click it instead of running the Python file.

## How to use

1. Type a question into the main prompt.
2. Use `Send` to analyze the current screenshot.
3. Use `Ask a specific area` if you want to highlight a specific region first.
4. Use `View History` to reopen saved guides.
5. Use `Import Guide` to load a previously exported `.cguide` or `.json` file.
6. Press `Enter` to send faster. If skip preview is off, the app shows a confirmation screen and you press `Enter` again to confirm.
7. Open `Extra settings` only when you need developer controls like the secret code, debug limit, or skip preview.

## Hotkey behavior

- `Ctrl+Shift+Q` is now a quick screenshot shortcut.
- It closes the visible UI first so the capture is clean.
- It then opens the continuation prompt with the screenshot preview.
- In that window, `Go Back` returns you to the app and `Accept` continues with analysis.

## Files

- `contextual_ai_app.py` is the main app.
- `saved_history.json` stores your local guide history.
- `output/` is used for generated output.
- `contextual_ai_app.spec` is the PyInstaller build recipe for the executable.
- `build/` contains generated build artifacts and can be deleted if you only want the source.

## Notes

- The app relies on a remote AI service for analysis, so internet access is required.
- Closing the app window exits the program.
- If you start it from a terminal and close the terminal, the app process ends with it.
- `Ctrl+Shift+Q` opens the quick screenshot flow while the app is still running.
