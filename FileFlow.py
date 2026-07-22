# ----------------------------------------------------------------------
# ----------------------  IMPORTS & CONSTANTS  -------------------------
# ----------------------------------------------------------------------
import os
import getpass
import shutil
import hashlib
import time
from datetime import datetime
import threading
import queue

# GUI - requires: pip install customtkinter
import customtkinter as ctk
from tkinter import filedialog, messagebox

# ----------------------------------------------------------------------
# ----------------------  COLOR & DESIGN SYSTEM  -----------------------
# ----------------------------------------------------------------------
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
# ----------------------  ANIMATION ENGINE  ---------------------------
# ----------------------------------------------------------------------
import math
import ctypes
from tkinter import Canvas

# --- Easing Functions ---
def ease_out_cubic(t):
    return 1 - (1 - t) ** 3

def ease_out_quart(t):
    return 1 - (1 - t) ** 4

def ease_out_back(t):
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2

# --- Reduce Motion Detection ---
def is_reduce_motion_enabled():
    """Check Windows 'Show animations' / Reduce Motion setting."""
    try:
        SPI_GETCLIENTAREAANIMATION = 0x1042
        enabled = ctypes.windll.user32.SystemParametersInfoW(SPI_GETCLIENTAREAANIMATION, 0, None, 0)
        return not enabled
    except Exception:
        return False

REDUCE_MOTION = is_reduce_motion_enabled()

# --- Smooth Property Animator ---
class Animator:
    """Manages smooth property transitions for widgets using after() callbacks."""

    @staticmethod
    def animate_property(widget, attr, end_value, duration=180, start_value=None):
        """Smoothly transition a widget property from current to end value."""
        if REDUCE_MOTION:
            widget.configure(**{attr: end_value})
            return

        def lerp_color(c1, c2, t):
            """Linearly interpolate between two hex colors."""
            if len(c1) == 7 and len(c2) == 7:
                r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
                r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
                r = int(r1 + (r2 - r1) * t)
                g = int(g1 + (g2 - g1) * t)
                b = int(b1 + (b2 - b1) * t)
                return f"#{r:02x}{g:02x}{b:02x}"
            return c2 if t >= 1 else c1

        if start_value is None:
            try:
                start_value = widget.cget(attr)
            except Exception:
                start_value = end_value

        steps = max(8, int(duration / 16))
        step_ms = duration // steps

        def _step(frame=0):
            t = ease_out_cubic(frame / steps)
            if attr == "border_color" or attr == "fg_color" or attr == "text_color":
                val = lerp_color(str(start_value), str(end_value), t)
            else:
                val = start_value + (end_value - start_value) * t if isinstance(start_value, (int, float)) else end_value
            try:
                widget.configure(**{attr: val})
            except Exception:
                pass
            if frame < steps:
                widget.after(step_ms, lambda: _step(frame + 1))

        _step()

    @staticmethod
    def animate_geometry(widget, height=None, width=None, duration=200):
        """Smoothly transition widget dimensions."""
        if REDUCE_MOTION:
            kw = {}
            if height is not None: kw["height"] = height
            if width is not None: kw["width"] = width
            if kw: widget.configure(**kw)
            return

        curr_h = widget.winfo_height() if height is not None else None
        curr_w = widget.winfo_width() if width is not None else None
        steps = max(8, int(duration / 16))
        step_ms = duration // steps

        def _step(frame=0):
            t = ease_out_cubic(frame / steps)
            kw = {}
            if height is not None and curr_h:
                kw["height"] = int(curr_h + (height - curr_h) * t)
            if width is not None and curr_w:
                kw["width"] = int(curr_w + (width - curr_w) * t)
            if kw:
                try: widget.configure(**kw)
                except: pass
            if frame < steps:
                widget.after(step_ms, lambda: _step(frame + 1))

        _step()

# --- Card Hover Mixin ---
class HoverMixin:
    """Adds hover scale + lift + border glow to any CTkFrame-based card."""

    def _setup_hover(self):
        if REDUCE_MOTION:
            return
        self._hover_active = False
        self._orig_border = self.cget("border_color")
        self.bind("<Enter>", self._on_hover_enter, add="+")
        self.bind("<Leave>", self._on_hover_leave, add="+")

    def _on_hover_enter(self, event=None):
        if REDUCE_MOTION or getattr(self, "_hover_active", False):
            return
        self._hover_active = True
        # Scale via padding + border glow
        Animator.animate_property(self, "border_color", C.ACCENT_BLUE, duration=200,
                                  start_value=self._orig_border)
        self._do_hover_enter()

    def _on_hover_leave(self, event=None):
        if not getattr(self, "_hover_active", False):
            return
        self._hover_active = False
        Animator.animate_property(self, "border_color", self._orig_border, duration=300,
                                  start_value=C.ACCENT_BLUE)
        self._do_hover_leave()

    def _do_hover_enter(self):
        """Override in subclass for specific hover behavior."""
        pass

    def _do_hover_leave(self):
        """Override in subclass for specific hover behavior."""
        pass


# --- Button Press Animation ---
def make_button_premium(btn, primary=True):
    """Add press/release and hover glow animations to a CTkButton."""
    if REDUCE_MOTION:
        return

    orig_fg = btn.cget("fg_color")
    orig_hover = btn.cget("hover_color")

    def _on_enter(e):
        if primary:
            # Scale effect via padding: simulate by geometry
            pass

    def _on_leave(e):
        pass

    def _on_press(e):
        # Scale down via geometry
        h = btn.winfo_height()
        w = btn.winfo_width()
        if h > 10 and w > 10:
            btn.configure(height=max(10, h - 2), width=max(10, w - 2))

    def _on_release(e):
        h = btn.winfo_height()
        w = btn.winfo_width()
        if h > 10 and w > 10:
            btn.configure(height=h + 2, width=w + 2)

    btn.bind("<ButtonPress-1>", _on_press, add="+")
    btn.bind("<ButtonRelease-1>", _on_release, add="+")


# --- Input Focus Animation ---
def setup_input_focus(entry):
    """Add focus border glow to a CTkEntry."""
    if REDUCE_MOTION:
        return
    def _on_focus_in(e):
        Animator.animate_property(entry, "border_color", C.ACCENT_BLUE, duration=150,
                                  start_value=entry.cget("border_color"))
    def _on_focus_out(e):
        Animator.animate_property(entry, "border_color", C.BORDER_COLOR, duration=200,
                                  start_value=C.ACCENT_BLUE)
    entry.bind("<FocusIn>", _on_focus_in, add="+")
    entry.bind("<FocusOut>", _on_focus_out, add="+")


# --- Number Counter Animation ---
def animate_counter(label, target_val, duration=800):
    """Animate a label's text from 0 to target value."""
    if REDUCE_MOTION:
        label.configure(text=str(target_val))
        return

    try:
        target = int(target_val)
    except ValueError:
        label.configure(text=str(target_val))
        return

    steps = max(12, int(duration / 16))
    step_ms = duration // steps

    def _step(frame=0):
        t = ease_out_quart(frame / steps)
        current = int(target * t)
        label.configure(text=str(max(0, current)))
        if frame < steps:
            label.after(step_ms, lambda: _step(frame + 1))

    _step()


# --- Shake Animation ---
def shake_widget(widget, intensity=6, duration=300):
    """Shake a widget horizontally."""
    if REDUCE_MOTION:
        return
    steps = duration // 20
    orig_x = widget.winfo_x()

    def _step(frame=0):
        if frame >= steps:
            try: widget.place_configure(x=orig_x)
            except: pass
            return
        offset = intensity * math.sin(frame * 2 * math.pi / 3) * (1 - frame / steps)
        try: widget.place_configure(x=orig_x + int(offset))
        except: pass
        widget.after(20, lambda: _step(frame + 1))

    _step()


# --- Page Transition ---
_current_page_overlay = None

def crossfade_switch(app, page_key, duration=200):
    """Crossfade between pages."""
    if REDUCE_MOTION:
        app._switch_page_direct(page_key)
        return

    # Create overlay for fade
    overlay = ctk.CTkFrame(app.page_container, fg_color=C.BG_PRIMARY, corner_radius=0)
    overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
    overlay.lift()

    steps = max(6, int(duration / 16))
    step_ms = duration // steps

    def _fade_in(frame=0):
        t = ease_out_cubic(frame / steps)
        if frame >= steps:
            app._switch_page_direct(page_key)
            _fade_out()
            return
        overlay.after(step_ms, lambda: _fade_in(frame + 1))

    def _fade_out(frame=0):
        t = ease_out_cubic(frame / steps)
        alpha = int(255 * t)
        try:
            bg = C.BG_PRIMARY
            if len(bg) == 7:
                overlay.configure(fg_color=f"{bg}{alpha:02x}")
        except:
            pass
        if frame >= steps:
            overlay.destroy()
            return
        overlay.after(step_ms, lambda: _fade_out(frame + 1))

    _fade_in()


# --- Success Ring Animation ---
def show_success_ring(parent):
    """Show an expanding success ring animation."""
    canvas = Canvas(parent, bg="", highlightthickness=0)
    canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
    canvas.lift()

    cx = parent.winfo_width() // 2 if parent.winfo_width() > 1 else 200
    cy = parent.winfo_height() // 2 if parent.winfo_height() > 1 else 200
    max_r = max(cx, cy) + 50
    steps = 30

    def _ring(frame=0):
        t = frame / steps
        r = int(20 + (max_r - 20) * ease_out_cubic(t))
        alpha = int(255 * (1 - t))
        color = C.ACCENT_EMERALD
        try:
            canvas.delete("ring")
            canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                               outline=color, width=2, tags="ring",
                               dash=(8, 4))
        except:
            pass
        if frame < steps:
            canvas.after(16, lambda: _ring(frame + 1))
        else:
            canvas.after(400, canvas.destroy)

    _ring()


# ----------------------------------------------------------------------
# ----------------------  ORIGINAL LOGIC  -----------------------------
# ----------------------------------------------------------------------
# 📂 Paths - populated by GUI or empty by default
SOURCE_FOLDER = ""
DEST_FOLDER   = ""
LOG_FILE      = ""
REPORT_FILE   = ""

# 📁 Categories
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

