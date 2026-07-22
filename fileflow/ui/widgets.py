# ----------------------------------------------------------------------
# ----------------------  ANIMATION ENGINE & REUSABLE WIDGETS  ---------
# ----------------------------------------------------------------------
import math
import ctypes
import customtkinter as ctk
from tkinter import Canvas, filedialog

from fileflow.constants import C, FONT_FAMILY


# ----------------------------------------------------------------------
#  Easing Functions
# ----------------------------------------------------------------------
def ease_out_cubic(t):
    return 1 - (1 - t) ** 3

def ease_out_quart(t):
    return 1 - (1 - t) ** 4

def ease_out_back(t):
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


# ----------------------------------------------------------------------
#  Reduce Motion Detection
# ----------------------------------------------------------------------
def is_reduce_motion_enabled():
    """Check Windows 'Show animations' / Reduce Motion setting."""
    try:
        SPI_GETCLIENTAREAANIMATION = 0x1042
        enabled = ctypes.windll.user32.SystemParametersInfoW(SPI_GETCLIENTAREAANIMATION, 0, None, 0)
        return not enabled
    except Exception:
        return False

REDUCE_MOTION = is_reduce_motion_enabled()


# ----------------------------------------------------------------------
#  Smooth Property Animator
# ----------------------------------------------------------------------
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


# ----------------------------------------------------------------------
#  Card Hover Mixin
# ----------------------------------------------------------------------
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


# ----------------------------------------------------------------------
#  Button Press Animation
# ----------------------------------------------------------------------
def make_button_premium(btn, primary=True):
    """Add press/release and hover glow animations to a CTkButton."""
    if REDUCE_MOTION:
        return

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


# ----------------------------------------------------------------------
#  Input Focus Animation
# ----------------------------------------------------------------------
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


# ----------------------------------------------------------------------
#  Number Counter Animation
# ----------------------------------------------------------------------
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


# ----------------------------------------------------------------------
#  Shake Animation
# ----------------------------------------------------------------------
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


# ----------------------------------------------------------------------
#  Page Transition
# ----------------------------------------------------------------------
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


# ----------------------------------------------------------------------
#  Success Ring Animation
# ----------------------------------------------------------------------
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
#  Hero Folder Card Widget
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

        # Header Row + Circular Icon
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


# ----------------------------------------------------------------------
#  Stat Card Widget
# ----------------------------------------------------------------------
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

        # Circular Icon
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

        # Large Number
        self.val_lbl = ctk.CTkLabel(
            top_row,
            text=value,
            font=ctk.CTkFont(family=FONT_FAMILY, size=24, weight="bold"),
            text_color=C.TEXT_HEADING,
            anchor="w",
        )
        self.val_lbl.grid(row=0, column=1, sticky="w")

        # Title
        ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            text_color=C.TEXT_MUTED,
            anchor="w",
        ).pack(fill="x", padx=16, pady=(0, 2))

        # Helper text
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
