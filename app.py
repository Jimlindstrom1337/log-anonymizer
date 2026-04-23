import os
import threading
import tkinter.filedialog as fd
import random
import tkinter as tk

import customtkinter as ctk
from tkinterdnd2 import TkinterDnD, DND_FILES

from anonymizer import anonymize, deanonymize, Lexicon

# ── Telavox brand palette ──────────────────────────────────────────────────
TV_GREEN        = "#2EC266"
TV_GREEN_HOVER  = "#25A556"
TV_BG           = "#1A1E2C"
TV_PANEL        = "#242838"
TV_PANEL_ALT    = "#2C3146"
TV_DROP_IDLE    = "#2C3146"
TV_DROP_ACTIVE  = "#1E3D2F"   # green-tinted glow when dragging over
TV_TEXT         = "#FFFFFF"
TV_SUBTEXT      = "#9AA0B4"
TV_ROW_A        = "#262B3C"
TV_ROW_B        = "#2A3050"

# Type chip colors
TYPE_CHIP = {
    "Telefon":       ("#1D4ED8", "#93C5FD"),   # blue
    "E-post":        ("#6D28D9", "#C4B5FD"),   # purple
    "Personnummer":  ("#92400E", "#FCD34D"),   # amber
    "IP-adress":     ("#991B1B", "#FCA5A5"),   # red
    "IPv6":          ("#9D174D", "#F9A8D4"),   # pink
    "UniqueID":      ("#065F46", "#6EE7B7"),   # teal
}
TYPE_LABELS = {
    "phone": "Telefon",
    "email": "E-post",
    "personnummer": "Personnummer",
    "ip_address": "IP-adress",
    "ipv6": "IPv6",
    "unique_id": "UniqueID",
}

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

FONT_BODY   = ("Inter", 13)
FONT_LABEL  = ("Inter", 12)
FONT_BOLD   = ("Inter", 13, "bold")
FONT_TITLE  = ("Inter", 22, "bold")
FONT_CHIP   = ("Inter", 11, "bold")

DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")


def green_btn(parent, text, command, width=160, state="normal"):
    return ctk.CTkButton(
        parent, text=text, command=command, width=width, height=36,
        state=state, font=FONT_BOLD,
        fg_color=TV_GREEN, hover_color=TV_GREEN_HOVER,
        text_color=TV_TEXT, corner_radius=8,
    )


def ghost_btn(parent, text, command, width=160, state="normal"):
    return ctk.CTkButton(
        parent, text=text, command=command, width=width, height=36,
        state=state, font=FONT_LABEL,
        fg_color=TV_PANEL_ALT, hover_color=TV_PANEL,
        text_color=TV_TEXT, border_width=1, border_color=TV_GREEN,
        corner_radius=8,
    )



class ConfettiOverlay:
    """Confetti bursting from the Invest button using tiny per-particle Frame
    widgets — no blocking canvas, so the rest of the UI stays fully interactive."""

    COLORS = ["#FF1744", "#F50057", "#00BCD4", "#2EC266", "#FFD600", "#FF6F00", "#9C27B0"]

    def __init__(self, parent, origin_widget):
        self.parent = parent
        self.running = True
        self.particles = []

        parent.update()
        bx = origin_widget.winfo_rootx() - parent.winfo_rootx() + origin_widget.winfo_width() // 2
        by = origin_widget.winfo_rooty() - parent.winfo_rooty() + origin_widget.winfo_height() // 2

        for _ in range(35):
            size = random.randint(4, 8)
            widget = tk.Frame(parent, bg=random.choice(self.COLORS), width=size, height=size)
            widget.place(x=bx, y=by)
            self.particles.append({
                'w': widget,
                'x': float(bx), 'y': float(by),
                'vx': random.uniform(-6, 6),
                'vy': random.uniform(-7, 0.5),
            })

        self._win_h = parent.winfo_height()
        self._animate()
        parent.after(1500, self._close)

    def _animate(self):
        if not self.running:
            return
        for p in self.particles:
            p['vx'] *= 0.91
            p['vy'] = p['vy'] * 0.91 + 0.12
            p['x'] += p['vx']
            p['y'] += p['vy']
            if p['y'] < self._win_h + 20:
                p['w'].place(x=int(p['x']), y=int(p['y']))
        self.parent.after(30, self._animate)

    def _close(self):
        self.running = False
        for p in self.particles:
            try:
                p['w'].destroy()
            except Exception:
                pass
        self.particles.clear()
        if getattr(self.parent, '_confetti', None) is self:
            self.parent._confetti = None


