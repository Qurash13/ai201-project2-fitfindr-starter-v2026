# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

I built FitFindr to help with secondhand shopping. I type what I'm looking for
in plain language, like `vintage graphic tee under $30` or `90s track jacket in
size M`. My agent searches 40 thrift listings from Depop, thredUp and Poshmark
for the best match in my size and price. Then it suggests one or two outfits
that pair the find with clothes already in my wardrobe, and writes a short
caption I could post about it. If nothing matches, it stops and tells me what to
change: the price, the size, or the words I used.

---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** My search goes through the 40 listings in `data/listings.json`. It drops any listing over the price ceiling or in the wrong size. It scores the rest by how many words from the description appear in each listing's title, description, style tags, category and colors, and drops anything that scores zero. No model call.
- **Inputs:** `description` (str): keywords like `"vintage graphic tee"`. `size` (str or None): a size like `"M"`, or None to skip the size filter. `max_price` (float or None): highest price allowed, inclusive, or None to skip the price filter.
- **Returns:** A `list[dict]` of up to 10 listing dicts (`config.SEARCH_RESULT_LIMIT`), best match first. Each dict is a full listing with `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand` (often None) and `platform`.
  **Size rule (my decision):** the listing's size is split on `/`, spaces and parentheses into whole tokens, and the requested size has to equal one of those tokens, ignoring case. So `"M"` matches `S/M` and `M/L`, but `"S"` does not match `US 9` or `XL (oversized)`, and `"L"` does not match `XL`. I decided listings sized `One Size` match any size, because they're meant to fit everyone.
- **When it has nothing:** Returns an empty list `[]`. It never returns None and never raises an exception.

### `suggest_outfit`

- **What it does:** Asks the model for one or two outfits built around the new item. When the wardrobe has items, the outfits name pieces I already own.
- **Inputs:** `new_item` (dict): one listing dict, the item found by search. `wardrobe` (dict): a dict with an `items` key holding a list of wardrobe item dicts (`name`, `category`, `colors`, `style_tags`, `notes`). The list may be empty.
- **Returns:** A non-empty `str` of outfit suggestions in plain text. With a wardrobe, each outfit names specific wardrobe pieces by their `name`.
- **When it has nothing:** I decided that if `wardrobe["items"]` is empty, it returns general styling advice for the item (what kinds of pieces and colors go with it) instead of raising or returning `""`.

### `create_fit_card`

- **What it does:** Asks the model for a short social-media-style caption about the find and the outfit. It should read like a real post, not a product description.
- **Inputs:** `outfit` (str): the text `suggest_outfit` returned. `new_item` (dict): the listing dict for the item.
- **Returns:** A `str` caption of 2–4 sentences. It names the item, mentions the price and the platform once each, and describes the vibe. It leaves the brand out when `brand` is None.
- **When it has nothing:** If `outfit` is empty or only whitespace, it returns the message `"Can't write a fit card without an outfit suggestion."` without calling the model.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, my loop puts a
message in `session["error"]` that says what I searched for and what to change
(raise the price limit, drop the size, or use broader words), and stops.
`suggest_outfit` and `create_fit_card` are never called. Otherwise, my loop puts
the first result in `session["selected_item"]` and goes to `suggest_outfit`,
then `create_fit_card`.

**Where it lives:** `agent.py::run_agent`

My loop is a `while` loop over a `next_step` value (`"search"` → `"suggest"` →
`"fit_card"` → `"done"`). After each step, it looks at what that step put in the
session to choose the next one. I call `trace.check_iterations()` on every pass.

**How the query is parsed:** I used regex, in `agent.py::parse_query`. One pattern
finds a price ceiling (`under $30`, `$40`). Another finds a size (`size M`,
`in size M`, `size 8`, `size US 8`, `in an S`). Each is cut out of the query,
and whatever words are left become the search description. For example,
`designer ballgown size XXS under $5` becomes
`{"description": "designer ballgown", "size": "XXS", "max_price": 5.0}`.

**What moves through the session:**
1. `query`: what I typed
2. `parsed`: description, size and max_price from `parse_query`
3. `search_results`: everything `search_listings` returned
4. `selected_item`: `search_results[0]`, read back out of the session and passed to `suggest_outfit`
5. `outfit_suggestion`: what `suggest_outfit` returned, read back out and passed to `create_fit_card` along with `selected_item`
6. `fit_card`: the caption
7. `error`: set only when the run stopped early. In that case 4–6 stay `None`.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Hey there! That Y2K baby tee is such a cute find, especially with the pink and purple butterfly print, and eighteen bucks is a total steal for Depop. It is going to look amazing in your closet! 

