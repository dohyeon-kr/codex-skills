#!/usr/bin/env python3
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


FORBIDDEN_TAGS = {
    "filter",
    "foreignObject",
    "image",
    "linearGradient",
    "mask",
    "pattern",
    "radialGradient",
    "script",
    "style",
    "text",
}


def local_name(tag):
    return tag.rsplit("}", 1)[-1]


def fail(message):
    print(f"FAIL: {message}")
    return 1


def main():
    if len(sys.argv) != 2:
        return fail("usage: validate_svg_icon.py path/to/icon.svg")

    path = Path(sys.argv[1])
    if not path.exists():
        return fail(f"file not found: {path}")

    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        return fail(f"invalid XML: {exc}")

    if local_name(root.tag) != "svg":
        return fail("root element must be <svg>")

    errors = []
    if root.get("viewBox") != "0 0 24 24":
        errors.append('root should use viewBox="0 0 24 24"')
    if root.get("fill") not in ("none", None):
        errors.append('root fill should be "none" or omitted')
    if root.get("stroke") not in ("currentColor", None):
        errors.append('root stroke should be "currentColor" or omitted')
    if root.get("stroke-linecap") not in ("round", None):
        errors.append('root stroke-linecap should be "round" or omitted')
    if root.get("stroke-linejoin") not in ("round", None):
        errors.append('root stroke-linejoin should be "round" or omitted')

    for element in root.iter():
        tag = local_name(element.tag)
        if tag in FORBIDDEN_TAGS:
            errors.append(f"forbidden SVG element: <{tag}>")
        href = element.get("href") or element.get("{http://www.w3.org/1999/xlink}href")
        if href and ("base64" in href or href.startswith(("http:", "https:", "data:"))):
            errors.append("external or embedded image/reference data is not allowed")
        if element.get("fill") and element.get("fill") != "none":
            errors.append(f'<{tag}> uses fill="{element.get("fill")}"; outline icons should avoid fills')

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1

    print("OK: SVG icon passes structural checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
