import csv, json, os, time, re, sys
from typing import Dict
from tqdm import tqdm

# pip install googletrans==4.0.0-rc1 tqdm
from googletrans import Translator

# ========== CONFIG ==========
INPUT  = "Sweden_merged_deduped.csv"
OUTPUT = "Sweden_merged_deduped_translated.csv"
CACHE  = "translation_cache.json"

TRANSLATE_SLEEP = 0.10   # delay between requests
RETRIES = 3              # retry attempts
RETRY_SLEEP = 1.0        # wait between retries
TRANSLATE_COLS = ("descriptionText",)   # only translate this column
EXPECTED_COLS = ["companyDescription","companyName","descriptionText","id","industries","jobFunction"]
# ============================

translator = Translator()

_ascii_re = re.compile(r'^[\x00-\x7F\s\W\d]+$')
def looks_english(s: str) -> bool:
    if not s:
        return True
    s = s.strip()
    if not s:
        return True
    return bool(_ascii_re.match(s))

def safe_translate(text: str, cache: Dict[str, str]) -> str:
    if text is None:
        return text
    s = str(text)
    if not s.strip():
        return s
    if s in cache:
        return cache[s]
    if looks_english(s):
        cache[s] = s
        return s

    for _ in range(RETRIES):
        try:
            out = translator.translate(s, dest="en").text
            cache[s] = out
            time.sleep(TRANSLATE_SLEEP)
            return out
        except Exception:
            time.sleep(RETRY_SLEEP)

    # fallback if all retries fail
    cache[s] = s
    return s

def ensure_expected_columns(fieldnames):
    for col in EXPECTED_COLS:
        if col not in fieldnames:
            fieldnames.append(col)
    return fieldnames

def main():
    if not os.path.exists(INPUT):
        print(f"Input not found: {INPUT}")
        sys.exit(1)

    # Load cache
    cache = {}
    if os.path.exists(CACHE):
        try:
            with open(CACHE, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except Exception:
            cache = {}

    # Read rows
    with open(INPUT, "r", encoding="utf-8", newline="") as fin:
        reader = csv.DictReader(fin)
        rows = list(reader)
        fieldnames = reader.fieldnames or []
    fieldnames = ensure_expected_columns(fieldnames)

    # Collect unique descriptionText
    unique_texts = set()
    for r in rows:
        val = r.get("descriptionText")
        if val and not looks_english(val) and val not in cache:
            unique_texts.add(val)

    print(f"Rows: {len(rows)}")
    print(f"Unique descriptionText to translate: {len(unique_texts)} (cached: {len(cache)})")

    # Translate only unique texts
    if unique_texts:
        for s in tqdm(unique_texts, desc="Translating descriptionText", unit="text"):
            if s in cache:
                continue
            _ = safe_translate(s, cache)
            if len(cache) % 100 == 0:
                with open(CACHE, "w", encoding="utf-8") as f:
                    json.dump(cache, f, ensure_ascii=False)

    # Write output
    with open(OUTPUT, "w", encoding="utf-8", newline="") as fout:
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        for r in tqdm(rows, desc="Writing rows", unit="row"):
            r["descriptionText"] = safe_translate(r.get("descriptionText"), cache)
            writer.writerow(r)

    with open(CACHE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False)

    print(f"Done. Wrote: {OUTPUT}")
    print(f"Cache saved: {CACHE}  (entries: {len(cache)})")

if __name__ == "__main__":
    main()
