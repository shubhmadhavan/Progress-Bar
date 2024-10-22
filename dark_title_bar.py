import ctypes as ct

import ctypes as ct

def dark_title_bar(window):
    window.update_idletasks()  # Ensure window is fully rendered before applying changes

    DWMWA_USE_IMMERSIVE_DARK_MODE = 20  # Value to enable dark mode on the title bar
    set_window_attribute = ct.windll.dwmapi.DwmSetWindowAttribute
    get_parent = ct.windll.user32.GetParent
    hwnd = get_parent(window.winfo_id())  # Get window handle

    # Apply dark mode to the title bar only
    rendering_policy = DWMWA_USE_IMMERSIVE_DARK_MODE
    value = ct.c_int(2)  # 2 enables dark mode, 0 disables it
    set_window_attribute(hwnd, rendering_policy, ct.byref(value), ct.sizeof(value))
