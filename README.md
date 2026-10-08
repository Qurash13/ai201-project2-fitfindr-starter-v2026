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

**Moment 4 (unit 4): diagnosing a run where everything passed**

- *What I asked for:* I asked Claude to run my test, score each try against my
  criteria exactly as written, and diagnose every miss.
- *What came back:* Every criterion was 5/5. Instead of stopping there, it
  read all 40 fit cards and found 32 written as if I were selling the item
  ("on my depop", "grab this before it's gone"). It traced that to my prompt
  never saying who was posting.
- *What I changed:* I treated that as my one improvement. I rewrote the
  `create_fit_card` prompt so the poster is the buyer, re-ran the whole test,
  and seller-voice cards went from 32/40 to 0/40. I also revised criterion 3
  (original kept), because "any title word" could pass even if the wrong item
  got passed along.

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

My before run is `results/run_2026-10-08_0149_before.md`, produced by `run_eval.py::main` running
`agent.py::run_agent` 5 times per scenario with caching off (80 model calls).

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before `suggest_outfit` | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Outfit mentions the item search found | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card names the platform (5 different items) | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Empty wardrobe still gets outfit advice | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

For criterion 4, my criterion says "5 different items", so I ran five scenarios
that each land on a different listing (lst_002, lst_004, lst_003, lst_005,
lst_019, across depop, poshmark and thredUp). Try *k* in my table is try 1 of
item *k*. I also ran every item 5 times, and all 25 of those cards named the
right platform too.

**Real output from one try of each**, from `results/` (written by
`run_eval.py::main`, produced by `agent.py::run_agent`):

Criterion 1, `vintage graphic tee under $30`, try 1. All three tools ran:

```
- stopped early: no
- selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
Fit card: Obsessed with this nostalgic butterfly baby tee and I can not believe it is only $18 on my depop right now! It gives the ultimate 2000s pop star off-duty energy when you style it with baggy dark wash jeans and a cropped hoodie. If you want to lean into a softer cottagecore vibe instead, just tuck it into khaki trousers with combat boots for the cutest contrast.
```

Criterion 2, `designer ballgown size XXS under $5`, try 1. It stopped with no outfit or fit card:

```
- stopped early: yes — Nothing matched 'designer ballgown' in size XXS under $5. Try: raise your price limit (listings start around $12); or drop the size; or use broader words like 'jacket', 'tee' or 'jeans'.
- selected_item: (none)
- search_results: 0
```

Criterion 3, `silk slip dress under $40`, try 1. "silk slip dress" from the title is in the outfit:

```
- selected_item: 90s Silk Slip Dress — Floral, Midi Length ($30.0, depop)
Outfit suggestion: Hey friend! Oh, you totally need to grab that 90s silk slip dress. It is such a versatile piece! Since it is listed under bottoms, wait—even if it is a dress, we can totally style it like a dreamy skirt or layer it up. 
```

Criterion 4, item 3 (`oversized flannel shirt`), try 1. "thredUp" is in the card:

```
- selected_item: Oversized Flannel Shirt — Plaid Red/Black ($22.0, thredUp)
Fit card: Score this vintage Woolrich red and black flannel on thredUp for just $22 and instantly nail that effortless, slouchy streetwear vibe. Layer it over a grey crewneck with wide-leg khakis and chunky sneakers for the ultimate cozy fit, or tie it around your waist with combat boots for a total grunge throwback. Trust me, you will live in this oversized XL piece all season long!
```

Criterion 5, `denim jacket under $50` with an empty wardrobe, try 1. It gave advice, with no crash:

