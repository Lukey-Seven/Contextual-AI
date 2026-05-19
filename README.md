@@ -7,7 +7,7 @@ Important things to know before you start:
- This app is built for Windows.
- You need internet access because the app sends your screenshot to a remote AI service for analysis.
- The app saves your previous guides in a local file called `saved_history.json`.
- You do not need VS Code to run the app, but it can help if you want to edit the code later.
- VS Code is the recommended way to open the project, run the app, and edit the code later.

## What the app does

@@ -26,14 +26,71 @@ Before installing the app, make sure you have:
- Internet access
- Permission to run apps that read your keyboard and take screenshots

If you do not have Python yet, install it from the official website:
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

## Install the app from scratch
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

@@ -68,9 +125,7 @@ python -m pip install --upgrade pip
pip install keyboard pyautogui requests pillow
```

## Run the app

After the packages finish installing, start the program with:
### 5) Run the app

```powershell
python contextual_ai_app.py