class App(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__(fg_color=TV_BG)
        self.TkdndVersion = TkinterDnD._require(self)
        self.title("Telavox — Log Anonymizer")
        self.geometry("800x640")
        self.minsize(600, 500)

        self._output_text = None
        self._selected_file = None
        self._lexicon = Lexicon()
        self._animating = False

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_tabs()

    def _show_confetti(self):
        if getattr(self, '_confetti', None):
            self._confetti._close()
        self._confetti = ConfettiOverlay(self, self._invest_btn)
        self._display_meme()

    _MEMES = [
        ("TELAVOX COIN", "GARANTERAT TILL MÅNEN 🚀"),
        ("BITCOIN? NEJ TACK", "JAG SATSAR PÅ TELAVOX COIN"),
        ("NÄR TELAVOX COIN DIPPAR", "DET ÄR BARA EN TILLFÄLLIG REA"),
        ("MIN INVESTERINGSSTRATEGI", "100% TELAVOX COIN"),
        ("CHEFEN: VAD GÖR DU?", "JAG KÖPER TELAVOX COIN"),
        ("TELAVOX COIN IDAG", "FERRARI IMORGON 🏎️"),
        ("WARREN BUFFETT HADE FEL", "HAN KÖPTE INTE TELAVOX COIN"),
        ("FAMILJEN: KOM PÅ MIDDAG", "JAG: TELAVOX COIN PUMPAR"),
        ("ETT LITET KÖP AV TELAVOX COIN", "ÄR DET VERKLIGEN FARLIGT?"),
        ("NÄR ALLA FRÅGAR OM AKTIER", "DU: HAR NI HÖRT OM TELAVOX COIN?"),
        ("TELAVOX COIN -50%", "BRA, NU KAN JAG KÖPA MER"),
        ("SÖMN ÄR FÖR DEM", "SOM INTE ÄGER TELAVOX COIN"),
    ]

    def _display_meme(self):
        top, bottom = random.choice(self._MEMES)

        popup = ctk.CTkToplevel(self)
        popup.title("Telavox Coin Meme")
        popup.configure(fg_color=TV_BG)
        popup.resizable(False, False)
        popup.transient(self)
        popup.grab_set()

        # Green top accent
        ctk.CTkFrame(popup, height=6, fg_color=TV_GREEN, corner_radius=0).pack(fill="x")

        # X button
        ctk.CTkButton(
            popup, text="✕", width=32, height=32,
            fg_color=TV_PANEL_ALT, hover_color="#FF4444",
            text_color=TV_TEXT, font=FONT_BOLD, corner_radius=6,
            command=popup.destroy,
        ).pack(anchor="ne", padx=8, pady=(8, 0))

        # Top text
        ctk.CTkLabel(
            popup, text=top, wraplength=380,
            font=("Impact", 36),
            text_color=TV_TEXT,
        ).pack(padx=24, pady=(16, 8))

        # Divider
        ctk.CTkFrame(popup, height=2, fg_color=TV_PANEL_ALT, corner_radius=0).pack(fill="x", padx=24)

        # Bottom text
        ctk.CTkLabel(
            popup, text=bottom, wraplength=380,
            font=("Impact", 32),
            text_color=TV_GREEN,
        ).pack(padx=24, pady=(8, 24))

        # Green bottom accent
        ctk.CTkFrame(popup, height=6, fg_color=TV_GREEN, corner_radius=0).pack(fill="x")

    # ── Header ─────────────────────────────────────────────────────────────

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color=TV_PANEL, corner_radius=0, height=64)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(1, weight=1)

        dot = ctk.CTkFrame(header, width=12, height=12, fg_color=TV_GREEN, corner_radius=6)
        dot.grid(row=0, column=0, padx=(20, 10), pady=20)

        ctk.CTkLabel(
            header, text="Log Anonymizer",
            font=FONT_TITLE, text_color=TV_TEXT, anchor="w",
        ).grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(
            header, text="Ingen data lämnar din maskin",
            font=FONT_LABEL, text_color=TV_SUBTEXT, anchor="e",
        ).grid(row=0, column=2, padx=20, sticky="e")

        # "Invest in Telavox Coin" button
        invest_btn = ctk.CTkButton(
            header,
            text="💰 Invest in Telavox Coin",
            command=self._show_confetti,
            font=("Inter", 10, "bold"),
            fg_color="#FFD600",
            hover_color="#FFC600",
            text_color="#000000",
            corner_radius=6,
            width=180,
            height=32,
        )
        invest_btn.grid(row=0, column=3, padx=(0, 12), pady=16)
        self._invest_btn = invest_btn

    # ── Tabs ───────────────────────────────────────────────────────────────

    def _build_tabs(self):
        self._tabs = ctk.CTkTabview(
            self,
            fg_color=TV_PANEL,
            segmented_button_fg_color=TV_PANEL_ALT,
            segmented_button_selected_color=TV_GREEN,
            segmented_button_selected_hover_color=TV_GREEN_HOVER,
            segmented_button_unselected_color=TV_PANEL_ALT,
            segmented_button_unselected_hover_color=TV_PANEL,
            text_color=TV_TEXT,
            corner_radius=12,
        )
        self._tabs.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)

        self._tabs.add("  Anonymisera fil  ")
        self._tabs.add("  Återskapa original  ")

        self._build_anonymize_tab(self._tabs.tab("  Anonymisera fil  "))
        self._build_restore_tab(self._tabs.tab("  Återskapa original  "))

    # ── Tab 1 — Anonymisera fil ────────────────────────────────────────────

    def _build_anonymize_tab(self, parent):
        parent.configure(fg_color=TV_PANEL)
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(2, weight=1)

        # Drop zone card
        self._drop_card = ctk.CTkFrame(
            parent, fg_color=TV_DROP_IDLE,
            corner_radius=12, border_width=2, border_color=TV_PANEL_ALT,
        )
        self._drop_card.grid(row=0, column=0, sticky="ew", pady=(8, 6))
        self._drop_card.grid_columnconfigure(0, weight=1)

        self._drop_icon = ctk.CTkLabel(
            self._drop_card, text="↓", font=("Inter", 28, "bold"),
            text_color=TV_SUBTEXT, width=40,
        )
        self._drop_icon.grid(row=0, column=0, padx=(16, 0), pady=16, sticky="w")

        self._file_label = ctk.CTkLabel(
            self._drop_card,
            text="Dra hit en fil  —  eller klicka Välj fil…",
            anchor="w", font=FONT_BODY, text_color=TV_SUBTEXT,
        )
        self._file_label.grid(row=0, column=1, sticky="ew", padx=8, pady=16)

        ghost_btn(self._drop_card, "Välj fil…", self._browse, width=120).grid(
            row=0, column=2, padx=(0, 14), pady=14,
        )

        for widget in (self._drop_card, self._file_label, self._drop_icon):
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind("<<Drop>>", self._on_drop)
            widget.dnd_bind("<<DragEnter>>", self._on_drag_enter)
            widget.dnd_bind("<<DragLeave>>", self._on_drag_leave)

        # Action row
        action = ctk.CTkFrame(parent, fg_color="transparent")
        action.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        action.grid_columnconfigure(1, weight=1)

        self._run_btn = green_btn(action, "Anonymisera", self._start, width=150, state="disabled")
        self._run_btn.grid(row=0, column=0, padx=(0, 14))

        self._progress = ctk.CTkProgressBar(
            action, height=8, corner_radius=4,
            fg_color=TV_PANEL_ALT, progress_color=TV_GREEN,
        )
        self._progress.grid(row=0, column=1, sticky="ew")
        self._progress.set(0)

        self._anon_status = ctk.CTkLabel(
            action, text="", anchor="e", width=200,
            font=FONT_LABEL, text_color=TV_SUBTEXT,
        )
        self._anon_status.grid(row=0, column=2, padx=(14, 0))

        # Results table
        self._table = ctk.CTkScrollableFrame(
            parent,
            label_text="Anonymiserade värden",
            label_font=FONT_BOLD,
            label_text_color=TV_SUBTEXT,
            fg_color=TV_PANEL_ALT,
            corner_radius=10,
            scrollbar_button_color=TV_PANEL,
            scrollbar_button_hover_color=TV_GREEN,
        )
        self._table.grid(row=2, column=0, sticky="nsew", pady=(0, 8))
        self._table.grid_columnconfigure(0, weight=0, minsize=120)
        self._table.grid_columnconfigure(1, weight=1)
        self._table.grid_columnconfigure(2, weight=1)
        self._build_table_header()

        self._save_btn = ghost_btn(
            parent, "Spara anonymiserad fil…", self._save, width=220, state="disabled"
        )
        self._save_btn.grid(row=3, column=0, pady=(4, 12))

    # ── Drag-and-drop events ────────────────────────────────────────────────

    def _on_drag_enter(self, event):
        self._drop_card.configure(
            fg_color=TV_DROP_ACTIVE, border_color=TV_GREEN
        )
        self._drop_icon.configure(text_color=TV_GREEN)

    def _on_drag_leave(self, event):
        self._drop_card.configure(
            fg_color=TV_DROP_IDLE, border_color=TV_PANEL_ALT
        )
        self._drop_icon.configure(text_color=TV_SUBTEXT)

    def _on_drop(self, event):
        self._on_drag_leave(event)
        path = event.data.strip().strip("{}")
        self._set_file(path)

    def _browse(self):
        self.update()
        path = fd.askopenfilename(
            parent=self,
            initialdir=DESKTOP,
            filetypes=[("Loggfiler", "*.log *.txt *.csv"), ("Alla filer", "*.*")],
        )
        if path:
            self._set_file(path)

    def _set_file(self, path):
        if not os.path.isfile(path):
            return
        self._selected_file = path
        self._drop_icon.configure(text="✓", text_color=TV_GREEN)
        self._file_label.configure(text=f"  {os.path.basename(path)}", text_color=TV_TEXT)
        self._drop_card.configure(border_color=TV_GREEN)
        self._run_btn.configure(state="normal")
        self._save_btn.configure(state="disabled")
        self._output_text = None
        self._lexicon = Lexicon()
        self._progress.set(0)
        self._anon_status.configure(text="")
        self._clear_table()

    # ── Processing ─────────────────────────────────────────────────────────

    def _start(self):
        self._run_btn.configure(state="disabled")
        self._save_btn.configure(state="disabled")
        self._anon_status.configure(text="Bearbetar…", text_color=TV_SUBTEXT)
        self._progress.set(0)
        self._lexicon = Lexicon()
        self._clear_table()
        self._animating = True
        self._animate_progress()
        threading.Thread(target=self._worker, daemon=True).start()

    def _animate_progress(self):
        if not self._animating:
            return
        val = self._progress.get()
        self._progress.set((val + 0.012) % 1.0)
        self.after(30, self._animate_progress)

    def _worker(self):
        try:
            with open(self._selected_file, encoding="utf-8", errors="replace") as f:
                text = f.read()
            output, lexicon = anonymize(text, self._lexicon)
            self._output_text = output
            self._lexicon = lexicon
            self.after(0, lambda: self._on_done(lexicon.entries()))
        except Exception as exc:
            self._animating = False
            self.after(0, lambda: self._anon_status.configure(text=f"Fel: {exc}"))
            self.after(0, lambda: self._run_btn.configure(state="normal"))

    def _on_done(self, entries):
        self._animating = False
        self._progress.set(1.0)
        self._anon_status.configure(
            text=f"✓  {len(entries)} värden ersatta", text_color=TV_GREEN
        )
        self._run_btn.configure(state="normal")
        self._save_btn.configure(state="normal")
        self._populate_table(entries)

    # ── Results table ───────────────────────────────────────────────────────

    def _build_table_header(self):
        for col, title in enumerate(["Typ", "Original", "Anonymiserat"]):
            ctk.CTkLabel(
                self._table, text=title, font=FONT_BOLD,
                anchor="w", text_color=TV_SUBTEXT,
            ).grid(row=0, column=col, sticky="ew", padx=10, pady=(6, 4))

    def _clear_table(self):
        for w in self._table.winfo_children():
            w.destroy()
        self._build_table_header()

    def _populate_table(self, entries):
        seen = set()
        unique_entries = [e for e in entries if not (e["original"] in seen or seen.add(e["original"]))]
        for i, e in enumerate(unique_entries, start=1):
            bg = TV_ROW_B if i % 2 == 0 else TV_ROW_A
            label = TYPE_LABELS.get(e["type"], e["type"])
            chip_bg, chip_fg = TYPE_CHIP.get(label, (TV_PANEL_ALT, TV_TEXT))

            ctk.CTkLabel(
                self._table, text=f"  {label}  ",
                anchor="center", font=FONT_CHIP,
                fg_color=chip_bg, text_color=chip_fg, corner_radius=6,
            ).grid(row=i, column=0, sticky="w", padx=(6, 3), pady=2)

            for col, val in enumerate([e["original"], e["replacement"]], start=1):
                ctk.CTkLabel(
                    self._table, text=val, anchor="w",
                    fg_color=bg, font=FONT_LABEL, text_color=TV_TEXT, corner_radius=4,
                ).grid(row=i, column=col, sticky="ew", padx=3, pady=2)

    def _save(self):
        if not self._output_text:
            return
        self.update()
        base, ext = os.path.splitext(self._selected_file)
        path = fd.asksaveasfilename(
            parent=self,
            defaultextension=ext or ".log",
            initialfile=os.path.basename(base) + "_anonymized" + (ext or ".log"),
            filetypes=[("Loggfiler", "*.log *.txt *.csv"), ("Alla filer", "*.*")],
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self._output_text)
            self._anon_status.configure(text="✓  Sparad", text_color=TV_GREEN)
            self._populate_restore_input()
            self._tabs.set("  Återskapa original  ")

    def _populate_restore_input(self):
        tb = self._restore_input._textbox

        # color per type — foreground only, matches chip palette
        tag_colors = {
            "phone":        "#93C5FD",
            "email":        "#C4B5FD",
            "personnummer": "#FCD34D",
            "ip_address":   "#FCA5A5",
            "ipv6":         "#F9A8D4",
        }
        for tag, fg in tag_colors.items():
            tb.tag_configure(tag, foreground=fg)

        self._restore_input.configure(state="normal")
        self._restore_input.delete("1.0", "end")
        self._restore_input.insert("1.0", self._output_text)

        for entry in self._lexicon.entries():
            placeholder = entry["replacement"]
            tag = entry["type"]
            if tag not in tag_colors:
                continue
            start = "1.0"
            while True:
                pos = tb.search(placeholder, start, stopindex="end", exact=True)
                if not pos:
                    break
                end = f"{pos}+{len(placeholder)}c"
                tb.tag_add(tag, pos, end)
                start = end

    # ── Tab 2 — Återskapa original ─────────────────────────────────────────

    def _build_restore_tab(self, parent):
        parent.configure(fg_color=TV_PANEL)
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(
            parent,
            text="Klistra in text med anonymiserade värden (t.ex. ett svar från Claude):",
            anchor="w", font=FONT_LABEL, text_color=TV_SUBTEXT,
        ).grid(row=0, column=0, sticky="ew", pady=(10, 4))

        self._restore_input = ctk.CTkTextbox(
            parent, fg_color=TV_PANEL_ALT, text_color=TV_TEXT,
            font=FONT_BODY, corner_radius=10,
            border_width=2, border_color=TV_PANEL_ALT,
        )
        self._restore_input.grid(row=1, column=0, sticky="nsew", pady=(0, 8))
        self._restore_input.bind("<FocusIn>",
            lambda e: self._restore_input.configure(border_color=TV_GREEN))
        self._restore_input.bind("<FocusOut>",
            lambda e: self._restore_input.configure(border_color=TV_PANEL_ALT))

        btn_row = ctk.CTkFrame(parent, fg_color="transparent")
        btn_row.grid(row=2, column=0, sticky="ew", pady=4)
        btn_row.grid_columnconfigure(1, weight=1)

        green_btn(btn_row, "Återskapa original", self._restore, width=200).grid(row=0, column=0)

        self._restore_status = ctk.CTkLabel(
            btn_row, text="", anchor="w", font=FONT_LABEL, text_color=TV_SUBTEXT,
        )
        self._restore_status.grid(row=0, column=1, padx=14)

        ctk.CTkLabel(
            parent, text="Text med återställda originalvärden:",
            anchor="w", font=FONT_LABEL, text_color=TV_SUBTEXT,
        ).grid(row=3, column=0, sticky="ew", pady=(8, 4))

        self._restore_output = ctk.CTkTextbox(
            parent, fg_color=TV_PANEL_ALT, text_color=TV_TEXT,
            font=FONT_BODY, corner_radius=10,
            border_width=2, border_color=TV_PANEL_ALT,
            state="disabled",
        )
        self._restore_output.grid(row=4, column=0, sticky="nsew", pady=(0, 12))

    def _restore(self):
        text = self._restore_input.get("1.0", "end").strip()
        if not text:
            self._restore_status.configure(text="Ingen text att återskapa.", text_color=TV_SUBTEXT)
            return
        if not self._lexicon.entries():
            self._restore_status.configure(
                text="Anonymisera en fil först för att bygga upp lexikonet.",
                text_color=TV_SUBTEXT,
            )
            return
        result = deanonymize(text, self._lexicon)
        self._restore_output.configure(state="normal")
        self._restore_output.delete("1.0", "end")
        self._restore_output.insert("1.0", result)
        self._restore_output.configure(state="disabled")
        self._restore_status.configure(text="✓  Klart", text_color=TV_GREEN)


if __name__ == "__main__":
    app = App()
    app.mainloop()
