"""One scoped UIA request per process. No hooks, raw keyboard injection or shell."""
import ctypes
import json
import os
from pathlib import Path
import struct
import sys
from .model import DeskTraceError, require, validate_step
from .privacy import sensitive

# Keep a private-desktop handle alive until process exit. Never switch the visible desktop.
_desktop_handle = None


def select_desktop(name):
    global _desktop_handle
    if not name:
        return
    require(isinstance(name, str) and name.startswith('DeskTrace-') and len(name) <= 100, 'INVALID_DESKTOP')
    from ctypes import wintypes as w
    u = ctypes.WinDLL('user32', use_last_error=True)
    u.OpenDesktopW.argtypes = [w.LPCWSTR, w.DWORD, w.BOOL, w.DWORD]
    u.OpenDesktopW.restype = w.HANDLE
    u.SetThreadDesktop.argtypes = [w.HANDLE]
    handle = u.OpenDesktopW(name, 0, False, 0x0001 | 0x0002 | 0x0040 | 0x0080)
    require(bool(handle) and bool(u.SetThreadDesktop(handle)), 'DESKTOP_UNAVAILABLE')
    _desktop_handle = handle


def modules():
    # Imported after SetThreadDesktop, before creating any UIA/COM objects.
    import win32api
    import win32con
    import win32gui
    import win32process
    from pywinauto import Desktop
    return win32api, win32con, win32gui, win32process, Desktop


def identity(hwnd, pid):
    api, con, gui, process, _ = modules()
    require(gui.IsWindow(hwnd) and gui.GetAncestor(hwnd, 2) == hwnd, 'WINDOW_GONE')
    _, actual = process.GetWindowThreadProcessId(hwnd)
    require(actual == pid, 'WINDOW_CHANGED')
    h = api.OpenProcess(0x1000, False, actual)
    try:
        created = process.GetProcessTimes(h)['CreationTime'].isoformat()
        from ctypes import wintypes as w
        query = ctypes.WinDLL('kernel32', use_last_error=True).QueryFullProcessImageNameW
        query.argtypes = [w.HANDLE, w.DWORD, w.LPWSTR, ctypes.POINTER(w.DWORD)]
        query.restype = w.BOOL
        size = w.DWORD(32768)
        path = ctypes.create_unicode_buffer(size.value)
        require(bool(query(int(h), 0, path, ctypes.byref(size))), 'PROCESS_IDENTITY_UNAVAILABLE')
        exe = path.value
    finally:
        h.Close()
    # These apps are outside DeskTrace's test scope. No authentication/security automation.
    denied = {'cmd.exe', 'powershell.exe', 'pwsh.exe', 'windowsterminal.exe', 'codex.exe',
              'chatgpt.exe', 'lockapp.exe', 'credentialuibroker.exe', 'keepass.exe',
              '1password.exe', 'bitwarden.exe', 'sechealthui.exe'}
    require(Path(exe).name.lower() not in denied, 'TARGET_NOT_ALLOWED')
    return {'hwnd': hwnd, 'pid': pid, 'created': created, 'class_name': gui.GetClassName(hwnd)}


def root_for(binding):
    current = identity(binding['hwnd'], binding['pid'])
    require(current == binding, 'WINDOW_CHANGED')
    return modules()[4](backend='uia').window(handle=binding['hwnd']).wrapper_object()


def is_password(control):
    # If a provider cannot answer this safety property, fail closed.
    try:
        return bool(control.element_info.element.CurrentIsPassword)
    except Exception:
        raise DeskTraceError('PASSWORD_STATE_UNKNOWN') from None


def scoped_controls(root, binding):
    controls = root.descendants()
    require(len(controls) <= 3000, 'CONTROL_LIMIT')
    return [c for c in controls if c.element_info.process_id == binding['pid']]


def locate(root, binding, loc):
    matches = []
    for c in scoped_controls(root, binding):
        info = c.element_info
        if info.control_type != loc['control_type']:
            continue
        if loc.get('automation_id') and info.automation_id != loc['automation_id']:
            continue
        password = is_password(c)
        if 'name' in loc:
            require(not password, 'PASSWORD_CONTROL_BLOCKED')
            if info.name != loc['name']:
                continue
        matches.append(c)
    require(bool(matches), 'LOCATOR_NOT_FOUND')
    require(len(matches) == 1, 'AMBIGUOUS_LOCATOR')
    require(not is_password(matches[0]), 'PASSWORD_CONTROL_BLOCKED')
    return matches[0]


