# Sync Selling skills for Claude

These are the Claude skills from the Sync Selling sessions, so you can run what Joe shows on the calls in your own business. Add them to Claude once and every improvement we make, and every new skill we add, reaches you without you doing anything.

The first one is **ABM campaign**, from the Deal Clinic on 10 November 2026. It finds the right person at the right business at the right moment, works out something you could send them that's so useful they'd pay to receive it, and writes the emails. Claude researches each business, a separate agent checks every fact, and another reads each email as the buyer would before you see it. Nothing sends until you've read it.

It's a first version. If something trips you up, reply to any Sync Selling email and tell us, and the fix will reach everyone.

## Add it to the Claude desktop app

1. Open Claude and click **Customize** in the sidebar, then **Plugins**. <!-- copycheck: allow us-ize-verbs -->
2. Click **Add marketplace** and paste `DirectsalesJoe/sync-selling-skills`.
3. Find **Sync Selling** in the list and click **Install**.
4. On the marketplace, turn on **Sync automatically**, so changes come through by themselves.

The skills then work in Cowork and in chat. Switch on web search, because the research needs it.

## Add it to Claude Code

In a Claude Code session, run these two commands:

```
/plugin marketplace add DirectsalesJoe/sync-selling-skills
/plugin install sync-selling@revitk
```

Then run `/plugin`, open **Marketplaces**, choose **revitk** and select **Enable auto-update**. Claude Code is the best place to run the ABM skill, because it can start a fresh agent for each step and saves every file into your folder. The two checks need Python 3, and on a Mac the first run may ask to install Apple's developer tools, which is fine to say yes to.

## Start it

Say this, with your own words in the brackets:

> We sell [what you sell] into [who you sell to]. We're creating an ABM campaign. Interview me to work out who the perfect person to contact is, what the perfect time is, and what we could send or offer them that they'd find so useful they'd be happy to pay to receive it. It can come from our own data, our knowledge, our expertise, or data that's publicly available on the internet.

It interviews you first, then works out what to hand people, then finds twenty businesses at the right moment for you to check, then runs the research and the emails on three of them before doing the rest.

## No install, or on ChatGPT

Paste the prompt above, then paste the contents of [the value test](plugins/sync-selling/skills/abm-campaign/references/the-value-test.md) and [the kinds of gift](plugins/sync-selling/skills/abm-campaign/references/gift-types.md) underneath it, and ask it to follow them. For each business after that, paste [the agent briefs](plugins/sync-selling/skills/abm-campaign/agents) one at a time, each in a new chat, with the files they ask for. The checks can't run there, so ask the checker to compare every quote against the research word for word itself.

## What's inside the ABM skill

- `SKILL.md` is the run, step by step, for Claude.
- `references/the-value-test.md` is the standard everything is judged by: is this worth paying for?
- `references/gift-types.md` is the eight kinds of thing you can hand a prospect, with examples.
- `references/interview.md`, `references/triggers-and-research.md` and `references/sending.md` cover the interview, the research and the sending.
- `agents/` holds the five briefs: research, decide the gift, write, check, and read as the buyer.
- `scripts/` holds two checks that need only Python: every quote is really in its source, and no phrase marks the email as automated.