```
- selected_item: Denim Jacket — Light Wash, Cropped ($42.0, poshmark)
Outfit suggestion: (You haven't saved any clothes yet, so these are general ideas. Add your wardrobe to get outfits built from what you own.)

Hey there! You are going to get so much wear out of this Wrangler jacket. Since it's a cropped light wash, it has that effortless vintage cool factor. 
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
| 1 | Matching query completes all three tools | 4 of 5 | MET (5/5) | Every try had `stopped early: no` plus an outfit and a fit card in the log |
| 2 | Impossible query stops before `suggest_outfit` | 5 of 5 | MET (5/5) | Every try stopped after step 2 of the trace, with no outfit or fit card, and the message has a "Try:" list of what to change |
| 3 | Outfit mentions the item search found | 4 of 5 | MET (5/5) | I checked each outfit for a word from the selected item's title. Every try had several ("silk", "slip", "dress") |
| 4 | Fit card names the platform | 4 of 5 | MET (5/5) | I checked each card for the item's platform name, ignoring capitals. 5/5 items, and 25/25 across all tries |
| 5 | Empty wardrobe still gets advice | 5 of 5 | MET (5/5) | All 5 tries returned a non-blank outfit suggestion, and none crashed |

**Diagnoses**

I missed nothing. Every criterion was met on every try. I don't think that
means my agent is perfect. I think some of my targets were too easy, and
reading the actual output showed me a real problem none of them catch.

**Were my targets low?** Yes, for 3 and 4.

- **Criterion 4** checks for the platform name, but my `create_fit_card` prompt
  literally tells the model to mention the platform. So it was almost
  guaranteed to pass, and it did, 25 of 25.
- **Criterion 3** is supposed to test the session, but it checks the model's
  text, and *any* title word counts, including generic ones like "90s" or
  "vintage". If my loop had passed the wrong 90s item to `suggest_outfit`, the
  outfit would still mention "90s" and the try would pass. So it can pass
  during exactly the state failure it's meant to catch. I revised it in
  `criteria.md` (original kept, revision underneath). The revised version
  compares ids in the trace: search's first result, `selected_item`, and the
  item `suggest_outfit` received. Scored from my before traces, it's still
  5/5 on criterion 3's scenario, and on every other scenario that reached
  `suggest_outfit`.

**The real failure my criteria missed: fit cards written as the seller.**
When I read the 40 fit cards from my before run, **32 of 40 (80%)** read like a
*seller's listing*, not a buyer showing off a find:

> "I can not believe it is only $18 **on my depop right now**!"
> "**Grab this** dreamy vintage find **over on my depop** for just $30 **before it is gone**!"
> "**Grab this** classic staple **over on my Poshmark closet** for just $42 before someone else snags it!"

- **Where:** the model's output, in `tools.py::create_fit_card`. The tool ran
  fine and the loop and session were fine.
- **Mechanism:** my prompt said "Write a caption for a social media post about
  this thrift find" and told it to mention the price and the platform, but it
  **never said who is posting**. A caption that names a price and "depop" looks
  exactly like a Depop listing, so the model filled the gap with the most
  common kind of post that has those details: someone selling it.
- **Pattern:** the same push shows up in `suggest_outfit` ("you totally need to
  grab this…"), but there it reads like a friend hyping it up, not a listing.
  So I treated it as one problem in the fit card prompt.

I counted "seller voice" as any card containing phrases like "my depop",
"my Poshmark closet", "grab it/this", "before it's gone", "listed" or
"available". I wrote that check while reading the cards, before I changed
anything.

---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

Printed with `python app.py ask '...' --trace`. The `trace.step()` calls are in
`agent.py::run_agent`, one per step. Step 2 is the MCP call.

**Happy path** (`vintage graphic tee under $30`, 4 steps):

```
[1] parse_query
      in:  'vintage graphic tee under $30'
      out: description='vintage graphic tee', size=None, max_price=30.0
[2] search_listings (via MCP)
      in:  description='vintage graphic tee', size=None, max_price=30.0
      out: lst_002, lst_006, lst_033, lst_015, lst_003, lst_012, lst_013, lst_014, lst_016, lst_017
      →    branch: 10 found, selected lst_002
[3] suggest_outfit
      in:  new_item=lst_002 (Y2K Baby Tee — Butterfly Print), wardrobe=10 items
      out: Hey there! Oh, you totally need to grab this Y2K baby tee. At eighteen dollars in excellent condition, it is a…
[4] create_fit_card
      in:  new_item=lst_002, outfit='Hey there! Oh, you totally need to grab '…
      out: Obsessed with this nostalgic butterfly baby tee and I can not believe it is only $18 on my depop right now! It…
```

**Empty search** (`designer ballgown size XXS under $5`, which stops after 2 steps):

```
[1] parse_query
      in:  'designer ballgown size XXS under $5'
      out: description='designer ballgown', size='XXS', max_price=5.0
[2] search_listings (via MCP)
      in:  description='designer ballgown', size='XXS', max_price=5.0
      out: [] (empty)
      →    branch: empty, stopping before suggest_outfit
```

**The three failure modes, triggered on purpose:**

| Failure | How I triggered it | What my agent said |
|---|---|---|
| Empty search | `python app.py ask 'designer ballgown size XXS under $5'` | Nothing matched 'designer ballgown' in size XXS under $5. Try: raise your price limit (listings start around $12); or drop the size; or use broader words like 'jacket', 'tee' or 'jeans'. |
| Empty wardrobe | `python app.py ask 'denim jacket under $50' --empty-wardrobe` | (You haven't saved any clothes yet, so these are general ideas. Add your wardrobe to get outfits built from what you own.) …then real styling advice for the jacket |
| Model unavailable | Ran `'90s track jacket in size M'` with a broken key and the cache off | Found a match, but couldn't get outfit ideas because the model couldn't be reached. The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com. Then run the same search again. |

The model-unavailable trace stops at step 3 instead of crashing:

```
[3] suggest_outfit
      in:  lst_004
      out: ModelUnavailable
      →    model unreachable, stopping
