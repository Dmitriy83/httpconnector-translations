"""Finalize Method.НовыеПараметры translations:
1. Update Return.Description to short text matching source line.
2. Add nested ** field keys under ParametersConversionJSON."""
from pathlib import Path

TARGET = Path(r"C:/git/HTTPConnector/dictionaries_en/src/CommonModules/КоннекторHTTP/Module_en.trans")

UPDATES = {
    # Replace the huge old value with a short one matching source line
    # "//  Структура - позволяет задать дополнительные параметры:"
    "Method.НовыеПараметры.Return.Description":
        "allows to specify additional parameters",
}

# Nested ** fields under ParametersConversionJSON
# (see source lines 381-400)
NESTED_KEYS = {
    "Method.НовыеПараметры.Return.ПараметрыПреобразованияJSON.ПрочитатьВСоответствие.Description":
        "If True, the JSON object will be read into a Map.\\nIf False, objects will be read into a Structure.",
    "Method.НовыеПараметры.Return.ПараметрыПреобразованияJSON.ФорматДатыJSON.Description":
        "format in which the date is represented in the string\\nthat needs to be converted.",
    "Method.НовыеПараметры.Return.ПараметрыПреобразованияJSON.ИменаСвойствСоЗначениямиДата.Description":
        "JSON property names\\nfor which date restoration from string should be called.",
    "Method.НовыеПараметры.Return.ПараметрыПреобразованияJSON.ИмяФункцииВосстановления.Description":
        "specifies the name of the function that will be called when reading\\neach property and must have the following parameters\\:",
    "Method.НовыеПараметры.Return.ПараметрыПреобразованияJSON.ИмяФункцииВосстановления.Свойство.Description":
        "specified only when reading JSON objects",
    "Method.НовыеПараметры.Return.ПараметрыПреобразованияJSON.ИмяФункцииВосстановления.Значение.Description":
        "value of a serializable type",
    "Method.НовыеПараметры.Return.ПараметрыПреобразованияJSON.ИмяФункцииВосстановления.ДополнительныеПараметры.Description":
        "",
    "Method.НовыеПараметры.Return.ПараметрыПреобразованияJSON.ИмяФункцииВосстановления.Return.Description":
        "value deserialized from JSON.",
    "Method.НовыеПараметры.Return.ПараметрыПреобразованияJSON.МодульФункцииВосстановления.Description":
        "specifies the module whose procedure will be used for\\nvalue restoration.",
    "Method.НовыеПараметры.Return.ПараметрыПреобразованияJSON.ДополнительныеПараметрыФункцииВосстановления.Description":
        "specifies additional parameters that\\nwill be passed to the value restoration function.",
    "Method.НовыеПараметры.Return.ПараметрыПреобразованияJSON.ИменаСвойствДляОбработкиВосстановления.Description":
        "specifies an array of JSON property names for which\\nthe restoration function will be called.",
    "Method.НовыеПараметры.Return.ПараметрыПреобразованияJSON.МаксимальнаяВложенность.Description":
        "specifies the maximum nesting level of the JSON object.",
    # Nested under Данные
    "Method.НовыеПараметры.Return.Данные.Ключ.Description":
        "field name.",
    "Method.НовыеПараметры.Return.Данные.Значение.Description":
        "field value.",
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

# Apply updates
for k, v in UPDATES.items():
    entries[k] = v

# Add nested keys (only if missing)
added = 0
for k, v in NESTED_KEYS.items():
    if k not in entries:
        entries[k] = v
        added += 1

out_lines = [header, ""] if header else []
for k in sorted(entries):
    out_lines.append(k + "=" + entries[k])
out_text = eol.join(out_lines) + eol
out_raw = out_text.encode("utf-8")
if has_bom:
    out_raw = b"\xef\xbb\xbf" + out_raw
TARGET.write_bytes(out_raw)

print(f"before: {before} entries")
print(f"updated:   {len(UPDATES)}")
print(f"added:     {added}")
print(f"after:  {len(entries)} entries")
