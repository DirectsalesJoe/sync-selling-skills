---
name: video-editor
description: >
  Edit a talking-head recording without opening an editing app: find and cut the retakes,
  shorten the long pauses, burn in captions and level the sound, all on the user's own
  computer. It can also help script the video before it's recorded. Triggers on "edit this
  video", "cut the retakes", "chop this recording up", "tidy up this video", "add captions to
  this video", "edit my FAQ video", or a video file handed over with a request to make it
  cleaner or shorter. This is the light version: one person talking to one camera, straight
  cuts and plain captions. Not for music, titles, zooms, extra footage, more than one camera
  or turning a wide video into a tall one.
---

# Video editor (light)

Someone records themselves talking. They stop, start again and repeat lines as often as they like, and they never open an editing app. This skill gives them back one clean video: the retakes are gone, the long pauses are shorter, the captions are on if they want them, and the sound is brought up towards the level YouTube and the social apps expect.

Everything runs on their computer. The recording is never uploaded, and the original file is never changed.

You need to be able to run commands and read files on their computer, which means Claude Code, the Code tab in the Claude desktop app, or Codex. If you're in a plain chat with no computer to work on, say so, and point them to the README in this repository for where to run it.

The scripts are in the `scripts` folder beside this file. Run them by their full path. On Windows, use `py` or `python` wherever this page says `python3`.

## Before you start

Ask these together, once, and skip any they've already answered:

1. Where is the recording? You need the file's path.
2. Do they want captions? The default is yes. The word being said shows in yellow unless they give you a colour, so offer their brand colour.
3. Is there anything that must stay in, or must come out?

If they haven't recorded yet, go to step 1. If they have, go to step 2.

## Step 0. Set up, the first time only

```
python3 scripts/setup.py
```

Tell them what it does before you run it: it makes one folder in their home directory and puts two free tools in it, one that turns speech into words and one that cuts video. It takes a minute or two, changes nothing else on the computer and needs no password. The first transcription also downloads a speech model of 486 MB, once.

It ends with `READY`. If it ends with anything else, the message says what to do, and `references/when-it-goes-wrong.md` covers the rest.

## Step 1. Script it, if they haven't recorded yet

Read `references/script-your-video.md` and follow it. It turns the questions their buyers ask into a short crib for each answer, and it tells them how to record so the edit is easy. The one habit that matters: when they fluff a line, they stop, breathe, and say the whole sentence again from the start.

## Step 2. Transcribe

Make a work folder beside the recording, named after it with `-edit` on the end. Then:

```
python3 scripts/transcribe.py "<the recording>" "<the work folder>"
```

On a recent laptop this takes about a quarter of the recording's length, so two minutes for an eight minute video. It writes four files into the work folder:

- `transcript.md`: the recording line by line, with what it proposes to cut. A line is everything said between two pauses, so one sentence can run across two lines.
- `plan.json`: the proposed edit, which is the file you change. Every cut the transcript proposes is already in it.
- `words.json`: every word with its timing.
- `takes.json`: which lines it thinks are retakes of which.

If they spoke a language other than English, add `--language` with its two-letter code.

## Step 3. Read the transcript and settle the plan

This step is your judgement, and it's the one that decides whether the edit is any good. The script finds the obvious retakes. You find the rest.

Read `transcript.md` from top to bottom. Then:

- **Check every proposed cut.** A line marked CUT should be an earlier go at a line that's said again afterwards. A restart should be the first go at a phrase that's then said properly. If the speaker repeated something on purpose, put it back.
- **Find what the script missed.** It only spots a retake that starts with the same words. Look for a sentence that's abandoned and begun again differently, "sorry" or "let me do that again", a cough, a word to someone off camera, the settling-in before they start ("right, okay, are we recording") and the reach for the stop button at the end.
- **Take out notes to self.** A line like "take two", "the short version" or "right, again" is the speaker talking to themselves. It comes out, and you tell them you cut it.
- **The last complete take wins.** People repeat a line until they're happy with it, so keep the final one, unless that one has a fault you can see in the words.
- **Only take out retakes, false starts and dead bits.** Never cut something they meant to say because the video would be shorter or tidier without it. If you think a section should go, ask.
- **Fix words it misheard.** If a word in the transcript plainly isn't what they said, such as a name or a trade word, correct its `"w"` in `words.json` now, because the captions are made from that file. If you can't tell what they said, ask.
- **It doesn't change the order.** If the recording seems to be in the wrong order, say so and ask what they want, because this version only cuts.

