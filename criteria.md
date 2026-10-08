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

## 3. The item search found is the item the next two tools receive

On a matching query, the listing that reaches `suggest_outfit` and
`create_fit_card` has the same `id` as `session["search_results"][0]` and
`session["selected_item"]`, and the user is never asked to type the item
again — in 5 of 5 tries.

**Why this target:**
Passing the item along is pure code: the loop reads `selected_item` out of the
session and hands it to the next tool. There is no model involved in that step,
so the ids either match every time or my session handling is broken. I'm
checking the `id` rather than the title because two listings could share
similar titles, but ids are unique.



---

## 4. The fit card is a postable caption with the facts right

For 5 different matching items, each fit card is 2–4 sentences, contains the
item's exact price (e.g. `$24`) and its platform name, and never contains the
words `None` or `null` — at least 4 of 5 cards pass all four checks.

**Why this target:**
The caption comes from the model, so its wording changes every run and I can't
control it fully. I can put the price and platform in the prompt, but the model
may still leave one out or run long, so I allow one miss. The `None` check is
there because 32 of the 40 listings have no brand: if my prompt fills in a
missing brand, the caption would say "None", and I want to catch that.



---

## 5. Search respects the size and price the user asked for

For 5 queries that include a size and/or a price ceiling, every listing in
`session["search_results"]` costs no more than the ceiling and has the
requested size as a whole size token (or is One Size) — 5 of 5 queries, with
zero wrong listings across all of them.

**Why this target:**
The sizes in the data come in four different formats (`S/M`, `W30 L30`,
`US 9`, `One Size`), and a simple substring test returns shoes when someone asks
for a small (`"s" in "us 9"`). This filter is deterministic code, so one wrong
listing is a bug I can find and fix, not model randomness. A user who asked for
"under $30" and sees a $45 item stops trusting every other result.



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
