"""Extract the exported-API schema from the OLD hand-translated EN source.

This schema captures every identifier that consumer code can touch:
  - Exported method names (Function/Procedure ... Export)
  - Parameter names and their defaults
  - Structure-field names built inside each exported method via
    `<var>.Insert("<Field>", ...)` (these become the return-value contract)

The schema is the authoritative API contract. After each EDT rebuild, run
`verify_api.py` to ensure the translated module still matches.

Source: `git show HEAD:src/en/CommonModules/HTTPConnector/Ext/Module.bsl`
    from the external HTTPConnector repo — this is the old hand-translated
    English source that real consumer code already uses.

Output: api_schema.json
"""
from __future__ import annotations
import json
import re
import subprocess
from pathlib import Path

OLD_EN_REPO = Path(r"C:/git/HTTPConnector")
OLD_EN_REL = "src/en/CommonModules/HTTPConnector/Ext/Module.bsl"

OUT = Path(r"C:/git/httpconnector-translations/api_schema.json")


def read_old_en() -> str:
    return subprocess.check_output(
        ["git", "-C", str(OLD_EN_REPO), "show", f"HEAD:{OLD_EN_REL}"],
        encoding="utf-8-sig",
    )


# Match function/procedure header up to "Export" on the same line.
# Params list may contain commas inside defaults (e.g. = New Structure("A,B")),
# but we keep the sig regex permissive and split params carefully below.
SIG_RE = re.compile(
    r"^\s*(Function|Procedure)\s+(\w+)\s*\(([^)]*)\)\s+Export\s*$",
    re.MULTILINE,
)

# Insert call: <var>.Insert("<Field>", ...) — capture var, field name
INSERT_RE = re.compile(r"(\w+)\s*\.\s*Insert\s*\(\s*\"([^\"]+)\"\s*,")

# Local-var assignment to a fresh Structure/Map/Array (the "result container")
LOCAL_INIT_RE = re.compile(
    r"^\s*(\w+)\s*=\s*New\s+(Structure|Map|Array)\b", re.MULTILINE
)

END_RE = re.compile(r"^\s*(EndFunction|EndProcedure)\b", re.MULTILINE)


def split_params(raw: str) -> list[dict]:
    """Split a parenthesized param list into [{name, default?}, ...].

    Handles Val/ByVal prefixes and defaults; ignores commas inside nested calls
    by tracking paren depth.
    """
    out: list[dict] = []
    parts: list[str] = []
    depth = 0
    cur = ""
    for ch in raw:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    if cur.strip():
        parts.append(cur)

    for p in parts:
        p = p.strip()
        if not p:
            continue
        # Strip "Val " prefix
        p = re.sub(r"^Val\s+", "", p)
        name_default = p.split("=", 1)
        name = name_default[0].strip()
        entry: dict = {"name": name}
        if len(name_default) == 2:
            entry["default"] = name_default[1].strip()
        out.append(entry)
    return out


def extract_function_body(text: str, sig_end: int) -> tuple[str, int]:
    """Return the body text between sig_end and the matching End(Procedure|Function)."""
    m = END_RE.search(text, sig_end)
    if not m:
        return text[sig_end:], len(text)
    return text[sig_end : m.start()], m.end()


def main() -> None:
    text = read_old_en()

    exports: list[dict] = []
    for m in SIG_RE.finditer(text):
        kind = m.group(1)
        name = m.group(2)
        params_raw = m.group(3)
        params = split_params(params_raw)
        body, _ = extract_function_body(text, m.end())

        # Identify result-container variable(s): first local assigned to
        # `New Structure/Map/Array`. Record fields via <var>.Insert("Field", ...).
        container_vars: list[str] = []
        for init in LOCAL_INIT_RE.finditer(body):
            var = init.group(1)
            if var not in container_vars:
                container_vars.append(var)

        # Prefer the first container that has Insert calls — that's the
        # builder variable (others may be short-lived locals).
        by_var: dict[str, list[str]] = {v: [] for v in container_vars}
        for ins in INSERT_RE.finditer(body):
            var, field = ins.group(1), ins.group(2)
            if var in by_var:
                if field not in by_var[var]:
                    by_var[var].append(field)

        # Pick the variable with most fields as "the" return builder; if none,
        # leave fields empty (procedure or primitive return).
        best_var = max(by_var, key=lambda v: len(by_var[v])) if by_var else None
        return_fields = by_var.get(best_var or "", [])

        entry = {
            "kind": kind,
            "name": name,
            "params": params,
        }
        if return_fields:
            entry["return_fields"] = return_fields
        exports.append(entry)

    schema = {
        "source": f"HTTPConnector repo HEAD:{OLD_EN_REL}",
        "module": "HTTPConnector",
        "note": (
            "Authoritative API contract. Fields listed under return_fields are "
            "what consumer code accesses on the return value of that method. "
            "Rebuilds must preserve every name verbatim."
        ),
        "exports": exports,
    }
    OUT.write_text(json.dumps(schema, ensure_ascii=False, indent=2), encoding="utf-8")
    with_fields = sum(1 for e in exports if e.get("return_fields"))
    print(f"wrote {OUT}  exports={len(exports)}  with return_fields={with_fields}")


if __name__ == "__main__":
    main()
