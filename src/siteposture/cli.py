from __future__ import annotations

import argparse
import json
from pathlib import Path

from .analyzer import analyze, as_jsonable, as_markdown, parse_raw_headers
from .fetch import fetch_once


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Safe-by-default HTTP response header posture checker")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--headers-file", type=Path, help="Analyze saved raw HTTP response headers")
    source.add_argument("--url", help="Perform one non-crawling GET against an authorized URL")
    parser.add_argument("--authorized", action="store_true", help="Confirm authorization for online checking")
    parser.add_argument("--scheme", choices=["http", "https"], default="https", help="Scheme for offline header analysis")
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown")
    parser.add_argument("--timeout", type=float, default=10.0)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.url:
        if not args.authorized:
            raise SystemExit("Online mode requires --authorized. Check only systems you own or are allowed to test.")
        snapshot = fetch_once(args.url, timeout=args.timeout)
        headers, scheme, target = snapshot.headers, args.url.split(":", 1)[0].lower(), f"{snapshot.url} (HTTP {snapshot.status})"
    else:
        headers = parse_raw_headers(args.headers_file.read_text(encoding="utf-8"))
        scheme, target = args.scheme, str(args.headers_file)

    findings = analyze(headers, scheme=scheme)
    if args.format == "json":
        print(json.dumps({"target": target, "findings": as_jsonable(findings)}, ensure_ascii=False, indent=2))
    else:
        print(as_markdown(findings, target))
    return 1 if any(item.severity in {"critical", "high", "medium"} for item in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())


