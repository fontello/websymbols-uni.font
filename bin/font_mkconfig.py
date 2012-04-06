#!/usr/bin/env python

import argparse
import yaml
import fontforge

parser = argparse.ArgumentParser(description='Font config generation tool')
parser.add_argument('-i', '--src_font', type=str, required=True,
    help='Input font')
parser.add_argument('-c', '--config', type=str, required=True,
    help='Output config')

def get_attrs(font, attrs):
    result = {}
    for a in attrs:
        result[a] = getattr(font, a)
    return result

args = parser.parse_args()

font = fontforge.open(args.src_font)

# add comment
config = """---
# This is configuration file for font builder and other support scripts.
# Format is descriped below.
#
#
# css-prefix: "icon-"             # prefix for css-generated classes
# demo-columns: 4                 # used for html demo page generation
#
# font:                           # all vars from here will be used as font
#                                 # params in fontforge
#   ...                           # http://fontforge.sourceforge.net/python.html
#
# transform:                      # Transformations applied to the font,
#                                 # order is "resize, offset"
#   resize: 0.68                  # Rescale glyphs around the center of bbox,
#                                 # resize=1 means no scaling
#   offset: -0.1                  # Shift glyphs vertically, positive offset
#                                 # shifts upward, offset=1 means shift upward
#                                 # to (ascent-descent) units
#
# glyphs:
#   - glyph1_file:                # file name, without extention
#       code: 0xNNN               # Symbol code 0x - hex
#       to: 0xNNN                 # Symbol code 0x - hex, remapped code
#       css: icon-gpyph1-name     # For generated CSS
#       search: [word1, word2]    # Search aliases (array). CSS name will be
#                                 # included automatically
#       transform:                # Additional transformation applied to that
#                                 # glyph
#         offset: 0.2
#
################################################################################
#
# Mapping rules:
#
# 1. Downshift 1Fxxx -> Fxxx, because 1Fxxx codes not shown in Chrome/Opera
#
"""

font_attrs = [
    "version",
    "fontname",
    "fullname",
    "familyname",
    "copyright",
    "ascent",
    "descent",
    "weight"
]

# add beginning part
config += """

css-prefix: "icon-"
demo-columns: 4


font:
  version: "{version}"

  # use !!!small!!! letters a-z, or Opera will fail under OS X
  # fontname will be also used as file name.
  fontname: "{fontname}"

  fullname: "{fullname}"
  familyname: "{familyname}"

  copyright: "{copyright}"

  ascent: {ascent}
  descent: {descent}
  weight: "{weight}"


""".format(**get_attrs(font, font_attrs))

# add glyphs part
config += """glyphs:
"""

for i, glyph in enumerate(font.glyphs()):
    if glyph.unicode == -1:
        continue

    code = '0x%04x' % glyph.unicode

    config += """
  - glyph{i}:
      code: {code}
""".format(i=i, code=code)


open(args.config, "w").write(config)
