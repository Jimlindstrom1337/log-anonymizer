import os
import threading
import tkinter.filedialog as fd

import customtkinter as ctk

from anonymizer import anonymize, deanonymize, Lexicon

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Log Anonymizer")
        self.geometry("740x580")
        self.minsize(540, 440)

        self._output_text = None
        self._selected_file = None
        self._lexicon = Lexicon()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        tabs = ctk.CTkTabview(self)
        tabs.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)

        tabs.add("Anonymisera fil")
        tabs.add("Återskapa original")

        self._build_anonymize_tab(tabs.tab("Anonymisera fil"))
        self._build_restore_tab(tabs.tab("Återskapa original"))

    # ------------------------------------------------------------------ #
    #  Tab 1 — Anonymisera fil
    # ------------------------------------------------------------------ #

    def _build_anonymize_tab(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(2, weight=1)

        file_frame = ctk.CTkFrame(parent)
        file_frame.grid(row=0, column=0, sticky="ew", pady=(12, 6))
        file_frame.grid_columnconfigure(0, weight=1)

        self._file_label = ctk.CTkLabel(
            file_frame, text="Ingen fil vald", anchor="w", text_color="gray"
        )
        self._file_label.grid(row=0, column=0, sticky="ew", padx=12, pady=10)

        ctk.CTkButton(
            file_frame, text="Välj fil…", width=110, command=self._browse
        ).grid(row=0, column=1, padx=(0, 10), pady=10)

        action_frame = ctk.CTkFrame(parent, fg_color="transparent")
        action_frame.grid(row=1, column=0, sticky="ew", pady=4)
        action_frame.grid_columnconfigure(1, weight=1)

        self._run_btn = ctk.CTkButton(
            action_frame,
            text="Anonymisera",
            width=140,
            state="disabled",
            command=self._start,
        )
        self._run_btn.grid(row=0, column=0, padx=(0, 12))

        self._progress = ctk.CTkProgressBar(action_frame)
        self._progress.grid(row=0, column=1, sticky="ew")
        self._progress.set(0)

        self._anon_status = ctk.CTkLabel(action_frame, text="", anchor="e", width=180)
        self._anon_status.grid(row=0, column=2, padx=(12, 0))

        self._table = ctk.CTkScrollableFrame(parent, label_text="Anonymiserade värden")
        self._table.grid(row=2, column=0, sticky="nsew", pady=8)
        self._table.grid_columnconfigure((0, 1, 2), weight=1)
        self._build_table_header()

        self._save_btn = ctk.CTkButton(
            parent,
            text="Spara anonymiserad fil…",
            state="disabled",
            command=self._save,
        )
        self._save_btn.grid(row=3, column=0, pady=(4, 12))

    def _browse(self):
        path = fd.askopenfilename(
            filetypes=[("Loggfiler", "*.log *.txt *.csv"), ("Alla filer", "*.*")]
        )
        if not path:
            return
        self._selected_file = path
        self._file_label.configure(
            text=os.path.basename(path), text_color=("gray10", "gray90")
        )
        self._run_btn.configure(state="normal")
        self._save_btn.configure(state="disabled")
        self._output_text = None
        self._lexicon = Lexicon()
        self._progress.set(0)
        self._anon_status.configure(text="")
        self._clear_table()

    def _start(self):
        self._run_btn.configure(state="disabled")
        self._save_btn.configure(state="disabled")
        self._anon_status.configure(text="Bearbetar…")
        self._progress.set(0)
        self._lexicon = Lexicon()
        self._clear_table()
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        try:
            with open(self._selected_file, encoding="utf-8", errors="replace") as f:
                text = f.read()
            self.after(0, lambda: self._progress.set(0.4))
            output, lexicon = anonymize(text, self._lexicon)
            self._output_text = output
            self._lexicon = lexicon
            self.after(0, lambda: self._on_done(lexicon.entries()))
        except Exception as exc:
            self.after(0, lambda: self._anon_status.configure(text=f"Fel: {exc}"))
            self.after(0, lambda: self._run_btn.configure(state="normal"))

    def _on_done(self, entries):
        self._progress.set(1.0)
        self._anon_status.configure(text=f"{len(entries)} värden ersatta")
        self._run_btn.configure(state="normal")
        self._save_btn.configure(state="normal")
        self._populate_table(entries)

    def _build_table_header(self):
        for col, title in enumerate(["Typ", "Original", "Anonymiserat"]):
            ctk.CTkLabel(
                self._table,
                text=title,
                font=ctk.CTkFont(weight="bold"),
                anchor="w",
            ).grid(row=0, column=col, sticky="ew", padx=8, pady=(4, 2))

    def _clear_table(self):
        for widget in self._table.winfo_children():
            widget.destroy()
        self._build_table_header()

    def _populate_table(self, entries):
        for i, e in enumerate(entries, start=1):
            bg = ("gray92", "gray18") if i % 2 == 0 else ("gray96", "gray16")
            type_display = e["replacement"].strip("[]")
            for col, val in enumerate([type_display, e["original"], e["replacement"]]):
                ctk.CTkLabel(
                    self._table,
                    text=val,
                    anchor="w",
                    fg_color=bg,
                    corner_radius=4,
                ).grid(row=i, column=col, sticky="ew", padx=4, pady=1)

    def _save(self):
        if not self._output_text:
            return
        base, ext = os.path.splitext(self._selected_file)
        path = fd.asksaveasfilename(
            defaultextension=ext or ".log",
            initialfile=os.path.basename(base) + "_anonymized" + (ext or ".log"),
            filetypes=[("Loggfiler", "*.log *.txt *.csv"), ("Alla filer", "*.*")],
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self._output_text)
            self._anon_status.configure(text="Sparad ✓")

    # ------------------------------------------------------------------ #
    #  Tab 2 — Återskapa original
    # ------------------------------------------------------------------ #

    def _build_restore_tab(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(
            parent,
            text="Klistra in text med anonymiserade värden (t.ex. ett svar från Claude):",
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", pady=(12, 4))

        self._restore_input = ctk.CTkTextbox(parent)
        self._restore_input.grid(row=1, column=0, sticky="nsew", pady=(0, 8))

        btn_row = ctk.CTkFrame(parent, fg_color="transparent")
        btn_row.grid(row=2, column=0, sticky="ew", pady=4)
        btn_row.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            btn_row,
            text="Återskapa original",
            width=180,
            command=self._restore,
        ).grid(row=0, column=0)

        self._restore_status = ctk.CTkLabel(btn_row, text="", anchor="w")
        self._restore_status.grid(row=0, column=1, padx=12)

        ctk.CTkLabel(
            parent,
            text="Text med återställda originalvärden:",
            anchor="w",
        ).grid(row=3, column=0, sticky="ew", pady=(8, 4))

        self._restore_output = ctk.CTkTextbox(parent, state="disabled")
        self._restore_output.grid(row=4, column=0, sticky="nsew", pady=(0, 12))

    def _restore(self):
        text = self._restore_input.get("1.0", "end").strip()
        if not text:
            self._restore_status.configure(text="Ingen text att återskapa.")
            return
        if not self._lexicon.entries():
            self._restore_status.configure(
                text="Anonymisera en fil först för att bygga upp lexikonet."
            )
            return
        result = deanonymize(text, self._lexicon)
        self._restore_output.configure(state="normal")
        self._restore_output.delete("1.0", "end")
        self._restore_output.insert("1.0", result)
        self._restore_output.configure(state="disabled")
        self._restore_status.configure(text="Klart ✓")


if __name__ == "__main__":
    app = App()
    app.mainloop()
