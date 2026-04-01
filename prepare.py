import os
import json
import hashlib
import re
import shutil

SGF_SOURCE = r"C:\Users\utku\Desktop\GoDATAbase\games"
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
SGF_OUT = os.path.join(OUTPUT_DIR, "sgf")
os.makedirs(SGF_OUT, exist_ok=True)

def extract_field(content, field):
    match = re.search(rf'{field}\[([^\]]*)\]', content)
    return match.group(1).strip() if match else ""

def extract_year(date_str):
    match = re.search(r'(\d{4})', date_str)
    return match.group(1) if match else ""

def extract_title(event_str):
    match = re.search(r'(\d+(?:st|nd|rd|th)?\s+)?(.+)', event_str)
    return match.group(2).strip() if match else event_str

index = []
errors = 0
processed = 0

for root, dirs, files in os.walk(SGF_SOURCE):
    for filename in files:
        if not filename.lower().endswith('.sgf'):
            continue
        filepath = os.path.join(root, filename)
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            hash_val = hashlib.md5(content.encode('utf-8', errors='ignore')).hexdigest()[:12]

            black   = extract_field(content, 'PB')
            white   = extract_field(content, 'PW')
            date    = extract_field(content, 'DT')
            result  = extract_field(content, 'RE')
            event   = extract_field(content, 'EV')
            country = extract_field(content, 'PC') or extract_field(content, 'BC') or ""
            rank_b  = extract_field(content, 'BR')
            rank_w  = extract_field(content, 'WR')

            year       = extract_year(date)
            title_name = extract_title(event) if event else ""

            dest = os.path.join(SGF_OUT, f"{hash_val}.sgf")
            shutil.copy2(filepath, dest)

            index.append({
                "hash": hash_val,
                "black": black,
                "white": white,
                "rankB": rank_b,
                "rankW": rank_w,
                "date": date,
                "year": year,
                "result": result,
                "event": event,
                "title": title_name,
                "country": country
            })

            processed += 1
            if processed % 1000 == 0:
                print(f"{processed} dosya işlendi...")

        except Exception as e:
            errors += 1

with open(os.path.join(OUTPUT_DIR, 'index.json'), 'w', encoding='utf-8') as f:
    json.dump(index, f, ensure_ascii=False, indent=2)

print(f"\nTamamlandı! {processed} oyun işlendi, {errors} hata.")
print(f"index.json oluşturuldu.")