```

Before I added handlers, a bad key would have crashed `run_agent` with a stack
trace. I added a `ModelUnavailable` handler around both model calls, and an
`MCPError` handler around the MCP search in case the server can't start.

**On the MCP move:** I moved `search_listings` onto MCP. In `mcp_server.py`
I registered it with `@mcp.tool()`, with typed inputs (`description: str`,
`size: str | None`, `max_price: float | None`) and a description written for
someone who can't see my code. It names the size rule, that prices are US
dollars, and that an empty result is `[]`. In `agent.py::run_agent` I swapped
the direct call for `call_tool("search_listings", {...})`. `python mcp_client.py`
lists the tool with those three inputs. Nothing behaved differently: I ran 4
queries both ways (including the impossible one) and the direct and MCP results
were identical, and an empty search still comes back as a list `[]`, not
`None` or a string. The only difference I noticed is speed, because each MCP
call starts the server process again.



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:** One prompt, in `tools.py::create_fit_card`. The old
prompt started "Write a caption for a social media post about this thrift find".
The new one says "You just BOUGHT this secondhand item and you're posting an
outfit photo wearing it", asks for first person as the buyer, and says it is
NOT selling it (no "my depop", "grab it", "shop it", "available" or "listed").
It now asks it to say *where I found it* and *what I paid*, instead of just
"mention the price and the platform". Nothing else changed: same tools, same
loop, same scenarios, same temperature (0.9), caching off.

**Which failure it was meant to fix:** The one my diagnosis found: 32 of 40 fit
cards in my before run were written in a seller's voice, because my prompt
never said who was posting.

### Run Log — After

My after run is `results/run_2026-10-08_0155_after.md`, produced by `run_eval.py::main` with the same
scenarios, 5 tries each, caching off (80 model calls).

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before `suggest_outfit` | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Outfit mentions the item search found | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3 (revised). Same id in search → `selected_item` → `suggest_outfit` | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card names the platform (5 different items) | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Empty wardrobe still gets outfit advice | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

And the number the change was aimed at:

| | Before | After |
|---|---|---|
| Fit cards flagged as seller voice by my phrase check | **32 of 40** | **3 of 40** |
| …that are actually seller voice when I read them | 32 of 40 | **0 of 40** |
| Fit cards naming the right platform (criterion 4, all tries) | 25 of 25 | 25 of 25 |

The 3 "after" flags are all false alarms from my check matching "my closet",
which a buyer says too ("the ultimate vintage find for my closet"). I checked
the before run for the same thing, and none of its 32 were flagged only by
"my closet". All 32 had real seller phrases like "on my depop" or "grab this".

Two real after cards, from the same items as the seller-voice examples above:

```
I scored this dreamy floral silk slip dress on depop for just $30 and I am completely obsessed with the 90s model-off-duty vibe. Layering my oversized grey crewneck right over top with chunky sneakers makes it the ultimate effortless daytime look. I cannot wait to wear this absolute steal on repeat all season long!
```

```
I am obsessed with this vintage Wrangler cropped denim jacket that I found on Poshmark for just $42. I styled it over a black midi dress with chunky sneakers to get that effortless contrast between feminine and casual. It gives off the ultimate streetwear vibe while keeping things super comfortable for everyday wear.
```

**Did it help, and how do I know:** Yes. Seller-voice fit cards went from 32 of
40 to 0 of 40 on reading, with the same 8 items and the same number of tries.
Nothing I was already passing broke: all five criteria are still 5/5, and every
card still names the right platform. All 40 after cards open in the buyer's
voice: 25 start with "Scored", 11 with "I", 2 with "Score!", and 1 each with
"Just" and "Finally".

---

## What's Still Broken

None of my five criteria are missed, so nothing here is a missed target.
These are the problems I found while reading the output that my criteria don't
cover, and what I'd do about each.

- **My criteria 3 and 4 were too easy, and 4 still is.** Criterion 4 passed
  25/25 even while 80% of the cards were in the wrong voice, so it measured
  something the prompt hands to the model. If I wrote it again, it would be
  "names the platform *and* is written as the buyer". I left it as written
  because it isn't broken, just low, and the rules say not to change a
  criterion just because I'd like a different one.
- **My search matches any keyword, not the kind of item.** `leather boots`
  returns a **Leather Belt** first, because "leather" matches and there are no
  boots in the data. My agent then styles a belt for someone who asked for
  boots. I'd fix it in `tools.py::search_listings` by requiring the item word
  (boots, jacket, tee) to match the title or category, and returning `[]`
  otherwise so my empty-search branch handles it. I stopped because the rules
  allow only one improvement this unit.
- **A data mistake leaks into the outfit text.** The silk slip dress (lst_013)
  has `category: "bottoms"` in `listings.json`, and in one try `suggest_outfit`
  wrote "Since it is listed under bottoms, wait—even if it is a dress…". The
  tool passed the field through as-is. I'd either fix the data or leave the
  category out of that prompt.
- **`suggest_outfit` is still a bit salesy** ("you totally need to grab this"). It
  reads like a friend hyping it up, not a listing, so I left it, but it's the
  same kind of prompt gap I fixed in the fit card.
- **My seller-voice check is just a phrase list.** It flagged 3 buyer cards
  because of "my closet". It was good enough to show a 32 → 0 change I could
  confirm by reading, but a better check would need someone (or a model) to
  judge the voice.
- **Each MCP search restarts the server.** I timed it at 1.23s through MCP
  versus 0.001s calling `search_listings` directly.
  Fine for one user. I'd keep a connection open if this were serving lots of
  people.
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
