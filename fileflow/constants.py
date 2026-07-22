# ----------------------------------------------------------------------
# ----------------------  COLOR & DESIGN SYSTEM  -----------------------
# ----------------------------------------------------------------------
import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Typography Font Family
FONT_FAMILY = "Anthropic Serif"

# -- DYNAMIC THEME SYSTEM (Dark / Light) --------------------------
# Access via C.XXX - e.g. C.C.BG_PRIMARY, C.C.TEXT_HEADING
# Switch with: C.set_mode("dark") or C.set_mode("light")
class _Theme:
    _mode = "dark"
    _palettes = {
        "dark": {
            "BG_PRIMARY":    "#09090B",   # App background - near-black charcoal
            "BG_SECONDARY":  "#111216",   # Sidebar & Header - slightly lighter
            "BG_CARD":       "#181A20",   # Card surface - soft dark
            "BG_INPUT":      "#20232B",   # Input field - discernible dark
            "BG_GLASS":      "#13151B", # Glass element - subtle dark elevation
            "BORDER_COLOR":  "#1E2028", # Subtle border - dark gray stroke
            "BORDER_HOVER":  "#5EA2FF",   # Hover border glow - crisp blue
            "ACCENT_BLUE":   "#5EA2FF",   # Primary Accent
            "ACCENT_PURPLE": "#6D7CFF",   # Secondary Accent
            "ACCENT_CYAN":   "#4FD1FF",   # Cyan accent
            "ACCENT_AMBER":  "#FBBF24",   # Warning amber
            "ACCENT_EMERALD":"#22C55E",   # Success green
            "ACCENT_RED":    "#F87171",   # Danger red
            "TEXT_HEADING":  "#F8FAFC",   # Primary Heading - near-white
            "TEXT_BODY":     "#CBD5E1",   # Body Text - soft silver
            "TEXT_MUTED":    "#94A3B8",   # Muted text - slate
            "TEXT_DISABLED": "#64748B",   # Disabled text - dimmed slate
            "PHASE1_COLOR":  "#5EA2FF",
            "PHASE2_COLOR":  "#6D7CFF",
        },
        "light": {
            "BG_PRIMARY":    "#F6F7FB",   # App background - warm off-white (Apple)
            "BG_SECONDARY":  "#FCFCFD",   # Sidebar & Header - warm white (Fluent 2)
            "BG_CARD":       "#FFFFFF",   # Card surface - pure white (elevation)
            "BG_INPUT":      "#F1F5F9",   # Input field - subtle warm gray
            "BG_GLASS":      "#F8F9FB",   # Glass element - warm glass white
            "BORDER_COLOR":  "#E5E7EB",   # Subtle border - warm gray stroke
            "BORDER_HOVER":  "#3B82F6",   # Hover border glow - Fluent blue
            "ACCENT_BLUE":   "#3B82F6",   # Primary Accent - Fluent blue
            "ACCENT_PURPLE": "#6366F1",   # Secondary Accent - Indigo
            "ACCENT_CYAN":   "#06B6D4",   # Cyan accent
            "ACCENT_AMBER":  "#D97706",   # Warning amber
            "ACCENT_EMERALD":"#16A34A",   # Success green
            "ACCENT_RED":    "#DC2626",   # Danger red
            "TEXT_HEADING":  "#0F172A",   # Primary Heading - deep navy (WCAG AAA)
            "TEXT_BODY":     "#1E293B",   # Body Text - dark slate (WCAG AA+)
            "TEXT_MUTED":    "#475569",   # Muted text - medium slate (WCAG AA)
            "TEXT_DISABLED": "#94A3B8",   # Disabled text - light slate
            "PHASE1_COLOR":  "#3B82F6",
            "PHASE2_COLOR":  "#6366F1",
        },
    }
    def __getattribute__(self, name):
        if name in ("_mode", "_palettes", "set_mode", "_key"):
            return super().__getattribute__(name)
        palette = self._palettes[self._mode]
        if name in palette:
            return palette[name]
        return super().__getattribute__(name)
    def set_mode(self, mode):
        self._mode = mode

C = _Theme()

# ----------------------------------------------------------------------
# ----------------------  FILE TYPE CATEGORIES  ------------------------
# ----------------------------------------------------------------------
file_types = {
    "Images":     [".jpg",".jpeg",".png",".webp",".bmp",".gif",".tiff",".tif",".heic",".heif",".svg"],
    "RAW_Images": [".raw",".cr2",".nef",".arw",".dng"],
    "Videos":     [".mp4",".mkv",".avi",".mov",".wmv",".flv",".webm",".mpeg",".mpg",".3gp",".m4v",".ts",".vob"],
    "Audio":      [".mp3",".wav",".aac",".flac",".ogg",".opus",".m4a",".wma",".aiff",".alac"],
    "Documents":  [".pdf",".txt",".doc",".docx",".odt",".xls",".xlsx",".ods",".ppt",".pptx",".odp",".csv",".rtf",".md",".epub"],
    "Archives":   [".zip",".rar",".7z",".tar",".gz",".bz2",".xz",".iso"],
    "Code":       [".py",".js",".html",".css",".java",".c",".cpp",".json",".xml",".yml",".yaml",".sh",".bat"]
}

MONTHS = {
    1:"January", 2:"February", 3:"March",    4:"April",
    5:"May",     6:"June",     7:"July",      8:"August",
    9:"September",10:"October",11:"November",12:"December"
}
