#!/usr/bin/env python3
"""fastfetch with the Quant night-sky logo, animated for a few seconds.

fastfetch draws the info once with frame 0 as a raw logo; then only the logo
area is redrawn in place (fastfetch positions info with absolute columns, so
overwriting the first WIDTH columns never touches it). With any arguments, or
when not on a terminal that fits, it behaves like plain fastfetch.
"""
import importlib.util
import json
import os
import random
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REAL = "/usr/bin/fastfetch"
HERE = Path(__file__).resolve().parent
CONFIG = HERE / "config.jsonc"
DESK = HERE.parent / "eww/extension/desktop/scripts/desk.py"   # the art lives here, shared with the desktop
FRAMES, DELAY = 14, 0.22                                        # ~3 s of animation
PAD_TOP, GAP = 1, 3

# --- art + colours (truecolor, same palette as the theme) ---
sys.dont_write_bytecode = True                                  # no __pycache__ in the repo
spec = importlib.util.spec_from_file_location("desk", DESK)
desk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(desk)
ART = desk.ART
WIDTH = max(len(t) for t, _ in ART)


def rgb(hexcol):
    h = hexcol.lstrip("#")
    return "\033[38;2;{};{};{}m".format(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


STAR, STAR_DIM = rgb("#d5c89a"), rgb("#6b6450")
MOON, TRAIL, GLINT, CLOUD = rgb("#cdd6f4"), rgb("#89b4fa"), rgb("#ffffff"), rgb("#7f849c")
RESET, BOLD = "\033[0m", "\033[1m"


def frame(rng, tick):
    """One frame: twinkling stars, and a glint running along the comet trail."""
    lines = []
    for row, (text, kind) in enumerate(ART):
        text = text.ljust(WIDTH)
        out = []
        for i, ch in enumerate(text):
            lone = text[i - 1:i] in ("", " ") and text[i + 1:i + 2] in ("", " ")
            if ch in "*." and lone:
                star = rng.choice(desk.TWINKLE[:4]) if ch == "*" else ch
                out.append((STAR if rng.random() > 0.35 else STAR_DIM) + star)
            elif ch in "~=-" and "C" in kind:
                # glint sweeps right-to-left down the trail, like the comet in the wallpaper
                hot = abs((WIDTH - i) + row * 3 - tick * 5 % (WIDTH + 30)) < 2
                out.append((GLINT + BOLD if hot else TRAIL) + ch + RESET)
            elif ch != " " and "M" in kind:
                out.append(MOON + BOLD + ch + RESET)
            elif ch != " " and "K" in kind:
                out.append(CLOUD + ch)
            else:
                out.append(" ")
        lines.append("".join(out) + RESET)
    return lines


def config_with_shell():
    """Copy of the Quant config whose `shell` modules show the user's shell, not this script
    (fastfetch reports its parent process, which is us). Falls back to the plain config."""
    try:
        cfg = json.loads(CONFIG.read_text())
        name = Path(f"/proc/{os.getppid()}/comm").read_text().strip()
        ver = re.search(r"\d+\.\d+(\.\d+)?", subprocess.run(
            [name, "--version"], capture_output=True, text=True, timeout=2).stdout or "")
        label = f"{name} {ver.group(0)}" if ver else name
        for m in cfg.get("modules", []):
            if isinstance(m, dict) and m.get("type") == "shell":
                m.update(type="custom", format=label)
        f = tempfile.NamedTemporaryFile("w", suffix=".jsonc", delete=False)
        json.dump(cfg, f)
        f.close()
        return f.name
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def main():
    if sys.argv[1:] or not sys.stdout.isatty():
        os.execv(REAL, [REAL, *sys.argv[1:]])

    cfg = config_with_shell()
    rng = random.Random()
    first = frame(rng, 0)
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write("\n".join(first) + "\n")
        logo = f.name
    try:
        out = subprocess.run(
            [REAL, "-c", cfg or str(CONFIG), "--file-raw", logo, "--logo-width", str(WIDTH),
             "--logo-height", str(len(ART)), "--logo-padding-top", str(PAD_TOP),
             "--logo-padding-right", str(GAP), "--pipe", "false"],
            capture_output=True, text=True).stdout
    finally:
        os.unlink(logo)
        if cfg:
            os.unlink(cfg)
    # autowrap off while printing: a long line (e.g. the GPU name) would otherwise wrap onto an
    # extra row and throw off the row count the redraw relies on. Long lines get clipped instead.
    sys.stdout.write("\033[?7l" + out + "\033[?7h")
    sys.stdout.flush()

    cols, rows = shutil.get_terminal_size()
    height = out.count("\n")
    if cols < WIDTH + 40 or height >= rows:      # wrapped or scrolled: cursor maths would be wrong
        return

    up = height - PAD_TOP                         # lines from the cursor back to the logo's first row
    restore = lambda *_: (sys.stdout.write("\033[?25h" + RESET), sys.stdout.flush())
    signal.signal(signal.SIGINT, lambda *_: (restore(), sys.exit(0)))
    sys.stdout.write("\033[?25l")                 # hide cursor while animating
    try:
        for tick in range(1, FRAMES + 1):
            time.sleep(DELAY)
            buf = [f"\033[{up}A\r"]
            for line in frame(rng, tick):
                buf.append(line + "\r\033[1B")
            buf.append(f"\033[{up - len(ART)}B\r" if up > len(ART) else "\r")
            sys.stdout.write("".join(buf))
            sys.stdout.flush()
    finally:
        restore()


if __name__ == "__main__":
    main()
