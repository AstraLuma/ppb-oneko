#!/usr/bin/env python3
"""
Generate the assets from an oneko source.

Requires ImageMagick
"""

# Command:
# convert $IMAGE \( $MASK -negate \) -compose CopyOpacity -composite $OUTPUT

# $SRC/bitmaps/$CHAR/$POSE.xbm + $SRC/bitmasks/$CHAR/$POSE.xbm = $OUT/$CHAR/$POSE.png
# $SRC/cursors/$CHAR_cursor.xbm + $SRC/cursors/$CHAR_cursor_mask.xbm = $OUT/$CHAR/cursor.png

import subprocess
from pathlib import Path
import sys
import shutil


def compose(image, mask, output):
    """
    Composes the given oneko image and mask into an RGBA, writing it to output.
    """
    subprocess.run([
        'convert',
        '-gravity', 'center',
        str(image),
        '-extent', '32x32',
        '(', str(mask), '-negate', ')',
        '-compose', 'CopyOpacity',
        '-composite',
        str(output),
    ], check=True)


def iter_poses(srcdir):
    for file in (srcdir / 'bitmaps').glob("*/*.xbm"):
        name = file.stem
        character = file.parent.name

        if character == 'tora':
            # Tora uses the neko masks
            maskname, _ = name.split('_', 1)
            mask = srcdir / 'bitmasks' / 'neko' / (maskname + '_mask.xbm')
        else:
            mask = srcdir / 'bitmasks' / character / (name + '_mask.xbm')

        yield file, mask, name


def iter_cursors(srcdir):
    for file in (srcdir / 'cursors').glob("*_cursor.xbm"):
        name = file.stem
        yield file, srcdir / 'cursors' / (name + '_mask.xbm'), name


def map_name(name):
    if '_' in name:
        pose, char = name.split('_', 1)
    else:
        pose = name
        char = 'neko'

    if char == 'cursor':
        char = {
            'mouse': 'neko',
            #'mouse': 'tora',
            'bone': 'dog',
            'bsd': 'bsd',
            'card': 'sakura',
            'petal': 'tomoyo',
        }[pose]
        pose = 'cursor'

    pose = {
        'utogi1': 'up_wall1',
        'utogi2': 'up_wall2',
        'dtogi1': 'down_wall1',
        'dtogi2': 'down_wall2',
        'ltogi1': 'left_wall1',
        'ltogi2': 'left_wall2',
        'rtogi1': 'right_wall1',
        'rtogi2': 'right_wall2',

        'dwleft1': 'downleft1',
        'dwleft2': 'downleft2',
        'dwright1': 'downright1',
        'dwright2': 'downright2',
        'mati2': 'neutral',
        'mati3': 'yawn',
        'jare2': 'idle_a',
        'kaki1': 'itch1',
        'kaki2': 'itch2',
        # Jare, Kaki, Akubi
    }.get(pose, pose)

    return char, pose


def main(oneko_src):
    dest = Path(__file__).resolve().parent / 'ppb_oneko'
    for image, mask, name in iter_poses(oneko_src):
        char, pose = map_name(name)
        print(char, pose)
        destdir = dest / char
        destdir.mkdir(parents=True, exist_ok=True)
        compose(image, mask, destdir / (pose + '.png'))

    for image, mask, name in iter_cursors(oneko_src):
        char, pose = map_name(name)
        print(char, pose)
        destdir = dest / char
        destdir.mkdir(parents=True, exist_ok=True)
        compose(image, mask, destdir / (pose + '.png'))

    # Special case
    shutil.copyfile(dest / 'neko' / 'cursor.png', dest / 'tora' / 'cursor.png')


if __name__ == '__main__':
    main(Path(sys.argv[1]))


# NEKO_STOP = mati2, mati2
# NEKO_JARE = jare2, mati2
# NEKO_KAKI = kaki1, kaki2
# NEKO_AKUBI = mati3, mati3
# NEKO_SLEEP = sleep*
# NEKO_AWAKE = awake*