`plan.json` has two lists, and you change both by hand:

- `keep` holds one entry per line that stays, with its start and end in seconds. To drop a whole line, delete its entry. The `text` in a keep entry is only a label so you can see which line it is, and it's shortened with "..." when the line is long. The start and end are what count.
- `cut` holds phrases to take out from inside a kept line, by their words. Copy the words exactly from `transcript.md`. If the same words are said more than once, add `"near"` with the second it starts at, so the right one comes out.

```json
{
 "keep": [
  {"start": 1.74, "end": 44.74, "text": "How much does it cost? Most people ... and that's why we do it this way."},
  {"start": 46.1, "end": 71.3, "text": "How long does it take? ..."}
 ],
 "cut": [
  {"text": "Most people think you have to, sorry,"},
  {"text": "so the first thing,", "near": 61.2}
 ]
}
```

Before you cut, tell them in a short list anything you're taking out that isn't a plain retake, with your reason. Don't ask about each obvious retake.

## Step 4. Cut

```
python3 scripts/edit.py "<the recording>" "<the work folder>" --captions --accent "#FFD400"
```

It writes `final.mp4`, `check.jpg` and `edit-report.md` into the work folder. Leave `--captions` off if they don't want them. Pauses longer than half a second between kept words are shortened as part of the cut, and the report says how many. The options you'll use:

| They want | Add |
|---|---|
| The finished video somewhere else | `--out "<path>.mp4"` |
| A different colour for the word being said | `--accent "#1F3FBF"` |
| The captions higher or lower | `--caption-y 0.8` (0 is the top of the frame, 1 is the bottom) |
| Bigger or smaller captions | `--caption-size 1.2` |
| Fewer words on screen at once | `--caption-words 3` |
| Their own font | `--font-file "<path to the .ttf>" --font-name "<the font's family name>"` |
| Captions with no pop as they appear | `--no-pop` |
| Tighter or looser pauses | `--tighten 0.4` (pauses longer than this many seconds are shortened; the default is 0.5) |
| More breathing room at each join | `--lead 0.15 --tail 0.2` |

## Step 5. Check it before you say it's done

1. Open `check.jpg` and look at it. It holds four frames taken at four points along the video. The captions should be on screen, easy to read and clear of the speaker's face. If they sit on the face, move them with `--caption-y` and run step 4 again.
2. Read `edit-report.md`. It says how long the video was and is, what came out, how many pauses were shortened and where the sound landed. If the sound stops short of -14 LUFS, the report says why, and nothing needs fixing.
3. Transcribe the finished video to check the joins:

```
python3 scripts/transcribe.py "<the work folder>/final.mp4" "<the work folder>/check" --check
```

Read `check/transcript.md` through. Every sentence should be whole, no word should be said twice across a join, nothing they meant to say should be missing, and every word should be one they'd want on screen in the captions. If something's wrong, fix `plan.json` or `words.json` in the work folder and run step 4 again. Step 2 doesn't need running again.

Then tell them where the video is, how long it was and how long it is now, what you took out, and anything you weren't sure about.

## Changes they ask for afterwards

Every change is a change to `plan.json` or an option on `edit.py`, then step 4 again. Cutting takes about a fifth of the recording's length, and nothing needs transcribing again.

- **"Put that bit back."** Add its entry back to `keep`, or delete it from `cut`.
- **"Take that bit out."** Delete its `keep` entry, or add its words to `cut`.
- **A word in the captions is wrong**, such as a name. Find the word in `words.json`, correct its `"w"`, and run step 4 again.

## What the light version doesn't do

It doesn't add music, titles, zooms or extra footage. It doesn't follow more than one camera, turn a wide video into a tall one, clean up noisy sound or correct colour. If they ask for one of those, say plainly that this version doesn't do it. Don't improvise half of it.

## If something goes wrong

`references/when-it-goes-wrong.md` lists what can go wrong and the fix for each.
