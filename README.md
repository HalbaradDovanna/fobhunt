# Screen Region Watcher

Watches a chosen rectangle of your screen and pops a notification + saves a
screenshot whenever it changes. Useful for things like watching local chat,
an intel channel, or a specific overview spot while you're tabbed away.

**How it works / why it's undetectable:** it only calls Windows' screen
capture API (via `mss`), the same mechanism a screenshot tool, OBS, or the
Windows Snipping Tool uses. It never opens the EVE process, reads its
memory, or sends it input — so it isn't a "third-party program interacting
with the client" in the sense CCP's rules care about. There's simply
nothing about it for the game to detect.

## Setup

```
pip install -r requirements.txt
```

## 1. Pick the regions

```
python select_region.py
```

You'll be prompted twice:
1. **Trigger region** — the small spot to watch, e.g. just the "unavailable" text.
2. **Capture region** — the larger area to screenshot once the trigger changes,
   e.g. the whole panel around it, so the screenshot actually has context.

Drag a box for each, release to confirm. Saves both to `region.json`.

Note: the trigger fires on *any* change in that spot, not specifically on the
text disappearing — so if "unavailable" flips back on later that'll also
notify. If you only care about one direction, just ignore the notifications
you don't need, or ask me to add text detection (OCR) so it only fires on
a specific word appearing/disappearing.

## 2. Choose a mode

**Diff mode (default)** — fires whenever the trigger region changes at all:

```
python watcher.py
```

**Match mode** — fires only when the trigger region starts looking like a
specific image you save ahead of time (an icon, an aggression flag, a piece
of text, whatever). First capture the reference at a moment when that thing
is visible:

```
python capture_reference.py
```

This saves `reference.png` from your trigger region. Then run:

```
python watcher.py --mode match
```

It only notifies on the rising edge — i.e. the moment the region starts
matching, not every single check while it continues to match — so it won't
spam you the whole time the thing stays on screen.

Options (both modes):
- `--interval 1.0`   seconds between checks
- `--threshold 0.02` diff mode: fraction of pixels that must change to count as "changed" (0–1).
  match mode: max fraction of pixels allowed to differ from `reference.png` and still count as a match — raise it if legit matches are getting missed due to slight color/anti-aliasing differences, lower it if it's matching things it shouldn't.
- `--cooldown 5.0`   minimum seconds between notifications

Example, match mode, more forgiving:
```
python watcher.py --mode match --threshold 0.05 --interval 0.5
```

Screenshots are saved in `changes/` with a timestamp (`change_*.png` for diff
mode, `match_*.png` for match mode). Desktop notifications are sent via
`plyer`; if that fails for any reason it falls back to a terminal beep +
printed path.

## Building .exe files (optional)

The scripts run fine with plain `python`, but if you want standalone
`.exe` files that don't need Python installed:

1. Make sure you're on Windows (PyInstaller builds for whatever OS it
   runs on — it can't cross-compile from Linux/Mac to Windows).
2. Double-click `build.bat` (or run it from `cmd`/PowerShell in this folder).
3. It installs `pyinstaller`, builds all three scripts, and drops
   `select_region.exe`, `capture_reference.exe`, and `watcher.exe` into a
   new `dist\` folder.
4. Copy all three `.exe` files into one folder together. Run
   `select_region.exe` first, then (for match mode) `capture_reference.exe`,
   then `watcher.exe`.

`watcher.exe` keeps its console window open so you can see status/Ctrl+C
to stop it; `select_region.exe` runs windowless since it's just the overlay.

## Tips

- Pick a tight region (e.g. just the local chat pilot list, or a specific
  HUD icon) rather than your whole screen — smaller regions mean fewer
  false positives from unrelated animation.
- If you're getting too many notifications from things like a blinking
  cursor or subtle glow effects, raise `--threshold`.
- Re-run `select_region.py` any time to change what's being watched.
