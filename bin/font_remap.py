#!/usr/bin/env python

import argparse
import yaml
import fontforge


# returns list of tuples:
# [(from_code1, to_code1), (from_code2, to_code2), ...]
def get_remap_config(glyphs):
    def get_remap_item(glyph):
        name, glyph = glyph.items()[0]
        return (glyph.get('from', glyph['code']), glyph['code'])
    return [get_remap_item(glyph) for glyph in glyphs]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Font remap tool')
    parser.add_argument('-c', '--config',   type=str, required=True,
        help='Config example: ../config.yml')
    parser.add_argument('-i', '--src_font', type=str, required=True,
        help='Input font')
    parser.add_argument('-o', '--dst_font', type=str, required=True,
        help='Output font')

    args = parser.parse_args()

    config = yaml.load(open(args.config, 'r'))

    remap_config = get_remap_config(config['glyphs'])
    #print "remap_config=", remap_config
    from_codes, to_codes = zip(*remap_config)

    # validate config: from codes
    if len(from_codes) > len(set(from_codes)):
        print "Error: from codes have duplicates"   # FIXME
        exit(1)

    # validate config: to codes
    if len(to_codes) > len(set(to_codes)):
        print "Error: to codes have duplicates"     # FIXME
        exit(1)

    codes_to_remap = [item for item in remap_config if item[0] != item[1]]
    #print "codes_to_remap=", codes_to_remap

    font = fontforge.open(args.src_font)

    # tmp font for copy()/paste()
    tmp_font = fontforge.font()
    tmp_font.encoding = 'Unicode'

    #print "move glyphs to tmp_font"
    for from_code, to_code in codes_to_remap:
        #print "0x%04x -> 0x%04x" % (from_code, to_code)
        font.selection.select(("unicode",), from_code)
        font.cut()
        tmp_font.selection.select(("unicode",), to_code)
        tmp_font.paste()

    #print "move glyphs from tmp_font to the right places"
    for from_code, to_code in codes_to_remap:
        #print "0x%04x -> 0x%04x" % (to_code, to_code)
        tmp_font.selection.select(("unicode",), to_code)
        tmp_font.cut()
        font.selection.select(("unicode",), to_code)
        font.paste()

    font.generate(args.dst_font)

    exit(0)
