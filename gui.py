from __future__ import annotations
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ttkbootstrap import Style
from ttkbootstrap.dialogs import Querybox
from typing import List
from logger import LogManager, VALID_LOG_TYPES
from save import export_json, export_csv, export_pdf, export_docx
from client_api import fetch_logs_from_api

class LogManagerApp:
    def __init__(self, root: tk.Tk):
        self.manager = LogManager()

        self.root = root
        self.root.title("TungLogger - Log Manager Pro Application")
        self.root.geometry("1500x750")
        self.style = Style("darkly")
        self.dark_mode = True

        self.nb = ttk.Notebook(self.root)
        self.tab_logs = ttk.Frame(self.nb)
        self.tab_export = ttk.Frame(self.nb)
        self.tab_api = ttk.Frame(self.nb)
        self.nb.add(self.tab_logs, text="Logs")
        self.nb.add(self.tab_export, text="Export")
        self.nb.add(self.tab_api, text="API")
        self.nb.pack(expand=True, fill="both")

        self._build_logs_tab()
        self._build_export_tab()
        self._build_api_tab()
        self._build_statusbar()
        self._apply_hover()

        ok, msg, _ = self.manager.refresh_from_db(limit=1000)
        self._status(msg)
        self._refresh_tree(self.manager.logs)

    def _build_statusbar(self):
        self.status = ttk.Label(self.root, text="Ready.", anchor="w")
        self.status.pack(side="bottom", fill="x", padx=8, pady=4)

    def _status(self, text: str):
        print(text)
        self.status.config(text=text)

    def _apply_hover(self):
        def on_enter(e): e.widget.config(cursor="hand2")
        def on_leave(e): e.widget.config(cursor="")
        for bttn in self.root.winfo_children():
            if isinstance(bttn, ttk.Widget):
                bttn.bind("<Enter>", on_enter)
                bttn.bind("<Leave>", on_leave)

    def _build_logs_tab(self):
        full_frame = ttk.Frame(self.tab_logs, padding=12)
        full_frame.pack(fill="both", expand=True)

        top = ttk.Frame(full_frame)
        top.pack(fill="x", pady=(0, 8))
        ttk.Label(top, text="Log message:").pack(side="left")
        self.ent_msg = ttk.Entry(top, width=60)
        self.ent_msg.pack(side="left", padx=6)
        self.cmb_type = ttk.Combobox(top, values=list(VALID_LOG_TYPES), width=10, state="readonly")
        self.cmb_type.set("INFO")
        self.cmb_type.pack(side="left", padx=6)
        ttk.Button(top, text="Save Log", command=self._save_log).pack(side="left", padx=6)
        ttk.Button(top, text="Filter…", command=self._open_filter).pack(side="left", padx=6)
        ttk.Button(top, text="Refresh", command=self._refresh_from_db).pack(side="left", padx=6)
        ttk.Button(top, text="Toggle Theme", command=self._toggle_theme).pack(side="right")

        self.tree = ttk.Treeview(full_frame, columns=("id", "type", "message", "host", "created"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("type", text="Type")
        self.tree.heading("message", text="Message")
        self.tree.heading("host", text="Hostname")
        self.tree.heading("created", text="Created At")
        self.tree.column("id", width=60, anchor="center")
        self.tree.column("type", width=90, anchor="center")
        self.tree.column("message", width=450)
        self.tree.column("host", width=160)
        self.tree.column("created", width=180)
        self.tree.pack(fill="both", expand=True)

    def _save_log(self):
        msg = self.ent_msg.get().strip()
        typ = self.cmb_type.get()
        if not msg:
            messagebox.showwarning("Validation", "Please enter a log message!")
            return
        ok, feedback, rec = self.manager.add_log(msg, typ)
        self._status(feedback)
        if ok and rec:
            messagebox.showinfo("Success", feedback)
            self._refresh_tree([rec] + self.manager.logs)
            self.ent_msg.delete(0, "end")
        else:
            messagebox.showerror("Error", feedback)

    def _open_filter(self):
        win = tk.Toplevel(self.root)
        win.title("Filter Logs")
        win.resizable(False, False)
        vars_ = []
        for t in VALID_LOG_TYPES:
            v = tk.BooleanVar(value=True)
            chk = ttk.Checkbutton(win, text=t, variable=v)
            chk.pack(anchor="w", padx=12, pady=6)
            vars_.append((t, v))

        def apply():
            selected = [t for (t, v) in vars_ if v.get()]
            if not selected:
                messagebox.showwarning("Filter", "Select at least one type!")
                return
            filtered = self.manager.filter_local(selected)
            self._refresh_tree(filtered)
            self._status(f"Filtered locally: {', '.join(selected)} ({len(filtered)} rows)")
            win.destroy()

        ttk.Button(win, text="Apply", command=apply).pack(pady=10)

    def _refresh_from_db(self):
        ok, msg, logs = self.manager.refresh_from_db(limit=300)
        self._status(msg)
        if ok:
            self._refresh_tree(logs)
        else:
            messagebox.showerror("DB Error", msg)

    def _refresh_tree(self, records):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for r in records:
            self.tree.insert("", "end", values=(r.id, r.log_type, r.log_message, r.hostname, str(r.created_at)))

    def _toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.style.theme_use("darkly" if self.dark_mode else "flatly")
        self._status("Successfully, theme changed!")

    def _build_export_tab(self):
        full_frame = ttk.Frame(self.tab_export, padding=16)
        full_frame.pack(fill="both", expand=True)

        ttk.Label(full_frame, text="Save current list as…").pack(anchor="center", pady=(0, 8))

        ttk.Button(full_frame, text="Export JSON", command=lambda: self._export("json")).pack(anchor="center", pady=6)
        ttk.Button(full_frame, text="Export CSV",  command=lambda: self._export("csv")).pack(anchor="center", pady=6)
        ttk.Button(full_frame, text="Export PDF",  command=lambda: self._export("pdf")).pack(anchor="center", pady=6)
        ttk.Button(full_frame, text="Export DOCX", command=lambda: self._export("docx")).pack(anchor="center", pady=6)
        ttk.Button(full_frame, text="Toggle Theme", command=self._toggle_theme).pack(side="right", padx=20, pady=100)

    def _export(self, kind: str):
        logs = self.manager.to_list_of_dicts()
        if not logs:
            messagebox.showwarning("Export", "There are no logs to export!")
            return
        exts = {
            "json": [("JSON", "*.json")],
            "csv":  [("CSV", "*.csv")],
            "pdf":  [("PDF", "*.pdf")],
            "docx": [("Word Document", "*.docx")],
        }
        path = filedialog.asksaveasfilename(defaultextension=f".{kind}", filetypes=exts.get(kind))
        if not path:
            return
        try:
            if kind == "json":
                export_json(logs, path)
            elif kind == "csv":
                export_csv(logs, path)
            elif kind == "pdf":
                export_pdf(logs, path)
            elif kind == "docx":
                export_docx(logs, path)
            messagebox.showinfo("Export", f"Exported to {kind.upper()} successfully.")
            self._status(f"Exported {len(logs)} logs to {path}.")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))
            self._status(f"Export failed: {e}")

    def _build_api_tab(self):
        full_frame = ttk.Frame(self.tab_api, padding=16)
        full_frame.pack(fill="both", expand=True)

        ttk.Label(full_frame, text="Server API Endpoint:").pack(anchor="center")
        self.ent_api = ttk.Entry(full_frame, width=120)
        self.ent_api.pack(anchor="center", pady=(5, 10))

        ttk.Button(full_frame, text="Fetch Logs", command=self._api_fetch).pack(anchor="center")
        ttk.Button(full_frame, text="Toggle Theme", command=self._toggle_theme).pack(side="right", padx=20, pady=100)

    def _api_fetch(self):
        endpoint = self.ent_api.get().strip()
        ok, msg, data = fetch_logs_from_api(endpoint)
        self._status(msg)
        if not ok:
            messagebox.showerror("API Error", msg)
            return

        items = []
        for row in data:
            t = str(row.get("log_type", "INFO")).upper()
            m = str(row.get("log_message", ""))
            if t in set(VALID_LOG_TYPES) and m:
                items.append((t, m))
        if not items:
            messagebox.showinfo("API", "Fetched data did not contain valid logs!")
            return

        ok2, msg2, count = self.manager.add_logs_bulk(items)
        self._status(msg2)
        if ok2:
            messagebox.showinfo("API", f"Imported {count} logs from API!")
            self._refresh_from_db()
        else:
            messagebox.showerror("Error, API Import!", msg2)