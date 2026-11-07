#!/usr/bin/env python3
"""Data for the Quant desktop widgets. One subcommand per widget, JSON on stdout.

  desk.py git | heat | ports | top | todo | gpu | quote   -> one JSON value (defpoll)
  desk.py art                                            -> JSON line per frame (deflisten)
  desk.py pomo [status|toggle|reset]                     -> focus timer
"""
import datetime as dt
import html
import json
import os
import random
import subprocess
import sys
import textwrap
import time
from pathlib import Path

HOME = Path.home()
REPO_ROOTS = [HOME / "code", HOME / "dotfiles", HOME]   # scanned 3 levels deep (HOME: 1)
CACHE = Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp")) / "quant-desk"
CACHE.mkdir(exist_ok=True)


def sh(*cmd, cwd=None):
    try:
        return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=5).stdout
    except (OSError, subprocess.TimeoutExpired):
        return ""


def git(repo, *args):
    # --no-optional-locks: never take index.lock while the user is committing
    return sh("git", "--no-optional-locks", "-C", str(repo), *args).strip()


def repos():
    """Repo list, cached 10 min. Skips AUR build clones."""
    cache = CACHE / "repos.json"
    if cache.exists() and time.time() - cache.stat().st_mtime < 600:
        return [Path(p) for p in json.loads(cache.read_text())]
    found = set()
    for root in REPO_ROOTS:
        depth = 1 if root == HOME else 3
        for cur, dirs, _ in os.walk(root):
            rel = Path(cur).relative_to(root)
            if ".git" in dirs:
                found.add(Path(cur))
                dirs.clear()
                continue
            if len(rel.parts) >= depth:
                dirs.clear()
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "node_modules"]
    keep = [r for r in found if "aur.archlinux.org" not in git(r, "remote", "get-url", "origin")]
    cache.write_text(json.dumps([str(r) for r in keep]))
    return keep


def cmd_git():
    rows = []
    for r in repos():
        last = git(r, "log", "-1", "--format=%ct")
        if not last:
            continue
        branch = git(r, "branch", "--show-current") or "detached"
        dirty = len([l for l in git(r, "status", "--porcelain").splitlines() if l])
        ahead = behind = 0
        if git(r, "rev-parse", "--abbrev-ref", "@{u}"):          # local refs only, never fetch
            ab = git(r, "rev-list", "--left-right", "--count", "HEAD...@{u}").split()
            if len(ab) == 2:
                ahead, behind = int(ab[0]), int(ab[1])
        rows.append({"name": r.name, "path": str(r), "branch": branch[:18], "dirty": dirty,
                     "ahead": ahead, "behind": behind, "ts": int(last),
                     "age": age(int(last))})
    rows.sort(key=lambda x: -x["ts"])
    return rows[:6]


def age(ts):
    s = int(time.time()) - ts
    for unit, n in (("d", 86400), ("h", 3600), ("m", 60)):
        if s >= n:
            return f"{s // n}{unit}"
    return "now"


def cmd_heat():
    """17 weeks x 7 days of the user's commits across all repos."""
    email = sh("git", "config", "--global", "user.email").strip()
    weeks = 17
    today = dt.date.today()
    start = today - dt.timedelta(days=today.weekday() + 7 * (weeks - 1))   # a Monday
    counts = {}
    for r in repos():
        out = git(r, "log", "--all", f"--since={start.isoformat()}", f"--author={email}", "--format=%cs")
        for d in out.split():
            counts[d] = counts.get(d, 0) + 1
    grid, total = [], 0
    for w in range(weeks):
        col = []
        for d in range(7):
            day = start + dt.timedelta(days=7 * w + d)
            n = counts.get(day.isoformat(), 0) if day <= today else -1
            total += max(n, 0)
            lvl = -1 if n < 0 else 0 if n == 0 else 1 if n < 3 else 2 if n < 6 else 3 if n < 10 else 4
            col.append({"l": lvl, "tip": f"{day:%a %d %b}: {max(n, 0)} commits"})
        grid.append(col)
    streak, day = 0, today
    while counts.get(day.isoformat()):
        streak += 1
        day -= dt.timedelta(days=1)
    return {"grid": grid, "total": total, "streak": streak}