For your first outfit, pair the tee with your baggy straight-leg jeans, throw on the black cropped zip hoodie just in case it gets chilly, and finish it off with your chunky white sneakers for the ultimate nostalgic vibe. 

For look number two, tuck the baby tee into your wide-leg khaki trousers, add the brown leather belt to pull it together, and wear your black combat boots to add a cool, edgy contrast to the sweet cottagecore print. Have so much fun styling it!

  Fit card: Just scored this dreamy butterfly baby tee and I am obsessed with the pink and purple print. It’s up on my depop right now for just $18, and you can totally style it with baggy denim and chunky sneakers for that ultimate Y2K nostalgia. Grab it before it's gone and get ready to live out all your best 2000s fashion fantasies!

0 model calls this session, 2 served from cache
```

And the empty-search branch, which stops before `suggest_outfit`:

```
$ python app.py ask 'designer ballgown size XXS under $5'

  Nothing matched 'designer ballgown' in size XXS under $5. Try: raise your price limit (listings start around $12); or drop the size; or use broader words like 'jacket', 'tee' or 'jeans'.

0 model calls this session
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; r = search_listings('graphic tee', max_price=30); print(len(r), 'results'); [print(l['id'], l['title'], l['size'], l['price'], l['platform']) for l in r]"
6 results
lst_002 Y2K Baby Tee — Butterfly Print S/M 18.0 depop
lst_006 Graphic Tee — 2003 Tour Bootleg Style L 24.0 depop
lst_033 Vintage Band Tee — Faded Grey L 19.0 depop
lst_015 Vintage Graphic Hoodie — Faded Black L 26.0 depop
lst_017 Mesh Long-Sleeve Top — Black S/M 15.0 depop
lst_011 Low-Rise Cargo Pants — Khaki W29 27.0 poshmark

$ python -c "from tools import search_listings; print(search_listings('designer ballgown', size='XXS', max_price=5))"
[]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
Hey there! These vintage 501s are an absolute thrift store holy grail, and that medium wash is going to be so versatile in your closet. 

Outfit one: Keep it effortlessly cool and casual by pairing the new jeans with your white ribbed tank top, layered under the oversized grey crewneck sweatshirt. Add the chunky white sneakers and the black crossbody bag for a comfy, classic 90s streetwear vibe. 

Outfit two: Let's lean into that vintage edge! Tuck the white ribbed tank top into the 501s, cinch them with your brown leather belt, and throw on the vintage black denim jacket. Finish this look off with your black combat boots for an effortlessly cool, tough-girl aesthetic. You will wear these constantly!
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
Nothing beats the effortless look of a broken-in medium wash, especially when paired with crisp white sneakers for that ultimate effortless streetwear vibe. These vintage Levi's 501s have the absolute best classic fit and are ready for a new home. Grab them for just $38 over on my depop before someone else snags them.
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* I asked Claude to run `app.py fields` and `app.py listings` and explain the data. Then I said I didn't understand the warning about sizes.
- *What came back:* A table using real sizes from the file. It showed that checking whether `"s"` appears in the size string matches `US 9` (a shoe), `One Size` and `XL (oversized)`, so a search for a small tee would return shoes and an XL shirt.
- *What I changed:* I chose whole-token size matching (split `S/M` into `S` and `M`, then compare whole pieces). I also decided `One Size` items match any size. I wrote that rule into my Tool Inventory before any code existed, and my `search_listings` follows it.

**Moment 2**

- *What I asked for:* I was running behind, so I asked Claude to build my tools and my loop from my Tool Inventory and run each one from the terminal.
- *What came back:* The first version of `parse_query` turned `90s track jacket in size M` into the description `90s track jacket in`. It removed `size M` but left the word "in" behind.
- *What I changed:* I had the size pattern also remove an optional `in` before `size`, so the description now comes out as `90s track jacket`. I also checked that the session carried the item through: the search's first result and `selected_item` were both `lst_004`.

**Moment 3: writing the criteria**

- *What I asked for:* Claude first drafted criteria 3–5 for me. I didn't
  understand them, and at first I thought "5 of 5" meant the number of search
  results, so I asked it to explain how to write a criterion.
- *What came back:* "X of 5" means running the same test five times and
  counting passes, and a criterion is a yes/no check plus how many of five must
  pass (5 for plain code, usually 4 when the model writes the output).
- *What I changed:* I replaced all three drafts with my own picks: the fit card
  names the platform (4 of 5); the outfit mentions the item search found
  (4 of 5); an empty wardrobe still gets advice (5 of 5).

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
