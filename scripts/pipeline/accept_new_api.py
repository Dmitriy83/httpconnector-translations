"""Compare current translated module's exports against api_schema.json and
optionally add any NEW exported methods to the schema.

Use case: upstream RU source adds a new exported method. After rebuild, this
tool lists additions. Run with --apply once you've reviewed the names and
decided they're intentional API additions — it adds them to api_schema.json
so `verify_api.py` stops flagging them.

Does NOT remove methods from schema — if RU upstream drops a method, that's
an API break, and you mark it manually with "upstream_removed": true.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

# Re-use the extractor from verify_api.py
sys.path.insert(0, str(Path(__file__).parent))
from verify_api import extract_exports, SCHEMA, MOD  # noqa: E402


def main() -> int:
    apply = "--apply" in sys.argv

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    expected = {e["name"]: e for e in schema["exports"]}
    actual = extract_exports(MOD.read_text(encoding="utf-8-sig"))

    new_names = sorted(set(actual) - set(expected))
    if not new_names:
        print("No new exports — schema already covers everything.")
        return 0

    print(f"Found {len(new_names)} new exported method(s):\n")
    additions = []
    for name in new_names:
        a = actual[name]
        params_str = ", ".join(
            p["name"] + (f" = {p['default']}" if "default" in p else "")
            for p in a["params"]
        )
        rf = a.get("return_fields", [])
        print(f"  {a['kind']} {name}({params_str})")
        if rf:
            print(f"    return_fields: {rf}")
        entry = {
            "kind": a["kind"],
            "name": name,
            "params": a["params"],
        }
        if rf:
            entry["return_fields"] = rf
        additions.append(entry)

    if not apply:
        print(f"\nDry-run. Re-run with --apply to add these {len(additions)} entries to api_schema.json.")
        return 0

    schema["exports"].extend(additions)
    # Keep sorted by name for stable diffs
    schema["exports"].sort(key=lambda e: e["name"].lower())
    SCHEMA.write_text(json.dumps(schema, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nadded {len(additions)} entries to {SCHEMA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
