# API Tester (CustomTkinter) — Runnable Version

This is a modern desktop API testing tool built with CustomTkinter (dark/light themes).
It supports GET/POST/PUT/DELETE/PATCH and stores history in an SQLite database (`data/history.db`).

## Quickstart
1. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS / Linux
   venv\\Scripts\\activate  # Windows
   ```
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
   If pip cannot find `customtkinter`, install via:
   ```bash
   pip install customtkinter
   ```
3. Run the app:
   ```bash
   python main.py
   ```

## Features
- Modern UI with CustomTkinter (dark/light mode toggle)
- Enter URL, choose method, optional headers (JSON) and body (JSON or text).
- Send request and view status, headers, body, and elapsed time.
- Request history persisted in `data/history.db` with in-app viewer.
- Filter history by URL substring, inspect and export saved responses.
