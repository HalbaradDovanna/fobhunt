"""
Watches a small TRIGGER region and, when it fires, saves a screenshot
of a larger CAPTURE region and sends a notification.

Two modes:
  diff mode (default)  - fires when the trigger region CHANGES from one
                          check to the next.
  match mode            - fires when the trigger region starts LOOKING LIKE
                          a saved reference.png (e.g. a specific icon,
                          aggression flag, or piece of text appearing).
                          Run capture_reference.py first to save that image.

This is PURE screen capture — it grabs pixels off your monitor the same
way a screenshot tool or OBS does. It never touches the EVE process,
its memory, or its window handle, and it never sends input to it.
There's nothing here for EVE (or any anti-cheat) to "detect" because
it doesn't interact with the game at all.

Usage:
    python select_region.py         # run once to pick trigger + capture areas
    python watcher.py               # diff mode: notify on any change
    python capture_reference.py     # save a reference image (for match mode)
    python watcher.py --mode match  # notify only when trigger matches reference.png
"""
import argparse
import json
import time
import sys
from datetime import datetime
from pathlib import Path

import mss
from PIL import Image, ImageChops
import numpy as np

try:
    from plyer import notification
    HAVE_PLYER = True
except ImportError:
    HAVE_PLYER = False


SCREENSHOT_DIR = Path("changes")
SCREENSHOT_DIR.mkdir(exist_ok=True)


def load_regions():
    region_file = Path("region.json")
    if not region_file.exists():
        print("No region.json found. Run select_region.py first.")
        sys.exit(1)
    with open(region_file) as f:
        data = json.load(f)

    # support both old single-region format and new trigger/capture format
    if "trigger" in data and "capture" in data:
        return data["trigger"], data["capture"]
    else:
        # old format: single region used for both watching and capturing
        return data, data


def grab(sct, region):
    shot = sct.grab(region)
    return Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")


def pct_changed(img_a, img_b):
    diff = ImageChops.difference(img_a.convert("L"), img_b.convert("L"))
    arr = np.array(diff)
    changed = np.count_nonzero(arr > 25)  # per-pixel brightness delta tolerance
    return changed / arr.size


def notify(image_path, title="Trigger fired"):
    if HAVE_PLYER:
        try:
            notification.notify(
                title=title,
                message=str(image_path),
                timeout=6,
            )
            return
        except Exception as e:
            print(f"(notification failed: {e})")
    print(f"\a[{title}] saved {image_path}")


def load_reference():
    ref_file = Path("reference.png")
    if not ref_file.exists():
        print("No reference.png found. Run capture_reference.py first (match mode needs it).")
        sys.exit(1)
    return Image.open(ref_file).convert("RGB")


def main():
    parser = argparse.ArgumentParser(description="Watch a small trigger region; screenshot a larger capture region on trigger.")
    parser.add_argument("--mode", choices=["diff", "match"], default="diff",
                         help="'diff' fires on any change; 'match' fires when the trigger region resembles reference.png (default diff)")
    parser.add_argument("--interval", type=float, default=1.0, help="seconds between checks (default 1.0)")
    parser.add_argument("--threshold", type=float, default=0.02,
                         help="diff mode: fraction of pixels changed to fire, 0-1 (default 0.02). "
                              "match mode: max fraction of pixels allowed to differ from reference.png to still count as a match (default 0.02)")
    parser.add_argument("--cooldown", type=float, default=5.0, help="seconds to wait after a trigger before re-arming (default 5.0)")
    args = parser.parse_args()

    trigger_region, capture_region = load_regions()
    print(f"Mode: {args.mode}")
    print(f"Trigger region: {trigger_region}")
    print(f"Capture region: {capture_region}")
    print(f"interval={args.interval}s  threshold={args.threshold}  cooldown={args.cooldown}s")
    print("Ctrl+C to stop.\n")

    reference = load_reference() if args.mode == "match" else None

    with mss.mss() as sct:
        baseline = grab(sct, trigger_region)
        last_trigger = 0.0
        was_matching = False  # match mode: only fire on the rising edge (not-matching -> matching)

        while True:
            time.sleep(args.interval)
            current = grab(sct, trigger_region)
            now = time.time()

            if args.mode == "match":
                diff_frac = pct_changed(reference.resize(current.size), current)
                is_matching = diff_frac <= args.threshold

                if is_matching and not was_matching and (now - last_trigger) >= args.cooldown:
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    out_path = SCREENSHOT_DIR / f"match_{ts}.png"
                    grab(sct, capture_region).save(out_path)
                    notify(out_path, title="Match detected")
                    last_trigger = now
                was_matching = is_matching

            else:  # diff mode
                changed_frac = pct_changed(baseline, current)
                if changed_frac >= args.threshold and (now - last_trigger) >= args.cooldown:
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    out_path = SCREENSHOT_DIR / f"change_{ts}.png"
                    grab(sct, capture_region).save(out_path)
                    notify(out_path, title="Trigger changed")
                    last_trigger = now
                    baseline = current
                elif changed_frac >= args.threshold:
                    baseline = current
                else:
                    baseline = current if changed_frac > 0 else baseline


if __name__ == "__main__":
    main()
