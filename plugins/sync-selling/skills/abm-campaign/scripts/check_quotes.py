#!/usr/bin/env python3
"""Check that every quoted phrase in an email is really in its sources.

Usage:
    python3 scripts/check_quotes.py <email.md> <source> [<source> ...]

Finds every phrase in double quotes ("..." or curly quotes) in the first file and looks
for it, word for word, in the source files (the pack, the proof bank, a saved web page).
Case, curly quotes, markdown emphasis and spacing are ignored; nothing else is.
A quote with an ellipsis is checked piece by piece.

A quote of three words or more that isn't in any source is a FAIL.
A shorter quote that isn't found is a FLAG, because one or two words are often a term
("account managers") rather than a quotation.

Exits 1 if anything fails. Needs only Python 3.
"""

import re
import sys
from pathlib import Path

QUOTE = re.compile(r'"([^"\n]{2,600})"|“([^”\n]{2,600})”')
ELLIPSIS = re.compile(r"\.\.\.|…")


def normalise(text: str) -> str:
    text = text.lower()
    text = (text.replace("‘", "'").replace("’", "'")
                .replace("“", '"').replace("”", '"'))
    text = re.sub(r"[*_`]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def strip_ends(piece: str) -> str:
    return piece.strip(" .,;:!?'\"()[]-")


def without_code(text: str) -> str:
    out, fenced = [], False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            fenced = not fenced
            continue
        if not fenced:
            out.append(line)
    return "\n".join(out)


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    target = Path(argv[1])
    sources = [Path(p) for p in argv[2:]]
    missing = [str(p) for p in [target, *sources] if not p.exists()]
    if missing:
        print("Can't find: " + ", ".join(missing))
        return 2

    corpus = " ".join(normalise(p.read_text(encoding="utf-8", errors="ignore")) for p in sources)
    text = without_code(target.read_text(encoding="utf-8", errors="ignore"))

    fails, flags, passes = [], [], 0
    for m in QUOTE.finditer(text):
        quote = m.group(1) or m.group(2)
        pieces = [strip_ends(normalise(p)) for p in ELLIPSIS.split(quote)]
        pieces = [p for p in pieces if p]
        for piece in pieces:
            if piece in corpus:
                passes += 1
            elif len(piece.split()) >= 3:
                fails.append(piece)
            else:
                flags.append(piece)

    for piece in fails:
        print(f'FAIL  not in any source: "{piece}"')
    for piece in flags:
        print(f'FLAG  short quote not found, check it is a term and not a quotation: "{piece}"')
    print(f"{passes} quoted phrase(s) found in the sources, {len(fails)} fail, {len(flags)} flag.")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
