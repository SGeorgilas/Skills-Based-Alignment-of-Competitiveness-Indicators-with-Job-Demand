import pandas as pd
import json, ast
from pathlib import Path

# ==== ΡΥΘΜΙΣΕ ΤΑ ====
INPUT_CSV       = r"C:\Users\Desktop PC\Desktop\ΔΙΠΛΩΜΑΤΙΚΗ\linkedin\Sweden\UPDATED\Sweden_with_skills.csv"  
URI_COLUMN_NAME = "skills"                                                                            
SKILLS_MAP_CSV  = r"C:\Users\Desktop PC\Desktop\ΔΙΠΛΩΜΑΤΙΚΗ\linkedin\skills_en.csv"                             
OUTPUT_CSV      = None  
ENCODING        = "utf-8"  
# =====================

# Διαβάζουμε mapping ESCO: URI -> preferredLabel
map_df = pd.read_csv(SKILLS_MAP_CSV, usecols=["conceptUri","preferredLabel"], dtype=str, low_memory=False, encoding=ENCODING)
uri2label = dict(zip(map_df["conceptUri"], map_df["preferredLabel"]))

inp = Path(INPUT_CSV)
if OUTPUT_CSV is None:
    OUTPUT_CSV = str(inp.with_name(inp.stem + "_with_names.csv"))

# Διαβάζουμε input CSV
df = pd.read_csv(inp, dtype=str, low_memory=False, encoding=ENCODING)
if URI_COLUMN_NAME not in df.columns:
    raise SystemExit(f"Στήλη '{URI_COLUMN_NAME}' δεν βρέθηκε. Βρέθηκαν: {list(df.columns)[:25]}...")

def parse_cell(cell):
    """Επιστρέφει πάντα λίστα από strings (URIs)."""
    if cell is None:
        return []
    if isinstance(cell, list):
        return [str(x) for x in cell]
    s = str(cell).strip()
    if not s:
        return []

    if s.startswith("[") and s.endswith("]"):
        try:
            return [str(x) for x in json.loads(s)]
        except Exception:
            try:
                return [str(x) for x in ast.literal_eval(s)]
            except Exception:
                return [s]

    if "http" in s and "," in s:
        return [t.strip().strip("'").strip('"') for t in s.split(",") if t.strip()]

    return [s]

def map_uris_to_labels(uri_list):
    names, missing = [], 0
    for u in uri_list:
        u = str(u)
        if u.startswith("http://") or u.startswith("https://"):
            lbl = uri2label.get(u)
            if lbl is None:
                missing += 1
                names.append(u)  
            else:
                names.append(lbl)
        else:
            names.append(u)
    return names, missing


lists_of_uris = df[URI_COLUMN_NAME].apply(parse_cell)

mapped_names = []
missing_total = 0
for uris in lists_of_uris:
    names, miss = map_uris_to_labels(uris)
    mapped_names.append(names)
    missing_total += miss

df[f"{URI_COLUMN_NAME}_names"] = mapped_names
df[f"{URI_COLUMN_NAME}_names_text"] = ["; ".join(lst) for lst in mapped_names]


df.to_csv(OUTPUT_CSV, index=False, encoding=ENCODING)
print(f"✅ Έτοιμο: {OUTPUT_CSV}")
print(f"ℹ️ URIs χωρίς mapping (κρατήθηκαν ως URI): {missing_total}")
