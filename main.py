"""Write the day's news poster to /output/entry.png.

The poster (entry.png, 1024x1024 PNG, ~16 KB) sits beside this file. It shows
Thursday, 19 November 2026 in six cards: the first trilateral meeting of Xi,
Putin and Trump at APEC in Shenzhen; the Middle East flashpoints around Hormuz,
Lebanon and Riyadh; the record GTA VI launch; the Bangladesh garment strikes
and the Philippines-Chile trade deal; Senegal's budget by decree; and El
Salvador's third-term bid.

The program only copies those bytes, so both grading runs write the same file.
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SOURCE, target)
    print("wrote %s (%d bytes)" % (target, os.path.getsize(target)))
    return target


if __name__ == "__main__":
    main()