def read_text(control):
    try:
        value = control.iface_value.CurrentValue
    except Exception:
        try:
            value = control.iface_text.DocumentRange.GetText(4097)
        except Exception:
            raise DeskTraceError('TEXT_PATTERN_UNAVAILABLE') from None
    require(len(value) <= 4096, 'TEXT_LIMIT')
    return value


def actionable(control, private_desktop=False):
    if not control.is_enabled():
        return False
    if control.is_visible():
        return True
    # A non-visible desktop reports all child UIA elements offscreen. Permit only
    # semantic Value/Invoke calls on explicitly requested private desktops and
    # controls whose real HWND still has WS_VISIBLE. Never inject physical input.
    handle = control.element_info.handle
    return bool(private_desktop and handle and modules()[2].IsWindowVisible(handle))


def perform(binding, step, private_desktop=False):
    validate_step(step)
    # A missing window can satisfy an explicit exists=false assertion; reused/replaced identity cannot.
    if step['action'] == 'assert_window' and step['state'] == 'exists':
        gui = modules()[2]
        if not gui.IsWindow(binding['hwnd']):
            return {'exists': False}
    root = root_for(binding)
    if step['action'] == 'assert_window':
        gui = modules()[2]
        return {'exists': True, 'minimized': bool(gui.IsIconic(binding['hwnd'])),
                'normal': bool(gui.IsWindowVisible(binding['hwnd']) and gui.GetWindowPlacement(binding['hwnd'])[1] == 1)}
    c = locate(root, binding, step['locator'])
    if step['action'] in ('invoke', 'set_text'):
        require(actionable(c, private_desktop), 'CONTROL_NOT_ACTIONABLE')
        try:
            if step['action'] == 'invoke':
                c.iface_invoke.Invoke()
            else:
                require(not c.iface_value.CurrentIsReadOnly, 'CONTROL_READ_ONLY')
                c.iface_value.SetValue(step['text'])
        except DeskTraceError:
            raise
        except Exception:
            raise DeskTraceError('PATTERN_UNAVAILABLE_OR_FAILED') from None
    root_for(binding)  # Post-action identity check; failure means outcome may be unknown.
    if step['action'] == 'assert_text':
        return {'text': read_text(c)}
    return {'enabled': bool(c.is_enabled()), 'visible': bool(c.is_visible())}


def inspect(binding):
    root = root_for(binding)
    out = []
    for c in scoped_controls(root, binding):
        if is_password(c):
            continue  # Do not read password name/text/AutomationId.
        info = c.element_info
        auto_id = info.automation_id
        if not auto_id or sensitive(auto_id):
            continue
        out.append({'locator': {'automation_id': auto_id, 'control_type': info.control_type},
                    'enabled': bool(c.is_enabled()), 'visible': bool(c.is_visible())})
    counts = {}
    for row in out:
        key = json.dumps(row['locator'], sort_keys=True)
        counts[key] = counts.get(key, 0) + 1
    for row in out:
        row['matches'] = counts[json.dumps(row['locator'], sort_keys=True)]
        row['stable_candidate'] = row['matches'] == 1
    return out


