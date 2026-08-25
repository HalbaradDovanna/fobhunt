"""
Run this AFTER select_region.py, at a moment when the thing you want to
detect is actually visible in your TRIGGER region (e.g. a specific icon,
aggression flag, or piece of text you want watcher.py to watch for).

It grabs a screenshot of the trigger region and saves it as reference.png.
watcher.py's --mode match compares live frames of the trigger region
against this image, and only fires when they're similar enough.
"""
import json
import sys
from pathlib import Path

import mss
from PIL import Image


def load_trigger_region():
    region_file = Path("region.json")
    if not region_file.exists():
        print("No region.json found. Run select_region.py first.")
        sys.exit(1)
    with open(region_file) as f:
        data = json.load(f)
    if "trigger" in data:
        return data["trigger"]
    return data  # old single-region format


def grab(sct, region):
    shot = sct.grab(region)
    return Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")


if __name__ == "__main__":
    region = load_trigger_region()
    with mss.mss() as sct:
        img = grab(sct, region)
        img.save("reference.png")
        print(f"Saved reference.png from trigger region {region}")
        print("Now run: python watcher.py --mode match")
