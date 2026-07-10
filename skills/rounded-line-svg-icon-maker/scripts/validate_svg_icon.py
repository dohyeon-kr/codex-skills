#!/usr/bin/env python3
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


MAX_SVG_BYTES = 1024 * 1024
ALLOWED_TAGS = {
    "circle",
    "defs",
    "desc",
    "ellipse",
    "g",
    "line",
    "path",
    "polygon",
    "polyline",
    "rect",
    "svg",
    "symbol",
    "title",
    "use",
}
FORBIDDEN_ATTRIBUTES = {"base", "style"}


def local_name(tag):
    return tag.rsplit("}", 1)[-1]


def fail(message):
    print(f"FAIL: {message}")
    return 1


def main():
    if len(sys.argv) != 2:
        return fail("usage: validate_svg_icon.py path/to/icon.svg")

    path = Path(sys.argv[1])
    if not path.is_file():
        return fail(f"file not found: {path}")

    try:
        with path.open("rb") as handle:
            data = handle.read(MAX_SVG_BYTES + 1)
    except OSError as exc:
        return fail(f"could not read file: {exc}")

    if len(data) > MAX_SVG_BYTES:
        return fail(f"SVG exceeds {MAX_SVG_BYTES} byte limit")

    lowered_data = data.lower()
    if b"<!doctype" in lowered_data or b"<!entity" in lowered_data:
        return fail("DTD and entity declarations are not allowed")
    if b"<?xml-stylesheet" in lowered_data:
        return fail("XML stylesheet declarations are not allowed")

    try:
        root = ET.fromstring(data)
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
        if tag not in ALLOWED_TAGS:
            errors.append(f"forbidden SVG element: <{tag}>")

        for attribute, value in element.attrib.items():
            attribute_name = local_name(attribute).lower()
            normalized_value = value.strip().lower()
            if attribute_name.startswith("on"):
                errors.append(f"event handler attribute is not allowed: {attribute_name}")
            if attribute_name in FORBIDDEN_ATTRIBUTES:
                errors.append(f"forbidden SVG attribute: {attribute_name}")
            if attribute_name == "href" and value and not value.startswith("#"):
                errors.append("only local fragment references are allowed")
            if "url(" in normalized_value or "javascript:" in normalized_value:
                errors.append(f"unsafe reference in attribute: {attribute_name}")

        if element.get("fill") and element.get("fill") != "none":
            errors.append(
                f'<{tag}> uses fill="{element.get("fill")}"; outline icons should avoid fills'
            )

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1

    print("OK: SVG icon passes structural checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
