# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
My search is a plain keyword match, not a model, so a query phrased with words
that aren't in a listing ("crewneck" when the listing says "tee") can miss even
though a matching item exists. The two model calls can also fail on a given try
(rate limit or a bad response). One miss in five allows for that. Anything below
4 would mean the normal path is unreliable, which is the one thing a user sees.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
This path never touches the model. `search_listings` is plain Python over a fixed
file, so the same impossible query returns `[]` every time, and the branch in
`run_agent` is an `if` on that list. Nothing in it is random, so a single failure
would be a real bug in my code, not bad luck. That's why it has to be 5 of 5.

---

## 3. The outfit is about the item search found

On a matching query, the outfit suggestion mentions the item in
`session["selected_item"]`: a word from its title (like "jacket" for "90s Track
Jacket") appears in the suggestion, in at least 4 of 5 tries.

**Why this target:**
The loop passes the item from the search to `suggest_outfit` through the
session, so the user never types it again. If the wrong item or nothing got
passed, the outfit would talk about something else, and this check would catch
it. The model writes the outfit text, though, so it might say "this piece"
instead of the item's name even when the right item arrived. One miss out of 5
gives it room for that.

---

## 4. The fit card names the platform

For 5 different items, the fit card names the item's platform (depop, thredUp
or poshmark), in at least 4 of 5 tries.

**Why this target:**
The caption is written by the model, so it comes out different every time and
might leave the platform out even though I put it in the prompt. One miss out
of 5 gives it room for that. If it missed more than once, the caption isn't
doing its job.

---

## 5. An empty wardrobe still gets outfit advice

On a matching query with an empty wardrobe (`--empty-wardrobe`), the agent
returns an outfit suggestion that is not blank and does not crash, in 5 of 5
tries.

**Why this target:**
The model writes the advice, but my code decides what happens with an empty
wardrobe: `suggest_outfit` checks for no items before calling the model, asks
for general styling advice instead, and returns a backup sentence if the model
sends back nothing. Crashing and coming back blank are both ruled out by plain
code, not by the model, so any miss would be a bug I can fix. That's why it's
5 of 5 and not 4.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
