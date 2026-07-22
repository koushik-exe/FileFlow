# ----------------------------------------------------------------------
# ----------------------  PURE HELPER FUNCTIONS  -----------------------
# ----------------------------------------------------------------------
import os
import hashlib
from datetime import datetime

from fileflow.constants import file_types, MONTHS


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
