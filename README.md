# Sync Selling skills for Claude

These are the Claude skills from the Sync Selling sessions, so you can run what Joe shows on the calls in your own business. Add them to Claude once and every improvement we make, and every new skill we add, reaches you without you doing anything.

The first one is **ABM campaign**, from the Deal Clinic on 10 November 2026. It finds the right person at the right business at the right moment, works out something you could send them that's so useful they'd pay to receive it, and writes the emails. Claude researches each business, a separate agent checks every fact, and another reads each email as the buyer would before you see it. Nothing sends until you've read it.

The second is **Video editor (light)**. You record yourself talking, with as many retakes as you like, and hand over the file. It cuts the retakes, shortens the long pauses, adds captions and sets the sound level, and you get one clean video back without opening an editing app. It runs on your own computer, so your recording never leaves it. [How to use it is here](#edit-a-video).

They're first versions. If something trips you up, reply to any Sync Selling email and tell us, and the fix will reach everyone.

## Edit a video

There's nothing to install first. You need the Claude desktop app, a video of you talking, and about ten minutes the first time.

1. Open the Claude desktop app, click **Code**, and choose the folder your video is in. The video editor needs the Code tab, because that's where Claude can work on a file on your computer. It can't run in a normal chat.
2. Paste this, with your video's file name in the brackets:

> Download the video-editor skill from https://github.com/DirectsalesJoe/sync-selling-skills (it's the folder plugins/sync-selling/skills/video-editor). Read its SKILL.md and follow it to edit [my-video.mp4]. Cut the retakes, shorten the long pauses and add captions.

Here's what happens next:

- **The first time, it sets itself up.** It puts two free tools in one folder on your computer and downloads a speech model of 486 MB. That takes a few minutes and happens once. It needs Python 3, and on a Mac the first run may ask to install Apple's developer tools, which is fine to say yes to.
- **It listens to your recording and writes out every word.** Then it finds the lines you said more than once and keeps the last go at each.
- **It tells you what it's taking out** if anything isn't a plain retake, so nothing you meant to say goes missing.
- **It gives you the finished video** in a folder beside your recording, with a note of what came out.

If it gets something wrong, tell it in your own words: "put the bit about pricing back", "make the captions bigger", "use our blue for the captions", "leave longer pauses". Each change takes a minute or two.

Haven't recorded yet? Say "Help me script a video that answers my buyers' top ten questions", and it writes you a crib for each answer and tells you how to record so the edit is easy.

The light version is for one person talking to one camera. It doesn't add music, titles or extra footage, and it doesn't turn a wide video into a tall one.

### On ChatGPT

Use Codex, the part of ChatGPT that can work on files on your computer. Open it on the folder your video is in and paste the same message. We built and tested the editor with Claude on a Mac. ChatGPT follows the same instructions file and Windows runs the same steps, so if either trips you up, tell us and we'll fix it.

### Keep it in Claude for good

Add the skills to Claude using the steps below. After that you only need to say "edit my-video.mp4" in the Code tab, and every improvement we make reaches you.

## Add the skills to the Claude desktop app

1. Open Claude and click **Customize** in the sidebar, then **Plugins**. <!-- copycheck: allow us-ize-verbs -->
2. Click **Add marketplace** and paste `DirectsalesJoe/sync-selling-skills`.
3. Find **Sync Selling** in the list and click **Install**.
4. On the marketplace, turn on **Sync automatically**, so changes come through by themselves.

The ABM skill then works in Cowork and in chat. Switch on web search, because the research needs it. The video editor works in the Code tab.

## Add the skills to Claude Code

In a Claude Code session, run these two commands:

```
/plugin marketplace add DirectsalesJoe/sync-selling-skills
/plugin install sync-selling@revitk
```

Then run `/plugin`, open **Marketplaces**, choose **revitk** and select **Enable auto-update**. Claude Code is the best place to run the ABM skill, because it can start a fresh agent for each step and saves every file into your folder. The two checks need Python 3, and on a Mac the first run may ask to install Apple's developer tools, which is fine to say yes to.

## Start the ABM campaign

Say this, with your own words in the brackets:

> We sell [what you sell] into [who you sell to]. We're creating an ABM campaign. Interview me to work out who the perfect person to contact is, what the perfect time is, and what we could send or offer them that they'd find so useful they'd be happy to pay to receive it. It can come from our own data, our knowledge, our expertise, or data that's publicly available on the internet.

It interviews you first, then works out what to hand people, then finds twenty businesses at the right moment for you to check, then runs the research and the emails on three of them before doing the rest.

## The ABM campaign with no install, or on ChatGPT

Paste the prompt above, then paste the contents of [the value test](plugins/sync-selling/skills/abm-campaign/references/the-value-test.md) and [the kinds of gift](plugins/sync-selling/skills/abm-campaign/references/gift-types.md) underneath it, and ask it to follow them. For each business after that, paste [the agent briefs](plugins/sync-selling/skills/abm-campaign/agents) one at a time, each in a new chat, with the files they ask for. The checks can't run there, so ask the checker to compare every quote against the research word for word itself.

## What's inside the ABM skill

- `SKILL.md` is the run, step by step, for Claude.
- `references/the-value-test.md` is the standard everything is judged by: is this worth paying for?
- `references/gift-types.md` is the eight kinds of thing you can hand a prospect, with examples.
- `references/interview.md`, `references/triggers-and-research.md` and `references/sending.md` cover the interview, the research and the sending.
- `agents/` holds the five briefs: research, decide the gift, write, check, and read as the buyer.
- `scripts/` holds two checks that need only Python: every quote is really in its source, and no phrase marks the email as automated.

## What's inside the video editor

- `SKILL.md` is the run, step by step, for Claude.
- `scripts/setup.py` installs the two free tools into one folder, once.
- `scripts/transcribe.py` turns the recording into words with timings and finds the retakes.
- `scripts/edit.py` cuts the video, shortens the pauses, adds the captions and sets the sound level.
- `references/script-your-video.md` is how it helps you script a video before you record it.
- `references/when-it-goes-wrong.md` is what can go wrong and the fix for each.

## Want more like this?

These skills come from Sync Selling, Joe Milnes's programme for founders and their teams. If you want this, and many other AI tools to help you sell with less effort in less time, [book a call here](https://app.revitk.com/widget/bookings/syncselling-email?utm_source=github&utm_medium=readme&utm_campaign=sync-selling-skills).
