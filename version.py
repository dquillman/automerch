import os
import subprocess
from pathlib import Path


def get_version() -> str:
    root = Path(__file__).resolve().parent
    # Prefer explicit VERSION file
    for p in (root / "VERSION", Path.cwd() / "VERSION"):
        try:
            if p.exists():
                v = p.read_text(encoding="utf-8").strip()
                if v:
                    return v
        except Exception:
            pass
    # Then env override
    v = os.getenv("AUTOMERCH_VERSION")
    if v:
        return v
    # Then git date+sha
    try:
        sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=root, stderr=subprocess.DEVNULL).decode().strip()
        date = subprocess.check_output(["git", "show", "-s", "--format=%cd", "--date=short", "HEAD"], cwd=root, stderr=subprocess.DEVNULL).decode().strip()
        if sha:
            return f"{date}+{sha}" if date else sha
    except Exception:
        pass
    return "0.0.0"
