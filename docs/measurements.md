# Measurements

## Supported measurement contract

The measurement interface supports these kinds:

- Height
- Chest
- Waist
- Hip
- Thigh
- Hand length
- Hand width
- Inseam
- Head circumference

`MeasurementRequest` identifies the requested kinds, pose landmarks, and optional calibration. `MeasurementEstimate` records a value in centimeters, confidence, and status. `MeasurementResult` groups estimates for a request.

## Current state

No measurement geometry or estimation algorithm has been implemented. `MeasurementEngine` intentionally raises `NotImplementedError` for calibration and estimation calls until an algorithm is validated.

## Implementation principles

- Keep all measurement logic in `src/ai/`.
- Keep UI code display-only.
- Use confidence and status rather than presenting uncertain values as facts.
- Require calibration where physical scale cannot be inferred safely.
- Keep measurement data local unless a user explicitly enables a future external feature.
