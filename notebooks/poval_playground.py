# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "lark>=1.2",
#     "marimo>=0.11",
#     "polars>=1.0",
# ]
# ///

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")


@app.cell
def _():
    default_rule = """\
    WHEN
    COL(origin) = "Barcelona"
    THEN
    COL(destination) != "Barcelona"
    GROUP BY
    "item"
    """
    return (default_rule,)


@app.cell
def _():
    import sys
    from pathlib import Path

    import marimo as mo
    import polars as pl

    root = Path(__file__).resolve().parent.parent
    src = root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    return mo, pl


@app.cell
def _(pl):
    df = pl.DataFrame(
        {
            "item": [
                "A1",
                "A1",
                "A1",
                "A2",
                "A2",
                "B1",
                "B1",
                "B2",
                "B2",
                "C1",
                "C1",
                "C2",
            ],
            "route": [
                "north",
                "north",
                "north",
                "south",
                "south",
                "east",
                "east",
                "west",
                "west",
                "north",
                "north",
                "south",
            ],
            "origin": [
                "Barcelona",
                "Barcelona",
                "Madrid",
                "Barcelona",
                "Madrid",
                "Barcelona",
                "Valencia",
                "Madrid",
                "Madrid",
                "Barcelona",
                "Barcelona",
                "Seville",
            ],
            "destination": [
                "Barcelona",
                "Valencia",
                "Madrid",
                "Barcelona",
                "Madrid",
                "Barcelona",
                "Valencia",
                "Madrid",
                "Barcelona",
                "Valencia",
                "Barcelona",
                "Madrid",
            ],
            "price": [10, 10, 12, 15, 15, 20, 20, 8, 9, 5, 5, 30],
            "quantity": [1, 2, 1, 3, 3, 4, 4, 2, 2, 1, 1, 6],
            "notes": [
                "ok",
                None,
                "checked",
                "ok",
                "checked",
                None,
                "ok",
                "ok",
                None,
                "ok",
                "ok",
                None,
            ],
        }
    )
    return (df,)


@app.cell
def _(mo):
    mo.md("""
    # Poval playground

    Edit the rule below. The notebook parses it, compiles **WHEN** / **THEN** to
    Polars expressions, shows violations, and prints the compiled expressions.
    """)
    return


@app.cell
def _(default_rule, mo):
    rule_editor = mo.ui.text_area(
        value=default_rule,
        label="Poval rule",
        full_width=True,
        rows=14,
        debounce=True,
    )
    rule_editor
    return (rule_editor,)


@app.cell
def _(df, rule_editor):
    from lark.exceptions import LarkError

    from poval import Poval
    from poval.evaluator import compile_rule
    from poval.parser import parse_avl

    source = rule_editor.value

    try:
        rule = parse_avl(source)
        compiled = compile_rule(rule)
        violations = Poval.evaluate(df, [source])
        violation_expr = Poval.compile_violation_expression([source])
        error = None
    except (ValueError, LarkError, TypeError) as exc:
        rule = None
        compiled = None
        violations = None
        violation_expr = None
        error = str(exc)
    return compiled, error, violation_expr, violations


@app.cell
def _(compiled, error, mo, violation_expr):
    if error:
        expressions_view = mo.callout(
            mo.md(f"**Parse / compile error:** `{error}`"),
            kind="danger",
        )
    elif compiled is not None and violation_expr is not None:
        violation_mask = compiled.when & ~compiled.then
        body = "\n".join(
            [
                "# WHEN",
                str(compiled.when),
                "",
                "# THEN",
                str(compiled.then),
                "",
                "# Violation mask (WHEN and not THEN)",
                str(violation_mask),
                "",
                "# Library violation expression",
                str(violation_expr),
            ]
        )
        expressions_view = mo.md(f"""
        ### Compiled Polars expressions

        ```python
        {body}
        ```
        """)
    else:
        expressions_view = mo.md("_Waiting for a valid rule..._")
    expressions_view
    return


@app.cell
def _(df, error, mo, violations):
    mo.md("### Sample data")
    mo.ui.table(df.to_dicts())
    if error:
        violations_view = mo.callout(
            mo.md(f"**Parse / compile error:** `{error}`"),
            kind="danger",
        )
    elif violations is None:
        violations_view = mo.md("_Waiting for a valid rule..._")
    else:
        violation_df = violations[0]
        if violation_df.height == 0:
            violations_view = mo.callout(
                mo.md("**PASSED** — no violating rows"),
                kind="success",
            )
        else:
            violations_view = mo.vstack(
                [
                    mo.callout(
                        mo.md(f"**FAILED** — {violation_df.height} violating row(s)"),
                        kind="warn",
                    ),
                    mo.md("### Violations"),
                    mo.ui.table(violation_df.to_dicts()),
                ]
            )
    mo.vstack([violations_view])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
 
    """)
    return


if __name__ == "__main__":
    app.run()