KNOWN = {22: "sshd", 53: "dns", 631: "cups", 3306: "mysql", 5432: "postgres",
         6379: "redis", 11434: "ollama", 27017: "mongodb"}


def cmd_net():
    """Bytes/s on the busiest non-loopback interface, from /proc/net/dev deltas."""
    now, tot = time.time(), {}
    for line in Path("/proc/net/dev").read_text().splitlines()[2:]:
        name, data = line.split(":", 1)
        f = data.split()
        if name.strip() != "lo":
            tot[name.strip()] = (int(f[0]), int(f[8]))
    prev_f = CACHE / "net.json"
    try:
        prev = json.loads(prev_f.read_text())
    except (OSError, ValueError):
        prev = {"t": now, "tot": tot}
    prev_f.write_text(json.dumps({"t": now, "tot": tot}))
    dt_ = max(now - prev["t"], 0.5)
    best = ("-", 0, 0)
    for k, (rx, tx) in tot.items():
        p = prev["tot"].get(k, (rx, tx))
        down, up = max(0, rx - p[0]) / dt_, max(0, tx - p[1]) / dt_
        if down + up >= best[1] + best[2]:
            best = (k, down, up)
    return {"iface": best[0], "down": human(best[1]), "up": human(best[2])}


def human(b):
    for unit in ("B", "K", "M", "G"):
        if b < 1024:
            return f"{b:.0f}{unit}/s" if unit == "B" else f"{b:.1f}{unit}/s"
        b /= 1024
    return f"{b:.1f}T/s"


def cmd_uptime():
    s = int(float(Path("/proc/uptime").read_text().split()[0]))
    d, h, m = s // 86400, s % 86400 // 3600, s % 3600 // 60
    return f"{d}d {h}h" if d else f"{h}h {m:02d}m"


def cmd_ports():
    """Listening TCP ports (dev servers), plus docker if it's running."""
    seen, rows = set(), []
    for line in sh("ss", "-ltnpH").splitlines():
        f = line.split()
        if len(f) < 4:
            continue
        addr, port = f[3].rsplit(":", 1)
        if port in seen or not port.isdigit():
            continue
        seen.add(port)
        proc = f[5].split('"')[1] if len(f) > 5 and '"' in f[5] else KNOWN.get(int(port), "system")
        proc = proc.removesuffix("-MainThread")
        local = addr.strip("[]") in ("127.0.0.1", "::1", "localhost")
        rows.append({"port": int(port), "proc": proc[:14], "scope": "local" if local else "open"})
    rows.sort(key=lambda x: x["port"])
    docker = None
    if sh("systemctl", "is-active", "docker").strip() == "active":
        docker = len(sh("docker", "ps", "-q").split())
    return {"ports": rows[:7], "docker": docker}


def cmd_top():
    """Top 3 by live CPU: second `top` sample (ps %cpu is a lifetime average)."""
    out = sh("top", "-b", "-n", "2", "-d", "0.5", "-o", "%CPU", "-w", "200")
    block = out.split("\ntop - ")[-1].splitlines()
    rows = []
    for line in block:
        f = line.split()
        if len(f) < 12 or not f[0].isdigit() or f[11] in ("top", "python3"):
            continue
        rows.append({"name": f[11][:16], "cpu": float(f[8].replace(",", "."))})
        if len(rows) == 3:
            break
    return rows


def cmd_gpu():
    """dGPU power state from sysfs. Never calls nvidia-smi (it would wake the GPU)."""
    for dev in Path("/sys/bus/pci/devices").iterdir():
        try:
            if (dev / "vendor").read_text().strip() == "0x10de" and (dev / "class").read_text().startswith("0x03"):
                return (dev / "power" / "runtime_status").read_text().strip()
        except OSError:
            pass
    return "none"


