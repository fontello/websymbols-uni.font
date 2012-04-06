#!/usr/bin/env python

import sys
import argparse
import yaml
import fontforge
import psMat


error = sys.stderr.write


# returns dict representing duplicate values of seq
# in seq = [1,1,2,3,3,3,3,4,5], out dict {1: 2, 3: 4}
def get_dups(seq):
    count = {}
    for s in seq:
        count[s] = count.get(s, 0) + 1
    dups = dict((k, v) for k, v in count.iteritems() if v > 1)
    return dups


# returns list of tuples:
# [(code1, {'resize': 1.0, 'offset': 0.0}), (code2, {}), ...]
def get_transform_config(config):
    font_transform = config.get('transform', {})

    def get_transform_item(glyph):
        name, glyph = glyph.items()[0]
        transform = font_transform.copy()
        glyph_transform = glyph.get('transform', {})
        if 'offset' in glyph_transform:
            offset = transform.get('offset', 0) + glyph_transform.get('offset')
            transform['offset'] = offset
        return (glyph.get('code'), transform)

    return [get_transform_item(glyph) for glyph in config['glyphs']]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Font transform tool')
    parser.add_argument('-c', '--config',   type=str, required=True,
        help='Config example: ../config.yml')
    parser.add_argument('-i', '--src_font', type=str, required=True,
        help='Input font')
    parser.add_argument('-o', '--dst_font', type=str, required=True,
        help='Output font')

    args = parser.parse_args()

    try:
        config = yaml.load(open(args.config, 'r'))
    except IOError as (errno, strerror):
        error("Cannot open %s: %s\n" % (args.config, strerror))
        sys.exit(1)
    except yaml.YAMLError, e:
        if hasattr(e, 'problem_mark'):
            mark = e.problem_mark
            error("YAML parser error in file %s at line %d, col %d" %
                (args.config, mark.line + 1, mark.column + 1))
        else:
            error("YAML parser error in file %s: %s" % (args.config, e))
        sys.exit(1)

    transform_config = get_transform_config(config)

    codes = zip(*transform_config)[0]

    # validate config: codes
    dups = get_dups(codes)
    if len(dups) > 0:
        error("Error in file %s: glyph codes aren't unique\n" % args.config)
        for k in sorted(dups.keys()):
            error("Duplicate code 0x%04x\n" % k)
        sys.exit(1)

    has_transform = lambda x: 'resize' in x or 'offset' in x
    codes_to_transform = [i for i in transform_config if has_transform(i[1])]

    try:
        font = fontforge.open(args.src_font)
    except:
        sys.exit(1)

    # set ascent/descent
    ascent = config.get('font', {}).get('ascent', None)
    descent = config.get('font', {}).get('descent', None)

    if ascent:
        font.ascent = ascent
    if descent:
        font.descent = descent

    # apply transformations
    for code, transform in codes_to_transform:
        try:
            font[code]
        except TypeError:
            error("Warning: no such glyph (code=0x%04x)\n" % code)
            continue

        font.selection.select(("unicode",), code)

        if 'resize' in transform:
            # bbox: a tuple representing a rectangle (xmin,ymin, xmax,ymax)
            bbox = font[code].boundingBox()

            # center of bbox
            x, y = (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2

            # move center of bbox to (0, 0)
            translate_matrix = psMat.translate(-x, -y)
            font.transform(translate_matrix)

            # scale around (0, 0)
            scale_matrix = psMat.scale(transform['resize'])
            font.transform(scale_matrix)

            # move center of bbox back to its old position
            translate_matrix = psMat.translate(x, y)
            font.transform(translate_matrix)

        if 'offset' in transform:
            # shift the selected glyph vertically
            offset = transform['offset'] * (font.ascent + font.descent)
            translate_matrix = psMat.translate(0, offset)
            font.transform(translate_matrix)
    try:
        font.generate(args.dst_font)
    except:
        error("Cannot write to file %s\n" % args.dst_font)
        sys.exit(1)

    sys.exit(0)
