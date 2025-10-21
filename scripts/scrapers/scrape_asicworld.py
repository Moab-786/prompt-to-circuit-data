import requests
import json
from pathlib import Path
import time
import re

# -----------------------------
# CONFIGURATION
# -----------------------------
INPUT_FILE = Path("data/processed/asicworld_vlinks.txt")
OUTPUT_DIR = Path("data/raw")
OUTPUT_FILE = OUTPUT_DIR / "raw_asicworld_crawled.jsonl"

HEADERS = {"User-Agent": "Mozilla/5.0"}
REQUEST_DELAY = 0.7
TIMEOUT = 10

# Keywords to detect *unwanted/testbench* examples
EXCLUDE_KEYWORDS = [
    "tb", "test", "wave", "bench", "stimulus", "driver", "monitor", "checker"
]

# Keywords that match *useful circuits*
INCLUDE_KEYWORDS = [
    "and", "or", "nand", "nor", "xor", "xnor", "not", "gate",
    "adder", "subtractor", "multiplier", "counter", "mux", "decoder",
    "encoder", "flipflop", "latch", "register", "fsm", "alu", "comparator"
]


# -----------------------------
# CORE FUNCTIONS
# -----------------------------
def is_relevant(filename: str, code: str) -> bool:
    """Decide whether the file is a useful example for prompt→circuit mapping."""
    name = filename.lower()

    # Exclude if it's a testbench/sim utility
    if any(kw in name for kw in EXCLUDE_KEYWORDS):
        return False

    # Include if filename or code contains relevant keywords
    if any(kw in name for kw in INCLUDE_KEYWORDS):
        return True
    if any(re.search(rf"\b{kw}\b", code.lower()) for kw in INCLUDE_KEYWORDS):
        return True

    # Default reject
    return False


def fetch_file(url: str):
    """Fetch Verilog file and return structured data if relevant."""
    filename = url.split("/")[-1]
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
    except Exception as e:
        print(f"❌ {filename}: {e}")
        return None

    code = resp.text.strip()

    if not code or len(code) < 30:
        return None
    if not is_relevant(filename, code):
        print(f"⚪ Skipped non-relevant: {filename}")
        return None

    # Create descriptive prompt from filename
    title = filename.replace(".v", "").replace("_", " ").title()
    prompt = f"Write Verilog code for {title}."

    return {
        "url": url,
        "filename": filename,
        "prompt": prompt,
        "verilog_code": code,
        "meta_tags": {"source": "asic-world", "category": "auto-crawled"}
    }


def main():
    print("\n--- Starting ASIC-World File Fetcher ---")
    if not INPUT_FILE.exists():
        print(f"❌ Input file not found: {INPUT_FILE}")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    urls = [u.strip() for u in INPUT_FILE.read_text().splitlines() if u.strip()]
    print(f"📂 Loaded {len(urls)} URLs to fetch.\n")

    all_examples = []
    for i, url in enumerate(urls, start=1):
        print(f"[{i}/{len(urls)}] ⬇️  {url}")
        data = fetch_file(url)
        if data:
            all_examples.append(data)
            with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(data, ensure_ascii=False) + "\n")
        time.sleep(REQUEST_DELAY)

    print(f"\n✅ Finished fetching. {len(all_examples)} relevant examples saved → {OUTPUT_FILE}\n")


if __name__ == "__main__":
    main()
