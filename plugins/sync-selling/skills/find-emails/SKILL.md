---
name: find-emails
description: >
  Find a person's work email, check an email works, find who holds a role at a company,
  list the people at a company, or look up a company, using the Lead Magic credits that
  come with Sync Selling. Needs the member's Sync Selling access code once. Triggers on
  "find their email", "what's the email for", "is this email real", "who's the managing
  director at", "who works at", "find the decision maker", "how many credits have I got",
  and whenever the ABM campaign skill needs an address.
---

# Find emails with your Sync Selling credits

Sync Selling members get Lead Magic credits on Revitk's account. This skill spends them for the member: it finds work emails, checks them, finds the person in a role, and looks up companies. Every lookup goes through `scripts/lookup.py`, which needs only Python 3.

## The first time

1. Ask the member for their Sync Selling access code. It starts `ssl_`. If they don't have one, tell them to reply to any Sync Selling email and ask for it, and carry on with whatever other email tool they have.
2. Run `python3 scripts/lookup.py setup <their code>`. It checks the code, saves it on their computer and says how many credits they have.
3. Never repeat the code back in the chat, write it into a file in their folder, or put it in a message. It's theirs, and anyone holding it can spend their credits.

## Looking people up

Run one lookup at a time, never several at once, so every credit is counted.

| What they want | Run | Usually costs |
|---|---|---|
| A person's work email | `python3 scripts/lookup.py email --first Jane --last Smith --domain example.co.uk` | 1 credit when found, nothing when not |
| To know an address works | `python3 scripts/lookup.py check-email someone@example.co.uk` | a quarter of a credit |
| Who holds a role | `python3 scripts/lookup.py role --title "Managing Director" --domain example.co.uk` | 2 credits when found |
| Who works at a company | `python3 scripts/lookup.py people --domain example.co.uk` | under 1 credit |
| What a company does, its size | `python3 scripts/lookup.py company --domain example.co.uk` | 1 credit |
| A mobile number | `python3 scripts/lookup.py mobile --profile-url https://www.linkedin.com/in/someone` | up to 5 credits |
| What they have left | `python3 scripts/lookup.py balance` | free |

Ask before a mobile lookup, because one costs as much as five emails.

Use the company's own web domain (`example.co.uk`), never a LinkedIn or Companies House address. When you don't know the domain, find the company's website first.

After each lookup, tell the member what was found and how many credits are left, which the script prints on its last line.

## Reading what comes back

- `status: valid` means Lead Magic found the address and checked it accepts mail. Use it.
- `catch_all` means the company's mail server accepts everything, so the address can't be proven. Mark it for the member to decide, and never send a campaign to it unchecked.
- `not_found` means no address could be found. That cost nothing. Try the role lookup, or another senior person at the company.
- When two sources give the same address, mark it confident. Where only this one does, say so.

## When it says no

- "That access code is not recognised": the code was mistyped or has been switched off. Ask the member to check it, and to reply to any Sync Selling email if it still fails.
- "You have used ... credits": they've run out. Tell them to reply to any Sync Selling email for a top-up, and carry on with whatever other email tool they have.
- "Couldn't reach the lookup service": their internet dropped or the service is down. Try once more in a minute, then stop and say so.

## Inside the ABM campaign

When the ABM campaign skill reaches "find their email", use this skill if the member has a code. Record where each address came from in the fact table, because many countries' privacy laws expect them to be able to say.
