"""Small Tk client for explicit recording; no passive capture or global hooks."""
import json
import queue
import threading
import tkinter as tk
from tkinter import filedialog, ttk
from .adapters.windows import WindowsAdapter, list_windows
from .engine import Recording, replay
from .model import DeskTraceError, validate_script
from .tk_runtime import configure_tk


class App:
    def __init__(self, root, *, desktop=None):
        self.root = root
        self.desktop = desktop
        self.adapter = self.recording = None
        self.windows = self.controls = []
        self.busy = False
        self.results = queue.Queue()
        root.title('DeskTrace · explicit desktop regression recorder')
        root.geometry('1000x760')
        frame = ttk.Frame(root, padding=12)
        frame.pack(fill='both', expand=True)
        ttk.Label(frame, text='Use an authorized, non-sensitive test window. Password controls are blocked. No global recording.').pack(anchor='w')
        self.consent = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text='I authorize operations on the selected test window and confirm the test data is non-sensitive', variable=self.consent).pack(anchor='w')
        self.capture = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text='Allow selected-window screenshot on failure (may contain visible personal data)', variable=self.capture).pack(anchor='w')
        row = ttk.Frame(frame); row.pack(fill='x', pady=6)
        self.window = ttk.Combobox(row, state='readonly', width=70); self.window.pack(side='left', fill='x', expand=True)
        ttk.Button(row, text='Refresh windows', command=self.refresh).pack(side='left', padx=4)
        ttk.Button(row, text='Bind selected', command=self.bind).pack(side='left')
        self.control = ttk.Combobox(frame, state='readonly'); self.control.pack(fill='x', pady=6)
        row = ttk.Frame(frame); row.pack(fill='x')
        self.action = ttk.Combobox(row, values=['set_text', 'invoke', 'assert_text', 'assert_control', 'assert_window'], state='readonly', width=18)
        self.action.set('set_text'); self.action.pack(side='left')
        self.state = ttk.Combobox(row, values=['enabled', 'visible', 'exists', 'normal', 'minimized'], state='readonly', width=16)
        self.state.set('enabled'); self.state.pack(side='left', padx=4)
        self.value = ttk.Combobox(row, values=['true', 'false'], state='readonly', width=8)
        self.value.set('true'); self.value.pack(side='left')
        ttk.Button(row, text='Execute + record', command=self.record_step).pack(side='left', padx=8)
        ttk.Label(frame, text='Input / expected text (saved in script as plain test data):').pack(anchor='w', pady=(8, 0))
        self.text = tk.Text(frame, height=3); self.text.pack(fill='x')
        ttk.Label(frame, text='Editable JSON script (Replay uses this editor):').pack(anchor='w', pady=(8, 0))
        self.editor = tk.Text(frame, height=16); self.editor.pack(fill='both', expand=True)
        row = ttk.Frame(frame); row.pack(fill='x', pady=6)
        ttk.Button(row, text='Load script', command=self.load).pack(side='left')
        ttk.Button(row, text='Save as new script', command=self.save).pack(side='left', padx=4)
        ttk.Button(row, text='Replay editor', command=self.replay_editor).pack(side='left')
        self.status = tk.StringVar(value='Select and authorize a target, then bind. Window titles and control text are not enumerated.')
        ttk.Label(frame, textvariable=self.status, wraplength=940).pack(anchor='w')
        self.set_editor({'version': 1, 'name': 'Desktop test', 'steps': []})
        root.after(100, self.drain)

    def set_editor(self, script):
        self.editor.delete('1.0', 'end')
        self.editor.insert('1.0', json.dumps(script, ensure_ascii=False, indent=2))

    def task(self, work, done):
        if self.busy:
            self.status.set('An operation is already running. Wait for its result.')
            return
        self.busy = True
        self.status.set('Running bounded operation…')
        def run():
            try:
                result = work(); self.results.put((done, result, None))
            except DeskTraceError as e:
                self.results.put((done, None, e.code + (f' · evidence: {e.evidence}' if e.evidence else '')))
            except Exception:
                self.results.put((done, None, 'OPERATION_ERROR'))
        threading.Thread(target=run, daemon=True).start()

    def drain(self):
        try:
            done, result, error = self.results.get_nowait()
            self.busy = False
            if error: self.status.set(error)
            else: done(result)
        except queue.Empty:
            pass
        self.root.after(100, self.drain)

    def refresh(self):
        def done(rows):
            self.windows = rows
            self.window['values'] = [f"HWND {r['hwnd']} · PID {r['pid']} · {r['class_name']}" for r in rows]
            self.status.set(f'{len(rows)} windows. Choose an explicitly authorized application.')
        self.task(lambda: list_windows(desktop=self.desktop), done)

    def bind(self):
        i = self.window.current()
        if not self.consent.get() or i < 0:
            self.status.set('Select a window and check authorization first.'); return
        row = self.windows[i]
        screenshot = self.capture.get()
        def work():
            a = WindowsAdapter(row['hwnd'], row['pid'], desktop=self.desktop, allow_screenshot=screenshot)
            return a, a.inspect()
        def done(value):
            self.adapter, self.controls = value
            self.recording = Recording(self.adapter, 'Desktop test', runs='runs')
            self.control['values'] = [f"{r['locator']['control_type']} · {r['locator']['automation_id']} · matches={r['matches']}" for r in self.controls]
            self.status.set('Bound. Inspect matches=1 selectors; changed windows require a new binding.')
        self.task(work, done)

    def authorized(self):
        if not self.consent.get() or self.adapter is None:
            self.status.set('Bind an authorized target first.'); return False
        # Revocation or enabling capture takes effect immediately for subsequent operations.
        self.adapter.allow_screenshot = self.capture.get()
        return True

    def record_step(self):
        if not self.authorized(): return
        try:
            script = validate_script(json.loads(self.editor.get('1.0', 'end')))
            step = {'action': self.action.get()}
            if step['action'] != 'assert_window':
                i = self.control.current()
                if i < 0: raise DeskTraceError('SELECT_CONTROL')
                step['locator'] = self.controls[i]['locator']
            if step['action'] == 'set_text': step['text'] = self.text.get('1.0', 'end-1c')
            if step['action'] == 'assert_text': step['expected'] = self.text.get('1.0', 'end-1c')
            if step['action'] in ('assert_window', 'assert_control'):
                step.update(state=self.state.get(), value=self.value.get() == 'true')
            r = Recording(self.adapter, script['name'], runs='runs'); r.script = script
            def done(_):
                self.recording = r; self.set_editor(r.script); self.status.set('Operation executed and recorded.')
            self.task(lambda: r.add(step), done)
        except Exception:
            self.status.set('INVALID_SCRIPT_OR_SELECTION')

    def replay_editor(self):
        if not self.authorized(): return
        try: script = validate_script(json.loads(self.editor.get('1.0', 'end')))
        except Exception: self.status.set('INVALID_SCRIPT'); return
        self.task(lambda: replay(script, self.adapter, 'runs'),
                  lambda r: self.status.set(f"{r['status']} · report: {r['run_dir']}/report.html"))

    def save(self):
        try:
            script = validate_script(json.loads(self.editor.get('1.0', 'end')))
            p = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON', '*.json')])
            if p:
                r = Recording(None, script['name']); r.script = script; r.save(p)
                self.status.set('Saved new script. Existing files are never overwritten.')
        except Exception:
            self.status.set('SAVE_FAILED: invalid script or existing output file')

    def load(self):
        from .model import load_script
        p = filedialog.askopenfilename(filetypes=[('JSON', '*.json')])
        if p:
            try: self.set_editor(load_script(p)); self.status.set('Loaded script; target binding is still required.')
            except Exception: self.status.set('LOAD_FAILED')


def main():
    configure_tk()
    root = tk.Tk()
    App(root)
    root.mainloop()
