#!/usr/bin/env python3
"""
JS File Analyzer
Usage: python3 js_analyzer.py -i js_files.txt -o report.txt
"""

import re
import argparse
import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

ENDPOINT_PATTERN = re.compile(r'''["'](\/[a-zA-Z0-9_\-\/\.\?\=\&\%]{2,})["']''')
VERSION_PATTERN  = re.compile(r'(?i)(version["\']?\s*[:=]\s*["\']?[\w\.\-]+|v\d+\.\d+(\.\d+)?)')
SECRET_PATTERN   = re.compile(
    r'(?i)(api[_-]?key|secret|token|access[_-]?key|password|authorization)["\']?\s*[:=]\s*["\']([A-Za-z0-9\-_\.\/+=]{8,})["\']'
)
URL_PATTERN      = re.compile(r'https?:\/\/[^\s"\'<>\)]+')


def analyze_js(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        content = resp.text
    except requests.RequestException as e:
        return {"error": str(e)}

    result = {"endpoints": set(), "versions": set(), "secrets": set(), "urls": set()}

    for m in ENDPOINT_PATTERN.findall(content):
        if len(m) < 100:
            result["endpoints"].add(m)

    for m in VERSION_PATTERN.findall(content):
        v = m[0] if isinstance(m, tuple) else m
        result["versions"].add(v.strip())

    for m in SECRET_PATTERN.findall(content):
        key_name, value = m
        result["secrets"].add(f"{key_name} = {value}")

    for m in URL_PATTERN.findall(content):
        result["urls"].add(m)

    return result


def main():
    parser = argparse.ArgumentParser(
        description="JS File Analyzer - Extracts versions, endpoints, secrets from JS files",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-i", "--input",
        default="js_files.txt",
        help="Input file containing JS URLs (default: js_files.txt)"
    )
    parser.add_argument(
        "-o", "--output",
        default="js_analysis_report.txt",
        help="Output report file name (default: js_analysis_report.txt)"
    )
    args = parser.parse_args()

    print(f"[*] Input  file : {args.input}")
    print(f"[*] Output file : {args.output}")
    print("-" * 50)

    try:
        with open(args.input) as f:
            js_urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[!] File not found: {args.input}")
        return

    print(f"[*] Total JS files to scan: {len(js_urls)}\n")

    report_lines = []

    for idx, url in enumerate(js_urls, 1):
        print(f"[{idx}/{len(js_urls)}] Analyzing: {url}")
        data = analyze_js(url)

        report_lines.append("=" * 80)
        report_lines.append(f"FILE: {url}")
        report_lines.append("=" * 80)

        if "error" in data:
            report_lines.append(f"  [ERROR] {data['error']}")
            continue

        if data["versions"]:
            report_lines.append("\n[Version Strings Found]")
            for v in sorted(data["versions"]):
                report_lines.append(f"  - {v}")

        if data["secrets"]:
            report_lines.append("\n[!! Possible Secrets/Keys Found !!]")
            for s in sorted(data["secrets"]):
                report_lines.append(f"  - {s}")

        if data["endpoints"]:
            report_lines.append("\n[Possible Endpoints/Paths Found]")
            for e in sorted(data["endpoints"])[:50]:
                report_lines.append(f"  - {e}")
            if len(data["endpoints"]) > 50:
                report_lines.append(f"  ... and {len(data['endpoints'])-50} more")

        if data["urls"]:
            report_lines.append("\n[External URLs Found]")
            for u in sorted(data["urls"])[:30]:
                report_lines.append(f"  - {u}")
            if len(data["urls"]) > 30:
                report_lines.append(f"  ... and {len(data['urls'])-30} more")

        report_lines.append("")

    with open(args.output, "w") as f:
        f.write("\n".join(report_lines))

    print(f"\n[+] Done! Report saved to: {args.output}")


if __name__ == "__main__":
    main()
