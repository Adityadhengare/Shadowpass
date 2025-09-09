#!/usr/bin/env python3
"""
ShadowPass - H4x0r Toolkit (Password Generator + Strength Checker)
Upgraded GUI: dark "hacker" theme, secure password generator (uses `secrets`),
strength meter, copy/save, console log, show/hide toggle and polished layout.

Save this file as `shadowpass_hacking_tool.py` and run:
    python shadowpass_hacking_tool.py

Dependencies: only Python standard library (Tkinter). To create an EXE later,
use PyInstaller:
    pip install pyinstaller
    pyinstaller --onefile --windowed --name ShadowPass shadowpass_hacking_tool.py

"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter import scrolledtext
import secrets
import string
import time
import os

# ----------------------------- Configuration -----------------------------
BG = '#071013'           # very dark background
PANEL = '#0d1b1e'        # panel background
FORE = '#00FF6A'         # hacker green
ACCENT = '#00A8FF'       # accent blue
WARN = '#FFB86B'         # warning/orange
DANGER = '#FF5C57'       # red
FONT_TITLE = ('Courier New', 18, 'bold')
FONT_NORMAL = ('Consolas', 11)
FONT_SMALL = ('Consolas', 9)

# Allowed characters for generated passwords (cleaned to avoid problematic whitespace)
ALLOWED_PUNCT = "!@#$%^&*()-_=+[]{};:,.<>/?|~"
ALLOWED_CHARS = string.ascii_letters + string.digits + ALLOWED_PUNCT

# ----------------------------- Helper functions -------------------------

def now():
    return time.strftime('%Y-%m-%d %H:%M:%S')

# ----------------------------- The App ---------------------------------
class ShadowPassApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('ShadowPass — H4x0r Toolkit')
        self.geometry('720x480')
        self.configure(bg=BG)
        self.resizable(False, False)

        # Style
        self.style = ttk.Style(self)
        try:
            self.style.theme_use('clam')
        except Exception:
            pass
        # Progressbar styles (may vary by platform)
        self.style.configure('red.Horizontal.TProgressbar', troughcolor=PANEL, background=DANGER)
        self.style.configure('yellow.Horizontal.TProgressbar', troughcolor=PANEL, background=WARN)
        self.style.configure('green.Horizontal.TProgressbar', troughcolor=PANEL, background=FORE)

        # Top: header / banner
        self.header_frame = tk.Frame(self, bg=BG)
        self.header_frame.pack(fill='x', padx=12, pady=(10, 4))

        self.header_label = tk.Label(self.header_frame,
                                     text='╔═[ SHADOWPASS ]═╗',
                                     font=FONT_TITLE, fg=FORE, bg=BG)
        self.header_label.pack(side='left')

        # Tagline entry (user can fill "this is hacking tool")
        self.tag_entry = tk.Entry(self.header_frame, font=FONT_SMALL, bg=PANEL, fg=FORE, insertbackground=FORE, width=30)
        self.tag_entry.insert(0, 'This is a hacking tool')
        self.tag_entry.pack(side='right', padx=(0, 6))

        self.btn_apply_tag = tk.Button(self.header_frame, text='Apply Tag', bg=ACCENT, fg='white', font=FONT_SMALL, command=self.apply_tag)
        self.btn_apply_tag.pack(side='right', padx=6)

        # Main content frames
        self.main_frame = tk.Frame(self, bg=BG)
        self.main_frame.pack(fill='both', expand=True, padx=12, pady=6)

        # Left panel (controls)
        self.left_panel = tk.Frame(self.main_frame, bg=PANEL, width=380, height=360)
        self.left_panel.pack(side='left', padx=(0,10), pady=6)
        self.left_panel.pack_propagate(False)

        # Right panel (console/log)
        self.right_panel = tk.Frame(self.main_frame, bg=PANEL, width=300, height=360)
        self.right_panel.pack(side='right', padx=(10,0), pady=6)
        self.right_panel.pack_propagate(False)

        # ---------------- Left: controls ----------------
        # Password label + entry
        lbl = tk.Label(self.left_panel, text='Password (enter or generate):', font=FONT_NORMAL, fg=FORE, bg=PANEL)
        lbl.pack(anchor='w', padx=10, pady=(12,4))

        self.entry_password = tk.Entry(self.left_panel, font=FONT_NORMAL, bg='black', fg=FORE, insertbackground=FORE, width=34, show='*')
        self.entry_password.pack(padx=10)
        self.entry_password.bind('<KeyRelease>', lambda e: self.on_password_change())

        # Show/hide toggle
        self.btn_toggle = tk.Button(self.left_panel, text='Show', bg='#2f2f2f', fg=FORE, font=FONT_SMALL, command=self.toggle_password)
        self.btn_toggle.pack(anchor='e', padx=12, pady=(6, 0))

        # Strength meter
        self.strength_label = tk.Label(self.left_panel, text='Strength: —', font=FONT_NORMAL, fg=FORE, bg=PANEL)
        self.strength_label.pack(anchor='w', padx=10, pady=(12,4))

        self.progress = ttk.Progressbar(self.left_panel, length=300, maximum=100, style='green.Horizontal.TProgressbar')
        self.progress.pack(padx=10)

        # Buttons row (Generate / Copy / Save)
        btn_frame = tk.Frame(self.left_panel, bg=PANEL)
        btn_frame.pack(fill='x', padx=10, pady=12)

        # Password length
        lbl_len = tk.Label(btn_frame, text='Len:', font=FONT_SMALL, fg=FORE, bg=PANEL)
        lbl_len.grid(row=0, column=0, padx=(0,6))
        self.len_var = tk.Entry(btn_frame, width=6, font=FONT_SMALL, bg='black', fg=FORE, insertbackground=FORE)
        self.len_var.insert(0, '16')
        self.len_var.grid(row=0, column=1)

        self.btn_generate = tk.Button(btn_frame, text='Generate', bg=ACCENT, fg='white', font=FONT_SMALL, command=self.generate_password)
        self.btn_generate.grid(row=0, column=2, padx=8)

        self.btn_copy = tk.Button(btn_frame, text='Copy', bg='#FFB86B', fg='black', font=FONT_SMALL, command=self.copy_password)
        self.btn_copy.grid(row=0, column=3, padx=8)

        self.btn_save = tk.Button(btn_frame, text='Save', bg='#7C4DFF', fg='white', font=FONT_SMALL, command=self.save_password)
        self.btn_save.grid(row=0, column=4, padx=8)

        # Extra controls: Clear / Exit
        extra_frame = tk.Frame(self.left_panel, bg=PANEL)
        extra_frame.pack(fill='x', padx=10, pady=(6,0))

        self.btn_clear = tk.Button(extra_frame, text='Clear', bg='#2f2f2f', fg=FORE, font=FONT_SMALL, command=self.clear_password)
        self.btn_clear.pack(side='left')

        self.btn_exit = tk.Button(extra_frame, text='Exit', bg=DANGER, fg='white', font=FONT_SMALL, command=self.quit)
        self.btn_exit.pack(side='right')

        # ---------------- Right: console/log ----------------
        console_label = tk.Label(self.right_panel, text='Console / Activity Log', font=FONT_NORMAL, fg=FORE, bg=PANEL)
        console_label.pack(anchor='w', padx=8, pady=(8,4))

        self.console = scrolledtext.ScrolledText(self.right_panel, bg='black', fg=FORE, font=FONT_SMALL, state='normal', width=36, height=18)
        self.console.pack(padx=8, pady=(0,8))
        self.console.insert('end', '[{}] ShadowPass initialized.\n'.format(now()))
        self.console.config(state='disabled')

        # Footnote / credits
        foot = tk.Label(self, text='Made with secrets + Tkinter — for learning & portfolio. Do not use for malicious activity.', font=('Arial',8), fg='gray', bg=BG)
        foot.pack(side='bottom', pady=(0,8))

        # Initial update
        self.update_strength_meter(0)

    # ---------------- UI actions ----------------
    def apply_tag(self):
        txt = self.tag_entry.get().strip()
        if txt:
            self.header_label.config(text=f'╔═[ {txt[:24]} ]═╗')
            self.log(f"Tagline applied: {txt}")

    def toggle_password(self):
        cur = self.entry_password.cget('show')
        if cur == '*' or cur == '•':
            # currently hidden -> show
            self.entry_password.config(show='')
            self.btn_toggle.config(text='Hide')
            self.log('Password unmasked')
        else:
            # currently visible -> hide
            self.entry_password.config(show='*')
            self.btn_toggle.config(text='Show')
            self.log('Password masked')

    def generate_password(self):
        # Secure generator using secrets
        s = self.len_var.get().strip()
        try:
            length = int(s) if s else 16
        except ValueError:
            messagebox.showerror('Invalid length', 'Please enter a valid integer for length (4-128).')
            return
        if length < 4 or length > 128:
            messagebox.showerror('Invalid length', 'Length must be between 4 and 128.')
            return

        pwd = ''.join(secrets.choice(ALLOWED_CHARS) for _ in range(length))
        # put generated password into entry and unmask so user can see it immediately
        self.entry_password.delete(0, 'end')
        self.entry_password.insert(0, pwd)
        self.entry_password.config(show='')
        self.btn_toggle.config(text='Hide')

        self.log(f'Generated password (len={length})')
        self.update_strength_from_password(pwd)

    def copy_password(self):
        pwd = self.entry_password.get()
        if not pwd:
            messagebox.showwarning('No password', 'Nothing to copy — generate or enter a password first.')
            return
        self.clipboard_clear()
        self.clipboard_append(pwd)
        self.log('Password copied to clipboard')
        messagebox.showinfo('Copied', 'Password copied to clipboard ✅')

    def save_password(self):
        pwd = self.entry_password.get()
        if not pwd:
            messagebox.showwarning('No password', 'Nothing to save — generate or enter a password first.')
            return
        default_name = f'shadowpass_{time.strftime("%Y%m%d_%H%M%S")}.txt'
        path = filedialog.asksaveasfilename(defaultextension='.txt', initialfile=default_name, filetypes=[('Text files','*.txt')])
        if not path:
            return
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write('ShadowPass — saved password\n')
                f.write(f'Time: {now()}\n')
                f.write(f'Tag: {self.tag_entry.get()}\n')
                f.write(f'Password: {pwd}\n')
            self.log(f'Saved password to {os.path.basename(path)}')
            messagebox.showinfo('Saved', f'Saved to {path}')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to save file: {e}')

    def clear_password(self):
        self.entry_password.delete(0, 'end')
        self.entry_password.config(show='*')
        self.btn_toggle.config(text='Show')
        self.update_strength_meter(0)
        self.log('Cleared password field')

    # ---------------- Strength logic ----------------
    def compute_score(self, pwd: str) -> int:
        if not pwd:
            return 0
        score = 0
        L = len(pwd)
        # length scoring
        if L >= 8:
            score += 1
        if L >= 12:
            score += 1
        # digit
        if any(c.isdigit() for c in pwd):
            score += 1
        # mix case
        if any(c.islower() for c in pwd) and any(c.isupper() for c in pwd):
            score += 1
        # punctuation
        if any(c in ALLOWED_PUNCT for c in pwd):
            score += 1
        return min(score, 5)

    def update_strength_from_password(self, pwd: str):
        s = self.compute_score(pwd)
        self.update_strength_meter(s)

    def update_strength_meter(self, score: int):
        value = score * 20
        self.progress['value'] = value
        # choose style
        if score <= 1:
            style_name = 'red.Horizontal.TProgressbar'
            lbl = 'Very Weak'
            color = DANGER
        elif score == 2:
            style_name = 'red.Horizontal.TProgressbar'
            lbl = 'Weak'
            color = DANGER
        elif score == 3:
            style_name = 'yellow.Horizontal.TProgressbar'
            lbl = 'Medium'
            color = WARN
        elif score == 4:
            style_name = 'green.Horizontal.TProgressbar'
            lbl = 'Strong'
            color = FORE
        else:
            style_name = 'green.Horizontal.TProgressbar'
            lbl = 'Very Strong'
            color = FORE
        try:
            self.progress.config(style=style_name)
        except Exception:
            pass
        self.strength_label.config(text=f'Strength: {lbl}', fg=color)

    # ---------------- Events & Logging ----------------
    def on_password_change(self):
        pwd = self.entry_password.get()
        self.update_strength_from_password(pwd)

    def log(self, message: str):
        timestamp = time.strftime('%H:%M:%S')
        self.console.config(state='normal')
        self.console.insert('end', f'[{timestamp}] {message}\n')
        self.console.see('end')
        self.console.config(state='disabled')


# ----------------------------- Run App ---------------------------------
if __name__ == '__main__':
    app = ShadowPassApp()
    app.mainloop()