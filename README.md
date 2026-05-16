# Blueprint Lens

Blueprint Lens is a Windows desktop helper that looks at a screenshot of your screen and turns it into a step-by-step visual guide. It is meant for people who want help using software without reading a long manual first.

Important things to know before you start:

- This app is built for Windows.
- You need internet access because the app sends your screenshot to a remote AI service for analysis.
- The app saves your previous guides in a local file called `saved_history.json`.
- VS Code is the recommended way to open the project, run the app, and edit the code later.

## What the app does

- Press a global hotkey to open the Blueprint Lens prompt.
- Type what you want to learn, or choose a specific area of the screen.
- The app captures your screen, sends it for AI analysis, and shows an overlay with suggested steps.
- You can click each step to highlight the matching part of the screen.
- You can save, export, import, and reopen past guides.

## What you need

Before installing the app, make sure you have:

- Windows 10 or Windows 11
- Python 3.10 or newer
- Internet access
- Permission to run apps that read your keyboard and take screenshots

## Recommended setup with VS Code

If you are new to coding, use VS Code for the easiest setup.

### 1) Install VS Code

1. Go to https://code.visualstudio.com/
2. Download and install Visual Studio Code for Windows
3. During installation, accept the default options

### 2) Open the project folder in VS Code

1. Start VS Code
2. Click Open Folder
3. Choose the folder that contains `contextual_ai_app.py`

### 3) Install Python if needed

If Python is not already installed, install it from the official website:

1. Go to https://www.python.org/downloads/
2. Download the latest Python 3 installer for Windows
3. During setup, check the box that says Add Python to PATH
4. Finish the installation

### 4) Open the VS Code terminal

In VS Code, open the terminal with Terminal > New Terminal.

### 5) Create a virtual environment

This keeps the app’s packages separate from the rest of your computer.

```powershell
python -m venv .venv
```

### 6) Turn on the virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

If Windows says script running is disabled, run this once in the same VS Code terminal and then try again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

### 7) Install the required Python packages

```powershell
python -m pip install --upgrade pip
pip install keyboard pyautogui requests pillow
```

### 8) Run the app

```powershell
python contextual_ai_app.py
```

When the app is running, you should see a message saying it is listening for `Ctrl+Shift+Q`.

## Optional setup without VS Code

Follow these steps in the folder that contains `contextual_ai_app.py`.

### 1) Open PowerShell in the project folder

If you are in File Explorer, open the project folder, click the address bar, type `powershell`, and press Enter.

### 2) Create a virtual environment

This keeps the app’s packages separate from the rest of your computer.

```powershell
python -m venv .venv
```

### 3) Turn on the virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

If Windows says script running is disabled, run this once in the same PowerShell window and then try again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

### 4) Install the required Python packages

```powershell
python -m pip install --upgrade pip
pip install keyboard pyautogui requests pillow
```

### 5) Run the app

```powershell
python contextual_ai_app.py
```

When the app is running, you should see a message saying it is listening for `Ctrl+Shift+Q`.

## How to use Blueprint Lens

1. Open the program you want help with.
2. Press `Ctrl+Shift+Q`.
3. Type what you want to do in the prompt window.
4. Choose one of these options:
   - Locate: analyze the whole screen and generate a guide
   - Ask a specific area: highlight a region first, then analyze it
   - Quick Inspect: click a single point on the screen to identify that UI element
5. Read the privacy notice and click Accept & Analyze.
6. Wait a few seconds while the app processes the screenshot.
7. Follow the overlay on the screen and click steps in the guide panel if you want the matching area highlighted.

## Useful buttons inside the app

- View History opens guides that were saved earlier.
- Import Guide loads a previously exported guide file.
- Continue Guide lets you ask for the next step after a guide is already open.
- Export Guide saves the current guide as a `.cguide` file.
- Done closes the overlay and returns you to the start screen.

## Troubleshooting

- If `python` is not recognized, reinstall Python and make sure Add Python to PATH was selected.
- If the hotkey does not work, restart PowerShell or VS Code as Administrator and try again.
- If the app cannot analyze the screen, check your internet connection.
- The app may not work on secure screens such as the Windows lock screen or UAC prompts.
- If you want to clear old guides, delete `saved_history.json` in the project folder.

## Files the app creates

- `saved_history.json` stores your local guide history.
- `.cguide` files are exported guides you can save and load later.

## If you want to edit the code later

You can open the folder in VS Code and change `contextual_ai_app.py`. The app is a Python/Tkinter desktop program, so changes are made directly in that file.