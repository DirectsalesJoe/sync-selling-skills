---
name: abm-campaign
description: >
  Run an account-based outreach campaign end to end, built around what you hand each
  prospect. Interviews the user about what they sell and to whom, works out the right
  person, the right moment and, above all, a gift so useful the prospect would pay to
  receive it; then finds a sample of businesses at that moment, researches each one,
  decides its gift, writes the emails from that decision, checks every fact and quote,
  and reads each email as the buyer before the user approves it. Triggers on "ABM
  campaign", "account-based", "who should I reach out to and when", "permissionless
  value proposition", "PVP", "what could we send them that's actually useful", "find
  businesses at the right moment and write to them", "research these accounts and
  write to them". Do NOT use for a high-volume cold email slate with no research per
  account, for replying to someone already in conversation, or for nurture emails to an
  existing list.
---

# Sync Selling ABM

This skill runs an account-based campaign: a small number of businesses, each researched, each sent something useful before they've agreed to anything.

The aim, in Joe's words from the Sync Selling session: "Find the right person at the right business, and reach out at the right time." And the question behind it: "If I had a full day to research on the internet, who would be the perfect client, at the perfect time, for me to approach? How would I do it?" Nobody has that full day for every prospect. Claude has.

Everything turns on one thing, what you hand them. The list, the research and the writing all exist to deliver it. A message that carries something they'd pay for gets read. A message that carries nothing doesn't, however well it's written. So most of this skill's effort, and every one of its checks, goes on the value of the gift.

Everything the skill reads is in this folder.

## Before you start

Read `references/the-value-test.md` in full, every run. It's the standard every step is judged by.

Ask the user which folder to work in, and make a campaign folder inside it:

```
abm/<campaign-name>/
  campaign-brief.md        the interview's answers
  proof-bank.md            the only things the emails may claim about the sender
  value-bank.md            every candidate gift, scored, and the ones chosen
  sample.md                the first twenty businesses, marked right or wrong
  accounts/<company>/
    pack.md                research, every fact with its source
    decision.md            the gift for this business, and send or don't
    gift/                  anything made for them (a sheet, a mock-up, a video link)
    email.md               the four emails
    check.md               the checker's findings
    read.md                the buyer's read
  review.md                the week's emails in one place for the user
  tracker.csv              every send and reply
  do-not-contact.csv       read before every send
```

What you need: web search and the ability to read web pages. An email-finding tool helps, and any will do. A sending tool only matters above ten to twenty emails a day. Python 3 runs the two checks in `scripts/`, with nothing to install. Run them from the campaign folder, giving the path to this skill's folder, the one this file sits in, written `<skill>` below.

Steps 4 to 8 each run on a **fresh agent**, given only its brief from `agents/` and the files the brief names. In Claude Code, use the Agent tool. Where there are no subagents, start a new chat for each step and paste the brief and the files. The reason is simple: the agent that checks an email or reads it as the buyer must never be the one that wrote it, because a writer can't see what's missing from its own work, and a writer handed the whole research pile lays out every fact instead of handing over the gift.

## The run

### 1. The interview

Follow `references/interview.md`. One question at a time. Most of the time goes on what the user knows that their buyers don't, because that's where the gift comes from. It ends with `campaign-brief.md` and `proof-bank.md`, which the user corrects before you go on.

### 2. The value workshop

This is the step that decides whether the campaign works, so give it the most thought.

1. Read the brief's "what we know that they don't" section and `references/gift-types.md`.
2. Generate at least ten candidate gifts, spread across the eight kinds. For each: what it is in one sentence, what it's built from, why this buyer at this moment would want it, and what it would cost to make per account.
3. Score every candidate on the scorecard in the value test. Tests one to four can be scored on a description; kill every candidate that fails one. Be hard: most of the ten should die, and that's the workshop doing its job.
4. Take the best two or three. For each, make one real example for a business you can find right now at the moment, using public sources, and score test five (specific to them) on that example. A gift that looks good in a description and thin on a real business is thin.
5. Put the examples in front of the user with the scorecard, and ask which they'd want to receive if they were the buyer.
6. Ask the user to show the chosen example to one real buyer, a customer or someone who's sat in the buyer's chair, before the first email sends, and to tell them they didn't write it so they can be honest. One real buyer saying "I'd want that" outweighs every test in this skill. If the user decides to skip it, write that in `value-bank.md` and say it again in the review, because it's the biggest risk left in the campaign.
7. Write `value-bank.md`: every candidate, its score, the ones killed and why, the one or two the user chose, and what the real buyer said.

If nothing passes, say so plainly and go back to part 4 of the interview with sharper questions. Never carry a weak gift forward hoping the writing will save it.

### 3. The sample

