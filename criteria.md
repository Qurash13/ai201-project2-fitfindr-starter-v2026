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
I picked 4 of 5 because my search is a plain keyword match, not a model. If I
use a word that isn't in a listing (like "crewneck" when the listing says "tee"),
it can miss even though a matching item exists. My two model calls can also
fail on a try, for example if I hit the rate limit. I allow one miss for that.
I didn't go lower than 4 because this is the path I use most, and it has to
work.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
I picked 5 of 5 because this path never uses the model. My `search_listings`
is plain Python reading a fixed file, so the same impossible query gives me `[]`
every time, and my branch in `run_agent` is just an `if` on that list. Nothing
here is random, so if it fails even once, that's a bug in my code, not bad
luck.

---

## 3. The outfit is about the item search found

On a matching query, the outfit suggestion mentions the item in
`session["selected_item"]`: a word from its title (like "jacket" for "90s Track
Jacket") appears in the suggestion, in at least 4 of 5 tries.

**Why this target:**
My loop passes the item from the search to `suggest_outfit` through the
session, so I never have to type it again. If the wrong item or nothing got
passed, the outfit would talk about something else, and I'd catch that with
this check. I picked 4 of 5 because the model writes the outfit text, so it
might say "this piece" instead of the item's name even when the right item
arrived. I allow one miss for that.

> **Revised in unit 4:** On a matching query, the trace shows the same listing
> id three times: the first result `search_listings` returned, the
> `selected_item`, and the `new_item` that reached `suggest_outfit`, in 5 of 5
> tries.
>
> **Why revised:** My original check could pass during exactly the failure it
> was meant to catch. Any word from the title counted, including generic ones
> like "90s" or "vintage" that appear in many titles. If my loop had passed the
> wrong 90s item along, the outfit would still say "90s" and the try would
> pass. It also checks the model's writing instead of the session. Comparing
> ids in the trace checks the state directly, and because passing the item
> along is plain code, 5 of 5 is the right target.

---

## 4. The fit card names the platform

For 5 different items, the fit card names the item's platform (depop, thredUp
or poshmark), in at least 4 of 5 tries.

**Why this target:**
I picked 4 of 5 because the model writes the caption, so it comes out
different every time and might leave the platform out even though I put it in
my prompt. I allow one miss for that. If it missed more than once, I'd say my
caption isn't doing its job.

---

## 5. An empty wardrobe still gets outfit advice

On a matching query with an empty wardrobe (`--empty-wardrobe`), the agent
returns an outfit suggestion that is not blank and does not crash, in 5 of 5
tries.

**Why this target:**
I picked 5 of 5 even though the model writes the advice, because my code
decides what happens with an empty wardrobe. My `suggest_outfit` checks for no
items before calling the model, asks for general styling advice instead, and
returns a backup sentence if the model sends back nothing. Crashing and coming
back blank are both stopped by my own code, not by the model, so any miss would
be a bug I can fix.

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
