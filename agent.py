"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import re

import config
import trace
from tools import suggest_outfit, create_fit_card
from generate import ModelUnavailable
from mcp_client import call_tool, MCPError


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. **Check session["error"] first** — if it isn't None,
        the run ended early and the later fields will still be None.

    ─────────────────────────────────────────────────────────────────────────
    TODO — build this, following the branch rule you wrote in Milestone 2.

      1. Start a session with new_session().

      2. Count the times round the loop, and call trace.check_iterations(count)
         on each one before you go again. It raises when the count passes
         MAX_ITERATIONS in config.py — see trace.py.

      3. Parse the query into a description, a size, and a max_price. Regex,
         string splitting, or asking the model are all fine — say which you
         chose in your README. Put the result in session["parsed"].

      4. Call search_listings() with what you parsed.
         Put the results in session["search_results"].

         ⚠️ THIS IS THE BRANCH. If nothing came back:
              - put a message in session["error"] saying what the user could
                change — "No results" is not that message
              - return the session
              - do NOT call suggest_outfit with nothing

      5. Choose an item — the first result is fine. Put it in
         session["selected_item"].

      6. Call suggest_outfit() with the selected item and the wardrobe.
         Put the result in session["outfit_suggestion"].

      7. Call create_fit_card() with the outfit and the item.
         Put the result in session["fit_card"].

      8. Return the session.

    ─────────────────────────────────────────────────────────────────────────
    IN UNIT 4 you come back and add two things:

      • Trace calls. One per step. `trace.step("search_listings", inputs=...,
        returned=...)` — see trace.py. Your README needs the output.

      • A handler for ModelUnavailable, so a bad key produces a message rather
        than a stack trace. The import is already at the top of this file.
    """
    session = new_session(query, wardrobe)
    session["parsed"] = parse_query(query)
    trace.step("parse_query", inputs=repr(query), returned=_show_parsed(session["parsed"]))

    # Each pass runs one step, then looks at what that step put in the session
    # to pick the next one. "done" ends the loop.
    next_step = "search"
    count = 0

    while next_step != "done":
        count += 1
        trace.check_iterations(count)

        if next_step == "search":
            parsed = session["parsed"]
            # search_listings runs on the MCP server (mcp_server.py), not in-process
            try:
                session["search_results"] = call_tool("search_listings", {
                    "description": parsed["description"],
                    "size": parsed["size"],
                    "max_price": parsed["max_price"],
                })
            except MCPError as exc:
                session["error"] = (
                    "The search service didn't start, so nothing was searched. "
                    "Run `python mcp_server.py` on its own to see why, then try again."
                )
                trace.step("search_listings (via MCP)", inputs=_show_parsed(parsed),
                           returned=str(exc).splitlines()[0], note="MCP failed, stopping")
                next_step = "done"
                continue

            # THE BRANCH: nothing found → explain and stop, never call suggest_outfit
            if not session["search_results"]:
                session["error"] = no_results_message(parsed)
                next_step = "done"
                note = "branch: empty, stopping before suggest_outfit"
            else:
                session["selected_item"] = session["search_results"][0]
                next_step = "suggest"
                note = f"branch: {len(session['search_results'])} found, selected {session['selected_item']['id']}"
            trace.step("search_listings (via MCP)", inputs=_show_parsed(parsed),
                       returned=", ".join(r["id"] for r in session["search_results"]) or "[] (empty)",
                       note=note)

        elif next_step == "suggest":
            item = session["selected_item"]
            empty_wardrobe = not (session["wardrobe"] or {}).get("items")
            try:
                session["outfit_suggestion"] = suggest_outfit(item, session["wardrobe"])
            except ModelUnavailable as exc:
                session["error"] = model_error_message("outfit ideas", exc)
                trace.step("suggest_outfit", inputs=item["id"], returned=type(exc).__name__,
                           note="model unreachable, stopping")
                next_step = "done"
                continue

            if empty_wardrobe:
                session["outfit_suggestion"] = (
                    "(You haven't saved any clothes yet, so these are general ideas. "
                    "Add your wardrobe to get outfits built from what you own.)\n\n"
                    + session["outfit_suggestion"]
                )
            trace.step("suggest_outfit",
                       inputs=f"new_item={item['id']} ({item['title']}), "
                              f"wardrobe={len((session['wardrobe'] or {}).get('items') or [])} items",
                       returned=session["outfit_suggestion"],
                       note="empty wardrobe, general advice" if empty_wardrobe else "")
            next_step = "fit_card"

        elif next_step == "fit_card":
            item = session["selected_item"]
            try:
                session["fit_card"] = create_fit_card(session["outfit_suggestion"], item)
            except ModelUnavailable as exc:
                session["error"] = model_error_message("a fit card", exc)
                trace.step("create_fit_card", inputs=item["id"], returned=type(exc).__name__,
                           note="model unreachable, stopping")
                next_step = "done"
                continue
            trace.step("create_fit_card",
                       inputs=f"new_item={item['id']}, outfit={session['outfit_suggestion'][:40]!r}…",
                       returned=session["fit_card"])
            next_step = "done"

    return session


def _show_parsed(parsed: dict) -> str:
    """parsed as one readable line for the trace."""
    return ", ".join(f"{k}={v!r}" for k, v in parsed.items())


def model_error_message(what: str, exc: Exception) -> str:
    """What broke, the reason generate.py gave, and what to try."""
    return (
        f"Found a match, but couldn't get {what} because the model couldn't be "
        f"reached. {exc} Then run the same search again."
    )


# ── query parsing ─────────────────────────────────────────────────────────────

_PRICE = re.compile(r"(?:under|below|less than|max|up to)?\s*\$\s*(\d+(?:\.\d+)?)", re.I)
_SIZE = re.compile(
    r"\b(?:in\s+)?size\s+((?:us\s+|w)?\d+(?:\.\d+)?|x{0,3}[sml]|xl|one size)\b"
    r"|\bin\s+(?:a\s+)?(x{0,3}[sml]|xl)\b",
    re.I,
)


def parse_query(query: str) -> dict:
    """
    Pull a size and a price ceiling out of the query with regex. Whatever is
    left over becomes the search description.

        "vintage graphic tee under $30, size M"
        → {"description": "vintage graphic tee", "size": "M", "max_price": 30.0}
    """
    max_price = None
    size = None
    rest = query

    price = _PRICE.search(rest)
    if price:
        max_price = float(price.group(1))
        rest = rest[:price.start()] + " " + rest[price.end():]

    size_match = _SIZE.search(rest)
    if size_match:
        size = (size_match.group(1) or size_match.group(2)).upper()
        rest = rest[:size_match.start()] + " " + rest[size_match.end():]

    description = " ".join(re.sub(r"[,.!?]", " ", rest).split())
    return {"description": description, "size": size, "max_price": max_price}


def no_results_message(parsed: dict) -> str:
    """Say what was searched for and what the user could loosen."""
    searched = f"'{parsed['description']}'"
    if parsed["size"]:
        searched += f" in size {parsed['size']}"
    if parsed["max_price"] is not None:
        searched += f" under ${parsed['max_price']:g}"

    tips = []
    if parsed["max_price"] is not None:
        tips.append("raise your price limit (listings start around $12)")
    if parsed["size"]:
        tips.append("drop the size")
    tips.append("use broader words like 'jacket', 'tee' or 'jeans'")

    return f"Nothing matched {searched}. Try: " + "; or ".join(tips) + "."


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
