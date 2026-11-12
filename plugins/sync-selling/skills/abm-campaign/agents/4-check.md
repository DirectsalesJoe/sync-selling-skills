# Agent 4: check the email

Run the two scripts first, then give a fresh agent this brief and nothing else. The checker is never the agent that wrote the email.

From the campaign folder, where `<skill>` is the path to this skill's folder:

```bash
python3 <skill>/scripts/check_quotes.py accounts/<company>/email.md accounts/<company>/pack.md proof-bank.md
python3 <skill>/scripts/check_quotes.py accounts/<company>/decision.md accounts/<company>/pack.md proof-bank.md
python3 <skill>/scripts/blocklist.py accounts/<company>/email.md
```

Run the first one on every text file in `accounts/<company>/gift/` as well. Every quote that isn't word for word in its source is a fail, and every fail on the block list is fixed before the agent reads it.

---

You check one business's gift and emails before they go. You check value first, then truth, then the writing. You don't rewrite anything. You name each fault, the line it's in, and what's wrong.

Read these, in this order, and nothing else:
1. The value test: [path to references/the-value-test.md]
2. The value decision, including the gift: [path to accounts/<company>/decision.md]
3. The gift as made, if it's a separate file: [paths in accounts/<company>/gift/, or "given in the email"]
4. The emails: [path to accounts/<company>/email.md]
5. The pack: [path to accounts/<company>/pack.md]
6. The proof bank: [path to proof-bank.md]
7. What the scripts reported: [paste the output]

Answer in this order, and write the answers to [accounts/<company>/check.md].

**1. The gift.** Read the gift itself as the person will receive it, never the decision's description of it. Is it as valuable as the decision says? Run the value test's first five tests on it with your own score, including the price, and say where you disagree with the decision. Is every fact in it in the pack, word for word where quoted? A gift that fails here sends the account back to the value decision, whatever the email is like.

**2. Value in the email.** Run the value test's eight tests on email 1 as written, which can differ from the decision. Did the gift survive the writing, or did it get buried under proof, context or politeness? Is the gift the biggest thing in the email? Could the reader act on it without replying? Is the ask small? For each of the eight, pass or fail with the line.

**3. Truth.** Go through email 1 sentence by sentence.
- Every fact about the business: which pack row is it, and does the row say exactly this? A fact with no row is a fail.
- Every claim about the sender: which proof bank line? Is it worded exactly as the line, or stretched? A stretched claim is a fail.
- Every number: does it appear in the pack or the proof bank exactly? A rounded or new number is a fail.
- Every inference about their business: is it softened ("often", "normally", "might")? An inference stated as fact is a fail.
- Is the trigger still live, according to the pack's check date? If the pack is more than a week old, say the trigger needs checking again before sending.

**4. Their words.** Does the email use their terms for their people, customers and product, where the pack has them? Name any place it uses a generic word where theirs exists.

**5. The writing.** Name any line that's about the sender when it could be about them, any sentence a busy reader would trip on, any phrase that sounds like every other cold email, and anything said twice.

**6. The follow-ups.** Does each one carry what the decision's follow-ups section gives it, and nothing invented? Does any say "just following up"? Does email 4 ask who else deals with it? Is the sign-off complete, with the opt-out line?

End with one line: **Ready to send / Fix and recheck / Back to the value decision.** Fix and recheck means one rewrite and one more check. Back to the value decision means the gift itself failed, and a better sentence won't fix it.

If an answer is "nothing wrong", say so in one line. Do not rewrite anything.
