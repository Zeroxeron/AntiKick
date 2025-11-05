import sys, time, argparse
import win32gui, win32con, win32api

DEFAULT_INTERVAL_SECONDS = 15 * 60  # 15 min
DEFAULT_TARGET = "roblox"

def find_target_window(target_name) -> None|int:
    """Return the first top-level hwnd whose title contains 'target_name' (case-insensitive)."""
    target = None
    def enum_cb(hwnd, extra):
        nonlocal target
        if target: return
        if not win32gui.IsWindowVisible(hwnd): return
        try: title = win32gui.GetWindowText(hwnd)
        except Exception: title = ""
        if title and target_name in title.lower(): target = hwnd
    win32gui.EnumWindows(enum_cb, None)
    return target

def send_to_window(hwnd):
    vk = 0x57 # SPACE = 0x20 W = 0x57
    try:
        prev_fg = win32gui.GetForegroundWindow()
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.05)
        win32api.keybd_event(vk, win32api.MapVirtualKey(vk, 0), 0, 0)  # keydown,  affects global focus.
        time.sleep(0.03)
        win32api.keybd_event(vk, win32api.MapVirtualKey(vk, 0), win32con.KEYEVENTF_KEYUP, 0)  # keyup
        time.sleep(0.03)
        if prev_fg and win32gui.IsWindow(prev_fg): win32gui.SetForegroundWindow(prev_fg)
        return True
    except Exception as e:
        print("Focus fallback failed:", e)
        return False

def run_loop(interval_seconds=DEFAULT_INTERVAL_SECONDS, target=DEFAULT_TARGET, verbose=True):
    print(f"Starting anti-kick loop for [{target}]  ({interval_seconds} seconds). Ctrl+C to stop.")
    try:
        while True:
            hwnd = find_target_window(target)
            if not hwnd:
                if verbose: print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [{target}] window not found. Retrying in 60s.")
                time.sleep(60)
                continue
            title = win32gui.GetWindowText(hwnd)
            if verbose: print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Found [{target}] window: hwnd={hwnd} title={title!r}")
            success = send_to_window(hwnd)
            if verbose: print("  -> input sent" if success else "  -> input failed")
            time.sleep(interval_seconds)
    except KeyboardInterrupt: print("Stopped by user.")

def parse_args(argv):
    p = argparse.ArgumentParser(description="Simple anti-AFK helper (Windows).")
    p.add_argument("--interval", type=float, default=DEFAULT_INTERVAL_SECONDS, help="Interval in seconds between simulated inputs (default 15 minutes).")
    p.add_argument("--target", type=str, default=DEFAULT_INTERVAL_SECONDS, help="Target window name (default: roblox)")
    return p.parse_args(argv)

if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    run_loop(interval_seconds=args.interval)