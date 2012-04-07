#!/usr/bin/env python

import sys
import argparse
import fontforge


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Font codes lister tool')
    parser.add_argument('-i', '--src_font', type=str, required=True,
        help='Input font')

    args = parser.parse_args()

    try:
        font = fontforge.open(args.src_font)
    except:
        sys.exit(1)

    codes = [glyph.unicode for glyph in font.glyphs() if glyph.unicode != -1]
    for code in sorted(codes):
        print "0x%04x" % code

    sys.exit(0)