hash_map = {}

# ----------------------------------------------------------------------
# ----------------------  HELPER FUNCTIONS  ---------------------------
# ----------------------------------------------------------------------
def get_file_hash(filepath):
    """SHA-256 hash - unchanged from original script."""
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()


def get_unique_filename(folder, filename):
    """Return a non-existing filename inside *folder*."""
    name, ext = os.path.splitext(filename)
    counter = 1
    new_name = filename
    while os.path.exists(os.path.join(folder, new_name)):
        new_name = f"{name}_{counter}{ext}"
        counter += 1
    return new_name


def get_image_date(filepath):
    """Read EXIF DateTimeOriginal - Pillow is required."""
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS
        image = Image.open(filepath)
        exif = image._getexif()
        if exif:
            for tag, value in exif.items():
                if TAGS.get(tag) == "DateTimeOriginal":
                    return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
    except Exception:
        pass
    return None


def get_file_date(filepath):
    """Best guess date (EXIF -> mtime)."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext in file_types["Images"] or ext in file_types["RAW_Images"]:
        exif_date = get_image_date(filepath)
        if exif_date:
            return exif_date
    return datetime.fromtimestamp(os.path.getmtime(filepath))


def get_category(file):
    """Which top-level folder the file belongs to."""
    ext = os.path.splitext(file)[1].lower()
    for category, exts in file_types.items():
        if ext in exts:
            return category
    return "Others"


def log(msg):
    """Append a line with timestamp to the log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_msg = f"[{timestamp}] {msg}"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(full_msg + "\n")


def get_folder_size(folder):
    """Recursive size in bytes."""
    total = 0
    if not os.path.exists(folder):
        return 0
    for root, _, files in os.walk(folder):
        for file in files:
            try:
                total += os.path.getsize(os.path.join(root, file))
            except Exception:
                pass
    return total


def format_size(size_bytes):
    """Human readable size string."""
    if size_bytes == 0:
        return "0 Bytes"
    elif size_bytes < 1024:
        return f"{size_bytes} Bytes"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes/1024:.2f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes/(1024**2):.2f} MB"
    else:
        return f"{size_bytes/(1024**3):.2f} GB"


# ----------------------------------------------------------------------
# ----------------------  PHASE 1 - ORGANISE  -------------------------
# ----------------------------------------------------------------------
def scan_existing_files():
    """Load already-present files from DEST_FOLDER into hash_map."""
    for root, _, files in os.walk(DEST_FOLDER):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path in (LOG_FILE, REPORT_FILE):
                continue
            try:
                file_hash = get_file_hash(file_path)
                hash_map[file_hash] = file_path
            except Exception:
                pass


def phase1_organize(update_cb=None):
    """
    Core of Phase 1 - exactly the same algorithm from the original script.
    update_cb is an optional callback for GUI live updates.
    """
    moved = duplicates = errors = 0

    scan_existing_files()

    for root, _, files in os.walk(SOURCE_FOLDER):
        for file in files:
            file_path = os.path.join(root, file)

            try:
                file_hash = get_file_hash(file_path)
                category = get_category(file)
                date = get_file_date(file_path)
                year = str(date.year)
                month = MONTHS[date.month]

                normal_folder = os.path.join(DEST_FOLDER, category, year, month)
                duplicate_folder = os.path.join(DEST_FOLDER, "Duplicates", category, year, month)

                if file_hash in hash_map:
                    # duplicate
                    os.makedirs(duplicate_folder, exist_ok=True)
                    unique_name = get_unique_filename(duplicate_folder, file)
                    dest_path = os.path.join(duplicate_folder, unique_name)
                    shutil.move(file_path, dest_path)

                    msg = f"DUPLICATE | {file} -> Duplicates/{category}/{year}/{month}/{unique_name}"
                    if update_cb: update_cb(msg)
                    log(msg)
                    duplicates += 1
                    continue

                # brand-new file
                hash_map[file_hash] = file_path
                os.makedirs(normal_folder, exist_ok=True)
                unique_name = get_unique_filename(normal_folder, file)
                dest_path = os.path.join(normal_folder, unique_name)
                shutil.move(file_path, dest_path)

                msg = f"MOVED | {file} -> {category}/{year}/{month}/{unique_name}"
                if update_cb: update_cb(msg)
                log(msg)
                moved += 1

            except Exception as e:
                msg = f"ERROR | {file} -> {e}"
                if update_cb: update_cb(msg)
                log(msg)
                errors += 1

    return moved, duplicates, errors


# ----------------------------------------------------------------------
# ----------------------  PHASE 2 - VERIFY  ---------------------------
# ----------------------------------------------------------------------
def phase2_verify(update_cb=None):
    """Same verification routine - only update_cb added."""
    normal_index = {}

    # build index of all non-duplicate files
    for root, _, files in os.walk(DEST_FOLDER):
        if "duplicates" in root.lower():
            continue
        for file in files:
            file_path = os.path.join(root, file)
            if file_path in (LOG_FILE, REPORT_FILE):
                continue
            try:
                file_hash = get_file_hash(file_path)
                parts = root.split(os.sep)
                if len(parts) >= 3:
                    category, year, month = parts[-3], parts[-2], parts[-1]
                    key = (category, year, month)
                    normal_index.setdefault(key, {})[file_hash] = file_path
            except Exception:
                pass

    perfect = []
    wrong   = []
    missing = []

    # walk duplicates and decide where they belong
    for root, _, files in os.walk(DEST_FOLDER):
        if "duplicates" not in root.lower():
            continue
        for file in files:
            file_path = os.path.join(root, file)
            try:
                file_hash = get_file_hash(file_path)
                parts = root.split(os.sep)
                if len(parts) >= 3:
                    category, year, month = parts[-3], parts[-2], parts[-1]
                    key = (category, year, month)

                    if key in normal_index and file_hash in normal_index[key]:
                        perfect.append(file_path)
                    else:
                        found_elsewhere = any(
                            file_hash in normal_index[k] for k in normal_index
                        )
                        (wrong if found_elsewhere else missing).append(file_path)
            except Exception:
                missing.append(file_path)

            if update_cb:
                update_cb(f"checked -> {file_path}")

    # write report
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("GOD MODE - DEEP VERIFICATION REPORT\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"PERFECT MATCH ({len(perfect)} files):\n\n")
        f.writelines(p + "\n" for p in perfect)
        f.write("\n" + "=" * 60 + "\n")
        f.write(f"\nWRONG LOCATION ({len(wrong)} files):\n\n")
        f.writelines(p + "\n" for p in wrong)
        f.write("\n" + "=" * 60 + "\n")
        f.write(f"\nMISSING - CRITICAL ({len(missing)} files):\n\n")
        f.writelines(p + "\n" for p in missing)

    return perfect, wrong, missing


# ----------------------------------------------------------------------
# ----------------------  REVERT / UNDO LOGIC  -------------------------
# ----------------------------------------------------------------------
def revert_organize(update_cb=None):
    """
    Reverts organized files from DEST_FOLDER back into SOURCE_FOLDER.
    Returns (restored_count, errors_count).
    """
    restored = 0
    errors = 0

    if not os.path.exists(DEST_FOLDER) or not os.path.exists(SOURCE_FOLDER):
        return 0, 0

    for root, _, files in os.walk(DEST_FOLDER):
        for file in files:
            file_path = os.path.join(root, file)

            # Skip log and report files
            if file_path in (LOG_FILE, REPORT_FILE):
                continue

            try:
                unique_name = get_unique_filename(SOURCE_FOLDER, file)
                dest_path = os.path.join(SOURCE_FOLDER, unique_name)

                shutil.move(file_path, dest_path)
                restored += 1

                msg = f"REVERTED | {file} -> Source/{unique_name}"
                if update_cb: update_cb(msg)
                log(msg)
            except Exception as e:
                msg = f"REVERT ERROR | {file} -> {e}"
                if update_cb: update_cb(msg)
                log(msg)
                errors += 1

    return restored, errors


# ----------------------------------------------------------------------
# ----------------------  CUSTOM WIDGETS  -----------------------------
# ----------------------------------------------------------------------
class HeroFolderCard(HoverMixin, ctk.CTkFrame):
    """Hero folder selection card with glass styling & gradient button."""

    def __init__(self, master, label: str, icon: str, default_path: str, accent_color: str, **kwargs):
        super().__init__(
            master,
            fg_color=C.BG_CARD,
            border_color=C.BORDER_COLOR,
            border_width=1,
            corner_radius=18,
            **kwargs
        )
        self.columnconfigure(1, weight=1)
        self._accent = accent_color
        self._setup_hover()

        # Header Row + Circular Icon (self-contained rounded label for perfect emoji centering)
        hdr_frame = ctk.CTkFrame(self, fg_color="transparent")
        hdr_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=16, pady=(16, 8))
        hdr_frame.columnconfigure(1, weight=1)

        ctk.CTkLabel(
            hdr_frame,
            text=icon,
            font=ctk.CTkFont(size=20),
            text_color=accent_color,
            fg_color=C.BG_GLASS,
            width=40,
            height=40,
            corner_radius=20,
        ).grid(row=0, column=0, padx=(0, 10))

        ctk.CTkLabel(
            hdr_frame,
            text=label,
            font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"),
            text_color=C.TEXT_HEADING,
            anchor="w",
        ).grid(row=0, column=1, sticky="w")

        # Entry + Browse Row
        self.var = ctk.StringVar(value=default_path)
        self.entry = ctk.CTkEntry(
            self,
            textvariable=self.var,
            fg_color=C.BG_INPUT,
            border_color=C.BORDER_COLOR,
            border_width=1,
            text_color=C.TEXT_BODY,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            corner_radius=10,
            height=40,
            placeholder_text="Select a folder path..."
        )
        self.entry.grid(row=1, column=0, sticky="ew", padx=(16, 8), pady=(0, 16))
        self.columnconfigure(0, weight=1)
        setup_input_focus(self.entry)

        self.btn = ctk.CTkButton(
            self,
            text="📁 Browse",
            width=100,
            height=40,
            corner_radius=10,
            fg_color=accent_color,
            hover_color=C.ACCENT_BLUE if accent_color != C.ACCENT_BLUE else C.ACCENT_PURPLE,
            text_color="#FFFFFF",
            font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
            command=self._browse,
        )
        self.btn.grid(row=1, column=1, padx=(0, 16), pady=(0, 16))
        make_button_premium(self.btn, primary=True)

    def _browse(self):
        path = filedialog.askdirectory()
        if path:
            self.var.set(path)

    def get(self) -> str:
        return self.var.get().strip()


