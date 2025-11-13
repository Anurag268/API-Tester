

# 🧪 Python API Tester – CustomTkinter + SQLite

A modern, Postman-like **API testing desktop application** built using **Python**, **CustomTkinter**, and **SQLite**.
This tool allows users to send HTTP requests (GET, POST, PUT, DELETE, PATCH), inspect responses, save history, parse cURL commands, and view/export data – all in a clean GUI interface.

---

## 🚀 Features

### 🔹 Core Functionality

* Send HTTP **GET, POST, PUT, DELETE, PATCH** requests
* Enter **URL**, **headers (JSON)**, and **request body (JSON/Text)**
* Pretty-printed JSON response
* Shows:

  * Response Status
  * Response Time
  * Response Length
  * Headers
  * Body

---

### 🔹 History System (SQLite)

* Every request + response is saved automatically
* Includes:

  * URL
  * Method
  * Headers
  * Body
  * Status Code
  * Response Body
  * Response Time
  * Timestamp
* Built-in History Viewer

  * Filter by URL substring
  * Select a history entry to view full details
  * Export saved response
  * Clear entire history

---

### 🔹 Modern CustomTkinter GUI

* Dark/Light/System theme support
* Responsive layout
* Styled TextBoxes & Buttons
* Status bar updates

---

### 🔹 cURL Parser (Paste → Auto-Fill)

Paste a `curl` command into the clipboard, click **Paste cURL**, and the app will extract:

* URL
* Method
* Headers
* Body

Examples it detects:

```bash
curl -X POST https://api.example.com -H "Content-Type: application/json" -d "{\"key\":\"value\"}"
```

---

### 🔹 Export Options

* Save response as **JSON / TXT**
* Save historical responses as JSON

---

### 🔹 Quality-of-life Features

* Auto-adds `https://` when missing
* Strip quotes and whitespace from URL
* Prevents malformed headers
* Multi-threaded requests (GUI never freezes)

---

## 📂 Project Structure

```
API-Tester/
│── main.py
│── ui/
│   └── main_window.py
│── data/
│   └── history.db
│── assets/ (optional icons)
│── README.md
│── requirements.txt
```

---

# ⚙️ Installation & Setup

### 1. Clone the project

```bash
git clone https://github.com/yourusername/api-tester.git
cd api-tester
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

(If `customtkinter` fails via pip → install manually: `pip install customtkinter`)

### 4. Run the app

```bash
python main.py
```

---

# 🖥️ How to Use the Application

### 1. Enter Request Details

* Enter the **URL**
* Select the **Method**
* Add optional **Headers (JSON object)**
* Add optional **Request Body (JSON or plain text)**

### 2. Send Request

Click **Send Request**
App sends the request in a separate thread.

### 3. View Response

Right panel shows:

* Status Code
* Time taken
* Response Length
* Headers
* Response Body
  (JSON pretty printed automatically)

### 4. Save Response

Click **Save Response** → export as `.json` or `.txt`.

### 5. View History

Click **History** to:

* Browse saved requests
* Filter by URL
* Double-click to view full details
* Save an old response
* Clear all request history

### 6. Paste cURL

Copy any CURL command → click **Paste cURL**
Fields auto-fill instantly.

---

# 📘 Functionality Breakdown (All Functions Explained)

---

## `init_db()`

Creates SQLite database & table:

* id
* timestamp
* url
* method
* headers
* body
* status_code
* response_headers
* response_text
* elapsed

---

## `_build_ui()`

Creates all GUI components:

* URL entry
* Method dropdown
* Headers input
* Body input
* Response display
* Status bar
* Buttons (Send, Clear, History, Theme, Save Response)

---

## `_toggle_theme()`

Switches between:

* Light
* Dark

---

## `_set_status(text)`

Updates status label at bottom.

---

## `_clear_fields()`

Clears:

* URL
* Method
* Body
* Headers
* Response outputs

---

## `_on_send_clicked()`

Validates URL & starts a background thread:

```python
threading.Thread(target=self._send_request, ...)
```

---

## `_send_request()`

Handles:

* Cleaning URL
* Parsing headers/body
* Sending API request
* Saving to DB
* Updating UI

Also auto-adds:

```python
if not url.startswith(('http://', 'https://')):
    url = "https://" + url
```

---

## `_display_response()`

Updates:

* Response Info
* Response Body
* Pretty JSON

---

## `_save_response()`

Opens file dialog → writes response to `.json` or `.txt`.

---

## `_save_to_db()`

Inserts request+response into SQLite.

---

## `_open_history_viewer()`

Displays:

* Treeview list of history
* Filter input
* Clear history button
* Click row → open details window

Uses `ttk.Treeview` (since CustomTkinter does not include Treeview).

---

## `_show_history_details(record_id)`

Opens a new window showing:

* URL
* Method
* Headers
* Body
* Response Headers
* Response Body
* Response Time
* Export option

---

## `_paste_curl()`

Parses full cURL command using `shlex.split`:

* Extracts method (`-X`)
* Extracts URL
* Extracts headers (`-H`)
* Extracts data (`-d`, `--data`, `--data-raw`)
* Auto-populates all fields

---


# 🛠️ Requirements

Contents of `requirements.txt`:

```
requests
customtkinter
```

SQLite and Tkinter come built-in with Python.

---

# 🧩 Future Enhancements

* Tabs for multiple requests
* Syntax highlighting
* Code “raw view” toggle
* Import/export request collections
* Auto-generated Python/cURL/Postman snippets
* Dark-mode optimized Treeview fonts

---

# ⭐ License

MIT License (or any license you prefer)

---

