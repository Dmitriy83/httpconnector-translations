"""Add missing .trans keys for Method.НовыеПараметры.Return.<Field>.Description.

EDT's dict generator created only 2 keys for НовыеПараметры while СоздатьСессию
got 16. This adds per-field keys for the top-level `*` bullets in the Return
doc comment before Function НовыеПараметры().
"""
from pathlib import Path

TARGET = Path(r"C:/git/HTTPConnector/dictionaries_en/src/CommonModules/КоннекторHTTP/Module_en.trans")

# Top-level * fields from the RU source doc (lines 368-422)
# Values are English translations. Escape \: for literal colons, \n for newlines.
NEW_KEYS = {
    "Method.НовыеПараметры.Return.Заголовки.Description":
        "see description Session.Headers.",
    "Method.НовыеПараметры.Return.Аутентификация.Description":
        "see description Session.Authentication",
    "Method.НовыеПараметры.Return.Прокси.Description":
        "see description Session.Proxy.",
    "Method.НовыеПараметры.Return.ПараметрыЗапроса.Description":
        "see description Session.RequestParameters.",
    "Method.НовыеПараметры.Return.ПроверятьSSL.Description":
        "see description Session.VerifySSL.",
    "Method.НовыеПараметры.Return.КлиентскийСертификатSSL.Description":
        "Default value\\: Undefined.",
    "Method.НовыеПараметры.Return.Cookies.Description":
        "see description Session.Cookies.",
    "Method.НовыеПараметры.Return.Таймаут.Description":
        "timeout for connection and operations, in seconds.\\nDefault value - 30 sec.",
    "Method.НовыеПараметры.Return.РазрешитьПеренаправление.Description":
        "True - redirects will be automatically allowed.\\nFalse - only one request to the server will be executed.",
    "Method.НовыеПараметры.Return.Json.Description":
        "data to serialize into JSON.",
    "Method.НовыеПараметры.Return.ПараметрыПреобразованияJSON.Description":
        "specifies JSON conversion parameters\\:",
    "Method.НовыеПараметры.Return.ПараметрыЗаписиJSON.Description":
        "used when writing a JSON object.",
    "Method.НовыеПараметры.Return.Данные.Description":
        "arbitrary data to send in the request.",
    "Method.НовыеПараметры.Return.Файлы.Description":
        "files to send",
    "Method.НовыеПараметры.Return.МаксимальноеКоличествоПовторов.Description":
        "number of connection/request send retries.\\nAn exponentially growing delay is applied between retries.\\n"
        "But if the status code is one of 413, 429, 503\\nand the response has a Retry-After header,\\n"
        "the delay is derived from this header's value\\nDefault value\\: 0 - retries are not performed.",
    "Method.НовыеПараметры.Return.МаксимальноеВремяПовторов.Description":
        "maximum total time (in seconds) for sending the request including retries.\\nDefault value\\: 600.",
    "Method.НовыеПараметры.Return.КоэффициентЭкспоненциальнойЗадержки.Description":
        "exponential delay change coefficient.\\n1 produces a sequence of delays\\: 1, 2, 4, 8, etc.\\n"
        "2 produces a sequence of delays\\: 2, 4, 8, 16, etc.\\n...\\nDefault value\\: 1.",
    "Method.НовыеПараметры.Return.ПовторятьДляКодовСостояний.Description":
        "Undefined - retries are performed for status codes >\\= 500.\\n"
        "Array - retries are performed for specific status codes.\\nDefault value\\: Undefined.",
}


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

existing_keys = set()
for ln in lines:
    if not ln or ln.startswith("#"):
        continue
    kv = split_kv(ln)
    if kv:
        existing_keys.add(kv[0])

new_to_add = [(k, v) for k, v in NEW_KEYS.items() if k not in existing_keys]
already = [k for k in NEW_KEYS if k in existing_keys]

print(f"already present: {len(already)}")
print(f"will add:        {len(new_to_add)}")

# Parse existing lines into dict, preserving header, then write sorted
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

for k, v in new_to_add:
    entries[k] = v

out = [header, ""] if header else []
for k in sorted(entries):
    out.append(k + "=" + entries[k])
out_text = eol.join(out) + eol
out_raw = out_text.encode("utf-8")
if has_bom:
    out_raw = b"\xef\xbb\xbf" + out_raw
TARGET.write_bytes(out_raw)

print(f"\ntotal entries in file: {len(entries)}")