class StatCard(HoverMixin, ctk.CTkFrame):
    """Premium 28px card metric display with circular icon container."""

    def __init__(self, master, title: str, value: str, icon: str, color: str, helper: str, **kwargs):
        super().__init__(
            master,
            fg_color=C.BG_CARD,
            border_color=C.BORDER_COLOR,
            border_width=1,
            corner_radius=16,
            **kwargs
        )
        self._stat_color = color
        self._setup_hover()

        top_row = ctk.CTkFrame(self, fg_color="transparent")
        top_row.pack(fill="x", padx=16, pady=(16, 6))
        top_row.columnconfigure(1, weight=1)

        # Circular Icon (self-contained rounded label for perfect emoji centering)
        ctk.CTkLabel(
            top_row,
            text=icon,
            font=ctk.CTkFont(size=20),
            text_color=color,
            fg_color=C.BG_GLASS,
            width=40,
            height=40,
            corner_radius=20,
        ).grid(row=0, column=0, padx=(0, 12))

        # Large 28px Number
        self.val_lbl = ctk.CTkLabel(
            top_row,
            text=value,
            font=ctk.CTkFont(family=FONT_FAMILY, size=24, weight="bold"),
            text_color=C.TEXT_HEADING,
            anchor="w",
        )
        self.val_lbl.grid(row=0, column=1, sticky="w")

        # Title (15px)
        ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            text_color=C.TEXT_MUTED,
            anchor="w",
        ).pack(fill="x", padx=16, pady=(0, 2))

        # Helper text (13px)
        self.helper_lbl = ctk.CTkLabel(
            self,
            text=helper,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=color if helper != "-" else C.TEXT_DISABLED,
            anchor="w",
        )
        self.helper_lbl.pack(fill="x", padx=16, pady=(0, 14))

    def set_value(self, val: str, helper: str = None):
        animate_counter(self.val_lbl, val, duration=800)
        if helper is not None:
            self.helper_lbl.configure(text=helper)


