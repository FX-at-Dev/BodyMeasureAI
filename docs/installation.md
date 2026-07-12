# Installation

## Requirements

- Windows 10 or later.
- Python 3.11.
- A local camera supported by OpenCV.

## Setup

```powershell
git clone <repository-url>
Set-Location BodyMeasureAI
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

If PowerShell blocks activation, use the environment's Python executable directly:

```powershell
.\.venv\Scripts\python.exe app.py
```

## Configuration

At startup, BodyLens loads `bodylens.json` from the current working directory. Override the location with `BODYLENS_CONFIG_PATH`.

```json
{
  "camera": { "index": 0, "width": 1280, "height": 720, "fps": 30.0 },
  "ai": { "model_complexity": 1, "smooth_landmarks": true, "min_detection_confidence": 0.5, "min_tracking_confidence": 0.5 },
  "ui": { "theme": "dark", "show_landmark_ids": false },
  "export": { "directory": "exports", "json_indent": 2 }
}
```

Use `BODYLENS_DEBUG=1` to enable debug-level console and file logging. Logs rotate daily in `logs/`.