def cmd_todo():
    """~/todo.md, one task per line. A trailing `~` marks it done: `do dishes ~`."""
    f = HOME / "todo.md"
    lines = f.read_text(errors="replace").splitlines() if f.exists() else []
    items = []
    for line in lines:
        s = line.strip()
        done = s.endswith("~")
        s = s.rstrip("~ ").strip()
        if s:
            items.append({"t": s[:40], "done": done})
    done = sum(i["done"] for i in items)
    return {"items": items[:8], "more": max(0, len(items) - 8), "done": done, "total": len(items)}


QUOTES = [
    ("Premature optimization is the root of all evil.", "Donald Knuth"),
    ("Beware of bugs in the above code; I have only proved it correct, not tried it.", "Donald Knuth"),
    ("Simplicity is prerequisite for reliability.", "Edsger Dijkstra"),
    ("Testing shows the presence, not the absence of bugs.", "Edsger Dijkstra"),
    ("If debugging is removing bugs, programming is putting them in.", "Edsger Dijkstra"),
    ("Talk is cheap. Show me the code.", "Linus Torvalds"),
    ("Bad programmers worry about the code. Good ones worry about data structures.", "Linus Torvalds"),
    ("Given enough eyeballs, all bugs are shallow.", "Eric S. Raymond"),
    ("Make it work, make it right, make it fast.", "Kent Beck"),
    ("I'm not a great programmer; I'm a good programmer with great habits.", "Kent Beck"),
    ("Any fool can write code a computer understands. Good programmers write code humans understand.", "Martin Fowler"),
    ("Programs must be written for people to read, and only incidentally for machines to execute.", "Harold Abelson"),
    ("The most dangerous phrase in the language is: we've always done it this way.", "Grace Hopper"),
    ("It's easier to ask forgiveness than it is to get permission.", "Grace Hopper"),
    ("When in doubt, use brute force.", "Ken Thompson"),
    ("One of my most productive days was throwing away 1000 lines of code.", "Ken Thompson"),
    ("UNIX is basically a simple operating system, but you have to be a genius to understand the simplicity.", "Dennis Ritchie"),
    ("The only way to learn a new programming language is by writing programs in it.", "Dennis Ritchie"),
    ("Controlling complexity is the essence of computer programming.", "Brian Kernighan"),
    ("Debugging is twice as hard as writing the code in the first place.", "Brian Kernighan"),
    ("There are two ways of constructing a software design: make it so simple there are obviously no deficiencies.", "Tony Hoare"),
    ("I call it my billion-dollar mistake. It was the invention of the null reference.", "Tony Hoare"),
    ("Simple things should be simple, complex things should be possible.", "Alan Kay"),
    ("The best way to predict the future is to invent it.", "Alan Kay"),
    ("The computer was born to solve problems that did not exist before.", "Bill Gates"),
    ("Measuring programming progress by lines of code is like measuring aircraft building progress by weight.", "Bill Gates"),
    ("Everyone should learn how to program a computer, because it teaches you how to think.", "Steve Jobs"),
    ("Real artists ship.", "Steve Jobs"),
    ("Software is like sex: it's better when it's free.", "Linus Torvalds"),
    ("Code is like humor. When you have to explain it, it's bad.", "Cory House"),
    ("First, solve the problem. Then, write the code.", "John Johnson"),
    ("Deleted code is debugged code.", "Jeff Sickel"),
    ("The best code is no code at all.", "Jeff Atwood"),
    ("There are only two hard things in computer science: cache invalidation and naming things.", "Phil Karlton"),
    ("Walking on water and developing software from a spec are easy if both are frozen.", "Edward V. Berard"),
    ("The function of good software is to make the complex appear to be simple.", "Grady Booch"),
    ("Perfection is achieved not when there is nothing more to add, but nothing left to take away.", "Antoine de Saint-Exupery"),
    ("Optimism is an occupational hazard of programming; feedback is the treatment.", "Kent Beck"),
    ("Code never lies, comments sometimes do.", "Ron Jeffries"),
    ("Weeks of coding can save you hours of planning.", "unknown"),
    ("It works on my machine.", "every developer, ever"),
    ("Hofstadter's Law: it always takes longer than you expect, even when you take it into account.", "Douglas Hofstadter"),
    ("Machines take me by surprise with great frequency.", "Alan Turing"),
    ("We can only see a short distance ahead, but we can see plenty there that needs to be done.", "Alan Turing"),
    ("The Analytical Engine weaves algebraic patterns just as the Jacquard loom weaves flowers.", "Ada Lovelace"),
    ("Truth can only be found in one place: the code.", "Robert C. Martin"),
    ("Clean code always looks like it was written by someone who cares.", "Robert C. Martin"),
    ("Java is to JavaScript what car is to carpet.", "Chris Heilmann"),
    ("Rust: fast, reliable, productive. Pick three.", "Rust community"),
    ("Clear is better than clever.", "Rob Pike"),
]
QUOTE_EVERY = 120   # seconds; each 2-minute slot picks a random quote, stable within the slot


