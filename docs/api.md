# API reference

The project currently exposes Python modules rather than a public network API. All interfaces run locally.

## Camera service

`CameraService(camera_index=0, resolution=None, fps=None)` manages an OpenCV capture device.

- `start() -> bool`: opens the selected device and applies settings.
- `stop() -> None`: safely releases the capture handle.
- `get_frame() -> Frame | None`: returns a BGR frame; safely attempts throttled reconnects after failure.
- `set_camera_index(index) -> bool`, `set_resolution(width, height) -> bool`, and `set_fps(fps) -> bool`: update capture preferences.
- `capture(filename) -> bool`: saves the most recently read frame.
- `last_error`: the most recent recoverable camera error, if any.

## Pose worker

`PoseWorker` is a `QThread` that owns a `PoseDetector`.

- `submit_frame(frame, frame_id)`: queues the newest BGR frame.
- `landmarks_ready(object, int)`: emits landmarks and their frame identifier.
- `inference_failed(str, int)`: emits recoverable inference failures.
- `inference_finished(int)`: marks a request complete.
- `stop()`: requests asynchronous shutdown.

## Configuration

`src.config.load_settings()` returns immutable `AppSettings` loaded from JSON. `ConfigurationManager.save()` persists a settings object atomically.

Configuration sections are `camera`, `ai`, `ui`, and `export`. See [Installation](installation.md#configuration).

## Domain models

`src.models` exports `Landmark`, `PoseFrame`, `CalibrationData`, `Measurement`, `MeasurementResult`, `BodyProfile`, and `ExportProfile`. Each model has `to_dict()` and `from_dict()` methods for JSON-safe local persistence.
