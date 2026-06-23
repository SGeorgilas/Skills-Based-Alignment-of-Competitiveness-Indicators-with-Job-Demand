# skills_extractor.py
from esco_skill_extractor import SkillExtractor
import pandas as pd
from tqdm import tqdm  # pip install tqdm
import time

# --- ΡΥΘΜΙΣΕΙΣ ---
INPUT_PATH  = r"C:/Users/Desktop PC/Desktop/ΔΙΠΛΩΜΑΤΙΚΗ/linkedin/UK/UPDATED/UK_merged_deduped_final.csv"
OUTPUT_PATH = r"C:/Users/Desktop PC/Desktop/ΔΙΠΛΩΜΑΤΙΚΗ/linkedin/UK/UPDATED/UK_with_skills.csv"
TEXT_COL    = "descriptionText"   
BATCH       = 50                  
# -------------------

t0 = time.time()

# 1) Φόρτωση CSV
print("CSV LOADED!")
df = pd.read_csv(INPUT_PATH, dtype=str, low_memory=False)

if TEXT_COL not in df.columns:
    raise SystemExit(f"Στήλη '{TEXT_COL}' δεν βρέθηκε. Διαθέσιμες: {list(df.columns)[:20]}...")

# 2) Περιγραφές ως καθαρά strings ("" για NaN)
descriptions = ["" if pd.isna(x) else str(x) for x in df[TEXT_COL].values]
N = len(descriptions)
print("DESCRIPTIONS LOADED!")
print(f"Σύνολο γραμμών: {N}")

# 3) Αρχικοποίηση extractor 
skill_extractor = SkillExtractor()

# 4) Εξαγωγή SKILLS με progress bar σε ΓΡΑΜΜΕΣ (ανά 50)
skills_out = []

with tqdm(total=N, desc="Extracting skills", unit="rows", dynamic_ncols=True) as pbar:
    for start in range(0, N, BATCH):
        chunk = descriptions[start:start + BATCH]
        skills_out.extend(skill_extractor.get_skills(chunk))
        pbar.update(len(chunk))  

# 5) Εγγραφή αποτελεσμάτων
df["skills"] = skills_out
df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
print(f"Done → {OUTPUT_PATH}  (rows: {len(df)}, elapsed: {time.time()-t0:.1f}s)")
