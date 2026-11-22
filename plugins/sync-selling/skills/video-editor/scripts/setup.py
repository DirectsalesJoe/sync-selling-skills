#!/usr/bin/env python3
"""One-off setup for the video editor. Safe to run again at any time.

    python3 setup.py            install, or check an install that's already there
    python3 setup.py --check    only check, install nothing

It makes one folder in your home directory (~/.sync-selling/video-editor) and puts two free tools
in it: faster-whisper, which turns speech into words with timings, and a copy of ffmpeg, which
cuts the video and burns in the captions. Nothing else on the computer is changed, and no
administrator password is needed. The first transcription also downloads a speech model (486 MB),
once.
"""
import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _env  # noqa: E402

PACKAGES = ["faster-whisper>=1.1", "imageio-ffmpeg>=0.5"]


def say(msg):
    print(msg, flush=True)


def has(ffmpeg, flag, name):
    try:
        out = subprocess.run([ffmpeg, "-hide_banner", flag], capture_output=True, text=True, timeout=30).stdout
    except Exception:
        return False
    return any(line.split()[1:2] == [name] for line in out.splitlines() if len(line.split()) > 1)


def pick_ffmpeg(vpy):
    """The first ffmpeg that can encode H.264; one that can also burn captions wins."""
    found = []
    try:
        bundled = subprocess.run([str(vpy), "-c", "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"],
                                 capture_output=True, text=True, timeout=120).stdout.strip()
        if bundled:
            found.append(bundled)
    except Exception:
        pass
    system = shutil.which("ffmpeg")
    if system:
        found.append(system)
    usable = [f for f in found if has(f, "-encoders", "libx264")]
    for f in usable:
        if has(f, "-filters", "subtitles"):
            return f, True
    return (usable[0], False) if usable else (None, False)


def main():
    check_only = "--check" in sys.argv
    if sys.version_info < (3, 9):
        sys.exit(f"This needs Python 3.9 or newer, and this is {sys.version.split()[0]}. "
                 "Install the latest Python from python.org, then run this again.")
    vpy = _env.venv_python()
    if not vpy.exists():
        if check_only:
            sys.exit("Not set up yet. Run setup.py without --check.")
        say(f"Making the editor's folder at {_env.HOME}")
        _env.HOME.mkdir(parents=True, exist_ok=True)
        r = subprocess.run([sys.executable, "-m", "venv", str(_env.VENV)])
        if r.returncode != 0 or not vpy.exists():
            sys.exit("Python couldn't make its own folder to install into. On Ubuntu or Debian, run "
                     "'sudo apt install python3-venv' and try again.")
    if not check_only:
        say("Installing the two tools (a minute or two the first time)...")
        subprocess.run([str(vpy), "-m", "pip", "install", "--quiet", "--upgrade", "pip"])
        r = subprocess.run([str(vpy), "-m", "pip", "install", "--quiet", *PACKAGES])
        if r.returncode != 0:
            sys.exit("The install failed. The lines above say why. The usual causes are no internet "
                     "connection, or a very new or very old Python: Python 3.10 to 3.13 is the safe range.")
    ok = subprocess.run([str(vpy), "-c", "import faster_whisper, imageio_ffmpeg"], capture_output=True, text=True)
    if ok.returncode != 0:
        sys.exit("The tools didn't install properly:\n" + ok.stderr.strip()[-600:])
    ffmpeg, can_caption = pick_ffmpeg(vpy)
    if not ffmpeg:
        sys.exit("No working copy of ffmpeg was found. Install ffmpeg (on a Mac: brew install ffmpeg; "
                 "on Windows: winget install Gyan.FFmpeg) and run this again.")
    _env.CONFIG.write_text(json.dumps({"ffmpeg": ffmpeg, "captions": can_caption}, indent=1), encoding="utf-8")
    say(f"ffmpeg: {ffmpeg}")
    if not can_caption:
        say("Heads up: this copy of ffmpeg can't burn in captions. Cutting works. For captions, install a "
            "full ffmpeg (on a Mac: brew install ffmpeg-full; on Windows: winget install Gyan.FFmpeg) and run this again.")
    say("READY. The editor is set up.")


if __name__ == "__main__":
    main()
