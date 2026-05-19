# Blueprint Lens

Blueprint Lens is a Windows desktop app that captures screenshots and turns them into step-by-step AI guidance. When the app launches, the main prompt opens automatically so you can start immediately.

## What it does

- Opens a prompt window on launch
- Analyzes a full-screen screenshot from your typed prompt
- Lets you choose a specific area before analysis
- Supports quick screenshot-based follow-up with `Ctrl+Shift+Q`
- Saves guide history locally in `saved_history.json`
- Lets you view, import, export, and continue guides

## Requirements

- Windows
- Python 3.x
- Internet access
- Permission to capture screenshots and listen for global hotkeys

## Install

If you want the simplest setup, use VS Code. You do not need VS Code to run the app, but it makes setup easier.

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

The prompt window should appear immediately after launch.

## How to use

1. Type a question into the main prompt.
2. Use `Send` to analyze the current screenshot.
3. Use `Locate` if you want the app to analyze the full screenshot after the consent step.
4. Use `Snip` if you want to highlight a specific region first.
5. Use `View History` to reopen saved guides.
6. Use `Import Guide` to load a previously exported `.cguide` or `.json` file.
7. Use `Quick Inspect` to click a point on the screen and analyze the nearby UI.

## Hotkey behavior

- `Ctrl+Shift+Q` is now a quick screenshot shortcut.
- It closes the visible UI first so the capture is clean.
- It then opens the continuation prompt with the screenshot preview.
- In that window, `Go Back` returns you to the app and `Accept` continues with analysis.

## Files

- `contextual_ai_app.py` is the main app.
- `saved_history.json` stores your local guide history.
- `output/` is used for generated output.
- `backup/` contains older copies of the app.

## Notes

- The app relies on a remote AI service for analysis, so internet access is required.
- Closing the app window exits the program.
- If you start it from a terminal and close the terminal, the app process ends with it.
