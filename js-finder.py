#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque

TARGET   = input("[*] Target URL  : ").strip()
OUTPUT   = input("[*] Output file : ").strip() or "js_files.txt"
MAX_PAGES = 20

visited_pages = set()
found_js      = set()
domain        = urlparse(TARGET).netloc
queue         = deque([TARGET])

session = requests.Session()
session.headers["User-Agent"] = "JS-Auditor/1.0"

print(f"\n[*] Crawling {TARGET} (max {MAX_PAGES} pages)...\n")

while queue and len(visited_pages) < MAX_PAGES:
    url = queue.popleft()
    if url in visited_pages:
        continue
    visited_pages.add(url)
    print(f"  [crawl] {url}")

    try:
        r = session.get(url, timeout=10)
    except Exception:
        continue

    soup = BeautifulSoup(r.text, "html.parser")

    for script in soup.find_all("script", src=True):
        js_url = urljoin(url, script["src"])
        found_js.add(js_url)

    for a in soup.find_all("a", href=True):
        link   = urljoin(url, a["href"])
        parsed = urlparse(link)
        if parsed.netloc == domain:
            clean = parsed.scheme + "://" + parsed.netloc + parsed.path
            if clean not in visited_pages:
                queue.append(clean)

print(f"\n[+] Pages Crawled : {len(visited_pages)}")
print(f"[+] JS Files Found: {len(found_js)}\n")

with open(OUTPUT, "w") as f:
    for js in sorted(found_js):
        try:
            status = session.head(js, allow_redirects=True, timeout=10).status_code
        except:
            status = "ERR"
        print(f"  [{status}] {js}")
        f.write(js + "\n")

print(f"\n[+] Saved to: {OUTPUT}"
