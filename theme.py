import ttkbootstrap as tb
from ttkbootstrap.style import ThemeDefinition

# VLC-inspired palette
VLC_ORANGE = "#FF8800"
VLC_ORANGE_HOVER = "#FFA733"
VLC_ORANGE_DARK = "#CC6D00"
VLC_DARK_BG = "#191919"
VLC_PANEL_BG = "#222222"
VLC_INPUT_BG = "#2b2b2b"
VLC_BORDER = "#3d3d3d"
VLC_TEXT = "#f5f5f5"
VLC_TEXT_MUTED = "#b0b0b0"

VLC_DARK_THEME_DEF = {
    "name": "vlc_dark",
    "colors": {
        "primary": VLC_ORANGE,
        "secondary": "#444444",
        "success": "#28a745",
        "info": "#17a2b8",
        "warning": VLC_ORANGE,
        "danger": "#e74c3c",
        "light": "#adb5bd",
        "dark": "#121212",
        "bg": VLC_DARK_BG,
        "fg": VLC_TEXT,
        "selectbg": VLC_ORANGE,
        "selectfg": "#ffffff",
        "border": VLC_BORDER,
        "inputfg": VLC_TEXT,
        "inputbg": VLC_INPUT_BG,
        "active": "#353535",
    },
    "mode": "dark",
}


def setup_theme(style: tb.Style = None) -> tb.Style:
    """Register and apply the custom VLC Dark theme to ttkbootstrap."""
    if style is None:
        style = tb.Style()

    if "vlc_dark" not in style.theme_names():
        theme = ThemeDefinition(
            name=VLC_DARK_THEME_DEF["name"],
            colors=VLC_DARK_THEME_DEF["colors"],
            mode=VLC_DARK_THEME_DEF["mode"],
        )
        style.register_theme(theme)

    style.theme_use("vlc_dark")

    # Custom style enhancements
    style.configure("TNotebook", background=VLC_DARK_BG, borderwidth=0)
    style.configure("TNotebook.Tab", padding=[18, 8], font=("Segoe UI", 10, "bold"))
    style.map(
        "TNotebook.Tab",
        background=[("selected", VLC_ORANGE), ("active", VLC_PANEL_BG)],
        foreground=[("selected", "#ffffff"), ("!selected", VLC_TEXT_MUTED)],
    )

    # Primary Action Button
    style.configure(
        "VLC.TButton",
        font=("Segoe UI", 10, "bold"),
        padding=(12, 6),
        background=VLC_ORANGE,
        foreground="#ffffff",
        borderwidth=0
    )
    style.map(
        "VLC.TButton",
        background=[("active", VLC_ORANGE_HOVER), ("disabled", "#555555")],
        foreground=[("disabled", "#888888")]
    )

    # Secondary Action Button (Crisp and readable on dark bg)
    style.configure(
        "Action.TButton",
        font=("Segoe UI", 9, "bold"),
        padding=(10, 5),
        background="#383838",
        foreground="#f0f0f0",
        borderwidth=1,
        bordercolor=VLC_BORDER
    )
    style.map(
        "Action.TButton",
        background=[("active", "#4a4a4a"), ("disabled", "#282828")],
        foreground=[("disabled", "#666666")]
    )

    # Danger Action Button
    style.configure(
        "Danger.TButton",
        font=("Segoe UI", 9, "bold"),
        padding=(10, 5),
        background="#4d1f1f",
        foreground="#ff6b6b",
        borderwidth=1,
        bordercolor="#6b2a2a"
    )
    style.map(
        "Danger.TButton",
        background=[("active", "#662626")]
    )

    # Treeview Styling
    style.configure(
        "Treeview",
        background=VLC_PANEL_BG,
        fieldbackground=VLC_PANEL_BG,
        foreground=VLC_TEXT,
        rowheight=30,
        font=("Segoe UI", 9),
        borderwidth=1,
        relief="solid"
    )
    style.map(
        "Treeview",
        background=[("selected", VLC_ORANGE)],
        foreground=[("selected", "#ffffff")]
    )

    style.configure(
        "Treeview.Heading",
        background="#2e2e2e",
        foreground=VLC_ORANGE,
        font=("Segoe UI", 9, "bold"),
        padding=(8, 6),
        relief="flat"
    )
    style.map(
        "Treeview.Heading",
        background=[("active", "#383838")],
        foreground=[("active", VLC_ORANGE_HOVER)]
    )

    style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"), foreground=VLC_ORANGE)
    style.configure("Muted.TLabel", foreground=VLC_TEXT_MUTED, font=("Segoe UI", 9))

    return style
