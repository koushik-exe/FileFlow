# FileFlow 🔥

**A modern desktop GUI file organizer – Fluent / Apple Spatial design, built with Python.**

FileFlow scans your folders and intelligently sorts files by category (images, documents, audio, video, archives, code, etc.), then moves them into neatly organized destination folders. It verifies every move via SHA-256 hashing, and lets you **revert** the entire operation if something doesn't feel right.

---

## ✨ Features

- **Smart categorization** – Automatically detects file types (images, documents, audio, video, archives, code, and more).
- **Date-based subfolders** – Groups organized files by year/month for time-based sorting.
- **Duplicate detection** – Identifies and flags duplicates before moving.
- **Phase 1: Organize** – Moves files into structured category folders.
- **Phase 2: Verify** – Re-hashes every moved file and cross-checks against the original SHA-256 to confirm data integrity.
- **One-click Revert** – Restores everything to its original location if needed.
- **Glass-morphism UI** – Dark modern interface with hero folder cards, live stats, and activity feed.
- **God Mode** – Full automation with an animated progress overlay.

---

## 📋 Requirements

- **Python 3.9+**
- Python packages (see [Installation](#-installation))

---

## 🚀 Installation

### Option 1: Run from source (recommended)

```bash
# 1. Clone or download this repository
# 2. Install dependencies
pip install customtkinter pillow

# 3. Launch FileFlow
python FileFlow.py
```

You can also double-click [`FileFlow.bat`](FileFlow.bat) (Windows) to launch it without opening a terminal.

### Option 2: Standalone executable (Windows)

A pre-built `.exe` is available in the releases section. Because FileFlow is **unsigned open-source software**, Windows Smart App Control / SmartScreen may show a warning when you first run it. This is normal — the warning just means the `.exe` hasn't been signed with a paid code-signing certificate. The software is safe and its source code is fully visible here on GitHub.

### Known Issue: Windows Smart App Control

On Windows 11 systems with Smart App Control enabled (increasingly common on new installs), FileFlow.exe may be blocked since it isn't yet code-signed.

**If you see this warning, try these in order:**

1. **Right-click** `FileFlow.exe` → **Properties** → check **"Unblock"** at the bottom → Apply → OK

2. **PowerShell unblock command** — open PowerShell and run:

   ```
   Unblock-File -Path "C:\path\to\your\FileFlow.exe"
   ```

   Replace the path with wherever you saved FileFlow.exe.

3. **If neither works**, Smart App Control is likely in strict enforcement mode, which blocks all unsigned apps with no per-app override. In that case:
   - **Alternative:** Run from source instead — see the "Run from source" section above
   - **Advanced workaround:** Smart App Control can be disabled entirely via Settings → Privacy & Security → Windows Security → App & browser control. This is a one-way change — once disabled, it can only be re-enabled via a clean Windows reinstall. Only do this if you understand and accept that tradeoff.

We're working on getting FileFlow code-signed to remove this issue entirely for future releases.
---

## 🎯 Usage

1. **Launch** FileFlow (via `python FileFlow.py`, [`FileFlow.bat`](FileFlow.bat), or the `.exe`).
2. **Select source and destination folders** using the hero folder cards.
3. Click **✨ Auto-Organize** to start Phase 1 (categorize & move).
4. Review the activity feed and stats.
5. Click **✓ Verify** to run Phase 2 (hash verification).
6. If anything went wrong, click **↺ Revert Changes** to undo everything.

---

## 🔨 Building the executable yourself

If you prefer to build the `.exe` from source (so you know exactly what's inside):

```bash
pip install pyinstaller
pyinstaller FileFlow.spec
```

The output will be placed in the `dist/` folder.

---

## 📄 License

This project is provided as-is for personal and educational use. See the [LICENSE](LICENSE) file for details (if present).

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to open an issue or submit a pull request.