def capture(binding, path):
    root = root_for(binding)
    if is_password(root) or any(is_password(c) for c in scoped_controls(root, binding)):
        return {'status': 'NOT RUN', 'reason': 'PASSWORD_CONTROL_PRESENT'}
    import win32ui
    from ctypes import wintypes as w
    from .image import bgra_to_png
    gui = modules()[2]
    hwnd = binding['hwnd']
    u = ctypes.WinDLL('user32', use_last_error=True)
    u.GetWindowDpiAwarenessContext.argtypes = [w.HWND]
    u.GetWindowDpiAwarenessContext.restype = w.HANDLE
    u.SetThreadDpiAwarenessContext.argtypes = [w.HANDLE]
    u.SetThreadDpiAwarenessContext.restype = w.HANDLE
    u.PrintWindow.argtypes = [w.HWND, w.HDC, w.UINT]
    u.PrintWindow.restype = w.BOOL
    # Match the target's logical pixels: GetWindowRect and PrintWindow must use
    # the same DPI coordinate system. This changes only this disposable thread.
    previous_context = u.SetThreadDpiAwarenessContext(u.GetWindowDpiAwarenessContext(hwnd))
    require(bool(previous_context), 'CAPTURE_DPI_CONTEXT_FAILED')
    dc_handle = None
    dc = mem = bitmap = old = None
    try:
        left, top, right, bottom = gui.GetWindowRect(hwnd)
        width, height = right - left, bottom - top
        require(0 < width <= 4096 and 0 < height <= 4096, 'CAPTURE_SIZE_LIMIT')
        dc_handle = gui.GetWindowDC(hwnd)
        dc = win32ui.CreateDCFromHandle(dc_handle)
        mem = dc.CreateCompatibleDC()
        bitmap = win32ui.CreateBitmap()
        bitmap.CreateCompatibleBitmap(dc, width, height)
        old = mem.SelectObject(bitmap)
        require(bool(u.PrintWindow(hwnd, mem.GetSafeHdc(), 2)), 'PRINT_WINDOW_FAILED')
        mem.SelectObject(old)
        old = None
        # Ask GDI for an explicit top-down DIB instead of assuming a DDB's row order.
        gdi = ctypes.WinDLL('gdi32', use_last_error=True)
        gdi.GetDIBits.argtypes = [w.HDC, w.HBITMAP, w.UINT, w.UINT, w.LPVOID, w.LPVOID, w.UINT]
        gdi.GetDIBits.restype = ctypes.c_int
        info = ctypes.create_string_buffer(struct.pack('<IiiHHIIiiII', 40, width, -height, 1, 32, 0, width * height * 4, 0, 0, 0, 0) + b'\0' * 4)
        pixels = ctypes.create_string_buffer(width * height * 4)
        require(gdi.GetDIBits(dc.GetSafeHdc(), bitmap.GetHandle(), 0, height, pixels, info, 0) == height, 'GET_DIBITS_FAILED')
        bits = pixels.raw
        require(len(set(bits[0::4])) > 1, 'CAPTURE_BLANK')
        png = bgra_to_png(width, height, bits)
        root_for(binding)
        with Path(path).open('xb') as f:
            f.write(png)
        return {'status': 'PASS', 'path': Path(path).name, 'width': width, 'height': height, 'method': 'PrintWindow-target-only'}
    finally:
        if mem and old: mem.SelectObject(old)
        if bitmap: gui.DeleteObject(bitmap.GetHandle())
        if mem: mem.DeleteDC()
        if dc: dc.DeleteDC()
        if dc_handle: gui.ReleaseDC(hwnd, dc_handle)
        u.SetThreadDpiAwarenessContext(previous_context)


def dispatch(request):
    select_desktop(request.get('desktop'))
    op = request['operation']
    if op == 'bind':
        return identity(request['hwnd'], request['pid'])
    if op == 'windows':
        api, con, gui, process, _ = modules()
        out = []
        def callback(hwnd, _):
            if not gui.IsWindowVisible(hwnd):
                return
            _, pid = process.GetWindowThreadProcessId(hwnd)
            row = {'hwnd': hwnd, 'pid': pid, 'class_name': gui.GetClassName(hwnd)}
            if request.get('include_titles'):
                title = gui.GetWindowText(hwnd)
                row['title'] = '[redacted]' if sensitive(title) else title
            out.append(row)
        gui.EnumWindows(callback, None)
        return out
    binding = request['binding']
    if op == 'perform': return perform(binding, request['step'], bool(request.get('desktop')))
    if op == 'inspect': return inspect(binding)
    if op == 'capture': return capture(binding, request['path'])
    raise DeskTraceError('UNKNOWN_OPERATION')


def main():
    try:
        request = json.loads(sys.stdin.read(2_100_000))
        data = dispatch(request)
        result = {'ok': True, 'data': data}
    except DeskTraceError as error:
        result = {'ok': False, 'code': error.code, 'data': {}}
    except Exception:
        result = {'ok': False, 'code': 'UIA_ERROR', 'data': {}}
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