# ----------------------------------------------------------------------
# ----------------------  MAIN APPLICATION  ---------------------------
# ----------------------------------------------------------------------
class FileFlowApp(ctk.CTk):
    """
    FileFlow Main Window - Premium Modern Desktop UI.
    """

    def __init__(self):
        super().__init__()

        self.title("FileFlow  -  Smart File Organizer")
        self._config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fileflow_config.json")
        self._theme_mode = "dark"

        # Load persisted theme
        try:
            import json
            if os.path.exists(self._config_path):
                with open(self._config_path, "r") as f:
                    cfg = json.load(f)
                if cfg.get("theme") == "light":
                    self._theme_mode = "light"
                    ctk.set_appearance_mode("light")
                    C.set_mode("light")
        except:
            pass

        # Dynamic sizing: 80% of screen dimensions, centered
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = int(screen_width * 0.80)
        window_height = int(screen_height * 0.80)

        # Center the window on screen
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.minsize(980, 700)
        self.configure(fg_color=C.BG_PRIMARY)

        # Window open animation: fade in + scale from 0.98
        if not REDUCE_MOTION:
            try: self.attributes("-alpha", 0)
            except: pass
            geom = self.geometry()
            self.after(20, lambda: self._animate_window_open(geom))
        else:
            self.attributes("-alpha", 1)

        # Activity history storage (max 5 shown, plus full log)
        self.activity_items = []
        self.full_activity_log = []

        # Page-switching navigation
        self.pages = {}
        self.current_page = "overview"
        self.nav_buttons = {}

        # Shared stats data for cross-page display
        self._stats = {
            "moved": 0, "dupes": 0, "errors": 0, "missing": 0,
            "time": "00:00:00", "perfect": 0, "wrong": 0,
            "size_before": "0 B", "size_after": "0 B",
        }

        self._build_ui()

        # Queue for thread-safe UI updates
        self.msg_queue: queue.Queue = queue.Queue()
        self.after(100, self._drain_queue)

    def _animate_window_open(self, geom):
        """Fade-in and scale-up animation on launch (250ms)."""
        steps = 16
        step_ms = 250 // steps
        try:
            self.attributes("-alpha", 0)
            # Parse geometry for scaling effect
            parts = geom.split("+")
            base_w = int(parts[0].split("x")[0]) if "x" in parts[0] else 1200
            base_h = int(parts[0].split("x")[1]) if "x" in parts[0] else 800
        except:
            return

        def _step(frame=0):
            t = ease_out_cubic(frame / steps)
            alpha = t
            scale = 0.98 + 0.02 * t
            w = int(base_w * scale)
            h = int(base_h * scale)
            try:
                self.attributes("-alpha", alpha)
                # Subtle scale via geometry
                if abs(scale - 1.0) > 0.001:
                    cx = (self.winfo_screenwidth() - w) // 2
                    cy = (self.winfo_screenheight() - h) // 2
                    self.geometry(f"{w}x{h}+{cx}+{cy}")
            except:
                pass
            if frame < steps:
                self.after(step_ms, lambda: _step(frame + 1))

        _step()

    # ------------------------------------------------------------------
    #   UI Construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        # -- MAIN LAYOUT: Sidebar (Left) + Content (Right) --------------
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # -- LEFT SIDEBAR ----------------------------------------------
        sidebar = ctk.CTkFrame(self, fg_color=C.BG_SECONDARY, width=200, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.pack_propagate(False)
        self._sidebar_ref = sidebar

        # Logo & App Title Header
        brand_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand_frame.pack(fill="x", padx=20, pady=24)

        ctk.CTkLabel(
            brand_frame,
            text="⬡",
            font=ctk.CTkFont(size=22),
            text_color="#FFFFFF",
            fg_color=C.ACCENT_BLUE,
            width=38,
            height=38,
            corner_radius=12,
        ).pack(side="left", padx=(0, 12))

        brand_text = ctk.CTkFrame(brand_frame, fg_color="transparent")
        brand_text.pack(side="left")

        ctk.CTkLabel(
            brand_text, text="FileFlow",
            font=ctk.CTkFont(family=FONT_FAMILY, size=20, weight="bold"),
            text_color=C.TEXT_HEADING
        ).pack(anchor="w")

        ctk.CTkLabel(
            brand_text, text="Smart File Organizer",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=C.TEXT_MUTED
        ).pack(anchor="w")

        # Nav Items List (page_key, label, icon)
        nav_items = [
            ("overview", "🏠 Overview"),
            ("pipeline", "⚙ Pipeline"),
            ("statistics", "📊 Statistics"),
            ("activity", "⏱ Activity"),
            ("settings", "🛠 Settings"),
        ]

        nav_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav_frame.pack(fill="x", padx=16, pady=10)

        for page_key, name in nav_items:
            is_active = (page_key == "overview")
            btn = ctk.CTkButton(
                nav_frame,
                text=name,
                anchor="w",
                height=40,
                corner_radius=10,
                fg_color=C.ACCENT_BLUE if is_active else "transparent",
                hover_color=C.ACCENT_PURPLE if is_active else C.BG_CARD,
                text_color=C.TEXT_HEADING if is_active else C.TEXT_MUTED,
                font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold" if is_active else "normal"),
                command=lambda k=page_key: self._switch_page(k),
            )
            btn.pack(fill="x", pady=3)
            self.nav_buttons[page_key] = btn

        # "Organize Smarter" promo card in sidebar bottom
        promo = ctk.CTkFrame(sidebar, fg_color=C.BG_CARD, border_color=C.BORDER_COLOR, border_width=1, corner_radius=14)
        promo.pack(fill="x", padx=16, pady=(30, 16))

        ctk.CTkLabel(promo, text="✨", font=ctk.CTkFont(size=18), text_color=C.ACCENT_PURPLE).pack(anchor="w", padx=14, pady=(12, 2))
        ctk.CTkLabel(promo, text="Organize Smarter", font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"), text_color=C.TEXT_HEADING).pack(anchor="w", padx=14)
        ctk.CTkLabel(promo, text="FileFlow uses smart rules to keep your files neat and organized.", font=ctk.CTkFont(family=FONT_FAMILY, size=11), text_color=C.TEXT_MUTED, wraplength=180).pack(anchor="w", padx=14, pady=(2, 12))

        # Fetch logged-in user dynamically
        try:
            current_username = getpass.getuser()
        except Exception:
            try:
                current_username = os.getlogin()
            except Exception:
                current_username = "User"

        avatar_letter = current_username[0].upper() if current_username else "U"

        # Profile Card at sidebar bottom
        profile = ctk.CTkFrame(sidebar, fg_color=C.BG_CARD, border_color=C.BORDER_COLOR, border_width=1, corner_radius=14)
        profile.pack(fill="x", side="bottom", padx=16, pady=20)

        ctk.CTkLabel(
            profile,
            text=avatar_letter,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#FFFFFF",
            fg_color=C.ACCENT_BLUE,
            width=34,
            height=34,
            corner_radius=17,
        ).pack(side="left", padx=10, pady=10)

        p_info = ctk.CTkFrame(profile, fg_color="transparent")
        p_info.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(p_info, text=current_username, font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"), text_color=C.TEXT_HEADING).pack(anchor="w")
        ctk.CTkLabel(p_info, text="Local User", font=ctk.CTkFont(family=FONT_FAMILY, size=11), text_color=C.TEXT_MUTED).pack(anchor="w")

        # -- RIGHT CONTENT CONTAINER ----------------------------------
        content_container = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        content_container.grid(row=0, column=1, sticky="nsew")
        content_container.columnconfigure(0, weight=1)
        content_container.rowconfigure(1, weight=1)

        # -- TOP HEADER BAR --------------------------------------------
        header_bar = ctk.CTkFrame(content_container, fg_color=C.BG_SECONDARY, height=72, corner_radius=0)
        header_bar.grid(row=0, column=0, sticky="ew")
        header_bar.pack_propagate(False)
        self._header_bar_ref = header_bar

        # Left Greeting
        h_left = ctk.CTkFrame(header_bar, fg_color="transparent")
        h_left.pack(side="left", padx=24, pady=12)

        ctk.CTkLabel(
            h_left, text=f"Welcome back, {current_username}! 👋",
            font=ctk.CTkFont(family=FONT_FAMILY, size=20, weight="bold"),
            text_color=C.TEXT_HEADING
        ).pack(anchor="w")

        ctk.CTkLabel(
            h_left, text="Let's organize your files and bring order to your chaos.",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            text_color=C.TEXT_MUTED
        ).pack(anchor="w")

        # Right Actions (Theme Toggle + Settings)
        h_right = ctk.CTkFrame(header_bar, fg_color="transparent")
        h_right.pack(side="right", padx=24)

        self.theme_toggle_btn = ctk.CTkButton(
            h_right, text=" ☀ Dark ",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=C.TEXT_BODY, fg_color=C.BG_CARD,
            hover_color=C.BG_INPUT,
            corner_radius=8, height=32, width=90,
            command=self._toggle_theme_header,
        )
        self.theme_toggle_btn.pack(side="left", padx=(0, 10))

        self.settings_btn = ctk.CTkButton(
            h_right, text=" ⚙ ",
            font=ctk.CTkFont(size=14),
            text_color=C.TEXT_BODY, fg_color=C.BG_CARD,
            hover_color=C.BG_INPUT,
            corner_radius=8, width=32, height=32,
            command=lambda: self._switch_page("settings"),
        )
        self.settings_btn.pack(side="left")

        # -- PAGE CONTAINER (content swaps based on nav selection) ----
        self.page_container = ctk.CTkFrame(content_container, fg_color="transparent")
        self.page_container.grid(row=1, column=0, sticky="nsew")
        self.page_container.columnconfigure(0, weight=1)
        self.page_container.rowconfigure(0, weight=1)

        # Build all pages (each wrapped in its own scrollable frame)
        self._build_overview_page()
        self._build_pipeline_page()
        self._build_statistics_page()
        self._build_activity_page()
        self._build_settings_page()

        # Show the default page
        self._switch_page_direct("overview")

    # ------------------------------------------------------------------
    #   Activity Display Helpers
    # ------------------------------------------------------------------
    def _render_empty_activity_state(self):
        """Render elegant empty state illustration."""
        for widget in self.act_container.winfo_children():
            widget.destroy()

        empty = ctk.CTkFrame(self.act_container, fg_color="transparent")
        empty.pack(fill="x", pady=20)

        ctk.CTkLabel(empty, text="📥", font=ctk.CTkFont(size=36), text_color=C.TEXT_DISABLED).pack()
        ctk.CTkLabel(empty, text="No activity yet", font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"), text_color=C.TEXT_BODY).pack(pady=(6, 2))
        ctk.CTkLabel(empty, text="Your file organization activity will appear here.", font=ctk.CTkFont(family=FONT_FAMILY, size=12), text_color=C.TEXT_MUTED).pack()

    def _add_activity_item(self, text: str):
        """Add recent activity item (keeping max 5). Also populates full log."""
        clean_text = text.strip()
        if not clean_text or clean_text.startswith("=") or clean_text.startswith("FINAL"):
            return

        # Store in full log for Activity page
        self.full_activity_log.append(clean_text)

        # Recent (max 5) for Overview page
        self.activity_items.insert(0, clean_text)
        if len(self.activity_items) > 5:
            self.activity_items.pop()

        for widget in self.act_container.winfo_children():
            widget.destroy()

        for item in self.activity_items:
            item_row = ctk.CTkFrame(self.act_container, fg_color=C.BG_GLASS, height=36, corner_radius=8)
            item_row.pack(fill="x", pady=3)

            icon = "✓" if "MOVED" in item or "REVERTED" in item or "complete" in item else "ℹ"
            color = C.ACCENT_EMERALD if "MOVED" in item or "complete" in item else C.ACCENT_BLUE

            ctk.CTkLabel(item_row, text=f" {icon} ", font=ctk.CTkFont(size=12, weight="bold"), text_color=color).pack(side="left", padx=(10, 6))
            ctk.CTkLabel(item_row, text=item, font=ctk.CTkFont(family=FONT_FAMILY, size=12), text_color=C.TEXT_BODY, anchor="w").pack(side="left", fill="x", expand=True)

        # Also refresh the activity log text widget if it exists on Activity page
        if hasattr(self, "activity_log_text") and self.activity_log_text.winfo_exists():
            self.activity_log_text.configure(state="normal")
            self.activity_log_text.delete("1.0", "end")
            self.activity_log_text.insert("1.0", "\n".join(reversed(self.full_activity_log)))
            self.activity_log_text.configure(state="disabled")

    # ------------------------------------------------------------------
    #   Thread-safe Queue Drain
    # ------------------------------------------------------------------
    def _drain_queue(self):
        """Main thread queue drainer for activity updates."""
        try:
            while True:
                msg = self.msg_queue.get_nowait()
                self._add_activity_item(msg)
        except queue.Empty:
            pass
        self.after(100, self._drain_queue)

    # ------------------------------------------------------------------
    #   Start Organizing Action
    # ------------------------------------------------------------------
    def _start_god_mode(self):
        global SOURCE_FOLDER, DEST_FOLDER, LOG_FILE, REPORT_FILE

        src = self.card_src.get()
        dst = self.card_dst.get()

        if not src or not dst:
            messagebox.showerror("Missing Folder", "Both source and destination folders must be selected.")
            shake_widget(self.card_src.entry if not src else self.card_dst.entry)
            return
        if not os.path.isdir(src):
            messagebox.showerror("Invalid Source", f"The folder does not exist:\n{src}")
            shake_widget(self.card_src.entry)
            return

        SOURCE_FOLDER = src
        DEST_FOLDER   = dst
        LOG_FILE      = os.path.join(DEST_FOLDER, "god_mode_log.txt")
        REPORT_FILE   = os.path.join(DEST_FOLDER, "deep_verification.txt")
        os.makedirs(DEST_FOLDER, exist_ok=True)

        self.btn_start.configure(state="disabled", text="⏳   Organizing...")
        self.lbl_pipeline_badge.configure(text=" • Running Phase 1 ", text_color=C.ACCENT_BLUE, fg_color="#0F172A")
        self.progress_bar.set(0.4)

        # Also update Pipeline page badges
        self.after(0, lambda: self._update_pipeline_badges("phase1"))

        worker = threading.Thread(target=self._worker, daemon=True)
        worker.start()

    # ------------------------------------------------------------------
    #   Worker Thread
    # ------------------------------------------------------------------
    def _worker(self):
        start_time = time.time()

        # Capture source size BEFORE files are moved
        before_messy = get_folder_size(SOURCE_FOLDER)

        # Phase 1
        moved, dupes, errors = phase1_organize(
            update_cb=lambda txt: self.msg_queue.put(txt)
        )
        self.msg_queue.put(f"Phase 1 Complete - Moved: {moved} | Dupes: {dupes} | Errors: {errors}")

        # Update to Phase 2
        self.after(0, lambda: self.lbl_pipeline_badge.configure(text=" • Running Phase 2 ", text_color=C.ACCENT_PURPLE, fg_color="#1E1B4B"))
        self.after(0, lambda: self.s2_badge.configure(fg_color=C.ACCENT_PURPLE, text_color="#FFFFFF"))
        self.after(0, lambda: self.progress_bar.set(0.8))
        self.after(0, lambda: self._update_pipeline_badges("phase2"))

        # Phase 2
        perfect, wrong, missing = phase2_verify(
            update_cb=lambda txt: self.msg_queue.put(txt)
        )
        self.msg_queue.put(f"Phase 2 Complete - Perfect: {len(perfect)} | Wrong: {len(wrong)} | Missing: {len(missing)}")

        elapsed = time.time() - start_time
        mins, secs = divmod(int(elapsed), 60)
        time_str = f"{mins:02d}:{secs:02d}"

        after_messy  = get_folder_size(DEST_FOLDER)

        # Store in shared stats dict (for Statistics & Pipeline pages)
        self._stats.update({
            "moved": moved, "dupes": dupes, "errors": errors,
            "missing": len(missing), "time": time_str,
            "perfect": len(perfect), "wrong": len(wrong),
            "size_before": format_size(before_messy),
            "size_after": format_size(after_messy),
        })

        # Update Stat Cards on Overview page
        self.after(0, lambda: self.stat_moved.set_value(str(moved)))
        self.after(0, lambda: self.stat_dupes.set_value(str(dupes)))
        self.after(0, lambda: self.stat_errors.set_value(str(errors)))
        self.after(0, lambda: self.stat_missing.set_value(str(len(missing))))
        self.after(0, lambda: self.stat_time.set_value(time_str, "Completed"))
        self.after(0, lambda: self.stat_perfect.set_value(str(len(perfect))))
        self.after(0, lambda: self.stat_wrong.set_value(str(len(wrong))))
        self.after(0, lambda: self.stat_size.set_value(f"{format_size(before_messy)} → {format_size(after_messy)}", "100% processed"))

        # Update Statistics page stat cards if they exist
        self.after(0, lambda: self._refresh_statistics_page_stats())

        # Update Pipeline page badges if they exist
        self.after(0, lambda: self._refresh_pipeline_page_stats())

        self.after(0, lambda: self.progress_bar.set(1.0))
        self.after(0, lambda: self.lbl_pipeline_badge.configure(text=" • Completed ", text_color=C.ACCENT_EMERALD, fg_color="#0F2A1E"))
        self.after(0, lambda: self.btn_start.configure(state="normal", text="▶   Start Organizing"))
        self.after(0, lambda: self._update_pipeline_badges("complete"))
        # Success animation
        self.after(200, lambda: show_success_ring(self.page_container))

    # ------------------------------------------------------------------
    #   Revert Action
    # ------------------------------------------------------------------
    def _start_revert(self):
        global SOURCE_FOLDER, DEST_FOLDER, LOG_FILE, REPORT_FILE

        src = self.card_src.get()
        dst = self.card_dst.get()

        if not src or not dst:
            messagebox.showerror("Missing Folder", "Both source and destination folders must be selected.")
            return
        if not os.path.exists(dst):
            messagebox.showerror("Invalid Destination", f"Destination folder does not exist:\n{dst}")
            return

        confirm = messagebox.askyesno("Confirm Revert", f"Are you sure you want to revert files from:\n{dst}\n\nBack to:\n{src}?")
        if not confirm:
            return

        SOURCE_FOLDER = src
        DEST_FOLDER   = dst
        LOG_FILE      = os.path.join(DEST_FOLDER, "god_mode_log.txt")
        REPORT_FILE   = os.path.join(DEST_FOLDER, "deep_verification.txt")

        self.btn_start.configure(state="disabled")
        self.btn_revert.configure(state="disabled", text="⏳   Reverting...")

        worker = threading.Thread(target=self._revert_worker, daemon=True)
        worker.start()

    def _revert_worker(self):
        restored, errors = revert_organize(
            update_cb=lambda txt: self.msg_queue.put(txt)
        )
        self.msg_queue.put(f"Revert Complete - Restored: {restored} | Errors: {errors}")

        self.after(0, lambda: self.btn_start.configure(state="normal"))
        self.after(0, lambda: self.btn_revert.configure(state="normal", text="↺   Revert Changes"))

    # ==================================================================
    #   PAGE NAVIGATION
    # ==================================================================
    def _switch_page(self, page_key: str):
        """Switch to the given page and highlight the active nav button."""
        if page_key == self.current_page and page_key in self.pages:
            return
        crossfade_switch(self, page_key, duration=200)

    def _switch_page_direct(self, page_key: str):
        """Direct page switch without animation (used by crossfade)."""
        # Hide all pages
        for key, frame in self.pages.items():
            frame.grid_remove()

        # Show selected page
        if page_key in self.pages:
            self.pages[page_key].grid(row=0, column=0, sticky="nsew")

        # Update nav button highlighting
        active_colors = (C.ACCENT_BLUE, C.ACCENT_PURPLE, C.TEXT_HEADING, "bold")
        inactive_colors = ("transparent", C.BG_CARD, C.TEXT_MUTED, "normal")

        for key, btn in self.nav_buttons.items():
            is_active = (key == page_key)
            fg, hover, txt, weight = active_colors if is_active else inactive_colors
            btn.configure(
                fg_color=fg,
                hover_color=hover,
                text_color=txt,
                font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight=weight),
            )

        self.current_page = page_key

    # ==================================================================
    #   OVERVIEW PAGE
    # ==================================================================
    def _build_overview_page(self):
        """Overview page - folder selectors, pipeline, stats, activity, action buttons."""
        page = ctk.CTkFrame(self.page_container, fg_color="transparent")
        page.columnconfigure(0, weight=1)
        page.rowconfigure(0, weight=1)

        body = ctk.CTkScrollableFrame(
            page,
            fg_color="transparent",
            scrollbar_button_color=C.BORDER_COLOR,
            scrollbar_button_hover_color=C.ACCENT_BLUE,
        )
        body.grid(row=0, column=0, sticky="nsew", padx=24, pady=20)
        body.columnconfigure(0, weight=1)

        # -- HERO SECTION: Folder Selection --
        hero_frame = ctk.CTkFrame(body, fg_color="transparent")
        hero_frame.grid(row=0, column=0, sticky="ew", pady=(0, 24))
        hero_frame.columnconfigure(0, weight=1)
        hero_frame.columnconfigure(2, weight=1)

        self.card_src = HeroFolderCard(hero_frame, "Source Folder", "📂", SOURCE_FOLDER, C.ACCENT_BLUE)
        self.card_src.grid(row=0, column=0, sticky="ew")

        ctk.CTkLabel(
            hero_frame,
            text="➔",
            font=ctk.CTkFont(size=14),
            text_color=C.TEXT_MUTED,
            fg_color=C.BG_CARD,
            border_color=C.BORDER_COLOR,
            border_width=1,
            width=38,
            height=38,
            corner_radius=19,
        ).grid(row=0, column=1, padx=12)

        self.card_dst = HeroFolderCard(hero_frame, "Destination Folder", "🗂️", DEST_FOLDER, C.ACCENT_PURPLE)
        self.card_dst.grid(row=0, column=2, sticky="ew")

        # -- PIPELINE PROGRESS SECTION --
        pipeline_card = ctk.CTkFrame(body, fg_color=C.BG_CARD, border_color=C.BORDER_COLOR, border_width=1, corner_radius=18)
        pipeline_card.grid(row=1, column=0, sticky="ew", pady=(0, 24))

        p_hdr = ctk.CTkFrame(pipeline_card, fg_color="transparent")
        p_hdr.pack(fill="x", padx=20, pady=(16, 12))
        ctk.CTkLabel(p_hdr, text="Pipeline Progress", font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"), text_color=C.TEXT_HEADING).pack(side="left")

        self.lbl_pipeline_badge = ctk.CTkLabel(
            p_hdr, text=" • Ready to Start ",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=C.ACCENT_EMERALD, fg_color="#0F2A1E", corner_radius=6, height=26
        )
        self.lbl_pipeline_badge.pack(side="right")

        steps_row = ctk.CTkFrame(pipeline_card, fg_color="transparent")
        steps_row.pack(fill="x", padx=20, pady=(0, 20))
        steps_row.columnconfigure(1, weight=1)

        s1_frame = ctk.CTkFrame(steps_row, fg_color="transparent")
        s1_frame.grid(row=0, column=0, sticky="w")
        self.s1_badge = ctk.CTkLabel(s1_frame, text=" 1 ", font=ctk.CTkFont(size=12, weight="bold"), text_color="#FFFFFF", fg_color=C.ACCENT_BLUE, corner_radius=12, width=24, height=24)
        self.s1_badge.pack(side="left", padx=(0, 10))
        s1_txt = ctk.CTkFrame(s1_frame, fg_color="transparent")
        s1_txt.pack(side="left")
        ctk.CTkLabel(s1_txt, text="Organize Files", font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"), text_color=C.TEXT_HEADING).pack(anchor="w")
        ctk.CTkLabel(s1_txt, text="Scanning and organizing your files", font=ctk.CTkFont(family=FONT_FAMILY, size=11), text_color=C.TEXT_MUTED).pack(anchor="w")

        self.progress_bar = ctk.CTkProgressBar(steps_row, height=4, fg_color="#1E2028", progress_color=C.ACCENT_BLUE)
        self.progress_bar.grid(row=0, column=1, padx=20, sticky="ew")
        self.progress_bar.set(0)

        s2_frame = ctk.CTkFrame(steps_row, fg_color="transparent")
        s2_frame.grid(row=0, column=2, sticky="e")
        self.s2_badge = ctk.CTkLabel(s2_frame, text=" 2 ", font=ctk.CTkFont(size=12, weight="bold"), text_color=C.TEXT_MUTED, fg_color=C.BG_GLASS, corner_radius=12, width=24, height=24)
        self.s2_badge.pack(side="left", padx=(0, 10))
        s2_txt = ctk.CTkFrame(s2_frame, fg_color="transparent")
        s2_txt.pack(side="left")
        ctk.CTkLabel(s2_txt, text="Deep Verify", font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"), text_color=C.TEXT_HEADING).pack(anchor="w")
        ctk.CTkLabel(s2_txt, text="Verifying and validating results", font=ctk.CTkFont(family=FONT_FAMILY, size=11), text_color=C.TEXT_MUTED).pack(anchor="w")

        # -- STATISTIC CARDS GRID --
        stats_grid = ctk.CTkFrame(body, fg_color="transparent")
        stats_grid.grid(row=2, column=0, sticky="ew", pady=(0, 24))
        for col_idx in range(4):
            stats_grid.columnconfigure(col_idx, weight=1)

        self.stat_moved = StatCard(stats_grid, "Files Moved", "0", "📄", C.ACCENT_BLUE, "Ready to organize")
        self.stat_moved.grid(row=0, column=0, sticky="ew", padx=4, pady=4)
        self.stat_dupes = StatCard(stats_grid, "Duplicates", "0", "📑", C.ACCENT_AMBER, "Will be skipped")
        self.stat_dupes.grid(row=0, column=1, sticky="ew", padx=4, pady=4)
        self.stat_errors = StatCard(stats_grid, "Errors", "0", "⚠️", C.ACCENT_RED, "No errors found")
        self.stat_errors.grid(row=0, column=2, sticky="ew", padx=4, pady=4)
        self.stat_missing = StatCard(stats_grid, "Missing Critical", "0", "🛡️", C.ACCENT_PURPLE, "All good")
        self.stat_missing.grid(row=0, column=3, sticky="ew", padx=4, pady=4)
        self.stat_time = StatCard(stats_grid, "Time Elapsed", "00:00:00", "⏱️", C.ACCENT_CYAN, "Waiting to start")
        self.stat_time.grid(row=1, column=0, sticky="ew", padx=4, pady=4)
        self.stat_perfect = StatCard(stats_grid, "Perfect Matches", "0", "⭐", C.ACCENT_EMERALD, "-")
        self.stat_perfect.grid(row=1, column=1, sticky="ew", padx=4, pady=4)
        self.stat_wrong = StatCard(stats_grid, "Wrong Location", "0", "📍", C.ACCENT_AMBER, "-")
        self.stat_wrong.grid(row=1, column=2, sticky="ew", padx=4, pady=4)
        self.stat_size = StatCard(stats_grid, "Size Processed", "0 B → 0 B", "📊", C.ACCENT_PURPLE, "0% processed")
        self.stat_size.grid(row=1, column=3, sticky="ew", padx=4, pady=4)

        # -- RECENT ACTIVITY SECTION --
        act_card = ctk.CTkFrame(body, fg_color=C.BG_CARD, border_color=C.BORDER_COLOR, border_width=1, corner_radius=18)
        act_card.grid(row=3, column=0, sticky="ew", pady=(0, 24))

        act_hdr = ctk.CTkFrame(act_card, fg_color="transparent")
        act_hdr.pack(fill="x", padx=20, pady=(16, 12))
        ctk.CTkLabel(act_hdr, text="📈  Recent Activity", font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"), text_color=C.TEXT_HEADING).pack(side="left")

        self.act_container = ctk.CTkFrame(act_card, fg_color="transparent")
        self.act_container.pack(fill="x", padx=20, pady=(0, 20))
        self._render_empty_activity_state()

        # -- BOTTOM ACTION BUTTONS BAR --
        action_bar = ctk.CTkFrame(body, fg_color="transparent")
        action_bar.grid(row=4, column=0, sticky="ew", pady=(0, 10))

        btn_center = ctk.CTkFrame(action_bar, fg_color="transparent")
        btn_center.pack(anchor="center")

        self.btn_start = ctk.CTkButton(
            btn_center, text="▶   Start Organizing", width=200, height=46,
            corner_radius=12, fg_color=C.ACCENT_BLUE, hover_color=C.ACCENT_PURPLE,
            text_color="#FFFFFF", font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"),
            command=self._start_god_mode,
        )
        self.btn_start.pack(side="left", padx=8)
        make_button_premium(self.btn_start, primary=True)

        self.btn_revert = ctk.CTkButton(
            btn_center, text="↺   Revert Changes", width=180, height=46,
            corner_radius=12, fg_color=C.BG_CARD, hover_color="#1E2028",
            border_width=1, border_color=C.BORDER_COLOR, text_color=C.TEXT_BODY,
            font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"),
            command=self._start_revert,
        )
        self.btn_revert.pack(side="left", padx=8)
        make_button_premium(self.btn_revert, primary=False)

        self.btn_quit = ctk.CTkButton(
            btn_center, text="✕   Quit", width=110, height=46,
            corner_radius=12, fg_color="#2D1517", hover_color="#3D1D24",
            border_width=1, border_color=C.ACCENT_RED, text_color=C.ACCENT_RED,
            font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"),
            command=self.destroy,
        )
        self.btn_quit.pack(side="left", padx=8)
        make_button_premium(self.btn_quit, primary=False)

        self.pages["overview"] = page

    # ==================================================================
    #   PIPELINE PAGE
    # ==================================================================
    def _build_pipeline_page(self):
        """Pipeline page - detailed two-phase progress view."""
        page = ctk.CTkFrame(self.page_container, fg_color="transparent")
        page.columnconfigure(0, weight=1)
        page.rowconfigure(0, weight=1)

        body = ctk.CTkScrollableFrame(
            page, fg_color="transparent",
            scrollbar_button_color=C.BORDER_COLOR,
            scrollbar_button_hover_color=C.ACCENT_BLUE,
        )
        body.grid(row=0, column=0, sticky="nsew", padx=24, pady=20)
        body.columnconfigure(0, weight=1)

        # Title
        title_card = ctk.CTkFrame(body, fg_color=C.BG_CARD, border_color=C.BORDER_COLOR, border_width=1, corner_radius=18)
        title_card.grid(row=0, column=0, sticky="ew", pady=(0, 24))

        title_hdr = ctk.CTkFrame(title_card, fg_color="transparent")
        title_hdr.pack(fill="x", padx=24, pady=20)

        ctk.CTkLabel(title_hdr, text="⚙  Pipeline Status", font=ctk.CTkFont(family=FONT_FAMILY, size=22, weight="bold"), text_color=C.TEXT_HEADING).pack(anchor="w")
        ctk.CTkLabel(title_hdr, text="Monitor the two-phase file organization process", font=ctk.CTkFont(family=FONT_FAMILY, size=13), text_color=C.TEXT_MUTED).pack(anchor="w", pady=(4, 0))

        # Phase 1 Card
        phase1_card = ctk.CTkFrame(body, fg_color=C.BG_CARD, border_color=C.BORDER_COLOR, border_width=1, corner_radius=18)
        phase1_card.grid(row=1, column=0, sticky="ew", pady=(0, 16))

        ph1_hdr = ctk.CTkFrame(phase1_card, fg_color="transparent")
        ph1_hdr.pack(fill="x", padx=20, pady=(16, 12))

        ctk.CTkLabel(ph1_hdr, text="Phase 1 -  Organize Files", font=ctk.CTkFont(family=FONT_FAMILY, size=17, weight="bold"), text_color=C.PHASE1_COLOR).pack(side="left")

        self.p1_badge = ctk.CTkLabel(
            ph1_hdr, text=" ● Pending ", font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=C.TEXT_MUTED, fg_color=C.BG_GLASS, corner_radius=6, height=26,
        )
        self.p1_badge.pack(side="right")

        ph1_body = ctk.CTkFrame(phase1_card, fg_color="transparent")
        ph1_body.pack(fill="x", padx=20, pady=(0, 20))

        self.p1_moved_lbl = ctk.CTkLabel(ph1_body, text="📄 Files Moved: 0", font=ctk.CTkFont(family=FONT_FAMILY, size=14), text_color=C.TEXT_BODY, anchor="w")
        self.p1_moved_lbl.pack(fill="x", pady=2)
        self.p1_dupes_lbl = ctk.CTkLabel(ph1_body, text="📑 Duplicates: 0", font=ctk.CTkFont(family=FONT_FAMILY, size=14), text_color=C.TEXT_BODY, anchor="w")
        self.p1_dupes_lbl.pack(fill="x", pady=2)
        self.p1_errors_lbl = ctk.CTkLabel(ph1_body, text="⚠️ Errors: 0", font=ctk.CTkFont(family=FONT_FAMILY, size=14), text_color=C.TEXT_BODY, anchor="w")
        self.p1_errors_lbl.pack(fill="x", pady=2)

        # Phase 2 Card
        phase2_card = ctk.CTkFrame(body, fg_color=C.BG_CARD, border_color=C.BORDER_COLOR, border_width=1, corner_radius=18)
        phase2_card.grid(row=2, column=0, sticky="ew", pady=(0, 16))

        ph2_hdr = ctk.CTkFrame(phase2_card, fg_color="transparent")
        ph2_hdr.pack(fill="x", padx=20, pady=(16, 12))

        ctk.CTkLabel(ph2_hdr, text="Phase 2 -  Deep Verify", font=ctk.CTkFont(family=FONT_FAMILY, size=17, weight="bold"), text_color=C.PHASE2_COLOR).pack(side="left")

        self.p2_badge = ctk.CTkLabel(
            ph2_hdr, text=" ● Pending ", font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=C.TEXT_MUTED, fg_color=C.BG_GLASS, corner_radius=6, height=26,
        )
        self.p2_badge.pack(side="right")

        ph2_body = ctk.CTkFrame(phase2_card, fg_color="transparent")
        ph2_body.pack(fill="x", padx=20, pady=(0, 20))

        self.p2_perfect_lbl = ctk.CTkLabel(ph2_body, text="⭐ Perfect Matches: 0", font=ctk.CTkFont(family=FONT_FAMILY, size=14), text_color=C.TEXT_BODY, anchor="w")
        self.p2_perfect_lbl.pack(fill="x", pady=2)
        self.p2_wrong_lbl = ctk.CTkLabel(ph2_body, text="📍 Wrong Location: 0", font=ctk.CTkFont(family=FONT_FAMILY, size=14), text_color=C.TEXT_BODY, anchor="w")
        self.p2_wrong_lbl.pack(fill="x", pady=2)
        self.p2_missing_lbl = ctk.CTkLabel(ph2_body, text="🛡️ Missing Critical: 0", font=ctk.CTkFont(family=FONT_FAMILY, size=14), text_color=C.TEXT_BODY, anchor="w")
        self.p2_missing_lbl.pack(fill="x", pady=2)

        # Progress Bar Card
        prog_card = ctk.CTkFrame(body, fg_color=C.BG_CARD, border_color=C.BORDER_COLOR, border_width=1, corner_radius=18)
        prog_card.grid(row=3, column=0, sticky="ew", pady=(0, 24))

        prog_hdr = ctk.CTkFrame(prog_card, fg_color="transparent")
        prog_hdr.pack(fill="x", padx=20, pady=(16, 12))
        ctk.CTkLabel(prog_hdr, text="📊 Overall Progress", font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"), text_color=C.TEXT_HEADING).pack(side="left")

        self.p_progress = ctk.CTkProgressBar(prog_card, height=8, fg_color="#1E2028", progress_color=C.ACCENT_BLUE, corner_radius=4)
        self.p_progress.pack(fill="x", padx=20, pady=(0, 20))
        self.p_progress.set(0)

        # Action buttons
        action_row = ctk.CTkFrame(body, fg_color="transparent")
        action_row.grid(row=4, column=0, sticky="ew", pady=(0, 10))

        btn_center = ctk.CTkFrame(action_row, fg_color="transparent")
        btn_center.pack(anchor="center")

        ctk.CTkButton(
            btn_center, text="◀  Back to Overview", width=200, height=46,
            corner_radius=12, fg_color=C.ACCENT_BLUE, hover_color=C.ACCENT_PURPLE,
            text_color="#FFFFFF", font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"),
            command=lambda: self._switch_page("overview"),
        ).pack(side="left", padx=8)

        self.pages["pipeline"] = page

    def _update_pipeline_badges(self, phase: str):
        """Update Pipeline page phase badges (phase1/phase2/complete)."""
        if not hasattr(self, "p1_badge") or not self.p1_badge.winfo_exists():
            return
        if phase == "phase1":
            self.p1_badge.configure(text=" ● Running... ", text_color=C.ACCENT_BLUE, fg_color="#0F172A")
            self.p2_badge.configure(text=" ● Pending ", text_color=C.TEXT_MUTED, fg_color=C.BG_GLASS)
        elif phase == "phase2":
            self.p1_badge.configure(text=" ✓ Complete ", text_color=C.ACCENT_EMERALD, fg_color="#0F2A1E")
            self.p2_badge.configure(text=" ● Running... ", text_color=C.ACCENT_PURPLE, fg_color="#1E1B4B")
        elif phase == "complete":
            self.p1_badge.configure(text=" ✓ Complete ", text_color=C.ACCENT_EMERALD, fg_color="#0F2A1E")
            self.p2_badge.configure(text=" ✓ Complete ", text_color=C.ACCENT_EMERALD, fg_color="#0F2A1E")
            if hasattr(self, "p_progress") and self.p_progress.winfo_exists():
                self.p_progress.set(1.0)

    def _refresh_pipeline_page_stats(self):
        """Update Pipeline page stat labels from _stats dict."""
        if not hasattr(self, "p1_moved_lbl") or not self.p1_moved_lbl.winfo_exists():
            return
        s = self._stats
        self.p1_moved_lbl.configure(text=f"📄 Files Moved: {s['moved']}")
        self.p1_dupes_lbl.configure(text=f"📑 Duplicates: {s['dupes']}")
        self.p1_errors_lbl.configure(text=f"⚠️ Errors: {s['errors']}")
        self.p2_perfect_lbl.configure(text=f"⭐ Perfect Matches: {s['perfect']}")
        self.p2_wrong_lbl.configure(text=f"📍 Wrong Location: {s['wrong']}")
        self.p2_missing_lbl.configure(text=f"🛡️ Missing Critical: {s['missing']}")

    # ==================================================================
    #   STATISTICS PAGE
    # ==================================================================
    def _build_statistics_page(self):
        """Statistics page - larger dedicated view of all 8 stat cards."""
        page = ctk.CTkFrame(self.page_container, fg_color="transparent")
        page.columnconfigure(0, weight=1)
        page.rowconfigure(0, weight=1)

        body = ctk.CTkScrollableFrame(
            page, fg_color="transparent",
            scrollbar_button_color=C.BORDER_COLOR,
            scrollbar_button_hover_color=C.ACCENT_BLUE,
        )
        body.grid(row=0, column=0, sticky="nsew", padx=24, pady=20)
        body.columnconfigure(0, weight=1)

        # Title
        title_card = ctk.CTkFrame(body, fg_color=C.BG_CARD, border_color=C.BORDER_COLOR, border_width=1, corner_radius=18)
        title_card.grid(row=0, column=0, sticky="ew", pady=(0, 24))

        title_hdr = ctk.CTkFrame(title_card, fg_color="transparent")
        title_hdr.pack(fill="x", padx=24, pady=20)

        ctk.CTkLabel(title_hdr, text="📊  Statistics Overview", font=ctk.CTkFont(family=FONT_FAMILY, size=22, weight="bold"), text_color=C.TEXT_HEADING).pack(anchor="w")
        ctk.CTkLabel(title_hdr, text="Detailed breakdown of file organization results", font=ctk.CTkFont(family=FONT_FAMILY, size=13), text_color=C.TEXT_MUTED).pack(anchor="w", pady=(4, 0))

        # Stats Grid - 4 columns, 2 rows
        stats_grid = ctk.CTkFrame(body, fg_color="transparent")
        stats_grid.grid(row=1, column=0, sticky="ew", pady=(0, 24))
        for col_idx in range(4):
            stats_grid.columnconfigure(col_idx, weight=1)

        s = self._stats
        self.s_moved = StatCard(stats_grid, "Files Moved", str(s["moved"]), "📄", C.ACCENT_BLUE, "Total files organized")
        self.s_moved.grid(row=0, column=0, sticky="ew", padx=6, pady=6)

        self.s_dupes = StatCard(stats_grid, "Duplicates", str(s["dupes"]), "📑", C.ACCENT_AMBER, "Duplicate files found")
        self.s_dupes.grid(row=0, column=1, sticky="ew", padx=6, pady=6)

        self.s_errors = StatCard(stats_grid, "Errors", str(s["errors"]), "⚠️", C.ACCENT_RED, "Files with errors")
        self.s_errors.grid(row=0, column=2, sticky="ew", padx=6, pady=6)

        self.s_missing_s = StatCard(stats_grid, "Missing Critical", str(s["missing"]), "🛡️", C.ACCENT_PURPLE, "Files not found elsewhere")
        self.s_missing_s.grid(row=0, column=3, sticky="ew", padx=6, pady=6)

        self.s_time = StatCard(stats_grid, "Time Elapsed", s["time"], "⏱️", C.ACCENT_CYAN, "Total processing time")
        self.s_time.grid(row=1, column=0, sticky="ew", padx=6, pady=6)

        self.s_perfect = StatCard(stats_grid, "Perfect Matches", str(s["perfect"]), "⭐", C.ACCENT_EMERALD, "Files in correct location")
        self.s_perfect.grid(row=1, column=1, sticky="ew", padx=6, pady=6)

        self.s_wrong = StatCard(stats_grid, "Wrong Location", str(s["wrong"]), "📍", C.ACCENT_AMBER, "Files in wrong category")
        self.s_wrong.grid(row=1, column=2, sticky="ew", padx=6, pady=6)

        self.s_size = StatCard(stats_grid, "Size Processed", f"{s['size_before']} → {s['size_after']}", "📊", C.ACCENT_PURPLE, "Source → Destination size")
        self.s_size.grid(row=1, column=3, sticky="ew", padx=6, pady=6)

        # Back button
        action_row = ctk.CTkFrame(body, fg_color="transparent")
        action_row.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        btn_center = ctk.CTkFrame(action_row, fg_color="transparent")
        btn_center.pack(anchor="center")

        ctk.CTkButton(
            btn_center, text="◀  Back to Overview", width=200, height=46,
            corner_radius=12, fg_color=C.ACCENT_BLUE, hover_color=C.ACCENT_PURPLE,
            text_color="#FFFFFF", font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"),
            command=lambda: self._switch_page("overview"),
        ).pack(side="left", padx=8)

        self.pages["statistics"] = page

    def _refresh_statistics_page_stats(self):
        """Update Statistics page stat cards from _stats dict."""
        if not hasattr(self, "s_moved") or not self.s_moved.winfo_exists():
            return
        s = self._stats
        self.s_moved.set_value(str(s["moved"]))
        self.s_dupes.set_value(str(s["dupes"]))
        self.s_errors.set_value(str(s["errors"]))
        self.s_missing_s.set_value(str(s["missing"]))
        self.s_time.set_value(s["time"])
        self.s_perfect.set_value(str(s["perfect"]))
        self.s_wrong.set_value(str(s["wrong"]))
        self.s_size.set_value(f"{s['size_before']} → {s['size_after']}")

    # ==================================================================
    #   ACTIVITY PAGE
    # ==================================================================
    def _build_activity_page(self):
        """Activity page - full activity log/history."""
        page = ctk.CTkFrame(self.page_container, fg_color="transparent")
        page.columnconfigure(0, weight=1)
        page.rowconfigure(0, weight=1)

        body = ctk.CTkScrollableFrame(
            page, fg_color="transparent",
            scrollbar_button_color=C.BORDER_COLOR,
            scrollbar_button_hover_color=C.ACCENT_BLUE,
        )
        body.grid(row=0, column=0, sticky="nsew", padx=24, pady=20)
        body.columnconfigure(0, weight=1)

        # Title
        title_card = ctk.CTkFrame(body, fg_color=C.BG_CARD, border_color=C.BORDER_COLOR, border_width=1, corner_radius=18)
        title_card.grid(row=0, column=0, sticky="ew", pady=(0, 24))

        title_hdr = ctk.CTkFrame(title_card, fg_color="transparent")
        title_hdr.pack(fill="x", padx=24, pady=20)
        ctk.CTkLabel(title_hdr, text="⏱  Activity Log", font=ctk.CTkFont(family=FONT_FAMILY, size=22, weight="bold"), text_color=C.TEXT_HEADING).pack(anchor="w")
        ctk.CTkLabel(title_hdr, text="Complete history of all file operations", font=ctk.CTkFont(family=FONT_FAMILY, size=13), text_color=C.TEXT_MUTED).pack(anchor="w", pady=(4, 0))

        # Log text area
        log_card = ctk.CTkFrame(body, fg_color=C.BG_CARD, border_color=C.BORDER_COLOR, border_width=1, corner_radius=18)
        log_card.grid(row=1, column=0, sticky="ew", pady=(0, 24))
        log_card.columnconfigure(0, weight=1)

        log_hdr = ctk.CTkFrame(log_card, fg_color="transparent")
        log_hdr.pack(fill="x", padx=20, pady=(16, 12))

        count_text = f"{len(self.full_activity_log)} entries"
        ctk.CTkLabel(log_hdr, text=f"📋 Full History ({count_text})", font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"), text_color=C.TEXT_HEADING).pack(side="left")

        # Scrolled text widget for full log
        text_frame = ctk.CTkFrame(log_card, fg_color=C.BG_INPUT, border_color=C.BORDER_COLOR, border_width=1, corner_radius=10)
        text_frame.pack(fill="both", padx=20, pady=(0, 20), expand=True)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        self.activity_log_text = ctk.CTkTextbox(
            text_frame, fg_color=C.BG_INPUT, text_color=C.TEXT_BODY,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            border_width=0, corner_radius=8, height=350,
            scrollbar_button_color=C.BORDER_COLOR,
            scrollbar_button_hover_color=C.ACCENT_BLUE,
        )
        self.activity_log_text.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

        # Populate with existing log entries
        self.activity_log_text.configure(state="normal")
        if self.full_activity_log:
            self.activity_log_text.insert("1.0", "\n".join(reversed(self.full_activity_log)))
        else:
            self.activity_log_text.insert("1.0", "No activity yet. Start organizing to see entries here.")
        self.activity_log_text.configure(state="disabled")

        # Back button
        action_row = ctk.CTkFrame(body, fg_color="transparent")
        action_row.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        btn_center = ctk.CTkFrame(action_row, fg_color="transparent")
        btn_center.pack(anchor="center")

        ctk.CTkButton(
            btn_center, text="◀  Back to Overview", width=200, height=46,
            corner_radius=12, fg_color=C.ACCENT_BLUE, hover_color=C.ACCENT_PURPLE,
            text_color="#FFFFFF", font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"),
            command=lambda: self._switch_page("overview"),
        ).pack(side="left", padx=8)

        self.pages["activity"] = page

    # ==================================================================
    #   SETTINGS PAGE
    # ==================================================================
    def _build_settings_page(self):
        """Settings page - default paths, theme toggle, version info."""
        page = ctk.CTkFrame(self.page_container, fg_color="transparent")
        page.columnconfigure(0, weight=1)
        page.rowconfigure(0, weight=1)

        body = ctk.CTkScrollableFrame(
            page, fg_color="transparent",
            scrollbar_button_color=C.BORDER_COLOR,
            scrollbar_button_hover_color=C.ACCENT_BLUE,
        )
        body.grid(row=0, column=0, sticky="nsew", padx=24, pady=20)
        body.columnconfigure(0, weight=1)

        # Title
        title_card = ctk.CTkFrame(body, fg_color=C.BG_CARD, border_color=C.BORDER_COLOR, border_width=1, corner_radius=18)
        title_card.grid(row=0, column=0, sticky="ew", pady=(0, 24))

        title_hdr = ctk.CTkFrame(title_card, fg_color="transparent")
        title_hdr.pack(fill="x", padx=24, pady=20)
        ctk.CTkLabel(title_hdr, text="🛠  Settings", font=ctk.CTkFont(family=FONT_FAMILY, size=22, weight="bold"), text_color=C.TEXT_HEADING).pack(anchor="w")
        ctk.CTkLabel(title_hdr, text="Configure application preferences", font=ctk.CTkFont(family=FONT_FAMILY, size=13), text_color=C.TEXT_MUTED).pack(anchor="w", pady=(4, 0))

        # Default Paths Card
        paths_card = ctk.CTkFrame(body, fg_color=C.BG_CARD, border_color=C.BORDER_COLOR, border_width=1, corner_radius=18)
        paths_card.grid(row=1, column=0, sticky="ew", pady=(0, 16))

        paths_hdr = ctk.CTkFrame(paths_card, fg_color="transparent")
        paths_hdr.pack(fill="x", padx=20, pady=(16, 12))
        ctk.CTkLabel(paths_hdr, text="📂  Default Folder Paths", font=ctk.CTkFont(family=FONT_FAMILY, size=17, weight="bold"), text_color=C.TEXT_HEADING).pack(anchor="w")

        paths_body = ctk.CTkFrame(paths_card, fg_color="transparent")
        paths_body.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(paths_body, text="Source Folder", font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"), text_color=C.TEXT_BODY, anchor="w").pack(fill="x", pady=(0, 4))

        src_frame = ctk.CTkFrame(paths_body, fg_color="transparent")
        src_frame.pack(fill="x", pady=(0, 12))

        self.settings_src_entry = ctk.CTkEntry(
            src_frame, fg_color=C.BG_INPUT, border_color=C.BORDER_COLOR,
            text_color=C.TEXT_BODY, font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            corner_radius=10, height=38, placeholder_text="C:/Users/.../Source",
        )
        self.settings_src_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            src_frame, text="Browse", width=80, height=38, corner_radius=10,
            fg_color=C.ACCENT_BLUE, hover_color=C.ACCENT_PURPLE, text_color="#FFFFFF",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            command=lambda: self.settings_src_entry.delete(0, "end") or self.settings_src_entry.insert(0, filedialog.askdirectory() or ""),
        ).pack(side="right")

        ctk.CTkLabel(paths_body, text="Destination Folder", font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"), text_color=C.TEXT_BODY, anchor="w").pack(fill="x", pady=(0, 4))

        dst_frame = ctk.CTkFrame(paths_body, fg_color="transparent")
        dst_frame.pack(fill="x", pady=(0, 0))

        self.settings_dst_entry = ctk.CTkEntry(
            dst_frame, fg_color=C.BG_INPUT, border_color=C.BORDER_COLOR,
            text_color=C.TEXT_BODY, font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            corner_radius=10, height=38, placeholder_text="C:/Users/.../Destination",
        )
        self.settings_dst_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            dst_frame, text="Browse", width=80, height=38, corner_radius=10,
            fg_color=C.ACCENT_PURPLE, hover_color=C.ACCENT_BLUE, text_color="#FFFFFF",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            command=lambda: self.settings_dst_entry.delete(0, "end") or self.settings_dst_entry.insert(0, filedialog.askdirectory() or ""),
        ).pack(side="right")

        # Theme Card
        theme_card = ctk.CTkFrame(body, fg_color=C.BG_CARD, border_color=C.BORDER_COLOR, border_width=1, corner_radius=18)
        theme_card.grid(row=2, column=0, sticky="ew", pady=(0, 16))

        theme_hdr = ctk.CTkFrame(theme_card, fg_color="transparent")
        theme_hdr.pack(fill="x", padx=20, pady=(16, 12))
        ctk.CTkLabel(theme_hdr, text="🎨  Appearance", font=ctk.CTkFont(family=FONT_FAMILY, size=17, weight="bold"), text_color=C.TEXT_HEADING).pack(anchor="w")

        theme_body = ctk.CTkFrame(theme_card, fg_color="transparent")
        theme_body.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(theme_body, text="Theme", font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"), text_color=C.TEXT_BODY, anchor="w").pack(fill="x", pady=(0, 8))

        self.theme_var = ctk.StringVar(value="Dark")
        theme_selector = ctk.CTkSegmentedButton(
            theme_body, values=["Dark", "Light"],
            variable=self.theme_var,
            fg_color=C.BG_GLASS, selected_color=C.ACCENT_BLUE,
            selected_hover_color=C.ACCENT_PURPLE,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            command=self._toggle_theme,
        )
        theme_selector.pack(anchor="w")

        # About Card
        about_card = ctk.CTkFrame(body, fg_color=C.BG_CARD, border_color=C.BORDER_COLOR, border_width=1, corner_radius=18)
        about_card.grid(row=3, column=0, sticky="ew", pady=(0, 24))

        about_hdr = ctk.CTkFrame(about_card, fg_color="transparent")
        about_hdr.pack(fill="x", padx=20, pady=(16, 12))
        ctk.CTkLabel(about_hdr, text="ℹ️  About", font=ctk.CTkFont(family=FONT_FAMILY, size=17, weight="bold"), text_color=C.TEXT_HEADING).pack(anchor="w")

        about_body = ctk.CTkFrame(about_card, fg_color="transparent")
        about_body.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(about_body, text="FileFlow  -  Smart File Organizer", font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"), text_color=C.TEXT_HEADING, anchor="w").pack(fill="x", pady=2)
        ctk.CTkLabel(about_body, text="Version 1.0.0", font=ctk.CTkFont(family=FONT_FAMILY, size=13), text_color=C.TEXT_BODY, anchor="w").pack(fill="x", pady=2)
        ctk.CTkLabel(about_body, text="Built with Python • CustomTkinter • PyInstaller", font=ctk.CTkFont(family=FONT_FAMILY, size=12), text_color=C.TEXT_MUTED, anchor="w").pack(fill="x", pady=2)

        # Back button
        action_row = ctk.CTkFrame(body, fg_color="transparent")
        action_row.grid(row=4, column=0, sticky="ew", pady=(0, 10))

        btn_center = ctk.CTkFrame(action_row, fg_color="transparent")
        btn_center.pack(anchor="center")

        ctk.CTkButton(
            btn_center, text="◀  Back to Overview", width=200, height=46,
            corner_radius=12, fg_color=C.ACCENT_BLUE, hover_color=C.ACCENT_PURPLE,
            text_color="#FFFFFF", font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"),
            command=lambda: self._switch_page("overview"),
        ).pack(side="left", padx=8)

        self.pages["settings"] = page

    def _toggle_theme_header(self):
        """Toggle theme from the header button."""
        new_mode = "light" if C._mode == "dark" else "dark"
        self._set_theme(new_mode)

    def _set_theme(self, mode):
        """Set theme mode and update all UI elements."""
        ctk.set_appearance_mode(mode)
        C.set_mode(mode)
        self._theme_mode = mode
        # Persist
        try:
            import json
            with open(self._config_path, "w") as f:
                json.dump({"theme": mode}, f)
        except:
            pass
        self._apply_theme()
        # Update toggle button text
        icon = " ☀ " if mode == "dark" else " 🌙 "
        label = "Dark" if mode == "dark" else "Light"
        self.theme_toggle_btn.configure(text=f"{icon}{label}")
        # Sync settings segmented button
        if hasattr(self, "theme_var") and self.theme_var.winfo_exists():
            display = "Dark" if mode == "dark" else "Light"
            self.theme_var.set(display)

    def _toggle_theme(self, choice: str):
        """Toggle between Dark and Light appearance mode (from Settings)."""
        mode = "dark" if choice == "Dark" else "light"
        self._set_theme(mode)

    def _apply_theme(self):
        """Reapply theme colors to all major containers after theme switch."""
        # Main window
        self.configure(fg_color=C.BG_PRIMARY)
        # Sidebar
        if hasattr(self, "_sidebar_ref"):
            self._sidebar_ref.configure(fg_color=C.BG_SECONDARY)
        # Header bar
        if hasattr(self, "_header_bar_ref"):
            self._header_bar_ref.configure(fg_color=C.BG_SECONDARY)
        # Theme toggle button
        if hasattr(self, "theme_toggle_btn"):
            self.theme_toggle_btn.configure(fg_color=C.BG_CARD, hover_color=C.BG_INPUT, text_color=C.TEXT_BODY)
        # Settings button
        if hasattr(self, "settings_btn"):
            self.settings_btn.configure(fg_color=C.BG_CARD, hover_color=C.BG_INPUT, text_color=C.TEXT_BODY)
        # Page container backgrounds are "transparent" - they inherit from parent
        # Reconfigure all page containers
        for key, page in self.pages.items():
            if hasattr(page, 'winfo_exists') and page.winfo_exists():
                for child in page.winfo_children():
                    if isinstance(child, ctk.CTkScrollableFrame):
                        child.configure(fg_color="transparent")
        # Update nav buttons
        if hasattr(self, "nav_buttons"):
            for key, btn in self.nav_buttons.items():
                is_active = (key == self.current_page)
                if is_active:
                    btn.configure(fg_color=C.ACCENT_BLUE, hover_color=C.ACCENT_PURPLE,
                                  text_color=C.TEXT_HEADING)
                else:
                    btn.configure(fg_color="transparent", hover_color=C.BG_CARD,
                                  text_color=C.TEXT_MUTED)


# ----------------------------------------------------------------------
# ----------------------  ENTRY POINT  --------------------------------
# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = FileFlowApp()
    app.mainloop()


