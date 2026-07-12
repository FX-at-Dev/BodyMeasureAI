# BodyLens

BodyLens is a privacy-first Windows desktop application for estimating body measurements from camera images. It runs locally with PySide6, OpenCV, and MediaPipe; it does not send camera frames to a cloud service.

> **Project status:** active MVP development. Live camera preview, threaded pose detection, skeleton rendering, configuration, logging, and typed data contracts are available. Measurement and calibration algorithms, review screens, and exports are designed but not yet implemented.

## Highlights

- Local webcam capture with resolution, FPS, camera-index, and reconnect support.
- MediaPipe pose inference isolated in a `QThread` worker.
- Antialiased pose skeleton with confidence-colored joints and optional landmark IDs.
- JSON-backed application configuration and daily rotating local logs.
- Strongly typed, JSON-safe models for landmarks, poses, calibration, measurements, profiles, and exports.

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Set `BODYLENS_DEBUG=1` before launch to enable debug logging. BodyLens loads `bodylens.json` from the working directory automatically; `BODYLENS_CONFIG_PATH` can point to another configuration file.

## Documentation

- [Installation](docs/installation.md)
- [Development](docs/development.md)
- [Architecture](docs/architecture.md)
- [API reference](docs/api.md)
- [AI and pose detection](docs/ai.md)
- [Calibration](docs/calibration.md)
- [Measurements](docs/measurements.md)
- [Roadmap](docs/roadmap.md)
- [Testing](docs/testing.md)
- [Contributing](docs/contributing.md)
- [Change log](docs/changelog.md)

## Privacy and accuracy

Camera data stays on the local machine unless a future, explicitly enabled feature changes that policy. BodyLens is not a medical device. The target accuracy is ±2 cm after calibration, but that target has not yet been validated or reached by an implemented measurement engine.
