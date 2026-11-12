# Sending, the follow-ups and the replies

## The number decides the channel

The sample told you how many businesses hit the moment each week. That number decides how the emails go.

- **Fewer than about twenty people to reach:** send everything from your own account. Email from your own inbox, a LinkedIn connection or message, and a phone call. At this volume each message deserves your own hands on it, and your own inbox is the most trusted address you've got.
- **More than ten to twenty emails a day:** use a sending tool (Instantly, Smartlead or similar) with several mailboxes on separate, warmed-up domains, so your main address never carries the risk. Set it up and warm the mailboxes for two or three weeks before the first send.

From your own inbox, keep it under ten to fifteen new emails a day, sent during working hours, with a random gap of several minutes between each. A burst of identical-looking emails at the same second is what spam filters look for.

If you send through Gmail from a script or an AI connector, check that your links arrive exactly as you wrote them. Some connectors rewrite every link into a redirect, and redirected links are a strong spam signal.

## The cadence

Four emails, in the same thread, each one shorter than the last.

1. **The email.** The gift, given or offered, and one small ask.
2. **Three days later, a follow-up.** One or two lines in the same thread. Bring the gift back to the top ("In case the sheet got buried, it's attached again") or add one new useful thing. Never "just checking in".
3. **Three days after that, another follow-up.** Ask for a decision either way. A no is an answer too, and it closes the loop: "Would this be useful, or is it not something you want to look at right now?"
4. **Then ask who else deals with it.** "If this isn't yours to look at, who would be the best person?" Some of the best replies come from this one.

Where you've found a second senior person at the same business, they can get their own short email the day after the first: "I wrote to Amy yesterday about [the gift], and thought it worth you seeing too." Only send it the next day, or "yesterday" isn't true.

The moment anyone at the business replies, every email to that business stops. An out-of-office isn't a reply. A bounce pauses everything until someone has looked at why.

## The law, and the line at the bottom

Check the rules where you are and where they are. In the UK, writing to someone at their business address about something relevant to their job is allowed, as long as you offer a way to opt out from the first email and can say where you got their details. Under the signature, in small type, add one line saying why you wrote and that they only need to say if they'd rather you didn't write again, with a link to your privacy notice.

Anyone who opts out goes on a do-not-contact list that every future campaign reads first.

## Replies

Nothing goes back to a prospect without the user reading it.

- **In your inbox.** Connect your inbox to Claude. When a reply lands, Claude reads it and the thread, drafts the answer, and leaves it in your drafts. You read it and press send.
- **In a team chat, if you have one set up.** The reply arrives in a channel with the drafted answer and three choices: send, edit or redraft. It goes back in their thread only when someone presses send. (This takes more setting up, so start with the inbox version.)

Tag every reply: interested, not now, no, wrong person, or opt-out. The tags tell you, after a few weeks, which gift and which moment are working.

When someone's interested, Joe's rule: "The best way to convert that is to pick up the phone." Offer two real times, or ring them if you have the number. Send the thing you offered straight away, whatever else happens.

## Keep a tracker

One file in the campaign folder, `tracker.csv`, one row per person:

```
company,person,role,email,address_confidence,trigger,trigger_date,gift,email_1_sent,follow_up_1,follow_up_2,ask_who_else,replied,reply_tag,notes
```

Read it every week. Change one thing at a time (the gift, the moment, the subject line), and only when at least twenty sends point the same way.
