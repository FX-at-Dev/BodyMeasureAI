# AI and pose detection

## Current implementation

BodyLens uses MediaPipe Pose to detect normalized landmarks from BGR OpenCV frames. The detector converts frames to RGB before processing and returns landmark objects when a pose is available.

`PoseWorker` creates and owns the detector inside its `QThread`. This prevents MediaPipe inference from executing in `CameraWidget` or the Qt paint path.

## Configurable behavior

`AISettings` controls:

- `model_complexity` from 0 to 2.
- `smooth_landmarks`.
- `min_detection_confidence` from 0.0 to 1.0.
- `min_tracking_confidence` from 0.0 to 1.0.

## Rendering

BodyLens does not use MediaPipe drawing utilities. `PoseRenderer` uses Qt painting to draw rounded antialiased skeleton lines, confidence-colored joints, and optional landmark IDs. `MeasurementRenderer` accepts normalized overlay lines for future measurement display.

## Limitations

Pose landmarks are not measurements. Their accuracy depends on pose, camera placement, lighting, framing, clothing, occlusion, and calibration. The current implementation does not calculate body dimensions.
