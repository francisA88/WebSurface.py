from ctypes import (
    byref,
    cdll,
    create_string_buffer,
    c_char_p,
    c_int,
    c_void_p,
    c_bool,
    POINTER,
    string_at,
    c_int32
)

# Loads the shared library
lib = cdll.LoadLibrary("./libwebsurface.so")
lib.initWebSurface.argtypes = [c_int, c_int, c_void_p]  # html as const char*
lib.initWebSurface.restype = c_int
lib.renderWebSurface.argtypes = []
lib.getSurfacePixels.argtypes = [c_int, POINTER(c_int), POINTER(c_int), POINTER(c_int)]
lib.getSurfacePixels.restype = c_void_p
lib.releaseSurfacePixels.argtypes = [c_int]
lib.destroySurface.argtypes = [c_int]
lib.isFocused.argtypes = [c_int]
lib.isFocused.restype = c_bool
lib.dispatchKeyEvent.argtypes = [c_int, c_void_p, c_int, c_int]


button_codes = {'none': 0, 'left': 1, 'middle': 2, 'right': 3}
non_printable_keycodes = [27, 9, 277, 279, 278, 127, 8, 13, 303, 304, 305, 273, 275, 274, 276, 306, 280, 281, 307, 308, 301] + list(range(282, 294))

SHIFT_MAP = {
    '`': '~', '1': '!', '2': '@', '3': '#', '4': '$', '5': '%', '6': '^',
    '7': '&', '8': '*', '9': '(', '0': ')', '-': '_', '=': '+',
    '[': '{', ']': '}', '\\': '|',
    ';': ':', "'": '"',
    ',': '<', '.': '>', '/': '?'
}

MOD_SHIFT = 1 << 1
MOD_CTRL  = 1 << 0
MOD_ALT   = 1 << 2
MOD_META  = 1 << 3
MOD_CAPSLOCK = 1 << 4

def get_text_from_keycode_and_modifiers(key: str, modifiers: int) -> str:
    """
    Returns the character string produced by a key and modifiers.
    Key is typically Kivy's event.key or a single-character string.
    """
    if not key or len(key) != 1:
        return ""

    shift = bool(modifiers & MOD_SHIFT)
    caps = bool(modifiers & MOD_CAPSLOCK)

    # Letters
    if key.isalpha():
        upper = shift ^ caps  # XOR: only one active makes uppercase
        return key.upper() if upper else key.lower()

    # Digits and symbols
    if key in SHIFT_MAP:
        return SHIFT_MAP[key] if shift else key

    return key  # Unaffected characters (space, etc.)


def make_modmask(modifiers):
    mask = 0
    if 'shift' in modifiers:
        mask |= MOD_SHIFT
    if 'ctrl' in modifiers:
        mask |= MOD_CTRL
    if 'alt' in modifiers:
        mask |= MOD_ALT
    if 'meta' in modifiers or 'super' in modifiers:
        mask |= MOD_META
    if 'capslock' in modifiers:
        mask |= MOD_CAPSLOCK
    return mask

def kivy_to_ultralight_vk(keycode: int) -> int:
    """Translate Kivy/SDL2 keycodes to Ultralight-compatible virtual key codes (VK_*)."""
    
    # Core printable range (A-Z, 0-9, punctuation) are same as ASCII, so pass them through.
    if 32 <= keycode <= 126:
        return keycode

    # Custom mapping for non-printables you listed
    mapping = {
        27: 0x1B,   # Escape
        278: 0x24,  # Home
        279: 0x23,  # End
        281: 0x22,  # Page Down (VK_NEXT)
        280: 0x21,  # Page Up (VK_PRIOR)
        277: 0x2D,  # Insert
        8:   0x08,  # Backspace
        9:   0x09,  # Tab
        13:  0x0D,  # Enter / Return

        # Arrows (assuming Kivy uses SDL defaults)
        273: 0x26,  # Up
        274: 0x28,  # Down
        275: 0x27,  # Right
        276: 0x25,  # Left

        # Modifier keys
        303: 0xA0,  # Left Shift (VK_LSHIFT)
        304: 0xA1,  # Right Shift (VK_RSHIFT)
        307: 0xA5,  # Right Alt (VK_RMENU)
        308: 0xA4,  # Left Alt (VK_LMENU)
        305: 0xA2,  # Left Ctrl (VK_LCONTROL)
        306: 0xA3,  # Right Ctrl (VK_RCONTROL)
        301: 0x14,  # Caps Lock
    }

    # Function keys (F1–F12)
    if 282 <= keycode <= 293:
        return 0x70 + (keycode - 282)

    # Return mapped value or fallback
    return mapping.get(keycode, 0)




