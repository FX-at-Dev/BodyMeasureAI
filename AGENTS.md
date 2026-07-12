# BodyLens Engineering Guide

You are a senior software engineer working on BodyLens.

## Product

BodyLens is a desktop AI application that estimates human body measurements from camera images.

Primary platform:
- Windows (first)
- macOS (later)
- Linux (later)

Future:
- Android
- iOS
- Web

---

## Stack

Python 3.11

PySide6

OpenCV

MediaPipe

NumPy

PyTest

Black

Ruff

Mypy

---

## Architecture

src/

    ai/
        pose_detector.py
        measurement_engine.py
        calibration.py

    workers/
        pose_worker.py

    renderers/
        pose_renderer.py
        overlay_renderer.py

    services/
        camera_service.py

    models/

    ui/
        pages/
        widgets/
        windows/

    utils/

tests/

assets/

exports/

---

## Rules

Never change folder structure.

Never rename existing modules unless instructed.

Never introduce unnecessary dependencies.

Always maintain backward compatibility.

Never block the Qt GUI thread.

All AI inference runs inside QThread workers.

Never use cv2.imshow().

Never use MediaPipe drawing utilities.

Rendering belongs only in renderers/.

Measurement logic belongs only in ai/.

UI only displays data.

Never mix UI and AI.

---

## Code Quality

Every change MUST pass:

black .

ruff check .

mypy src --explicit-package-bases

pytest

---

## Style

Use:

Python 3.11

PEP8

Type hints everywhere

Docstrings

Small methods

Dependency injection where appropriate

---

## Performance

Target:

30 FPS minimum

60 FPS preferred

No UI freezes

No blocking operations

Reuse objects whenever possible.

---

## Security

No telemetry.

No cloud calls.

No hidden uploads.

Everything runs locally unless explicitly enabled.

---

## Goal

Produce production-quality code.

Never generate placeholder implementations if a real implementation is reasonable.