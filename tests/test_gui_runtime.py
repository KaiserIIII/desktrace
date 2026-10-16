import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from desktrace.tk_runtime import configure_tk


class TkRuntimeTests(unittest.TestCase):
    def test_local_base_install_fallback_preserves_explicit_configuration(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            for folder, file in [('tcl8.6', 'init.tcl'), ('tk8.6', 'tk.tcl')]:
                p = base / 'tcl' / folder; p.mkdir(parents=True); (p / file).write_text('', encoding='utf8')
            with patch.dict(os.environ, {}, clear=True), patch('sys.base_prefix', d):
                configure_tk()
                self.assertEqual(os.environ['TCL_LIBRARY'], str(base / 'tcl/tcl8.6'))
                os.environ['TCL_LIBRARY'] = 'explicit-setting'
                configure_tk()
                self.assertEqual(os.environ['TCL_LIBRARY'], 'explicit-setting')

    def test_missing_tcl_files_are_not_invented(self):
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ, {}, clear=True), patch('sys.base_prefix', d):
            configure_tk()
            self.assertNotIn('TCL_LIBRARY', os.environ)
