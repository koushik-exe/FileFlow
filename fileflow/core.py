# ----------------------------------------------------------------------
# ----------------------  CORE ORGANIZATION LOGIC  ---------------------
# ----------------------------------------------------------------------
import os
import shutil
from datetime import datetime
from dataclasses import dataclass

from fileflow.constants import MONTHS
from fileflow.utils import (
    get_file_hash,
    get_unique_filename,
    get_image_date,
    get_file_date,
    get_category,
)


@dataclass
class RunContext:
    """Holds source/destination folders and log/report file paths."""
    src: str = ""
    dst: str = ""
    log: str = ""
    report: str = ""


hash_map = {}


def log(msg, log_file):
    """Append a line with timestamp to the log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_msg = f"[{timestamp}] {msg}"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(full_msg + "\n")


def scan_existing_files(ctx: RunContext):
    """Load already-present files from DEST_FOLDER into hash_map."""
    for root, _, files in os.walk(ctx.dst):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path in (ctx.log, ctx.report):
                continue
            try:
                file_hash = get_file_hash(file_path)
                hash_map[file_hash] = file_path
            except Exception:
                pass


def phase1_organize(ctx: RunContext, update_cb=None):
    """
    Core of Phase 1 - exactly the same algorithm from the original script.
    update_cb is an optional callback for GUI live updates.
    """
    moved = duplicates = errors = 0

    scan_existing_files(ctx)

    for root, _, files in os.walk(ctx.src):
        for file in files:
            file_path = os.path.join(root, file)

            try:
                file_hash = get_file_hash(file_path)
                category = get_category(file)
                date = get_file_date(file_path)
                year = str(date.year)
                month = MONTHS[date.month]

                normal_folder = os.path.join(ctx.dst, category, year, month)
                duplicate_folder = os.path.join(ctx.dst, "Duplicates", category, year, month)

                if file_hash in hash_map:
                    # duplicate
                    os.makedirs(duplicate_folder, exist_ok=True)
                    unique_name = get_unique_filename(duplicate_folder, file)
                    dest_path = os.path.join(duplicate_folder, unique_name)
                    shutil.move(file_path, dest_path)

                    msg = f"DUPLICATE | {file} -> Duplicates/{category}/{year}/{month}/{unique_name}"
                    if update_cb: update_cb(msg)
                    log(msg, ctx.log)
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
                log(msg, ctx.log)
                moved += 1

            except Exception as e:
                msg = f"ERROR | {file} -> {e}"
                if update_cb: update_cb(msg)
                log(msg, ctx.log)
                errors += 1

    return moved, duplicates, errors


def phase2_verify(ctx: RunContext, update_cb=None):
    """Same verification routine - only update_cb added."""
    normal_index = {}

    # build index of all non-duplicate files
    for root, _, files in os.walk(ctx.dst):
        if "duplicates" in root.lower():
            continue
        for file in files:
            file_path = os.path.join(root, file)
            if file_path in (ctx.log, ctx.report):
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
    for root, _, files in os.walk(ctx.dst):
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
    with open(ctx.report, "w", encoding="utf-8") as f:
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


def revert_organize(ctx: RunContext, update_cb=None):
    """
    Reverts organized files from DEST_FOLDER back into SOURCE_FOLDER.
    Returns (restored_count, errors_count).
    """
    restored = 0
    errors = 0

    if not os.path.exists(ctx.dst) or not os.path.exists(ctx.src):
        return 0, 0

    for root, _, files in os.walk(ctx.dst):
        for file in files:
            file_path = os.path.join(root, file)

            # Skip log and report files
            if file_path in (ctx.log, ctx.report):
                continue

            try:
                unique_name = get_unique_filename(ctx.src, file)
                dest_path = os.path.join(ctx.src, unique_name)

                shutil.move(file_path, dest_path)
                restored += 1

                msg = f"REVERTED | {file} -> Source/{unique_name}"
                if update_cb: update_cb(msg)
                log(msg, ctx.log)
            except Exception as e:
                msg = f"REVERT ERROR | {file} -> {e}"
                if update_cb: update_cb(msg)
                log(msg, ctx.log)
                errors += 1

    return restored, errors
