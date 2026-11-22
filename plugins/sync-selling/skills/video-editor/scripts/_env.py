"""Shared by the three scripts: where the editor keeps its own Python, and which ffmpeg it uses.

The editor installs its tools into one folder in the user's home directory, so nothing is added to
the Python they already have and nothing needs an administrator password.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

HOME = Path(os.environ.get("VIDEO_EDITOR_HOME") or (Path.home() / ".sync-selling" / "video-editor"))
VENV = HOME / "venv"
CONFIG = HOME / "config.json"


def venv_python():
    return VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def hop():
    """Run this script again inside the editor's own Python, unless we're already there."""
    vpy = venv_python()
    if not vpy.exists():
        setup = Path(__file__).with_name("setup.py")
        sys.exit(f'The editor isn\'t set up yet. Run this first:\n  "{sys.executable}" "{setup}"')
    if Path(sys.prefix).resolve() == VENV.resolve():
        return
    sys.exit(subprocess.call([str(vpy), *sys.argv]))


def config():
    if not CONFIG.exists():
        sys.exit("The editor isn't set up yet. Run setup.py first.")
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def ffmpeg():
    return config()["ffmpeg"]


def run(cmd, cwd=None, check=True):
    """Run a command quietly and return what it printed on stderr."""
    p = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    err = p.stderr.decode("utf-8", "replace")
    if check and p.returncode != 0:
        tail = "\n".join(err.strip().splitlines()[-12:])
        sys.exit(f"ffmpeg stopped with an error:\n{tail}")
    return err


def read_audio(src):
    """The recording's sound as numbers, mono at 16,000 samples a second, read with our own ffmpeg."""
    import numpy as np
    p = subprocess.run([ffmpeg(), "-v", "error", "-i", str(src), "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0 or len(p.stdout) < 3200:
        tail = p.stderr.decode("utf-8", "replace").strip().splitlines()[-3:]
        sys.exit("Couldn't read any sound from that recording.\n" + "\n".join(tail))
    return np.frombuffer(p.stdout, dtype=np.int16).astype(np.float32) / 32768.0


def probe(src):
    """What ffmpeg says about the recording: frames a second, and whether it has picture, sound and HDR."""
    import re
    p = subprocess.run([ffmpeg(), "-hide_banner", "-i", str(src)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    err = p.stderr.decode("utf-8", "replace")
    video = next((ln for ln in err.splitlines() if "Stream #" in ln and " Video: " in ln
                  and "attached pic" not in ln), None)
    audio = any("Stream #" in ln and " Audio: " in ln for ln in err.splitlines())
    fps = None
    if video:
        m = re.search(r"([\d.]+) fps", video) or re.search(r"([\d.]+) tbr", video)
        if m:
            fps = float(m.group(1))
    hdr = bool(video) and ("arib-std-b67" in video or "smpte2084" in video)
    return {"video": bool(video), "audio": audio, "fps": fps, "hdr": hdr}
