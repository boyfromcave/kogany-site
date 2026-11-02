#!/usr/bin/env python3
"""Fail if any internal href/src in public/ points at a file that does not exist."""
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
bad = 0
for page in root.rglob("*.html"):
    for ref in re.findall(r'(?:href|src)="(/[^"#?]*)', page.read_text(encoding="utf-8")):
        target = root / ref.lstrip("/")
        if ref.endswith("/"):
            target = target / "index.html"
        if not target.exists():
            print(f"{page.relative_to(root)}: broken link {ref}")
            bad += 1
print(f"{bad} broken internal links")
sys.exit(1 if bad else 0)
