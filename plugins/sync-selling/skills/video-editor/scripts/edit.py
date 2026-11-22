#!/usr/bin/env python3
"""Step 2: cut the recording to the plan, tighten the pauses, add captions, level the sound.

    python3 edit.py <video> <work folder> [--captions] [--accent "#FFD400"] [--out <file.mp4>]

It reads words.json and plan.json from the work folder (transcribe.py wrote both) and writes:
  final.mp4        the finished video
  check.jpg        four frames from it, to look at before saying it's done
  edit-report.md   what was cut, how long it is now, and the sound level
  cut_words.json   the words on the finished video's timeline

What it does, in order:
  1. Keeps only the words inside the plan's "keep" entries.
  2. Finds where the sound really starts and stops around each kept run, so no word is clipped.
  3. Shortens any pause longer than --tighten seconds between kept words.
  4. With --captions, burns in captions a few words at a time, with the word being said in the
     accent colour and a small pop as each caption appears.
  5. Sets the loudness to -14 LUFS with one flat volume change, which is what YouTube and the
     social apps expect, and never lets a peak clip.

The recording itself is never changed. Run it again with different options as often as you like.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _env  # noqa: E402

_env.hop()

import argparse  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402
from fractions import Fraction  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("src")
ap.add_argument("work")
ap.add_argument("--plan", help="the plan to cut to (default: plan.json in the work folder)")
ap.add_argument("--out", help="where to write the finished video (default: final.mp4 in the work folder)")
ap.add_argument("--captions", action="store_true", help="burn captions into the picture")
ap.add_argument("--accent", default="#FFD400", help="the colour of the word being said, as a hex code")
ap.add_argument("--caption-y", type=float, help="how far down the frame the captions sit, 0 (top) to 1 (bottom)")
ap.add_argument("--caption-words", type=int, help="the most words in one caption")
ap.add_argument("--caption-size", type=float, default=1.0, help="1.0 is the normal size; 1.2 is a fifth bigger")
ap.add_argument("--font-file", help="a .ttf or .otf font to use in place of the plain one")
ap.add_argument("--font-name", help="that font's family name, as the font itself reports it")
ap.add_argument("--no-pop", action="store_true", help="captions appear with no pop")
ap.add_argument("--tighten", type=float, default=0.5, help="pauses longer than this many seconds are shortened")
ap.add_argument("--lead", type=float, default=0.08, help="seconds kept before the first sound of each piece")
ap.add_argument("--tail", type=float, default=0.12, help="seconds kept after the last sound of each piece")
ap.add_argument("--loudness", type=float, default=-14.0, help="target loudness in LUFS")
ap.add_argument("--no-loudness", action="store_true", help="leave the volume as recorded")
ap.add_argument("--max-side", type=int, default=1080, help="shrink the picture if its short side is bigger than this")
ap.add_argument("--crf", type=int, default=18, help="picture quality: lower is better and bigger; 18 is very good")
ap.add_argument("--keep-parts", action="store_true", help="keep the temporary pieces, for fault finding")
a = ap.parse_args()

src = Path(a.src).expanduser().resolve()
work = Path(a.work).expanduser().resolve()
if not src.exists():
    sys.exit(f"Can't find the recording at {src}")
for need in ("words.json",):
    if not (work / need).exists():
        sys.exit(f"{work / need} is missing. Run transcribe.py first.")
plan_path = Path(a.plan).expanduser().resolve() if a.plan else work / "plan.json"
if not plan_path.exists():
    sys.exit(f"Can't find the plan at {plan_path}")
out = Path(a.out).expanduser().resolve() if a.out else work / "final.mp4"
cfg = _env.config()
FF = cfg["ffmpeg"]
if a.captions and not cfg.get("captions"):
    sys.exit("This copy of ffmpeg can't burn in captions. Run setup.py again and follow what it says, "
             "or run this without --captions.")
if not re.fullmatch(r"#?[0-9a-fA-F]{6}", a.accent):
    sys.exit('--accent needs a six-figure hex colour, like "#FFD400"')

words = json.load(open(work / "words.json", encoding="utf-8"))["words"]
plan_all = json.load(open(plan_path, encoding="utf-8"))
plan = plan_all.get("keep") or []
cuts = plan_all.get("cut") or []
spans = sorted((float(p["start"]), float(p["end"])) if isinstance(p, dict) else (float(p[0]), float(p[1])) for p in plan)
if not spans:
    sys.exit('The plan keeps nothing. Add at least one entry to "keep" in plan.json.')

# ---------------------------------------------------------------- the recording's shape
shape = _env.probe(src)
if not shape["video"]:
    sys.exit("That file has no picture in it. This edits video recordings.")
if not shape["audio"]:
    sys.exit("That file has no sound in it, so there's nothing to cut by.")
rate = Fraction(shape["fps"] or 30).limit_denominator(1001)
hdr = shape["hdr"]

STANDARD = [Fraction(24000, 1001), Fraction(24), Fraction(25), Fraction(30000, 1001), Fraction(30),
            Fraction(50), Fraction(60000, 1001), Fraction(60)]
fps = min(STANDARD, key=lambda f: abs(float(f) - float(rate)))
if abs(float(fps) - float(rate)) / float(rate) > 0.03:
    fps = Fraction(round(float(rate) * 100), 100)
if fps > 60:
    fps = Fraction(60)
FPS = float(fps)
FPS_ARG = f"{fps.numerator}/{fps.denominator}"

png = subprocess.run([FF, "-v", "error", "-i", str(src), "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
                     capture_output=True).stdout
if len(png) < 24:
    sys.exit("Couldn't read a frame from that recording. Is it a video file?")
W, H = int.from_bytes(png[16:20], "big"), int.from_bytes(png[20:24], "big")
short = min(W, H)
scale = a.max_side / short if short > a.max_side else 1.0
OW, OH = int(round(W * scale / 2) * 2), int(round(H * scale / 2) * 2)

# ---------------------------------------------------------------- where the sound is
HOP = 0.01
x = _env.read_audio(src)
duration = len(x) / 16000.0
n = len(x) // 160
db = 20 * np.log10(np.sqrt((x[: n * 160].reshape(n, 160) ** 2).mean(axis=1)) + 1e-9)
speech, floor = float(np.percentile(db, 95)), float(np.percentile(db, 10))
THR = min(floor + 0.3 * (speech - floor), speech - 12)
quiet = db < THR


def quiet_after(t, limit):
    """The first moment at or after t where it has gone quiet (three frames running), up to limit."""
    i, end = max(0, int(t / HOP)), min(n - 3, int(limit / HOP))
    while i <= end:
        if quiet[i] and quiet[i + 1] and quiet[i + 2]:
            return i * HOP
        i += 1
    return None


def quiet_before(t, limit):
    """The last moment at or before t where it was still quiet (three frames running), back to limit."""
    i, start = min(n - 1, int(t / HOP)), max(2, int(limit / HOP))
    while i >= start:
        if quiet[i] and quiet[i - 1] and quiet[i - 2]:
            return (i + 1) * HOP
        i -= 1
    return None


# ---------------------------------------------------------------- which words stay, and the pieces
def kept(w):
    mid = (w["s"] + w["e"]) / 2
    return any(s - 0.01 <= mid <= e + 0.01 for s, e in spans)


keep = [kept(w) for w in words]


def norm(text):
    return re.sub(r"[^a-z0-9]", "", text.lower())


# "cut" entries name a phrase to take out, by its words. Find each one in the recording.
letters = [norm(w["w"]) for w in words]
blob = "".join(letters)
word_at, pos = {}, 0            # where each word starts in the run of letters
for i, t in enumerate(letters):
    if t:
        word_at[pos] = i
    pos += len(t)
ends = {p + len(letters[i]): i for p, i in word_at.items()}
for c in cuts:
    text, near = (c.get("text", ""), c.get("near")) if isinstance(c, dict) else (str(c), None)
    want = norm(text)
    if not want:
        continue
    hits, at = [], blob.find(want)
    while at != -1:
        if at in word_at and at + len(want) in ends:
            hits.append((word_at[at], ends[at + len(want)]))
        at = blob.find(want, at + 1)
    if not hits:
        sys.exit(f'A "cut" entry in the plan isn\'t in the recording, word for word: "{text}". '
                 "Copy the words exactly from transcript.md.")
    if len(hits) > 1 and near is None:
        times = ", ".join(f"{words[h[0]]['s']:.1f}" for h in hits)
        sys.exit(f'"{text}" is said {len(hits)} times, at {times} seconds. Add "near": <seconds> to that cut entry '
                 "to say which one comes out.")
    first, last = min(hits, key=lambda h: abs(words[h[0]]["s"] - float(near))) if near is not None else hits[0]
    for i in range(first, last + 1):
        keep[i] = False
if not any(keep):
    sys.exit("No words fall inside the plan's times. Check the start and end times in plan.json against transcript.md.")
runs, cur = [], []
for i, w in enumerate(words):
    if not keep[i]:
        if cur:
            runs.append(cur)
        cur = []
        continue
    if cur and w["s"] - words[cur[-1]]["e"] > a.tighten:
        runs.append(cur)
        cur = []
    cur.append(i)
if cur:
    runs.append(cur)

pauses = [(words[b[0]]["s"] - words[a_[-1]]["e"]) for a_, b in zip(runs, runs[1:]) if b[0] == a_[-1] + 1]

pieces = []
for r in runs:
    first, last = words[r[0]], words[r[-1]]
    lo = words[r[0] - 1]["e"] + 0.02 if r[0] > 0 else 0.0
    hi = words[r[-1] + 1]["s"] - 0.02 if r[-1] + 1 < len(words) else duration
    lo, hi = min(lo, first["s"]), max(hi, last["e"])
    q = quiet_before(first["s"] + 0.05, max(lo, first["s"] - 0.3))
    start = max((min(q, first["s"]) if q is not None else first["s"]) - a.lead, lo, 0.0)
    q = quiet_after(last["e"] - 0.05, min(hi, last["e"] + 0.3))
    end = min((max(q, last["e"]) if q is not None else last["e"]) + a.tail, hi, duration)
    if end - start > 0.05:
        pieces.append([start, end])
pieces.sort()
merged = [pieces[0]]
for s, e in pieces[1:]:
    if s - merged[-1][1] < 0.04:
        merged[-1][1] = max(merged[-1][1], e)
    else:
        merged.append([s, e])

# snap every piece to whole frames, so sound and picture stay the same length
segs, last_f = [], 0
for s, e in merged:
    sf, ef = max(last_f, int(round(s * FPS))), int(round(e * FPS))
    if ef - sf < 2:
        continue
    segs.append({"f0": sf, "n": ef - sf, "start": sf / FPS, "dur": (ef - sf) / FPS})
    last_f = ef
if not segs:
    sys.exit("Nothing was left to keep after the cut. Check plan.json.")
offset = 0.0
for g in segs:
    g["offset"] = offset
    offset += g["dur"]
total = offset

cut_words = []
for i, w in enumerate(words):
    if not keep[i]:
        continue
    mid = (w["s"] + w["e"]) / 2
    g = next((g for g in segs if g["start"] - 0.02 <= mid <= g["start"] + g["dur"] + 0.02), None)
    if g is None:
        continue
    s = g["offset"] + min(max(w["s"] - g["start"], 0.0), g["dur"])
    e = g["offset"] + min(max(w["e"] - g["start"], 0.0), g["dur"])
    if cut_words and s < cut_words[-1]["s"] + 0.01:
        s = cut_words[-1]["s"] + 0.01
    cut_words.append({"w": w["w"], "s": round(s, 3), "e": round(max(e, s + 0.01), 3)})
json.dump({"duration": total, "words": cut_words}, open(work / "cut_words.json", "w", encoding="utf-8"), indent=1)

# ---------------------------------------------------------------- captions
portrait = OH > OW
vf_caption = None
if a.captions:
    def find_font():
        if a.font_file:
            p = Path(a.font_file).expanduser()
            if not p.exists():
                sys.exit(f"Can't find the font at {p}")
            if not a.font_name:
                sys.exit("--font-file needs --font-name too: the family name the font reports, like \"Poppins\"")
            return p, a.font_name, 0
        if sys.platform == "darwin":
            cands = [("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "Arial"),
                     ("/Library/Fonts/Arial Bold.ttf", "Arial"),
                     ("/System/Library/Fonts/Supplemental/Verdana Bold.ttf", "Verdana")]
        elif os.name == "nt":
            win = os.environ.get("WINDIR", r"C:\Windows")
            cands = [(win + r"\Fonts\arialbd.ttf", "Arial"), (win + r"\Fonts\segoeuib.ttf", "Segoe UI")]
        else:
            cands = [("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "DejaVu Sans"),
                     ("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", "Liberation Sans"),
                     ("/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf", "DejaVu Sans"),
                     ("/usr/share/fonts/liberation-sans/LiberationSans-Bold.ttf", "Liberation Sans")]
        for path, name in cands:
            if Path(path).exists():
                return Path(path), name, -1
        return None, "Arial", -1

    font_path, font_name, bold = find_font()
    fonts = work / "fonts"
    if fonts.exists():
        shutil.rmtree(fonts)
    fonts.mkdir()
    if font_path:
        shutil.copy(font_path, fonts / font_path.name)

    size = round((OW * 0.075 if portrait else OH * 0.062) * a.caption_size)
    y = round(OH * (a.caption_y if a.caption_y is not None else (0.72 if portrait else 0.86)))
    max_words = a.caption_words or (3 if portrait else 5)
    max_chars = max(10, int((OW * 0.86) / (size * 0.56)))
    hexc = a.accent.lstrip("#")
    accent = f"&H{hexc[4:6]}{hexc[2:4]}{hexc[0:2]}&".upper()

    chunks, cur = [], []
    for w in cut_words:
        text = " ".join(c["w"] for c in cur + [w])
        if cur and (len(cur) >= max_words or len(text) > max_chars or w["s"] - cur[-1]["e"] > 0.35
                    or cur[-1]["w"][-1:] in ".,!?;:"):
            chunks.append(cur)
            cur = []
        cur.append(w)
    if cur:
        chunks.append(cur)

    def ts(t):
        cs = int(round(max(t, 0.0) * 100))
        return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"

    def show(w):
        t = re.sub(r"[{}\\]", "", w["w"]).rstrip(".,;:")
        return t or w["w"]

    events = []
    for ci, c in enumerate(chunks):
        c_end = min(chunks[ci + 1][0]["s"], c[-1]["e"] + 0.6) if ci + 1 < len(chunks) else min(c[-1]["e"] + 0.4, total)
        shown = False
        for j, w in enumerate(c):
            s = w["s"]
            e = c[j + 1]["s"] if j + 1 < len(c) else c_end
            if e - s < 0.02:
                continue
            head = f"\\an5\\pos({OW // 2},{y})"
            first, shown = not shown, True
            if first and not a.no_pop:
                head += "\\fscx86\\fscy86\\t(0,90,\\fscx100\\fscy100)"
            parts = [f"{{\\1c{accent}}}{show(x)}{{\\1c&HFFFFFF&}}" if k == j else show(x) for k, x in enumerate(c)]
            events.append(f"Dialogue: 0,{ts(s)},{ts(e)},Cap,,0,0,0,,{{{head}}}{' '.join(parts)}")

    ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {OW}
PlayResY: {OH}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{font_name},{size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,{bold},0,0,0,100,100,0,0,1,{max(2, round(size * 0.08))},{max(1, round(size * 0.03))},5,40,40,40,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(events) + "\n"
    (work / "captions.ass").write_text(ass, encoding="utf-8")
    vf_caption = "subtitles=captions.ass:fontsdir=fonts"

# ---------------------------------------------------------------- cut the pieces
parts = work / "parts"
if parts.exists():
    shutil.rmtree(parts)
parts.mkdir()
def length(t):
    return f"{t:.1f} seconds" if t < 120 else f"{t / 60:.1f} minutes"


print(f"Cutting it into {len(segs)} pieces: {length(duration)} down to {length(total)}...", flush=True)
for k, g in enumerate(segs):
    vf = []
    if (OW, OH) != (W, H):
        vf.append(f"scale={OW}:{OH}")
    vf.append(f"fps={FPS_ARG}")
    if vf_caption:
        vf += [f"setpts=PTS+{g['offset']:.6f}/TB", vf_caption, "setpts=PTS-STARTPTS"]
    fade = min(0.012, g["dur"] / 4)
    af = (f"afade=t=in:st=0:d={fade:.4f},afade=t=out:st={g['dur'] - fade:.6f}:d={fade:.4f},"
          f"apad=whole_dur={g['dur']:.6f}")
    _env.run([FF, "-v", "error", "-y", "-ss", f"{g['start']:.6f}", "-t", f"{g['dur'] + 0.5:.6f}", "-i", str(src),
              "-map", "0:v:0", "-map", "0:a:0", "-vf", ",".join(vf), "-af", af,
              "-c:v", "libx264", "-preset", "veryfast", "-crf", str(a.crf), "-pix_fmt", "yuv420p", "-r", FPS_ARG,
              "-frames:v", str(g["n"]), "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", "-t", f"{g['dur']:.6f}",
              f"parts/p{k:04d}.mov"], cwd=str(work))
    if (k + 1) % 20 == 0 or k + 1 == len(segs):
        print(f"  {k + 1} of {len(segs)}", flush=True)
(parts / "list.txt").write_text("".join(f"file 'p{k:04d}.mov'\n" for k in range(len(segs))), encoding="utf-8")

# ---------------------------------------------------------------- level the sound, join it up
gain, measured, peak = 0.0, None, None
if not a.no_loudness:
    err = _env.run([FF, "-hide_banner", "-nostats", "-f", "concat", "-safe", "0", "-i", "parts/list.txt", "-vn",
                    "-af", f"loudnorm=I={a.loudness}:TP=-1:LRA=11:print_format=json", "-f", "null", "-"], cwd=str(work))
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", err, re.S)
    if m:
        try:
            j = json.loads(m.group(0))
            measured, peak = float(j["input_i"]), float(j["input_tp"])
            if measured > -70:
                gain = max(min(a.loudness - measured, -1.0 - peak, 30.0), -30.0)
        except (ValueError, KeyError):
            pass
out.parent.mkdir(parents=True, exist_ok=True)
_env.run([FF, "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "parts/list.txt", "-c:v", "copy",
          "-af", f"volume={gain:.2f}dB", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(out)],
         cwd=str(work))
if not a.keep_parts:
    shutil.rmtree(parts, ignore_errors=True)

# ---------------------------------------------------------------- four frames to look at
marks = [total * f for f in (0.1, 0.37, 0.63, 0.9)]
if a.captions and cut_words:
    marks = [min(cut_words, key=lambda w: abs(w["s"] - t))["s"] + 0.15 for t in marks]
marks = [min(max(t, 0.0), max(total - 0.1, 0.0)) for t in marks]
cmd = [FF, "-v", "error", "-y"]
for t in marks:
    cmd += ["-ss", f"{t:.3f}", "-i", str(out)]
tile_w = 420 if portrait else 800
graph = "".join(f"[{i}:v]scale={tile_w}:-2[t{i}];" for i in range(4))
graph += "[t0][t1][t2][t3]hstack=inputs=4" if portrait else "[t0][t1]hstack[a];[t2][t3]hstack[b];[a][b]vstack"
_env.run(cmd + ["-filter_complex", graph, "-frames:v", "1", "-q:v", "3", str(work / "check.jpg")], check=False)

# ---------------------------------------------------------------- the report
removed = duration - total
lines = [f"# Edit report for {src.name}", "",
         f"- Recording: {length(duration)}, {W}x{H}, {FPS:.2f} frames a second.",
         f"- Finished video: {length(total)}, {OW}x{OH}. {removed:.1f} seconds came out, in {len(segs) - 1} joins.",
         f"- Words kept: {len(cut_words)} of {len(words)}.",
         f"- Pauses shortened: {len(pauses)}" + (f", the longest of them {max(pauses):.1f} seconds before the cut." if pauses else "."),
         f"- Captions: {'on, accent ' + a.accent if a.captions else 'off'}."]
if measured is not None:
    lines.append(f"- Sound: recorded at {measured:.1f} LUFS, moved by {gain:+.1f} dB to about {measured + gain:.1f} LUFS "
                 f"(peak {peak + gain:.1f} dBTP).")
    if abs((measured + gain) - a.loudness) > 1.0:
        lines.append(f"  It stops short of {a.loudness:.0f} LUFS because going louder would have distorted the loudest moment. "
                     "That's normal, and nothing needs fixing.")
if hdr:
    lines.append("- The recording was filmed in HDR. The colours can look flat in the finished video. "
                 "See references/when-it-goes-wrong.md.")
takes = work / "takes.json"
if takes.exists():
    t = json.load(open(takes, encoding="utf-8"))
    cut_lines = [ln for ln in t["lines"] if not any(s - 0.01 <= (ln["start"] + ln["end"]) / 2 <= e + 0.01 for s, e in spans)]
    if cut_lines or cuts:
        lines += ["", "## What came out", ""]
        lines += [f"- Whole line, {ln['start']:.1f} to {ln['end']:.1f}: {ln['text']}" for ln in cut_lines]
        lines += [f"- Phrase: {c.get('text') if isinstance(c, dict) else c}" for c in cuts]
lines += ["", f"The finished video is at `{out}`. `check.jpg` holds four frames from it, taken at four points along the video."]
(work / "edit-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

print(f"Done: {out}")
print(f"{length(duration)} down to {length(total)}, {len(segs) - 1} joins, {len(pauses)} pauses shortened" +
      (", captions on" if a.captions else "") +
      (f", sound at about {measured + gain:.1f} LUFS" if measured is not None else "") + ".")
if hdr:
    print("Note: this was filmed in HDR, so check the colours. See references/when-it-goes-wrong.md.")
print(f"Look at {work / 'check.jpg'} before you say it's done, and read {work / 'edit-report.md'}.")
