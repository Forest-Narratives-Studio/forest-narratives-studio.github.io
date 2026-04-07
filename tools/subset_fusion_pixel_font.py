#!/usr/bin/env python3
"""
Rebuild src/assets/fonts/fusion-pixel-12px-proportional-latin.woff2 as a tiny subset.

The upstream "latin" regional woff2 (~700 KiB) embeds vast Unicode coverage. This site
only needs ASCII + Russian Cyrillic + a few punctuation marks.

Full source for regeneration:
  https://github.com/TakWolf/fusion-pixel-font/releases
  → fusion-pixel-font-12px-proportional-otf.woff2-v*.zip → *-latin.otf.woff2

Usage:
  pip install fonttools brotli
  python tools/subset_fusion_pixel_font.py [path/to/full-latin.woff2]
"""

from __future__ import annotations

import os
import sys

try:
    from fontTools.ttLib import TTFont
    from fontTools.subset import Options, Subsetter
except ImportError:
    print("Install: pip install fonttools brotli", file=sys.stderr)
    raise SystemExit(1)


def build_unicodes() -> list[int]:
    """Ranges and codepoints used by RU/EN copy on the site; expand if locales add symbols."""
    out: set[int] = set()
    for a, b in ((0x20, 0x7E), (0x400, 0x45F)):
        out.update(range(a, b + 1))
    out.update(
        {
            0xA0,  # nbsp
            0xAB,
            0xBB,  # « »
            0x2013,
            0x2014,  # – —
            0x201C,
            0x201D,  # “ ”
            0x2026,  # …
        }
    )
    return sorted(out)


def main() -> None:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fonts_dir = os.path.join(root, "src", "assets", "fonts")
    default_full = os.path.join(fonts_dir, "fusion-pixel-12px-proportional-latin.full.woff2")
    src = sys.argv[1] if len(sys.argv) > 1 else default_full
    dst = os.path.join(fonts_dir, "fusion-pixel-12px-proportional-latin.woff2")

    if not os.path.isfile(src):
        print("Source font not found:", src, file=sys.stderr)
        print("Pass path to full regional latin woff2, or save it as:", default_full, file=sys.stderr)
        raise SystemExit(1)

    font = TTFont(src)
    opts = Options()
    opts.flavor = "woff2"
    subs = Subsetter(options=opts)
    subs.populate(unicodes=build_unicodes())
    subs.subset(font)
    os.makedirs(fonts_dir, exist_ok=True)
    font.save(dst)

    print("Wrote", dst, "—", os.path.getsize(dst), "bytes")


if __name__ == "__main__":
    main()
