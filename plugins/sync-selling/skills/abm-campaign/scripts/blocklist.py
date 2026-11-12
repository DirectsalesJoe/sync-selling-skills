#!/usr/bin/env python3
"""Catch the phrases that make a cold email read as automated or about the sender.

Usage:
    python3 scripts/blocklist.py <email.md> [<email.md> ...]

FAIL lines must be fixed before the email goes on. FLAG lines have legitimate uses,
so read each one and decide. Text inside ``` fences is skipped.
Add your own patterns to the two lists below, each with what to do instead.

Exits 1 if anything fails. Needs only Python 3.
"""

import re
import sys
from pathlib import Path

I = re.IGNORECASE

FAIL = [
    (r"—", "Em dash. Use a comma, a colon, a full stop or brackets."),
    (r" – ", "Spaced en dash. Use a comma, a colon, a full stop or brackets."),
    (r"hope (this|the|my) (email |message |note )?finds you", "Start with their situation instead."),
    (r"\bjust (checking in|following up|circling back|touching base|wanted to)", "Bring the gift back, or add one useful thing."),
    (r"\b(touch(ing)? base|circl(e|ing) back)\b", "Say what you want in plain words."),
    (r"\bquick question\b", "Ask the question."),
    (r"\bcongratulations on\b", "The moment is your reason to write. Write about their situation instead."),
    (r"\b(saw|see|noticed|notice) (that )?you('re| are) hiring\b", "State what the ad says, and what it means for them."),
    (r"\bI came across\b", "Say what you found, and why it matters to them."),
    (r"\bpick your brains?\b", "Ask for something smaller, or give something first."),
    (r"\bhop on a (quick )?call\b", "Ask one question they can answer in a word."),
    (r"\b(leverag(e|es|ed|ing)|utili[sz](e|es|ed|ing)|optimi[sz](e|es|ed|ing)|synerg(y|ies))\b", "Use, help, show, buy."),
    (r"\b(game[- ]?changer|cutting[- ]edge|revolutioni[sz](e|es|ed|ing)|best[- ]in[- ]class|world[- ]class solution)\b", "Say what it does, with a number if you have one."),
    (r"\{\{[^}]*\}\}|\[[A-Za-z][A-Za-z ,'-]{1,40}\](?!\()", "A merge field or placeholder was left in, like [phone] or {{first_name}}."),
    (r"\b(TODO|TBC|TBD|FIXME)\b", "Something was left unfinished."),
]

FLAG = [
    (r"\b(calendly\.com|cal\.com|book a time|grab a time|find a time)\b", "A calendar link on a first touch is a big ask. Fine in a reply."),
    (r"\b(30|thirty|45|forty-five|60|sixty) minutes\b", "Long for a stranger. Make the ask smaller."),
    (r"\bminutes of your time\b", "Asks for their time before giving anything."),
    (r"\b(I'?m|I am|I wanted to) reach(ing)? out\b", "Often fine. Check the line says why it's them, not that you're writing."),
    (r"\b(we are a|we're a) (leading|top|trusted|premier)\b", "About the sender. Say what you did for someone like them."),
    (r"\b(our (solution|platform|product|services?))\b", "About the sender. Check the sentence is really about them."),
    (r"\bwould love to\b", "Says what you want. Say what they get."),
    (r"\bdemo\b", "A demo is a pitch. Check the gift comes first."),
    (r"!.*!", "More than one exclamation mark in a line."),
    (r"\b(free|no obligation|no strings)\b", "Check it doesn't read as a sales offer."),
    (r"\b(color|favorite|behavior|organiz(e|ed|ing)|prioritiz(e|ed|ing)|analyz(e|ed|ing)|center)\b", "US spelling. Fine if the reader is American."),
]


def lines_outside_code(text):
    fenced = False
    for n, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith("```"):
            fenced = not fenced
            continue
        if not fenced:
            yield n, line


def check(path: Path):
    fails = flags = 0
    text = path.read_text(encoding="utf-8", errors="ignore")
    for n, line in lines_outside_code(text):
        for pattern, fix in FAIL:
            m = re.search(pattern, line, I)
            if m:
                fails += 1
                print(f"FAIL  {path.name}:{n}  '{m.group(0)}'  {fix}")
        for pattern, fix in FLAG:
            m = re.search(pattern, line, I)
            if m:
                flags += 1
                print(f"FLAG  {path.name}:{n}  '{m.group(0)}'  {fix}")
    return fails, flags


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    total_fail = total_flag = 0
    for name in argv[1:]:
        path = Path(name)
        if not path.exists():
            print(f"Can't find {name}")
            return 2
        f, g = check(path)
        total_fail += f
        total_flag += g
    print(f"{total_fail} fail, {total_flag} flag.")
    return 1 if total_fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