Follow `references/triggers-and-research.md`. Find twenty businesses at the moment, each with its trigger, date and source. The user marks each one right or wrong. Write the false positives into the brief. Count how many hit the moment each week or month, which decides how many emails go and which channel they go through (`references/sending.md`). Write `sample.md`.

Then write the full run, steps 4 to 8, for three businesses from the sample before doing any more. If the gift or the opening line is weak with real businesses in it, fix that now.

Once the user is happy with those three, run the rest of the sample, then search for new businesses at the moment the same way each week. A batch is the businesses that go through steps 4 to 8 together, usually one week's.

### 4. Research each business

Fresh agent, `agents/1-research.md`, one per business. Writes `accounts/<company>/pack.md`: the trigger checked live, the people and their addresses with how sure we are, a fact table with every fact sourced, the raw material for the gift, and their own words quoted exactly.

### 5. Decide the gift

Fresh agent, `agents/2-value.md`. It picks the gift for this business, makes it specific from the pack, scores it, chooses at most two proof lines and the ask, and lays out the email's parts in order. It writes no email. **If the gift doesn't pass for this business, the business gets no email.** That's the most important rule in the skill.

If the decision says something has to be made before sending (a sheet, a document, a list), make it now, from the decision and the pack only, and save it in `accounts/<company>/gift/`. If it needs the user (a video they record, a mock-up in their own design tool), put it on the review as "to make" and hold that email. An email that offers something that doesn't exist yet doesn't send.

### 6. Write the emails

Fresh agent, `agents/3-write.md`. It sees the decision, the proof bank and only the pack rows the decision names. It writes email 1, two follow-ups, the ask for who else deals with it, and a second-contact email if the decision names one.

### 7. Check

Run the scripts, then a fresh agent with `agents/4-check.md`:

```bash
python3 <skill>/scripts/check_quotes.py accounts/<company>/email.md accounts/<company>/pack.md proof-bank.md
python3 <skill>/scripts/check_quotes.py accounts/<company>/decision.md accounts/<company>/pack.md proof-bank.md
python3 <skill>/scripts/blocklist.py accounts/<company>/email.md
```

Run the first check on every text file in `gift/` too, because the gift is what they'll judge you on. The checker reads the gift as well as the email, and it reads value first, then truth, then the writing.

### 8. Read as the buyer

Fresh agent, `agents/5-read.md`, playing the named person at their desk. Its first question is whether they'd pay for what's in the email, and once it has read the email it opens the gift and answers that question again.

### After the check and the read

- If either says the gift failed, go back to step 5 for that business, never to the writer. The fresh value agent gets the earlier decision and the findings, and either proposes a different gift or says no. If the second gift fails too, that business gets no email.
- Otherwise, one rewrite: a fresh writer from `agents/3-write.md`, given the previous email and the checker's findings on value, truth and the writing, plus the reader's points about where they had to work something out or noticed the writing. Then the scripts and the checker once more. One rewrite only, because each extra round makes the email longer and blander.
- Anything the reader asked for that the pack and proof bank don't hold goes to the user as a question, never into the email.

### 9. The user reads every email

Put every email for the batch into `review.md`, business by business: the gift itself (or a link to it in `gift/`), the email, the price the buyer would pay, how sure we are of the address, whether the trigger is still live, anything still to make, and the checker's and reader's one-line verdicts. Say whether the real-buyer test from step 2 was done. Nothing sends until the user has read it and said yes. If a word changes after the yes, that email waits for another yes.

### 10. Send, follow up, handle replies

Follow `references/sending.md`: the channel the number decides, the four-email cadence three days apart, everything stopping the moment anyone at the business replies, the opt-out line, replies drafted into the user's inbox and never sent without them, and the tracker updated as you go.

## The rules that keep it worth reading and honest

- **No gift, no email.** A business whose gift fails the value test gets nothing. Sending nothing costs nothing. Sending an empty email costs the user's name with that business.
- **The value is big and the ask is very small.** Joe's rule: "you want to make the value of the lead magnet very big, but the ask very, very small." One line, answerable in a word.
- **Given beats offered, and offered beats asking.** Give the gift in the email where it fits. Where it doesn't, it already exists and is offered in the past tense.
- **Nothing about the business that isn't in its pack with a source.** Nothing about the sender that isn't in the proof bank. No invented or rounded number.
- **Every quote is word for word**, and a script checks it.
- **The moment is stated as fact, and what you infer from it is softened.** The opener is about their situation, never "I saw you're hiring" or a congratulation.
- **Decide, write, check and read are separate agents.**
- **Nothing sends without the user reading it.**
- **Three by hand before the rest.** Run the whole thing on three businesses before scaling, and change one thing at a time once it's running.
- **UK English where the user is in the UK, and no em dashes**, which read as machine-written to a lot of buyers now.
