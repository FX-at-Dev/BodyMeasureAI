# Roadmap

## Current milestone

- Live camera preview.
- Configurable camera capture and reconnect behavior.
- QThread-based MediaPipe pose detection.
- Custom skeleton rendering.
- Typed models and measurement-engine interfaces.

## MVP next steps

1. Implement calibration using a validated physical reference workflow.
2. Implement measurement algorithms for height, hand size, chest, waist, hip, thigh, inseam, and head circumference.
3. Add confidence/quality checks and clear user guidance for captures.
4. Build review and results pages with editable measurement values.
5. Implement local JSON and CSV export.
6. Add local measurement-session storage and deletion controls.

## Validation and performance

- Validate the ±2 cm post-calibration target against representative ground-truth data.
- Profile camera acquisition, pose inference, and painting independently.
- Maintain a minimum 30 FPS experience where supported by available hardware.
- Expand hardware and resolution compatibility testing on Windows.

## Future exploration

- Hand and face mesh support.
- Depth estimation and 3D reconstruction.
- Measurement history.
- Optional, explicitly enabled cloud sync.
- macOS, Linux, Android, iOS, and web clients.
