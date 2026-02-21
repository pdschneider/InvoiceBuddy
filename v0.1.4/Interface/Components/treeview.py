# Interface/Components/treeview.py
import os, logging
from pypdf import PdfReader
import customtkinter as ctk
if not hasattr(ctk, "CTkScrollableFrame"):
    logging.critical(f"CTkScrollableFrame missing.")
from Utils.load_settings import load_data_path
from customtkinter import CTkImage
from PIL import Image

class Treeview:
    def __init__(self, globals_obj, parent, get_dir=None):
        self.globals = globals_obj
        self.parent = parent
        self._rows = []
        self._selected = set()
        self._last_idx = None
        self._rename_bind_id = None

        if get_dir is None:
            self.get_dir = self.globals.sources["inbox"]
        elif callable(get_dir):
            self.get_dir = get_dir
        else:
            self.get_dir = lambda: str(get_dir)
        if not hasattr(self.globals, "file_identity"):
            self.globals.file_identity = {}
        self._build_ui()

    def _build_ui(self):
        try:
            self.selection_frame = ctk.CTkScrollableFrame(self.parent)
            self.selection_frame.pack(fill="both", expand=True, pady=0, padx=10)
        except Exception as e:
            self.selection_frame = ctk.CTkFrame(self.parent)
            self.selection_frame.pack(fill="both", expand=True, pady=0, padx=10)
            logging.critical(f"Could not create scrollable frame: {e}. Using regular CTkFrame instead.")

        folder_path = self.get_dir().strip()
        if folder_path:
            files = sorted(
                [f  for f in os.listdir(folder_path)
                    if os.path.isfile(os.path.join(folder_path, f))
                    and f.lower().endswith(".pdf")])
        else:
            logging.info(f"Inbox folder not found.")
            return

        for idx, file in enumerate(files):
            row = ctk.CTkFrame(self.selection_frame, height=42, corner_radius=8)
            row.pack(fill="x", padx=8, pady=3)

            base_name = os.path.splitext(file)[0]

            identity_state = {"cycle": 0}
            icons = [self.globals.invoice_icon, self.globals.card_icon, self.globals.po_icon]
            types = ["Invoice", "Card", "Purchase"]

            full_path = os.path.join(self.get_dir(), file)
            saved_type = self._load_identity(full_path)

            if saved_type in types:
                identity_state["cycle"] = types.index(saved_type)
            self.globals.file_identity[file] = saved_type

            identity = ctk.CTkButton(row, image=icons[identity_state["cycle"]], text=None, width=40)
            identity.configure(command=lambda s=identity_state, b=identity, f=file: 
                               self._cycle_identity(s, b, icons, f))
            identity.pack(side="left", padx=12, pady=8)

            label = ctk.CTkLabel(row, text=base_name, anchor="w")
            label.pack(side="left", padx=12, pady=8, fill="x", expand=True)
            self._rows.append((row, file))

            # Button Bindings
            row.bind("<Button-1>", lambda e, i = idx, f = file: self._on_row_click(e, i, f)) # Single Click
            label.bind("<Button-1>", lambda e, i = idx, f = file: self._on_row_click(e, i, f)) # Single Click

            row.bind("<Shift-Button-1>", lambda e, i = idx, f = file: self._on_shift_click(e, i, f), add = "+") # Shift Click
            label.bind("<Shift-Button-1>", lambda e, i = idx, f = file: self._on_shift_click(e, i, f), add = "+") # Shift Click

            row.bind("<Control-Button-1>",   lambda e, i=idx, f=file: self._on_ctrl_click(e, i, f), add="+") # Ctr Click
            label.bind("<Control-Button-1>", lambda e, i=idx, f=file: self._on_ctrl_click(e, i, f), add="+") # Ctr Click

            label.bind("<Double-1>",lambda e, l=label, f=file: self._start_rename(e, l, f, folder_path)) # Double click outside

    def _load_identity(self, filepath):
        """Read the Identity metadata from a PDF using pypdf. Returns 'Invoice' if missing."""
        try:
            reader = PdfReader(filepath)
            if reader.metadata:
                # Try our custom field first
                identity = reader.metadata.get("/Identity")
                if identity:
                    return str(identity)
                # Fallback to Subject if we used that
                subject = reader.metadata.get("/Subject")
                if subject:
                    return str(subject)
            return "Invoice"  # Default
        except Exception as e:
            logging.debug(f"Could not read metadata from {os.path.basename(filepath)}: {e}")
            return "Invoice"

    def _cycle_identity(self, state, button, icons, filename):
        state["cycle"] = (state["cycle"] + 1) % len(icons)
        new_icon = icons[state["cycle"]]
        button.configure(image=new_icon, text=None)

        types =["Invoice", "Card", "Purchase"]
        current_type = types[state["cycle"]]
        self.globals.file_identity[filename] = current_type
        logging.info(f"{filename} changed to {current_type}")

        self.selection_frame.bind("<Control-a>", lambda e: self._select_all(), add="+") # Ctr a
        self.selection_frame.bind("<Control-A>", lambda e: self._select_all(), add="+") # Ctr A

        self.selection_frame.focus_set()

    def _start_rename(self, event, label, filename, inbox_path):
        x = (label.winfo_rootx() - self.selection_frame.winfo_rootx())
        y = (label.winfo_rooty() - self.selection_frame.winfo_rooty())
        width = label.winfo_width()
        height = label.winfo_height()

        edit = ctk.CTkEntry(self.selection_frame, width=width - 20, height=height)
        edit.place(x=x + 0, y=y)
        base_name = os.path.splitext(filename)[0]
        edit.insert(0, base_name)
        edit.focus_set()
        edit.select_range(0, "end")

        root = self.parent.winfo_toplevel()

        def on_click_outside(ev):
            if not edit.winfo_exists():
                return
            try:
                ex, ey = edit.winfo_rootx(), edit.winfo_rooty()
                ew, eh = edit.winfo_width(), edit.winfo_height()
                if not (ex <= ev.x_root <= ex + ew and ey <= ev.y_root <= ey + eh):
                    _finish()
            except Exception as e:
                logging.warning(f"Entry widget error: {e}")

        self._rename_bind_id = root.bind("<Button-1>", on_click_outside, "+")
        bind_id = root.bind("<Button-1>", on_click_outside, "+")

        def _finish(ev=None):
            new_base_name = edit.get().strip()
            edit.destroy()
            root.unbind("<Button-1>", bind_id)
            if not new_base_name or new_base_name == base_name:
                return
            if getattr(ev, "keysym", None) == "Escape":
                return
            new_name = new_base_name + ".pdf"

            src_path = os.path.join(inbox_path, filename)
            dst_path = os.path.join(inbox_path, new_name)

            if os.path.exists(dst_path):
                logging.error(f"File {new_name} already exists.")
                return

            try:
                os.rename(src_path, dst_path)
                label.configure(text=new_base_name)
                # Update the stored filename to the new full name
                for i, (row, old_file) in enumerate(self._rows):
                    if old_file == filename:
                        self._rows[i] = (row, new_name)
                        break
                # Update selected set if this file was selected
                if filename in self._selected:
                    self._selected.remove(filename)
                    self._selected.add(new_name)
                logging.info(f"Renamed: {filename} → {new_name}")
            except Exception as e:
                logging.error(f"Rename failed: {e}")

            if hasattr(self, "_rename_bind_id"):
                root.unbind("<Button-1>", self._rename_bind_id)
                del self._rename_bind_id

        edit.bind("<Return>", _finish)
        edit.bind("<FocusOut>", _finish)
        edit.bind("<Escape>", lambda e: (root.unbind("<Button-1>", bind_id), edit.destroy()))

    def _apply_highlight(self, row, on=True):
        row.configure(fg_color="white" if on else "transparent")

    def _on_row_click(self, event, idx, filename):
        if event.state & 0x0001:
            return
        if event.state & 0x0004:
            return
        self.selection_clear()
        self._selected.add(filename)
        self._last_idx = idx
        row, _ = self._rows[idx]
        self._apply_highlight(row, on=True)
        self.selection_frame.focus_set()

    def selection_clear(self):
        for row, _ in self._rows:
            self._apply_highlight(row, on=False)
        self._selected.clear()
        self._last_idx = None

    def _on_shift_click(self, event, idx, filename):
        if self._last_idx is None:
            self._on_row_click(event, idx, filename)
            return
        start, end = sorted([self._last_idx, idx])
        self.selection_clear()
        for i in range(start, end + 1):
            row, name = self._rows[i]
            self._selected.add(name)
            self._apply_highlight(row, on=True)
        self._last_idx = idx

    def _on_ctrl_click(self, event, idx, filename):
        row, _ = self._rows[idx]
        if filename in self._selected:
            self._selected.remove(filename)
            self._apply_highlight(row, on=False)
        else:
            self._selected.add(filename)
            self._apply_highlight(row, on=True)
        self._last_idx = idx

    def _select_all(self):
        self.selection_clear()
        for row, name in self._rows:
            self._selected.add(name)
            self._apply_highlight(row,on=True)
        self._last_idx = len(self._rows) - 1 if self._rows else None

    def refresh(self, extension=None):
        for row, _ in self._rows:
            row.destroy()
        self._rows.clear()
        self.selection_clear()

        folder_path = self.get_dir().strip()
        if not os.path.isdir(folder_path):
            return
        files = [
            f for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f))
            and f.lower().endswith('.pdf')]
        if extension:
            files = [f for f in files if f.lower().endswith(extension)]

        for idx, file in enumerate(files):
            row = ctk.CTkFrame(self.selection_frame, height=42, corner_radius=8)
            row.pack(fill="x", padx=8, pady=3)

            base_name = os.path.splitext(file)[0]

            identity_state = {"cycle": 0}
            icons = [self.globals.invoice_icon, self.globals.card_icon, self.globals.po_icon]
            types = ["Invoice", "Card", "Purchase"]

            full_path = os.path.join(self.get_dir(), file)
            saved_type = self._load_identity(full_path)

            if saved_type in types:
                identity_state["cycle"] = types.index(saved_type)
            self.globals.file_identity[file] = saved_type

            identity = ctk.CTkButton(row, image=icons[identity_state["cycle"]], text=None, width=40)
            identity.configure(command=lambda s=identity_state, b=identity, f=file: 
                               self._cycle_identity(s, b, icons, f))
            identity.pack(side="left", padx=12, pady=8)

            label = ctk.CTkLabel(row, text=base_name, anchor="w")
            label.pack(side="left", padx=12, pady=8, fill="x", expand=True)
            self._rows.append((row, file))

            row.bind("<Button-1>", lambda e, i=idx, f=file: self._on_row_click(e, i, f))
            label.bind("<Button-1>", lambda e, i=idx, f=file: self._on_row_click(e, i, f))
            row.bind("<Shift-Button-1>", lambda e, i=idx, f=file: self._on_shift_click(e, i, f), add="+")
            label.bind("<Shift-Button-1>", lambda e, i=idx, f=file: self._on_shift_click(e, i, f), add="+")
            row.bind("<Control-Button-1>", lambda e, i=idx, f=file: self._on_ctrl_click(e, i, f), add="+")
            label.bind("<Control-Button-1>", lambda e, i=idx, f=file: self._on_ctrl_click(e, i, f), add="+")
            label.bind("<Double-1>", lambda e, l=label, f=file: self._start_rename(e, l, f, folder_path))

            self.selection_frame.focus_set()

    def selection(self):
        "Returns a list of the filenames the user has highlighted."
        return list(self._selected)
