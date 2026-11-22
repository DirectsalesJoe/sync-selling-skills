# When something goes wrong

Each row is something that can go wrong, why it happens and what fixes it. Tell the user what happened in plain words before you fix it.

## Setting up

| What you see | Why | The fix |
|---|---|---|
| `python3` isn't found | Python isn't installed | On a Mac, running `python3` once offers to install Apple's developer tools, and it's fine to say yes. On Windows, run `winget install Python.Python.3.12`, or install it from python.org, then use `py` in place of `python3`. |
| "This needs Python 3.9 or newer" | The computer's Python is too old | Install the latest Python from python.org and run setup again with that one. |
| "The install failed" | No internet connection, or a Python so new the tools haven't caught up with it | Check the connection and run setup again. If it still fails, install Python 3.12 and run setup with that. |
| "This copy of ffmpeg can't burn in captions" | The copy of ffmpeg it found was built without the captions part | On a Mac, `brew install ffmpeg-full`. On Windows, `winget install Gyan.FFmpeg`. Then run setup again. Cutting works without it. |
| The speech model won't download | The download was blocked, or the connection dropped part way | Run the transcribe step again, and it carries on. On a work computer, a firewall may be blocking huggingface.co, which is where the model comes from. |

## Transcribing

| What you see | Why | The fix |
|---|---|---|
| "No speech was found" | The file has no sound, or the wrong language was set | Play the file and check it has sound. If they spoke another language, add `--language` with its two-letter code. |
| Names or trade words are wrong | The small speech model guesses at words it doesn't know | Correct the word's `"w"` in `words.json`, which fixes the captions. If a lot is wrong, run it again with `--model medium`, which is slower and more accurate. |
| The whole recording comes back as one or two lines | They talk without long pauses | That's fine. Retakes inside a line are cut by their words, in the plan's `cut` list. To split it into more lines, run it again with `--gap 0.5 --reuse`, which uses the words it already has. |
| It's slow | A long recording on an older computer | On a recent laptop it takes about a quarter of the recording's length. `--model base` is faster and less accurate. |

## Cutting

| What you see | Why | The fix |
|---|---|---|
| "A cut entry in the plan isn't in the recording, word for word" | The words in `cut` don't match the transcript | Copy the words exactly from `transcript.md`, from the first word of the phrase to the last. |
| "... is said 2 times" | The same words come up more than once | Add `"near"` to that entry, with the second the one to cut starts at. |
| A word is clipped at a join | The speaker ran two words together, so there was no quiet to cut in | Run the cut again with `--lead 0.15 --tail 0.2`. If it's still clipped, change the plan so the cut falls one word earlier or later. |
| A join feels rushed | The pause that's left is short | Run it again with `--tail 0.25`, or raise `--tighten` so fewer pauses are shortened. |
| The captions sit on the speaker's face | They're framed low in the picture | Move the captions with `--caption-y`. Try 0.9 for lower, or 0.12 to put them at the top. |
| The colours look flat or washed out | The recording was filmed in HDR, which most phones now do unless it's switched off | For next time, on an iPhone: Settings, Camera, Record Video, HDR Video off. For this recording, convert it to standard colour first with ffmpeg's `zscale` and `tonemap` filters, if this copy of ffmpeg has them, then edit the converted file. Tell the user you've done that. |
| The report says the sound stops short of -14 LUFS | One loud moment, such as a laugh or a clap, would have clipped | Nothing to fix. The volume is raised as far as it can go without distorting. |
| The picture is smaller than the recording | Anything bigger than 1080 on its short side is shrunk, to keep the edit quick | Add `--max-side 2160` to keep a 4K picture. It takes about four times as long. |
| "ffmpeg stopped with an error" | Usually an unusual file, such as a screen recording with no camera track | Read the lines under the message. If the file is damaged or in an odd format, convert it to an ordinary MP4 first and edit that. |

## Starting again

Deleting the work folder loses nothing but the edit. To remove the editor from the computer completely, delete the `.sync-selling/video-editor` folder in the home directory.
