#!/usr/bin/env python3
"""
Build a strict Unutterable subset for the Strange House page.

Goals:
- keep only symbols used on the page (+ digits and punctuation)
- enforce ethical glyph swaps in font cmap:
  O/О -> glyph for "0"
  T/Т -> glyph for "t"
"""

from __future__ import annotations

import json
import os
import string
from pathlib import Path

from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "src" / "assets" / "fonts"
LOCALES = ROOT / "src" / "locales"

SRC_FONT = FONTS / "Unutterable-Regular.otf"
DST_FONT = FONTS / "Unutterable-Regular-subset.woff2"
CHARS_FILE = FONTS / "unutterable-subset-chars.txt"


def collect_chars() -> set[str]:
    chars: set[str] = set()

    for lang in ("en", "ru"):
        data = json.loads((LOCALES / f"{lang}.json").read_text(encoding="utf-8"))
        sh = data["strangeHouse"]
        nav = data["nav"]

        meta = sh["meta"]
        ld = sh.get("ld") or {}
        fields: list[str] = [
            sh["title"],
            meta.get("title", ""),
            meta.get("description", ""),
            meta.get("ogImageAlt", ""),
            sh["dialogue"]["visitorSpeaker"],
            sh["dialogue"]["visitorLine"],
            sh["dialogue"]["studioSpeaker"],
            sh["dialogue"]["studioLine"],
            sh["question"],
            sh["choices"]["download"],
            sh["choices"].get("downloadAria", ""),
            sh["choices"]["back"],
            sh["images"]["heroAlt"],
            sh["images"]["interiorAlt"],
            sh["images"]["roadAlt"],
            nav["en"],
            nav["ru"],
        ] + sh["paragraphs"]
        for _key, val in ld.items():
            if isinstance(val, str):
                fields.append(val)

        for text in fields:
            chars.update(text)

    # Static UI text from templates.
    chars.update({"E", "N", "Р", "У"})
    chars.update("(c) 2023–2026")

    # Always keep full digits.
    chars.update("0123456789")

    # Keep punctuation and braces for future copy/copyright use.
    chars.update(string.punctuation)
    chars.update("«»„“”’‘…—–№←©")

    # Drop control whitespace except regular space.
    chars.discard("\n")
    chars.discard("\t")
    return chars


def save_chars(chars: set[str]) -> None:
    ordered = "".join(sorted(chars))
    CHARS_FILE.write_text(ordered + "\n", encoding="utf-8")


def build_subset(chars: set[str]) -> None:
    font = TTFont(str(SRC_FONT))
    opts = Options()
    opts.flavor = "woff2"
    opts.drop_tables += ["SVG"]
    subsetter = Subsetter(options=opts)
    subsetter.populate(text="".join(sorted(chars)))
    subsetter.subset(font)
    font.save(str(DST_FONT))


def remap_ethical_glyphs() -> None:
    font = TTFont(str(DST_FONT))
    cmap = font["cmap"]

    # Resolve target glyph names from safe source codepoints.
    glyph_zero = None
    glyph_t = None
    for table in cmap.tables:
        glyph_zero = glyph_zero or table.cmap.get(0x0030)  # "0"
        glyph_t = glyph_t or table.cmap.get(0x0074)  # "t"

    if not glyph_zero or not glyph_t:
        raise RuntimeError("Safe source glyphs for '0' or 't' are missing in subset.")

    for table in cmap.tables:
        table.cmap[0x004F] = glyph_zero  # Latin O
        table.cmap[0x041E] = glyph_zero  # Cyrillic О
        table.cmap[0x0054] = glyph_t  # Latin T
        table.cmap[0x0422] = glyph_t  # Cyrillic Т

    font.save(str(DST_FONT))


def to_unicode_ranges(chars: set[str]) -> str:
    points = sorted(ord(ch) for ch in chars)
    ranges: list[tuple[int, int]] = []
    start = end = points[0]
    for p in points[1:]:
        if p == end + 1:
            end = p
            continue
        ranges.append((start, end))
        start = end = p
    ranges.append((start, end))

    lines = []
    for a, b in ranges:
        if a == b:
            lines.append(f"U+{a:04X}")
        else:
            lines.append(f"U+{a:04X}-{b:04X}")
    return ",\n    ".join(lines) + ";"


def main() -> None:
    chars = collect_chars()
    if not chars:
        raise RuntimeError("No characters collected for subset.")
    save_chars(chars)
    build_subset(chars)
    remap_ethical_glyphs()

    size = os.path.getsize(DST_FONT)
    print(f"Wrote {DST_FONT} ({size} bytes)")
    print("Suggested unicode-range:")
    print(to_unicode_ranges(chars))


if __name__ == "__main__":
    main()
