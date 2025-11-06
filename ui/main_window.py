import customtkinter as ctk
from tkinter import messagebox, filedialog
import json, threading, time, sqlite3
from pathlib import Path
import requests

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_FILE = DATA_DIR / 'history.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    url TEXT,
                    method TEXT,
                    headers TEXT,
                    body TEXT,
                    status_code INTEGER,
                    response_headers TEXT,
                    response_text TEXT,
                    elapsed REAL
                )''')
    conn.commit()
    conn.close()

init_db()

class ApiTesterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode('System')  # System, Light, Dark
        ctk.set_default_color_theme('blue')
        self.title('API Tester — CustomTkinter (SQLite history)')
        self.geometry('1100x720')
        self._build_ui()

    def _build_ui(self):
        # Top frame: inputs
        top = ctk.CTkFrame(self)
        top.pack(side='top', fill='x', padx=12, pady=12)

        self.url_var = ctk.StringVar()
        self.method_var = ctk.StringVar(value='GET')
        self.search_var = ctk.StringVar()

        ctk.CTkLabel(top, text='URL:').grid(row=0, column=0, sticky='w', padx=(6,4))
        ctk.CTkEntry(top, textvariable=self.url_var, width=760).grid(row=0, column=1, columnspan=3, sticky='w')

        ctk.CTkLabel(top, text='Method:').grid(row=1, column=0, sticky='w', pady=(8,0), padx=(6,4))
        ctk.CTkOptionMenu(top, values=['GET','POST','PUT','DELETE','PATCH'], variable=self.method_var).grid(row=1, column=1, sticky='w', pady=(8,0))

        ctk.CTkButton(top, text='Send Request', command=self._on_send_clicked).grid(row=1, column=2, padx=8, pady=(8,0))
        ctk.CTkButton(top, text='Clear', command=self._clear_fields).grid(row=1, column=3, padx=8, pady=(8,0))
        ctk.CTkButton(top, text='History', command=self._open_history_viewer).grid(row=1, column=4, padx=8, pady=(8,0))
        ctk.CTkButton(top, text='Theme', command=self._toggle_theme).grid(row=0, column=4, padx=8, pady=(4,0))

        # Main panes
        main_pane = ctk.CTkFrame(self)
        main_pane.pack(fill='both', expand=True, padx=12, pady=(0,12))

        left = ctk.CTkFrame(main_pane)
        left.pack(side='left', fill='both', expand=True, padx=(0,6))

        right = ctk.CTkFrame(main_pane)
        right.pack(side='right', fill='both', expand=True, padx=(6,0))

        ctk.CTkLabel(left, text='Headers (JSON)').pack(anchor='w', padx=6, pady=(6,0))
        self.headers_box = ctk.CTkTextbox(left, width=520, height=180)
        self.headers_box.pack(fill='both', expand=False, padx=6)

        ctk.CTkLabel(left, text='Body (JSON or text)').pack(anchor='w', padx=6, pady=(8,0))
        self.body_box = ctk.CTkTextbox(left, width=520, height=320)
        self.body_box.pack(fill='both', expand=True, padx=6, pady=(0,6))

        ctk.CTkLabel(right, text='Response Info').pack(anchor='w', padx=6, pady=(6,0))
        self.resp_meta = ctk.CTkTextbox(right, width=480, height=100)
        self.resp_meta.pack(fill='x', padx=6)

        ctk.CTkLabel(right, text='Response Body').pack(anchor='w', padx=6, pady=(8,0))
        self.resp_body = ctk.CTkTextbox(right, width=480, height=420)
        self.resp_body.pack(fill='both', expand=True, padx=6, pady=(0,6))

        # bottom bar
        bottom = ctk.CTkFrame(self)
        bottom.pack(side='bottom', fill='x', padx=12, pady=8)
        ctk.CTkButton(bottom, text='Save Response', command=self._save_response).pack(side='left')
        ctk.CTkButton(bottom, text='Export (.txt/.json)', command=self._save_response).pack(side='left', padx=6)
        self.status_label = ctk.CTkLabel(bottom, text='Ready')
        self.status_label.pack(side='left', padx=(20,4))

    def _toggle_theme(self):
        current = ctk.get_appearance_mode()
        ctk.set_appearance_mode('Dark' if current=='Light' else 'Light')

    def _set_status(self, txt):
        self.status_label.configure(text=txt)

    def _clear_fields(self):
        self.url_var.set('')
        self.method_var.set('GET')
        self.headers_box.delete('0.0','end')
        self.body_box.delete('0.0','end')
        self.resp_meta.delete('0.0','end')
        self.resp_body.delete('0.0','end')
        self._set_status('Cleared')

    def _on_send_clicked(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning('Validation', 'Please enter a URL')
            return
        method = self.method_var.get().upper()
        threading.Thread(target=self._send_request, args=(method, url), daemon=True).start()

    def _send_request(self, method, url):
        headers = {}
        body = None
        headers_raw = self.headers_box.get('0.0','end').strip()
        body_raw = self.body_box.get('0.0','end').strip()

        if headers_raw:
            try:
                headers = json.loads(headers_raw)
                if not isinstance(headers, dict):
                    raise ValueError('Headers must be JSON object/dict')
            except Exception as e:
                self.after(0, lambda: messagebox.showerror('Headers Error', f'Invalid JSON for headers:\n{e}'))
                self._set_status('Invalid headers JSON')
                return

        if body_raw:
            try:
                body = json.loads(body_raw)
            except Exception:
                body = body_raw

        self._set_status('Sending...')
        start = time.time()
        try:
            # ✅ FIX: Ensure URL has http/https prefix
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            resp = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=body if isinstance(body, (dict, list)) else None,
                data=body if isinstance(body, str) else None,
                timeout=30
            )
            elapsed = time.time() - start
            self.after(0, self._display_response, resp, elapsed)
            self._save_to_db(url, method, headers, body, resp, elapsed)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror('Request Error', str(e)))
            self._set_status('Error')

    def _display_response(self, resp, elapsed):
        self.resp_meta.delete('0.0','end')
        meta = f'Status: {resp.status_code}\nTime: {elapsed:.3f}s\nLength: {len(resp.content)} bytes\n'
        self.resp_meta.insert('0.0', meta)
        body = resp.text
        try:
            parsed = json.loads(body)
            pretty = json.dumps(parsed, indent=2, ensure_ascii=False)
        except Exception:
            pretty = body
        self.resp_body.delete('0.0','end')
        self.resp_body.insert('0.0', pretty)
        self._set_status(f'{resp.status_code} in {elapsed:.2f}s')

    def _save_response(self):
        body = self.resp_body.get('0.0','end').strip()
        if not body:
            messagebox.showinfo('Empty', 'No response to save')
            return
        path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON','*.json'),('Text','*.txt'),('All files','*.*')])
        if not path:
            return
        with open(path, 'w', encoding='utf-8') as f:
            f.write(body)
        messagebox.showinfo('Saved', f'Saved response to {path}')

    def _save_to_db(self, url, method, headers, body, resp, elapsed):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('INSERT INTO history (timestamp, url, method, headers, body, status_code, response_headers, response_text, elapsed) VALUES (datetime("now"),?,?,?,?,?,?,?,?)',
                  (url, method, json.dumps(headers, ensure_ascii=False), json.dumps(body, ensure_ascii=False) if isinstance(body, (dict,list)) else (body or ''), resp.status_code, json.dumps(dict(resp.headers), ensure_ascii=False), resp.text, elapsed))
        conn.commit()
        conn.close()

    def _open_history_viewer(self):
        viewer = ctk.CTkToplevel(self)
        viewer.title('Request History')
        viewer.geometry('1000x520')

        top = ctk.CTkFrame(viewer)
        top.pack(fill='x', padx=8, pady=8)

        ctk.CTkLabel(top, text='Filter by URL contains:').pack(side='left')
        search_entry = ctk.CTkEntry(top, textvariable=self.search_var, width=420)
        search_entry.pack(side='left', padx=6)
        ctk.CTkButton(top, text='Search', command=lambda: load_rows(tree, self.search_var.get())).pack(side='left', padx=6)
        ctk.CTkButton(top, text='Clear', command=lambda: (self.search_var.set(''), load_rows(tree, ''))).pack(side='left', padx=6)
        ctk.CTkButton(top, text='Clear History', command=lambda: clear_history(tree)).pack(side='right', padx=6)

        cols = ('id','ts','method','url','status','time')
        tree = ctk.CTkTreeview(viewer, columns=cols, show='headings', height=18)
        tree.heading('id', text='ID')
        tree.heading('ts', text='Timestamp')
        tree.heading('method', text='Method')
        tree.heading('url', text='URL')
        tree.heading('status', text='Status')
        tree.heading('time', text='Elapsed(s)')

        tree.column('id', width=50, anchor='center')
        tree.column('ts', width=160)
        tree.column('method', width=70, anchor='center')
        tree.column('url', width=440)
        tree.column('status', width=70, anchor='center')
        tree.column('time', width=80, anchor='center')

        tree.pack(fill='both', expand=True, padx=8, pady=(0,8))

        def load_rows(treeview, filter_text=''):
            for i in treeview.get_children():
                treeview.delete(i)
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            if filter_text:
                cur.execute('SELECT id, timestamp, method, url, status_code, elapsed FROM history WHERE url LIKE ? ORDER BY id DESC LIMIT 500', (f'%{filter_text}%',))
            else:
                cur.execute('SELECT id, timestamp, method, url, status_code, elapsed FROM history ORDER BY id DESC LIMIT 500')
            rows = cur.fetchall()
            conn.close()
            for r in rows:
                treeview.insert('', 'end', values=r)
        def clear_history(treeview):
            if not messagebox.askyesno('Confirm', 'Delete ALL history records? This cannot be undone.'):
                return
            conn = sqlite3.connect(DB_FILE)
            conn.execute('DELETE FROM history')
            conn.commit()
            conn.close()
            load_rows(treeview)
            messagebox.showinfo('Cleared', 'History cleared')
        def on_select(event):
            sel = tree.selection()
            if not sel:
                return
            item = tree.item(sel[0])['values']
            rec_id = item[0]
            self._show_history_details(rec_id)
        tree.bind('<<TreeviewSelect>>', on_select)
        load_rows(tree)

    def _show_history_details(self, record_id):
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute('SELECT id, timestamp, url, method, headers, body, status_code, response_headers, response_text, elapsed FROM history WHERE id=?', (record_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            messagebox.showinfo('Not found', 'Record not found')
            return
        win = ctk.CTkToplevel(self)
        win.title(f'History Record #{record_id}')
        win.geometry('900x650')

        text = ctk.CTkTextbox(win, width=880, height=520)
        text.pack(padx=8, pady=8)
        display = f"""ID: {row[0]}
Timestamp: {row[1]}
URL: {row[2]}
Method: {row[3]}

--- Request Headers ---\n{row[4]}
--- Request Body ---\n{row[5]}

--- Response (status {row[6]}) ---\nHeaders:\n{row[7]}

Body:\n{row[8]}

Elapsed: {row[9]}s
"""
        text.insert('0.0', display)
        def save_from_history():
            resp_body = row[8] or ''
            path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON','*.json'),('Text','*.txt')])
            if not path: return
            with open(path, 'w', encoding='utf-8') as f:
                f.write(resp_body)
            messagebox.showinfo('Saved', f'Response saved to {path}')
        btn = ctk.CTkButton(win, text='Save Response', command=save_from_history)
        btn.pack(pady=6)


if __name__ == '__main__':
    app = ApiTesterApp()
    app.mainloop()
