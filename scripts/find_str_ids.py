"""Find all Стр* identifiers in RU source."""
import re
from pathlib import Path

text = Path(r"C:/Users/DmitryZhikharev/AppData/Local/1C/1cedtstart/projects/HTTP connector/HTTPConnector_ru/src/CommonModules/КоннекторHTTP/Module.bsl").read_text(encoding="utf-8-sig")
no_str = re.sub(r'"[^"]*"', '""', text)
no_comm = re.sub(r"//[^\n]*", "", no_str)
idents = set(re.findall(r"\b(Стр[А-Яа-яёЁ]+)\b", no_comm))
Path(r"C:/git/1c-translations-with-model/str_ids.out").write_text("\n".join(sorted(idents)), encoding="utf-8")
print(f"found {len(idents)} Стр* identifiers")
