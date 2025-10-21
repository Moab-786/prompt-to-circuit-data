import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pathlib import Path
import time
from collections import deque

# -----------------------------
# CONFIGURATION
# -----------------------------
START_URL = "https://www.asic-world.com/"
DOMAIN = "asic-world.com"
OUTPUT_DIR = Path("data/processed")
OUTPUT_FILE = OUTPUT_DIR / "asicworld_vlinks.txt"
HEADERS = {"User-Agent": "Mozilla/5.0"}

MAX_DEPTH = 4          # How deep to go in the site
REQUEST_DELAY = 1.0    # Seconds between requests
TIMEOUT = 10           # Timeout for requests

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def get_links(url):
    """Return internal links and .v file links on the given page."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
    except Exception as e:
        print(f"❌ Failed {url}: {e}")
        return [], []

    soup = BeautifulSoup(r.text, "html.parser")
    internal_links, verilog_links = [], []

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith("#") or href.startswith("javascript"):
            continue

        # Safely handle invalid or malformed URLs
        try:
            full_url = urljoin(url, href)
            parsed = urlparse(full_url)
        except Exception:
            continue

        # Keep only same-domain pages
        if DOMAIN not in parsed.netloc:
            continue

        # Filter file types
        if full_url.endswith(".v"):
            verilog_links.append(full_url)
        elif full_url.endswith(".html") or full_url.endswith("/"):
            internal_links.append(full_url)

    return list(set(internal_links)), list(set(verilog_links))


# -----------------------------
# CRAWLER (BFS)
# -----------------------------
def crawl(start_url):
    """Breadth-first crawl to collect all .v file URLs."""
    visited = set()
    discovered_vfiles = set()
    queue = deque([(start_url, 0)])
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("\n--- Starting ASIC-World Deep Crawl ---")
    while queue:
        current_url, depth = queue.popleft()
        if depth > MAX_DEPTH or current_url in visited:
            continue

        visited.add(current_url)
        print(f"[Depth {depth}] 🔍 {current_url}")

        internal, vfiles = get_links(current_url)

        # Save discovered Verilog files
        for v in vfiles:
            if v not in discovered_vfiles:
                discovered_vfiles.add(v)
                with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                    f.write(v + "\n")
                print(f"   ➕ Found Verilog file: {v}")

        # Queue internal pages for next depth
        for link in internal:
            if link not in visited:
                queue.append((link, depth + 1))

        time.sleep(REQUEST_DELAY)

    print(f"\n✅ Crawl completed — {len(discovered_vfiles)} Verilog files found.")
    print(f"Saved at: {OUTPUT_FILE}\n")


if __name__ == "__main__":
    crawl(START_URL)
