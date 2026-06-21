## WordPress  tool

A lightweight recon toolkit for WordPress and general web targets.

---

## Installation

```bash
pip install requests beautifulsoup4
```

---

## Tools

### 1. `hiddenpath.py` — Hidden Path Scanner

Scans a target for publicly accessible sensitive files and directories such as `/wp-config.php`, `/.env`, `/backup.zip`, `/phpmyadmin/`, and more.

```bash
python3 hiddenpath.py -u https://target.com
python3 hiddenpath.py -u https://target.com -w paths.txt -o report.txt
```

| Flag | Description |
|------|-------------|
| `-u` | Target URL |
| `-w` | Custom wordlist file (optional) |
| `-o` | Output file (default: `paths_report.txt`) |
| `-t` | Thread count (default: 5, max: 10) |
| `--show-404` | Include 404 results in output |

---

### 2. `jsfinder.py` — JS File Crawler

Crawls a website and collects all JavaScript file URLs, then verifies their HTTP status.

```bash
python3 jsfinder.py
# Prompts for: Target URL and output filename
```

Output → `js_files.txt`

---

### 3. `jsscan.py` — JS File Analyzer

Analyzes JavaScript files for exposed endpoints, API keys, version strings, and external URLs.

```bash
python3 jsscan.py -i js_files.txt -o report.txt
```

| Flag | Description |
|------|-------------|
| `-i` | Input file containing JS URLs |
| `-o` | Output report file (default: `js_analysis_report.txt`) |

---

## Workflow

```bash
# Step 1 — Scan for hidden paths
python3 hiddenpath.py -u https://target.com

# Step 2 — Crawl and collect JS files
python3 jsfinder.py

# Step 3 — Analyze collected JS files
python3 jsscan.py -i js_files.txt
```

> ⚠️ Use only on targets you own or have explicit permission to test.

## Auther
SIDDHARTH
