#!/usr/bin/env python3
"""
Public Path Finder - WordPress + General
Usage: python3 path_finder.py -u https://example.com -w paths.txt -o report.txt
"""

import requests
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# Default fallback wordlist (agar file na do)
DEFAULT_WORDLIST = [
    "/wp-login.php", "/wp-admin/", "/wp-json/", "/wp-json/wp/v2/",
    "/wp-json/wp/v2/users", "/wp-json/wp/v2/posts", "/wp-json/wp/v2/pages",
    "/xmlrpc.php", "/wp-config.php", "/wp-config.php.bak",
    "/wp-content/", "/wp-content/uploads/", "/wp-content/plugins/",
    "/wp-content/themes/", "/wp-includes/", "/wp-content/debug.log",
    "/.env", "/.htaccess", "/backup.zip", "/backup.sql", "/db.sql",
    "/phpinfo.php", "/info.php", "/readme.html", "/robots.txt",
    "/sitemap.xml", "/.git/HEAD", "/.git/config", "/composer.json",
    "/admin/", "/login/", "/login.php", "/phpmyadmin/", "/uploads/",
    "/api/", "/api/v1/", "/api/v2/", "/server-status", "/debug.log",
]

STATUS_COLORS = {
    200: "✅", 201: "✅",
    301: "➡️ ", 302: "➡️ ",
    401: "🔒", 403: "🚫",
    404: "❌", 500: "💥",
}

def load_wordlist(filepath):
    """File se paths load karo"""
    try:
        with open(filepath, "r") as f:
            paths = []
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):  # blank lines aur comments skip
                    continue
                if not line.startswith("/"):
                    line = "/" + line               # slash missing ho to add kar do
                paths.append(line)
        print(f"[+] Wordlist loaded : {filepath} ({len(paths)} paths)")
        return paths
    except FileNotFoundError:
        print(f"[!] Wordlist file not found: {filepath}")
        print(f"[*] Using default built-in wordlist ({len(DEFAULT_WORDLIST)} paths)")
        return DEFAULT_WORDLIST

def check_path(session, base_url, path):
    url = base_url.rstrip("/") + path
    try:
        r = session.get(url, timeout=8, allow_redirects=False)
        return (url, r.status_code, len(r.content))
    except requests.RequestException:
        return (url, "ERR", 0)

def main():
    parser = argparse.ArgumentParser(
        description="Public Path Finder",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("-u", "--url",
        help="Target URL (e.g. https://example.com)")
    parser.add_argument("-w", "--wordlist",
        help="Path to wordlist file (one path per line)\n"
             "Example: -w paths.txt\n"
             "If not given, built-in default list is used")
    parser.add_argument("-o", "--output",
        default="paths_report.txt",
        help="Output report file (default: paths_report.txt)")
    parser.add_argument("-t", "--threads",
        type=int, default=5,
        help="Threads (default: 5, max: 10)")
    parser.add_argument("--show-404",
        action="store_true",
        help="Show 404 results too (hidden by default)")
    args = parser.parse_args()

    # Input lena
    target   = args.url or input("[*] Target URL  : ").strip()
    wl_file  = args.wordlist or input("[*] Wordlist file (Enter = use default) : ").strip()
    output   = args.output
    threads  = min(args.threads, 10)

    if not target.startswith("http"):
        target = "https://" + target

    # Wordlist decide karo
    if wl_file:
        wordlist = load_wordlist(wl_file)
    else:
        print(f"[*] Using default built-in wordlist ({len(DEFAULT_WORDLIST)} paths)")
        wordlist = DEFAULT_WORDLIST

    print(f"\n[*] Target  : {target}")
    print(f"[*] Output  : {output}")
    print(f"[*] Threads : {threads}")
    print(f"[*] Paths   : {len(wordlist)}")
    print("-" * 60)

    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

    results = []

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {
            executor.submit(check_path, session, target, path): path
            for path in wordlist
        }
        for future in as_completed(futures):
            url, status, size = future.result()
            icon = STATUS_COLORS.get(status, "⚠️ ")
            if status != 404 or args.show_404:
                print(f"  {icon} [{status}] {url}  ({size} bytes)")
            results.append((status, url, size))

    results.sort(key=lambda x: (str(x[0]), x[1]))

    with open(output, "w") as f:
        f.write(f"Path Finder Report\n")
        f.write(f"Target   : {target}\n")
        f.write(f"Wordlist : {wl_file or 'built-in default'}\n")
        f.write(f"Total    : {len(results)} paths checked\n")
        f.write("=" * 60 + "\n\n")

        for label, codes in [
            ("✅  FOUND (200/201)",      [200, 201]),
            ("🔒  AUTH REQUIRED (401)", [401]),
            ("🚫  FORBIDDEN (403)",      [403]),
            ("➡️   REDIRECTS (301/302)", [301, 302]),
            ("💥  SERVER ERROR (500)",   [500]),
        ]:
            matched = [(s, u, sz) for s, u, sz in results if s in codes]
            if matched:
                f.write(f"{label}\n")
                f.write("-" * 40 + "\n")
                for s, u, sz in matched:
                    f.write(f"  [{s}] {u}  ({sz} bytes)\n")
                f.write("\n")

    print(f"\n[+] Done! Report saved to: {output}")
    found = [r for r in results if r[0] in [200, 201, 401, 403]]
    print(f"[+] Interesting paths: {len(found)}")

if __name__ == "__main__":
    main()