def cmd_quote():
    slot = int(time.time() // QUOTE_EVERY)
    q, a = random.Random(slot).choice(QUOTES)
    # pre-wrapped: eww labels ellipsize long text instead of wrapping it reliably
    return {"lines": textwrap.wrap(f"\u201c{q}\u201d", 50), "a": a}


# --- Weather (wttr.in, cached; location from IP unless WEATHER_LOC is set) ----
WEATHER_LOC = ""          # e.g. "Mumbai" or "19.07,72.87"; empty = guess from IP
ICONS = {  # wttr.in weather codes -> nerd-font (md) icons
    "clear": ("\U000f0599", "\U000f0594"), "partly": ("\U000f0595", "\U000f0f31"),
    "cloudy": "\U000f0590", "fog": "\U000f0591", "rain": "\U000f0597", "pour": "\U000f0596",
    "sleet": "\U000f067f", "snow": "\U000f0598", "storm": "\U000f067e",
}
KIND = {113: "clear", 116: "partly", 119: "cloudy", 122: "cloudy", 143: "fog", 248: "fog", 260: "fog",
        200: "storm", 386: "storm", 389: "storm", 392: "storm", 395: "snow"}
KIND.update({c: "rain" for c in (176, 263, 266, 293, 296, 353)})
KIND.update({c: "pour" for c in (299, 302, 305, 308, 356, 359)})
KIND.update({c: "sleet" for c in (179, 182, 185, 281, 284, 311, 314, 317, 320, 350, 362, 365, 374, 377)})
KIND.update({c: "snow" for c in (227, 230, 323, 326, 329, 332, 335, 338, 368, 371)})


def cmd_weather():
    cache = CACHE / "weather.json"
    try:
        url = f"https://wttr.in/{WEATHER_LOC.replace(' ', '+')}?format=j1"
        d = json.loads(sh("curl", "-sf", "-m", "8", url))
        c, today = d["current_condition"][0], d["weather"][0]
        astro = today["astronomy"][0]
        now = dt.datetime.now().time()
        rise = dt.datetime.strptime(astro["sunrise"], "%I:%M %p").time()
        sset = dt.datetime.strptime(astro["sunset"], "%I:%M %p").time()
        icon = ICONS[KIND.get(int(c["weatherCode"]), "cloudy")]
        if isinstance(icon, tuple):
            icon = icon[0] if rise <= now < sset else icon[1]
        out = {"ok": True, "icon": icon, "desc": c["weatherDesc"][0]["value"].strip().lower(),
               "temp": c["temp_C"], "feels": c["FeelsLikeC"], "hum": c["humidity"],
               "hi": today["maxtempC"], "lo": today["mintempC"]}
        cache.write_text(json.dumps(out))
        return out
    except (ValueError, KeyError, IndexError, OSError):
        try:                                   # offline: keep showing the last good reading
            return json.loads(cache.read_text())
        except (OSError, ValueError):
            return {"ok": False, "icon": "\U000f0590", "desc": "weather unavailable", "temp": "--",
                    "feels": "--", "hum": "--", "hi": "--", "lo": "--"}


# --- ASCII art: night sky over a cloud bank, like the wallpaper ---------------
# M = moon, C = comet/trail, K = clouds, P = prompt; '*' marks a twinkling star.
ART = [
    ("  *        .            .        *      .", "S"),
    ("      .         *    _.._     .", "M"),
    ("  .        .       .' .  `.       ~~==-", "MC"),
    ("                  /  o   . \\  ~~==--     *", "MC"),
    ("     *      .    |  .   O   |==--    .", "MC"),
    ("                  \\  .   o /~--         .", "MC"),
    ("   .     ~~~===--- `._..-'      *", "MC"),
    ("          .   *        .            .", "S"),
    ("       .--.    .   _        .  .-~~-.   *", "K"),
    ("    .-(    )-.  .-( )-.  .-(      )-.", "K"),
    ("   (__________)(_______)(__________)  .", "K"),
]
COL = {"S": "#d5c89a", "M": "#cdd6f4", "C": "#89b4fa", "K": "#7f849c"}
TWINKLE = [".", "*", "+", "·", " "]


def art_frame(rng):
    lines = []
    width = max(len(t) for t, _ in ART)
    for text, kind in ART:
        text = text.ljust(width)
        out = []
        for i, ch in enumerate(text):
            e = html.escape(ch)
            lone = text[i - 1:i] in ("", " ") and text[i + 1:i + 2] in ("", " ")
            if ch in "*." and lone:
                if ch == "*":
                    e = rng.choice(TWINKLE[:4])
                out.append(f"<span foreground='{COL['S']}' alpha='{rng.choice([45, 70, 100])}%'>{e}</span>")
            elif ch in "~=-" and "C" in kind:
                out.append(f"<span foreground='{COL['C']}'>{e}</span>")
            elif ch != " " and "M" in kind:
                out.append(f"<span foreground='{COL['M']}' weight='bold'>{e}</span>")
            elif ch != " " and "K" in kind:
                out.append(f"<span foreground='{COL['K']}'>{e}</span>")
            else:
                out.append(e)
        lines.append("".join(out))
    return lines


def cmd_art():
    rng = random.Random()
    while True:
        print(json.dumps(art_frame(rng), ensure_ascii=False), flush=True)
        time.sleep(1.5)


# --- Focus timer (pomodoro) -----------------------------------------------------
POMO = CACHE / "pomo.json"
WORK, BREAK = 25 * 60, 5 * 60


def pomo_load():
    try:
        return json.loads(POMO.read_text())
    except (OSError, ValueError):
        return {"phase": "work", "left": WORK, "running": False, "end": 0, "count": 0}


def pomo_status():
    s = pomo_load()
    if s["running"]:
        s["left"] = max(0, int(s["end"] - time.time()))
        if s["left"] == 0:                       # phase finished: flip and notify
            done = s["phase"]
            s["count"] += done == "work"
            s["phase"] = "break" if done == "work" else "work"
            s["left"] = BREAK if s["phase"] == "break" else WORK
            s["running"] = False
            POMO.write_text(json.dumps(s))
            sh("notify-send", "-a", "focus", "Focus timer",
               "Break time, stretch." if done == "work" else "Break over, back to it.")
    total = WORK if s["phase"] == "work" else BREAK
    s["clock"] = f"{s['left'] // 60:02d}:{s['left'] % 60:02d}"
    s["pct"] = round(100 * (1 - s["left"] / total), 1)
    return s


def cmd_pomo(action="status"):
    s = pomo_status()
    if action == "toggle":
        if s["running"]:
            s.update(running=False)
        else:
            s.update(running=True, end=time.time() + s["left"])
    elif action == "reset":
        s.update(phase="work", left=WORK, running=False)
    if action != "status":
        POMO.write_text(json.dumps({k: s[k] for k in ("phase", "left", "running", "end", "count")}))
        s = pomo_status()
    return s


if __name__ == "__main__":
    cmd, *rest = sys.argv[1:] or ["git"]
    if cmd == "art":
        cmd_art()
    else:
        out = globals()[f"cmd_{cmd}"](*rest)
        print(out if isinstance(out, str) else json.dumps(out, ensure_ascii=False))
