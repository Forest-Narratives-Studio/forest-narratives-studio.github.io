#!/usr/bin/env python3
"""
Build WOFF2 subsets for Voluntary Consent page fonts.

Faces: CozetteVector (regular body/CTA), TT2020Base-Regular (short description),
denistina_en (title), Tiny5-Regular (lang/copyright micro).
Charset: voluntaryConsent + nav locale strings (ru/en), plus digits/punctuation.
When locales still hold stub copy, also merge glyph coverage from the Steam
promo markdown (RU+EN) so subsets already cover final promo text.
"""

from __future__ import annotations

import json
import os
import re
import string
from pathlib import Path

from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parent.parent
FONTS_OUT = ROOT / "src" / "assets" / "fonts"
LOCALES = ROOT / "src" / "locales"
CHARS_FILE = FONTS_OUT / "voluntary-consent-subset-chars.txt"

PROMO_MD_CANDIDATES = [
    Path(os.environ["OMB_STEAM_PROMO_MD"]) if "OMB_STEAM_PROMO_MD" in os.environ else None,
    ROOT.parent / "OMB" / "OMB_docs" / "Steam" / "Промо текст.md",
    Path(r"C:\Projects\OMB\OMB_docs\Steam\Промо текст.md"),
]

SRC_FONT_DIR_CANDIDATES = [
    Path(os.environ["OMB_FONTS_DIR"]) if "OMB_FONTS_DIR" in os.environ else None,
    ROOT.parent / "OMB" / "OMB_assets" / "output" / "fonts",
    Path(r"C:\Projects\OMB\OMB_assets\output\fonts"),
]

FACES: list[tuple[str, str]] = [
    ("CozetteVector.ttf", "CozetteVector-subset.woff2"),
    ("TT2020Base-Regular.ttf", "TT2020Base-Regular-subset.woff2"),
    ("denistina_en.ttf", "denistina_en-subset.woff2"),
    ("Tiny5-Regular.ttf", "Tiny5-Regular-subset.woff2"),
]

BBCODE_RE = re.compile(r"\[/?[^\]]+\]")
FENCE_RE = re.compile(r"```(?:[^\n]*)\n(.*?)```", re.DOTALL)


def resolve_first(candidates: list[Path | None], label: str) -> Path:
    for candidate in candidates:
        if candidate is None:
            continue
        if candidate.exists():
            return candidate
    tried = ", ".join(str(c) for c in candidates if c is not None)
    raise FileNotFoundError(f"{label} not found. Tried: {tried}")


def walk_strings(node: object, out: list[str]) -> None:
    if isinstance(node, str):
        out.append(node)
        return
    if isinstance(node, dict):
        for value in node.values():
            walk_strings(value, out)
        return
    if isinstance(node, list):
        for item in node:
            walk_strings(item, out)


def collect_locale_fields() -> list[str]:
    fields: list[str] = []
    for lang in ("en", "ru"):
        data = json.loads((LOCALES / f"{lang}.json").read_text(encoding="utf-8"))
        walk_strings(data.get("voluntaryConsent") or {}, fields)
        walk_strings(data.get("nav") or {}, fields)
    return fields


def collect_promo_chars(promo_path: Path) -> set[str]:
    text = promo_path.read_text(encoding="utf-8")
    chars: set[str] = set()
    for block in FENCE_RE.findall(text):
        cleaned = BBCODE_RE.sub("", block)
        chars.update(cleaned)
    return chars


def locales_look_like_stubs(locale_text: str) -> bool:
    """True when voluntaryConsent still looks stubby / incomplete for promo."""
    lowered = locale_text.casefold()
    stub_markers = (
        "заглушк",
        "placeholder",
        "в разработке",
        "under development",
        "coming soon",
    )
    if any(marker in lowered for marker in stub_markers):
        return True
    # Promo has distinctive long phrases; absence suggests stubs.
    promo_markers = ("нейросохранност", "neural safekeeping", "аутопси", "autopsy")
    return not any(marker in lowered for marker in promo_markers)


def collect_chars(promo_path: Path) -> set[str]:
    locale_fields = collect_locale_fields()
    locale_text = "\n".join(locale_fields)
    chars: set[str] = set(locale_text)

    # Static UI / chrome that may appear beside locale strings.
    chars.update({"E", "N", "Р", "У"})
    chars.update("(c) 2023–2026")

    chars.update("0123456789")
    chars.update(string.punctuation)
    chars.update("«»„“”’‘…—–№←©°")

    if locales_look_like_stubs(locale_text):
        promo_chars = collect_promo_chars(promo_path)
        chars.update(promo_chars)
        print(f"Locales look stubby; merged promo charset from {promo_path}")
    else:
        print(f"Using final locale charset ({len(locale_fields)} strings from voluntaryConsent+nav)")

    chars.discard("\n")
    chars.discard("\t")
    chars.discard("\r")
    return chars


def save_chars(chars: set[str]) -> None:
    ordered = "".join(sorted(chars))
    CHARS_FILE.write_text(ordered + "\n", encoding="utf-8")


def build_subset(src: Path, dst: Path, chars: set[str]) -> None:
    font = TTFont(str(src))
    opts = Options()
    opts.flavor = "woff2"
    opts.drop_tables += ["SVG"]
    subsetter = Subsetter(options=opts)
    subsetter.populate(text="".join(sorted(chars)))
    subsetter.subset(font)
    font.save(str(dst))


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
    src_dir = resolve_first(SRC_FONT_DIR_CANDIDATES, "OMB fonts directory")
    promo_path = resolve_first(PROMO_MD_CANDIDATES, "Steam promo markdown")
    FONTS_OUT.mkdir(parents=True, exist_ok=True)

    chars = collect_chars(promo_path)
    if not chars:
        raise RuntimeError("No characters collected for subset.")
    save_chars(chars)

    for src_name, dst_name in FACES:
        src = src_dir / src_name
        if not src.exists():
            raise FileNotFoundError(f"Source font missing: {src}")
        dst = FONTS_OUT / dst_name
        build_subset(src, dst, chars)
        size = os.path.getsize(dst)
        print(f"Wrote {dst} ({size} bytes)")

    # Drop unused Bold subset if present from prior builds.
    legacy_bold = FONTS_OUT / "CozetteVectorBold-subset.woff2"
    if legacy_bold.exists():
        legacy_bold.unlink()
        print(f"Removed legacy {legacy_bold.name}")

    print(f"Wrote {CHARS_FILE} ({len(chars)} unique chars)")
    print("Suggested unicode-range:")
    print(to_unicode_ranges(chars))


if __name__ == "__main__":
    main()
