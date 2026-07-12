# Calibration

Calibration is required to convert image-space distances into physical measurements. It is not yet implemented as an algorithm or UI workflow.

## Current contract

`CalibrationData` stores:

- A named physical reference.
- Its known length in centimeters.
- Its measured image length in pixels.
- An optional centimeters-per-pixel scale.
- A confidence value.

`MeasurementEngine.calibrate()` defines the future interface that will turn a `CalibrationInput` into a calibration profile.

## Planned workflow

1. Ask the user to place a known reference in the capture scene.
2. Validate visibility, scale, camera angle, and reference detection quality.
3. Calculate and store a reusable local scale.
4. Display calibration confidence and require recalibration when conditions change.
5. Apply the calibration only to compatible camera geometry and measurement views.

## Accuracy policy

The project target is ±2 cm after calibration. This is a product goal, not a current guarantee. Any future calibration algorithm must be validated against controlled ground-truth data before results are presented as accurate estimates.
