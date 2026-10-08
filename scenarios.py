"""
The runs your test needs. ← UNIT 4, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
the empty-search branch needs an impossible query. One about the fit card needs
the same item run more than once. Working that out is Milestone 3's first step,
and this file is where you write it down.

`run_eval.py` runs everything here five times and writes the run log — five
because your criteria are written out of five.

Three scenarios are filled in to show the shape. Add or change whatever your
own criteria need — these are a starting point, not a fixed set.
"""

SCENARIOS = [
    {
        # A query the data can match. Criterion 1.
        "name": "matching query completes",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        # A query nothing can match. Criterion 2 — the branch.
        "name": "impossible query stops early",
        "query": "designer ballgown size XXS under $5",
        "wardrobe": "example",
        "criterion": 2,
    },
    {
        # Criterion 3 — state. Does a word from selected_item's title show up
        # in the outfit suggestion? Any normal query works; this one lands on
        # lst_013, "90s Silk Slip Dress — Floral, Midi Length".
        "name": "outfit mentions the selected item",
        "query": "silk slip dress under $40",
        "wardrobe": "example",
        "criterion": 3,
    },
    # Criterion 4 — "for 5 different items", so five queries that each land on
    # a different listing, across all three platforms. Try 1 of each is the
    # criterion's five tries; tries 2-5 are extra evidence.
    {
        "name": "fit card item 1 (lst_002, depop)",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        "name": "fit card item 2 (lst_004, poshmark)",
        "query": "90s track jacket in size M",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        "name": "fit card item 3 (lst_003, thredUp)",
        "query": "oversized flannel shirt",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        "name": "fit card item 4 (lst_005, depop)",
        "query": "corduroy wide-leg pants",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        "name": "fit card item 5 (lst_019, poshmark)",
        "query": "platform sneakers size 8",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        # A user with nothing saved. Criterion 5, and one of the three failure modes.
        "name": "empty wardrobe",
        "query": "denim jacket under $50",
        "wardrobe": "empty",
        "criterion": 5,
    },
]

WARDROBES = ("example", "empty")


def validate() -> list[str]:
    """Complain about anything malformed, before a long run rather than during."""
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("query", "").strip():
            problems.append(f"scenario {i} has no query")
        if scenario.get("wardrobe") not in WARDROBES:
            problems.append(
                f"scenario {i} has wardrobe {scenario.get('wardrobe')!r} — "
                f"it should be one of {WARDROBES}"
            )
    return problems
