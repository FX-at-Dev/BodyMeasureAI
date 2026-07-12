# Contributing

## Before you begin

- Read `AGENTS.md` and `PROJECT_CONTEXT.md`.
- Preserve the existing folder structure and module names.
- Do not introduce cloud calls, telemetry, hidden uploads, or unnecessary dependencies.
- Keep camera and body data local by default.

## Engineering rules

- Use Python 3.11, type hints, and concise docstrings.
- Run AI inference in `QThread` workers only.
- Do not block the Qt GUI thread or `paintEvent()`.
- Do not use `cv2.imshow()` or MediaPipe drawing utilities.
- Keep rendering in `renderers/`, measurement logic in `ai/`, and UI presentation in `ui/`.

## Development workflow

1. Create focused changes with tests.
2. Format and lint the relevant files.
3. Run the required project checks.
4. Keep commits small and describe behavior, not implementation trivia.

See [Development](development.md) and [Testing](testing.md) for commands.
