#!/usr/bin/env python3
"""Step 1: turn a recording into words with timings, and find the retakes.

    python3 transcribe.py <video> <work folder> [--language en] [--model small] [--gap 0.8] [--reuse] [--check]

Writes four files into the work folder:
  words.json       every word with its start and end, in seconds of the recording
  transcript.md    the recording line by line, with KEEP or CUT against each line, for reading
  takes.json       which lines are retakes of which, and the restarts found inside lines
  plan.json        the proposed edit. Change this file, then run edit.py

A new line starts wherever the speaker stops for longer than --gap seconds. Two kinds of retake
are looked for:
  - a whole line that says nearly the same as a line just before it. The last take is kept.
  - a restart inside a line, where the speaker begins a phrase, stops, and begins it again with
    the same few words ("so what we do is, so what we do instead is..."). The first go comes
    out.
Both are proposals. Read transcript.md and correct plan.json before cutting.

Everything runs on this computer. The recording is not uploaded anywhere.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _env  # noqa: E402

_env.hop()

import argparse  # noqa: E402
import difflib  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
from pathlib import Path  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("src")
ap.add_argument("out")
ap.add_argument("--language", default="en", help="the language spoken, as a two-letter code; 'auto' to detect it")
ap.add_argument("--model", default="small", help="tiny, base, small, medium or large-v3: bigger is slower and more accurate")
ap.add_argument("--gap", type=float, default=0.8, help="a silence this long starts a new line")
ap.add_argument("--reuse", action="store_true", help="use the words already in the work folder, without listening again")
ap.add_argument("--check", action="store_true", help="for checking a finished video: write the transcript only, no plan")
a = ap.parse_args()

src = Path(a.src).expanduser()
if not src.exists():
    sys.exit(f"Can't find the recording at {src}")
out = Path(a.out).expanduser()
out.mkdir(parents=True, exist_ok=True)

if a.reuse and (out / "words.json").exists():
    saved = json.load(open(out / "words.json", encoding="utf-8"))
    words, duration, language = saved["words"], saved["duration"], saved.get("language", a.language)
else:
    from faster_whisper import WhisperModel  # noqa: E402

    import logging

    import ctranslate2

    ctranslate2.set_log_level(logging.ERROR)
    print(f"Loading the speech model '{a.model}' (a 486 MB download the first time)...", flush=True)
    try:
        model = WhisperModel(a.model, device="cpu", compute_type="int8")
    except Exception:
        model = WhisperModel(a.model, device="cpu", compute_type="default")

    print("Listening to the recording...", flush=True)
    audio = _env.read_audio(src)
    duration = len(audio) / 16000.0
    segments, info = model.transcribe(
        audio,
        language=None if a.language == "auto" else a.language,
        word_timestamps=True,
        vad_filter=True,
        condition_on_previous_text=False,   # so a repeated take isn't tidied away as a repeat
    )
    words, told = [], 0
    for seg in segments:
        for j, w in enumerate(seg.words or []):
            text = w.word.strip()
            if not text:
                continue
            joined_on = j > 0 and not w.word.startswith(" ")    # the model wrote it as part of the word before
            if words and (joined_on or not re.search(r"[A-Za-z0-9]", text) or text[0] in "'’"):
                words[-1]["w"] += text                      # "£600" + ",000", "30" + "%", "o" + "'clock"
                words[-1]["e"] = round(float(w.end), 3)
                continue
            words.append({"w": text, "s": round(float(w.start), 3), "e": round(float(w.end), 3)})
        if words and words[-1]["e"] - told >= 120:
            told = words[-1]["e"]
            print(f"  ...{told / 60:.0f} of {duration / 60:.0f} minutes", flush=True)
    if not words:
        sys.exit("No speech was found in that recording. Check it has sound, and that --language is right.")
    language = info.language

    # Speech models sometimes write words over silence ("Thank you for watching"). Drop any word
    # that has no sound where the model placed it, so it can't reach the captions.
    import numpy as np

    frames = len(audio) // 160
    level = 20 * np.log10(np.sqrt((audio[: frames * 160].reshape(frames, 160) ** 2).mean(axis=1)) + 1e-9)
    loud, floor = float(np.percentile(level, 95)), float(np.percentile(level, 10))
    heard = level >= min(floor + 0.3 * (loud - floor), loud - 12)

    def has_sound(w):
        i0, i1 = max(0, int((w["s"] - 0.1) * 100)), min(frames, int((w["e"] + 0.1) * 100) + 1)
        return i1 > i0 and bool(heard[i0:i1].any())

    silent = [w for w in words if not has_sound(w)]
    if silent and len(silent) < len(words):
        words = [w for w in words if has_sound(w)]
        print(f"  Left out {len(silent)} words the model wrote where there was no sound: "
              f"\"{' '.join(w['w'] for w in silent)[:120]}\"", flush=True)


def tok(text):
    return re.sub(r"[^a-z0-9]", "", text.lower())


# ---- lines: a new one wherever the speaker pauses
lines, cur = [], []
for i, w in enumerate(words):
    if cur and w["s"] - words[cur[-1]]["e"] > a.gap:
        lines.append(cur)
        cur = []
    cur.append(i)
if cur:
    lines.append(cur)

def is_retake(first, second):
    """True when `first` reads as an earlier go at `second`: nearly the same words, or a false start of it."""
    if not first or not second:
        return False
    sm = difflib.SequenceMatcher(None, first, second)
    matched = sum(blk.size for blk in sm.get_matching_blocks())
    if sm.ratio() >= 0.7:
        return True
    # a false start: "So the first thing you..." and then the whole line. The opening has to match,
    # give or take one stray word, and most of the first go has to be in the second.
    same_start = first[:2] == second[:2] or first[1:3] == second[:2] or first[:2] == second[1:3]
    return len(first) >= 3 and same_start and matched / len(first) >= 0.8 and len(first) <= len(second) + 2


def toks(indices):
    return [t for t in (tok(words[i]["w"]) for i in indices) if t]


# ---- whole-line retakes: a later line that repeats an earlier one joins its group; the last is kept
groups = []
for n, idx in enumerate(lines):
    mine = toks(idx)
    placed = False
    for g in groups:
        if n - g[-1] > 4:
            continue
        theirs = toks(lines[g[-1]])
        if is_retake(theirs, mine) or (theirs and mine and difflib.SequenceMatcher(None, theirs, mine).ratio() >= 0.55):
            g.append(n)
            placed = True
            break
    if not placed:
        groups.append([n])
keep_line = {g[-1] for g in groups}
retake_of = {n: g[-1] for g in groups for n in g[:-1]}

# ---- retakes inside a kept line
restarts = []


def note(n, indices):
    restarts.append({"line": n, "start": words[indices[0]]["s"], "end": words[indices[-1]]["e"],
                     "text": " ".join(words[i]["w"] for i in indices)})


for n in sorted(keep_line):
    idx = lines[n]
    gone = set()
    # 1. a whole sentence said again straight afterwards: the first go comes out
    sents, cur = [], []
    for i in idx:
        cur.append(i)
        if words[i]["w"][-1:] in ".?!":
            sents.append(cur)
            cur = []
    if cur:
        sents.append(cur)
    for k in range(len(sents) - 1):
        if is_retake(toks(sents[k]), toks(sents[k + 1])):
            note(n, sents[k])
            gone.update(sents[k])
    # 2. a phrase begun, dropped and begun again
    left = [i for i in idx if i not in gone]
    t = [tok(words[i]["w"]) for i in left]
    p = 0
    while p < len(left):
        cut_to = None
        # the same two to eight words said twice in a row
        for size in range(min(8, (len(left) - p) // 2), 1, -1):
            if all(t[p:p + size]) and t[p:p + size] == t[p + size:p + 2 * size]:
                cut_to = p + size
                break
        # the same three-word opening again within a dozen words, after a comma or a hesitation,
        # and only once (three times is a list, and comes from someone speaking on purpose)
        if cut_to is None and p + 3 <= len(left) and all(t[p:p + 3]):
            def broke_off(q):
                before, here = words[left[q - 1]], words[left[q]]
                return before["w"][-1:] in ",.;:?!-…" or here["s"] - before["e"] >= 0.3
            again = [q for q in range(p + 3, min(p + 14, len(left) - 2)) if t[q:q + 3] == t[p:p + 3]]
            earlier = [q for q in range(max(0, p - 13), p - 2) if t[q:q + 3] == t[p:p + 3]]
            if len(again) == 1 and not earlier and broke_off(again[0]):
                q = again[0]
                later = [r for r in range(q + 3, min(q + 14, len(left) - 2)) if t[r:r + 3] == t[p:p + 3]]
                if not later:
                    cut_to = q
        if cut_to is not None:
            note(n, left[p:cut_to])
            p = cut_to
        else:
            p += 1
restarts.sort(key=lambda r: r["start"])

plan = {
    "keep": [{"start": words[lines[n][0]]["s"], "end": words[lines[n][-1]]["e"],
              "text": " ".join(words[i]["w"] for i in lines[n])} for n in sorted(keep_line)],
    "cut": [{"text": r["text"], "near": r["start"]} for r in restarts],
}
for k in plan["keep"]:
    if len(k["text"]) > 90:
        k["text"] = k["text"][:60] + " ... " + k["text"][-25:]

json.dump({"source": str(src.resolve()), "duration": duration, "language": language, "model": a.model, "words": words},
          open(out / "words.json", "w", encoding="utf-8"), indent=1)
if not a.check:
    json.dump({"gap": a.gap,
               "lines": [{"line": n, "start": words[idx[0]]["s"], "end": words[idx[-1]]["e"],
                          "text": " ".join(words[i]["w"] for i in idx),
                          "keep": n in keep_line, "retake_of": retake_of.get(n)} for n, idx in enumerate(lines)],
               "restarts": restarts},
              open(out / "takes.json", "w", encoding="utf-8"), indent=1)
    json.dump(plan, open(out / "plan.json", "w", encoding="utf-8"), indent=1)

with open(out / "transcript.md", "w", encoding="utf-8") as f:
    f.write(f"# Transcript of {src.name}\n\n")
    length = f"{duration:.0f} seconds" if duration < 120 else f"{duration / 60:.1f} minutes"
    if a.check:
        f.write(f"{len(words)} words, {length}. This is a finished video, transcribed to check the joins. Read it through: "
                "every sentence should be whole, and no word should be said twice in a row. Anything marked CUT or "
                "\"Proposed cut\" below is a line that still seems to be said twice.\n\n")
    else:
        f.write(f"{len(words)} words, {length}, in {len(lines)} lines. "
                f"Proposed to cut: {len(retake_of)} whole-line retakes and {len(restarts)} restarts inside a line. "
                "Every proposed cut is already in plan.json.\n\n")
        f.write("A line is everything said between two pauses, so one sentence can run across two lines. KEEP stays in. "
                "CUT is a retake of the line it names. The number in front of each sentence is the second it starts at "
                "in the recording.\n\n")
    for n, idx in enumerate(lines):
        s, e = words[idx[0]]["s"], words[idx[-1]]["e"]
        mark = "KEEP" if n in keep_line else f"CUT, a retake of line {retake_of[n]:03d}"
        f.write(f"## Line {n:03d}, {s:.2f} to {e:.2f}: {mark}\n\n")
        sent = []
        for i in idx:
            sent.append(i)
            if words[i]["w"][-1:] in ".?!" or len(sent) >= 28:
                f.write(f"- [{words[sent[0]]['s']:8.2f}] {' '.join(words[j]['w'] for j in sent)}\n")
                sent = []
        if sent:
            f.write(f"- [{words[sent[0]]['s']:8.2f}] {' '.join(words[j]['w'] for j in sent)}\n")
        for r in restarts:
            if r["line"] == n:
                f.write(f"\nProposed cut inside this line, a restart at {r['start']:.2f}: \"{r['text']}\"\n")
        f.write("\n")

if a.check:
    print(f"{len(words)} words. Read {out / 'transcript.md'} to check the joins. There's no plan to change in this folder.")
else:
    print(f"{len(words)} words in {len(lines)} lines. Proposed to cut: {len(retake_of)} whole-line retakes "
          f"and {len(restarts)} restarts inside a line.")
    print(f"Read {out / 'transcript.md'}, correct {out / 'plan.json'}, then run edit.py.")
