"""Verify the translated HTTPConnector module matches the API schema.

Runs against the current EDT-translated output. Exits non-zero on any
breaking change (missing method, renamed parameter, missing return field).

Missing from schema (i.e., new methods in RU source) are reported as INFO
rather than errors — they need to be added to api_schema.json manually after
human review.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

SCHEMA = Path(r"C:/git/httpconnector-translations/api_schema.json")
MOD = Path(
    r"C:/Users/DmitryZhikharev/AppData/Local/1C/1cedtstart/projects/HTTP connector/"
    r"HTTPConnector_translated_project/src/CommonModules/HTTPConnector/Module.bsl"
)


SIG_RE = re.compile(
    r"^\s*(Function|Procedure)\s+(\w+)\s*\(([^)]*)\)\s+Export\s*$",
    re.MULTILINE,
)
INSERT_RE = re.compile(r"(\w+)\s*\.\s*Insert\s*\(\s*\"([^\"]+)\"\s*,")
LOCAL_INIT_RE = re.compile(
    r"^\s*(\w+)\s*=\s*New\s+(Structure|Map|Array)\b", re.MULTILINE
)
END_RE = re.compile(r"^\s*(EndFunction|EndProcedure)\b", re.MULTILINE)


def split_params(raw: str) -> list[dict]:
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
        p = re.sub(r"^Val\s+", "", p)
        nd = p.split("=", 1)
        name = nd[0].strip()
        entry: dict = {"name": name}
        if len(nd) == 2:
            entry["default"] = nd[1].strip()
        out.append(entry)
    return out


def extract_exports(text: str) -> dict[str, dict]:
    by_name: dict[str, dict] = {}
    for m in SIG_RE.finditer(text):
        kind = m.group(1)
        name = m.group(2)
        params = split_params(m.group(3))
        end_m = END_RE.search(text, m.end())
        body = text[m.end() : end_m.start() if end_m else len(text)]

        container_vars: list[str] = []
        for init in LOCAL_INIT_RE.finditer(body):
            if init.group(1) not in container_vars:
                container_vars.append(init.group(1))
        by_var: dict[str, list[str]] = {v: [] for v in container_vars}
        for ins in INSERT_RE.finditer(body):
            v, f = ins.group(1), ins.group(2)
            if v in by_var and f not in by_var[v]:
                by_var[v].append(f)
        best = max(by_var, key=lambda v: len(by_var[v])) if by_var else None
        return_fields = by_var.get(best or "", [])

        by_name[name] = {
            "kind": kind,
            "name": name,
            "params": params,
            "return_fields": return_fields,
        }
    return by_name


def main() -> int:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    expected = {e["name"]: e for e in schema["exports"]}
    actual = extract_exports(MOD.read_text(encoding="utf-8-sig"))

    errors: list[str] = []
    info: list[str] = []

    # Check each expected export
    for name, exp in expected.items():
        act = actual.get(name)
        if act is None:
            if exp.get("upstream_removed"):
                info.append(
                    f"DEPRECATED (upstream-removed, expected absent): {exp['kind']} {name}"
                )
                continue
            errors.append(f"MISSING method: {exp['kind']} {name}(...) — not found in translated module")
            continue
        if exp.get("upstream_removed"):
            errors.append(
                f"UNEXPECTED PRESENCE: {name} is marked upstream_removed but appears in translated module"
            )
            continue
        # Kind
        if act["kind"] != exp["kind"]:
            errors.append(f"KIND CHANGED for {name}: expected {exp['kind']}, got {act['kind']}")
        # Params: compare name+order
        exp_names = [p["name"] for p in exp["params"]]
        act_names = [p["name"] for p in act["params"]]
        if exp_names != act_names:
            errors.append(
                f"PARAMS CHANGED for {name}:\n"
                f"  expected: ({', '.join(exp_names)})\n"
                f"  actual:   ({', '.join(act_names)})"
            )
        # Return fields: every expected field must be present (extra allowed).
        exp_fields = exp.get("return_fields", [])
        if exp_fields:
            act_fields = act.get("return_fields", [])
            missing = [f for f in exp_fields if f not in act_fields]
            if missing:
                errors.append(
                    f"RETURN FIELDS missing for {name}: {missing}\n"
                    f"  expected: {exp_fields}\n"
                    f"  actual:   {act_fields}"
                )

    # Extra methods in actual not in schema — informational
    extras = sorted(set(actual) - set(expected))
    for name in extras:
        a = actual[name]
        p = ", ".join(x["name"] for x in a["params"])
        info.append(f"NEW method (add to schema if intended): {a['kind']} {name}({p})")

    # Report
    if errors:
        print(f"=== API CONTRACT VIOLATIONS ({len(errors)}) ===")
        for e in errors:
            print(f"  - {e}")
    if info:
        print(f"\n=== INFO: new methods not in schema ({len(info)}) ===")
        for i in info:
            print(f"  * {i}")

    if not errors and not info:
        print(f"API OK — {len(expected)} exports verified against schema")
    elif not errors:
        print(f"\nAPI OK — {len(expected)} exports verified; {len(info)} new methods (review)")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
