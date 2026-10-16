"""Repair Tcl resource discovery in Windows venvs using the same base install."""
import os
from pathlib import Path
import sys


def configure_tk():
    import tkinter
    for key, folder, resource in [('TCL_LIBRARY', f'tcl{tkinter.TclVersion}', 'init.tcl'),
                                  ('TK_LIBRARY', f'tk{tkinter.TkVersion}', 'tk.tcl')]:
        candidate = Path(sys.base_prefix) / 'tcl' / folder
        if key not in os.environ and (candidate / resource).is_file():
            os.environ[key] = str(candidate)
