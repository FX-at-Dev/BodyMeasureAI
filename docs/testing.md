# Testing

Run the required quality checks from the repository root:

```powershell
.\.venv\Scripts\black.exe --check .
.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\mypy.exe src --explicit-package-bases
.\.venv\Scripts\pytest.exe
```

## Test principles

- Use pytest fixtures, `monkeypatch`, and deterministic fakes for OpenCV and MediaPipe.
- Do not require a physical camera, GPU, internet connection, or cloud service.
- Test worker signals and lifecycle behavior without running UI inference on the main thread.
- Exercise JSON round trips for persisted models and configuration.
- Add a regression test for every fixed defect when practical.
