"""Revert: remove the 18 Method.НовыеПараметры.Return.<Field>.Description keys
that I added — EDT doesn't use them, they just clutter the dict."""
from pathlib import Path

TARGET = Path(r"C:/git/HTTPConnector/dictionaries_en/src/CommonModules/КоннекторHTTP/Module_en.trans")

TO_REMOVE = [
    "Method.НовыеПараметры.Return.Заголовки.Description",
    "Method.НовыеПараметры.Return.Аутентификация.Description",
    "Method.НовыеПараметры.Return.Прокси.Description",
    "Method.НовыеПараметры.Return.ПараметрыЗапроса.Description",
    "Method.НовыеПараметры.Return.ПроверятьSSL.Description",
    "Method.НовыеПараметры.Return.КлиентскийСертификатSSL.Description",
    "Method.НовыеПараметры.Return.Cookies.Description",
    "Method.НовыеПараметры.Return.Таймаут.Description",
    "Method.НовыеПараметры.Return.РазрешитьПеренаправление.Description",
    "Method.НовыеПараметры.Return.Json.Description",
    "Method.НовыеПараметры.Return.ПараметрыПреобразованияJSON.Description",
    "Method.НовыеПараметры.Return.ПараметрыЗаписиJSON.Description",
    "Method.НовыеПараметры.Return.Данные.Description",
    "Method.НовыеПараметры.Return.Файлы.Description",
    "Method.НовыеПараметры.Return.МаксимальноеКоличествоПовторов.Description",
    "Method.НовыеПараметры.Return.МаксимальноеВремяПовторов.Description",
    "Method.НовыеПараметры.Return.КоэффициентЭкспоненциальнойЗадержки.Description",
    "Method.НовыеПараметры.Return.ПовторятьДляКодовСостояний.Description",
]


def split_kv(line):
    i = 0
    while i < len(line):
        if line[i] == "\\" and i + 1 < len(line):
            i += 2
            continue
        if line[i] == "=":
            return line[:i], line[i + 1:]
        i += 1
    return None


raw = TARGET.read_bytes()
has_bom = raw.startswith(b"\xef\xbb\xbf")
if has_bom:
    raw = raw[3:]
text = raw.decode("utf-8")
eol = "\r\n" if "\r\n" in text else "\n"
lines = text.split(eol)

header = None
entries = {}
for ln in lines:
    if not ln:
        continue
    if ln.startswith("#"):
        if header is None:
            header = ln
        continue
    kv = split_kv(ln)
    if kv:
        entries[kv[0]] = kv[1]

before = len(entries)
removed = 0
for k in TO_REMOVE:
    if k in entries:
        del entries[k]
        removed += 1

out_lines = [header, ""] if header else []
for k in sorted(entries):
    out_lines.append(k + "=" + entries[k])
out_text = eol.join(out_lines) + eol
out_raw = out_text.encode("utf-8")
if has_bom:
    out_raw = b"\xef\xbb\xbf" + out_raw
TARGET.write_bytes(out_raw)

print(f"before: {before} entries")
print(f"removed: {removed}")
print(f"after:  {len(entries)} entries")
