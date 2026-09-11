import ttkbootstrap as tb
from ttkbootstrap.style import ThemeDefinition

# VLC-inspired palette & layered dark surfaces
VLC_ORANGE = "#FF8800"
VLC_ORANGE_HOVER = "#FFA733"
VLC_ORANGE_DARK = "#CC6D00"
VLC_DARK_BG = "#141414"
VLC_PANEL_BG = "#1e1e1e"
VLC_INPUT_BG = "#282828"
VLC_BORDER = "#383838"
VLC_TEXT = "#f5f5f5"
VLC_TEXT_MUTED = "#a5a5a5"

# Semantic Color Tags for Activity Console & Badges
COLOR_SUCCESS = "#2ecc71"
COLOR_ERROR = "#e74c3c"
COLOR_WARN = "#f39c12"
COLOR_INFO = "#ff8800"
COLOR_URL = "#3498db"
COLOR_STREAM = "#ff9800"
COLOR_DOWNLOAD = "#29b6f6"

VLC_DARK_THEME_DEF = {
    "name": "vlc_dark",
    "colors": {
        "primary": VLC_ORANGE,
        "secondary": "#3e3e3e",
        "success": COLOR_SUCCESS,
        "info": COLOR_DOWNLOAD,
        "warning": VLC_ORANGE,
        "danger": COLOR_ERROR,
        "light": "#b0b0b0",
        "dark": "#101010",
        "bg": VLC_DARK_BG,
        "fg": VLC_TEXT,
        "selectbg": VLC_ORANGE,
        "selectfg": "#ffffff",
        "border": VLC_BORDER,
        "inputfg": VLC_TEXT,
        "inputbg": VLC_INPUT_BG,
        "active": "#323232",
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
    style.configure("TNotebook.Tab", padding=[16, 9], font=("Segoe UI", 10, "bold"))
    style.map(
        "TNotebook.Tab",
        background=[("selected", VLC_ORANGE), ("active", VLC_PANEL_BG)],
        foreground=[("selected", "#ffffff"), ("!selected", VLC_TEXT_MUTED)],
    )

    # Primary Action Button
    style.configure(
        "VLC.TButton",
        font=("Segoe UI", 10, "bold"),
        padding=(14, 7),
        background=VLC_ORANGE,
        foreground="#ffffff",
        borderwidth=0
    )
    style.map(
        "VLC.TButton",
        background=[("active", VLC_ORANGE_HOVER), ("disabled", "#444444")],
        foreground=[("disabled", "#777777")]
    )

    # Secondary Action Button (Crisp and readable on dark bg)
    style.configure(
        "Action.TButton",
        font=("Segoe UI", 9, "bold"),
        padding=(10, 5),
        background="#353535",
        foreground="#f0f0f0",
        borderwidth=1,
        bordercolor=VLC_BORDER
    )
    style.map(
        "Action.TButton",
        background=[("active", "#464646"), ("disabled", "#242424")],
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
        rowheight=32,
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
        background="#2a2a2a",
        foreground=VLC_ORANGE,
        font=("Segoe UI", 9, "bold"),
        padding=(8, 7),
        relief="flat"
    )
    style.map(
        "Treeview.Heading",
        background=[("active", "#363636")],
        foreground=[("active", VLC_ORANGE_HOVER)]
    )

    style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"), foreground=VLC_ORANGE)
    style.configure("Subheader.TLabel", font=("Segoe UI", 10, "bold"), foreground=VLC_TEXT)
    style.configure("Muted.TLabel", foreground=VLC_TEXT_MUTED, font=("Segoe UI", 9))
    style.configure("Card.TFrame", background=VLC_PANEL_BG, relief="flat")
    style.configure("CardHeader.TLabel", font=("Segoe UI", 10, "bold"), foreground=VLC_ORANGE)

    return style


def setup_treeview_tags(tree):
    """Configure common row tags for Treeview widgets."""
    tree.tag_configure("streamed", foreground=COLOR_STREAM)
    tree.tag_configure("downloaded", foreground=COLOR_DOWNLOAD)
    tree.tag_configure("even", background="#1e1e1e")
    tree.tag_configure("odd", background="#242424")
