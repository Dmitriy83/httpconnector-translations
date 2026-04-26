"""More thorough check: Cyrillic outside doc comments in translated module."""
import re
from pathlib import Path

MOD = Path(r"C:/Users/DmitryZhikharev/AppData/Local/1C/1cedtstart/projects/HTTP connector/HTTPConnector_translated_project/src/CommonModules/HTTPConnector/Module.bsl")
OUT = Path(r"C:/git/httpconnector-translations/check_translated.out")

lines = MOD.read_bytes().decode("utf-8-sig").split("\n")

bad = []  # (line_no, category, content)
for i, ln in enumerate(lines, 1):
    # Strip leading whitespace for check
    stripped = ln.lstrip()
    if not stripped:
        continue
    if stripped.startswith("//"):
        # Doc comment — we only care about doc comments that have Russian IDENTIFIERS (in signature-like format)
        # But for this check, focus on code
        if re.search(r"[А-Яа-яЁё]", ln):
            bad.append((i, "doc_comment", ln.rstrip()))
        continue
    # Actual code line
    if re.search(r"[А-Яа-яЁё]", ln):
        bad.append((i, "CODE", ln.rstrip()))

with OUT.open("w", encoding="utf-8") as f:
    code_issues = [b for b in bad if b[1] == "CODE"]
    doc_issues = [b for b in bad if b[1] == "doc_comment"]
    f.write(f"=== CODE lines with Cyrillic ({len(code_issues)}) — ACTIONABLE ===\n")
    for lno, _, ln in code_issues:
        f.write(f"  {lno:5d}: {ln}\n")
    f.write(f"\n=== DOC comment lines with Cyrillic ({len(doc_issues)}) — translation gaps in .trans ===\n")
    for lno, _, ln in doc_issues[:50]:
        f.write(f"  {lno:5d}: {ln}\n")

print(f"CODE issues: {len(code_issues)}  DOC issues: {len(doc_issues)}")
print(f"wrote {OUT}")
