# Development

## Environment

Use the same virtual environment as installation:

```powershell
.\.venv\Scripts\Activate.ps1
```

## Run the application

```powershell
python app.py
```

## Design constraints

- Prefer dependency injection for hardware and AI components.
- Keep public APIs backward compatible.
- Keep processing and rendering separate.
- Treat camera images and body data as sensitive local data.
- Profile before optimizing, especially for capture, inference, and paint work.

## Configuration for development

Use `BODYLENS_CONFIG_PATH` to point to an isolated JSON settings file. This avoids altering your normal local preferences while testing camera or AI setting combinations.

Use `BODYLENS_DEBUG=1` for debug logs. Do not commit generated `bodylens.json`, `logs/`, `exports/`, caches, or virtual environments.
