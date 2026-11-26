"""Generate kartu SVG (Contribution Activity + Language Stack) untuk README profil.

Pemakaian:
  python3 scripts/generate_cards.py --theme newsprint --data /tmp/cards.json --out assets

Format /tmp/cards.json:
  {
    "owner": "yunjacqwu",
    "total": 25,
    "days": [{"date": "2026-01-01", "count": 0}, ...],   # urut, ~1 tahun
    "languages": {"JavaScript": 12345, "PHP": 4567, ...}  # bytes
  }
"""
import argparse
import json
import os
from html import escape

# ============================ THEMES ============================
# Ganti warna di sini kalau mau bikin tema sendiri.
THEMES = {
    "newsprint": {
        "bg": "#efe9dc", "panel": "#f8f4ea",
        "border": "#2b2b2b", "panel_border": "#2b2b2b",
        "title": "#111111", "sub": "#6b604f", "text": "#1d1d1d", "muted": "#7a6f5d",
        "accent": "#8a1c1c", "track": "#e4dbc8", "empty": "#e6dfcf",
        "levels": ["#d6c4a0", "#b48a55", "#8a5a2b", "#4a2c12"],
        "bars": ["#1d1d1d", "#8a1c1c", "#6b604f", "#a07a3f", "#3d5a6c", "#9a8f7c"],
        "glows": [],
        "font_title": "Georgia, 'Times New Roman', serif",
        "font_body": "Georgia, 'Times New Roman', serif",
    },
    "midnight": {
        "bg": "#0b0d10", "panel": "#111418",
        "border": "#23272e", "panel_border": "#2d333b",
        "title": "#f0f3f6", "sub": "#8b949e", "text": "#e6edf3", "muted": "#8b949e",
        "accent": "#2dd4bf", "track": "#21262d", "empty": "#1b1f24",
        "levels": ["#0f3d3a", "#16675f", "#1f9e8f", "#2dd4bf"],
        "bars": ["#2dd4bf", "#5eead4", "#94a3b8", "#64748b", "#475569", "#334155"],
        "glows": [],
        "font_title": "'Segoe UI', Inter, Helvetica, Arial, sans-serif",
        "font_body": "'Segoe UI', Inter, Helvetica, Arial, sans-serif",
    },
    "sunset": {
        "bg": "#140f1f", "panel": "#1b1428",
        "border": "#3a2a52", "panel_border": "#4b3668",
        "title": "#fff4ec", "sub": "#b9a6c9", "text": "#f5e9f0", "muted": "#a996b8",
        "accent": "#ff8a5b", "track": "#2a2038", "empty": "#251c33",
        "levels": ["#4a2340", "#8a2f4f", "#d9485f", "#ff8a5b"],
        "bars": ["#ff8a5b", "#ff5e7e", "#c86bfa", "#7c6cf2", "#ffd166", "#f0abfc"],
        "glows": ["#ff5e7e", "#7c6cf2"],
        "font_title": "'Segoe UI', Inter, Helvetica, Arial, sans-serif",
        "font_body": "'Segoe UI', Inter, Helvetica, Arial, sans-serif",
    },
    "matcha": {
        "bg": "#0e130f", "panel": "#131a14",
        "border": "#253328", "panel_border": "#2f4233",
        "title": "#ecf5e9", "sub": "#93a896", "text": "#e3eee0", "muted": "#8aa08d",
        "accent": "#a3e635", "track": "#1f2a21", "empty": "#1a231c",
        "levels": ["#2b4a1f", "#4d7c2a", "#7cb342", "#a3e635"],
        "bars": ["#a3e635", "#4ade80", "#facc15", "#fb923c", "#2dd4bf", "#e5e7eb"],
        "glows": ["#4ade80", "#facc15"],
        "font_title": "'Segoe UI', Inter, Helvetica, Arial, sans-serif",
        "font_body": "'Segoe UI', Inter, Helvetica, Arial, sans-serif",
    },
}

W = 880


def frame(t, h, uid):
    """Kartu luar + panel dalam + glow opsional."""
    glow_defs, glow_shapes = "", ""
    spots = [(170, 20), (W - 140, h - 10), (W * 0.55, h)]
    for i, color in enumerate(t["glows"]):
        gid = f"{uid}g{i}"
        glow_defs += (f'<radialGradient id="{gid}"><stop offset="0" stop-color="{color}" stop-opacity="0.35"/>'
                      f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>')
        x, y = spots[i % len(spots)]
        glow_shapes += f'<circle cx="{x}" cy="{y}" r="170" fill="url(#{gid})"/>'
    return (
        f'<defs>{glow_defs}<clipPath id="{uid}c"><rect x="10" y="10" width="{W-20}" height="{h-20}" rx="24"/></clipPath></defs>'
        f'<rect x="10" y="10" width="{W-20}" height="{h-20}" rx="24" fill="{t["bg"]}" stroke="{t["border"]}" stroke-width="1.5"/>'
        f'<g clip-path="url(#{uid}c)">{glow_shapes}</g>'
        f'<rect x="36" y="38" width="{W-72}" height="{h-76}" rx="18" fill="{t["panel"]}" fill-opacity="0.92" '
        f'stroke="{t["panel_border"]}" stroke-width="1.2"/>'
    )


def text(x, y, s, size, color, font, weight="normal", anchor="start", extra=""):
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" font-weight="{weight}" '
            f'fill="{color}" text-anchor="{anchor}" {extra}>{escape(str(s))}</text>')


def activity_svg(data, t):
    h = 260
    days = data["days"][-371:]
    # Susun per minggu (kolom), Minggu di baris paling atas
    from datetime import date
    first = date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7  # Minggu = 0
    cells = [None] * offset + days
    weeks = [cells[i:i + 7] for i in range(0, len(cells), 7)][-53:]

    mx = max((d["count"] for d in days), default=0) or 1

    def level(c):
        if c <= 0:
            return 0
        return min(4, max(1, -(-c * 4 // mx)))

    size, gap = 11, 3
    x0, y0 = 56, 114
    out = [frame(t, h, "a")]
    out.append(text(56, 78, "Contribution Activity", 25, t["title"], t["font_title"], "bold"))
    out.append(text(57, 101, f'{data["total"]} contributions in the last year', 13, t["sub"], t["font_body"], "600"))

    # Legend
    lx = W - 90 - 5 * 14
    out.append(text(lx - 8, 86, "Less", 11, t["muted"], t["font_body"], anchor="end"))
    for i, col in enumerate([t["empty"]] + t["levels"]):
        out.append(f'<rect x="{lx + i*14}" y="76" width="{size}" height="{size}" rx="2.5" fill="{col}"/>')
    out.append(text(lx + 5 * 14 + 6, 86, "More", 11, t["muted"], t["font_body"]))

    for wi, week in enumerate(weeks):
        for di, d in enumerate(week):
            if d is None:
                continue
            lv = level(d["count"])
            col = t["empty"] if lv == 0 else t["levels"][lv - 1]
            out.append(f'<rect x="{x0 + wi*(size+gap)}" y="{y0 + di*(size+gap)}" width="{size}" height="{size}" '
                       f'rx="2.5" fill="{col}"><title>{d["date"]}: {d["count"]}</title></rect>')

    out.append(text(W - 30, h - 20, f'@{data["owner"]}', 10, t["muted"], t["font_body"], anchor="end"))
    return svg_wrap(h, "".join(out))


def stack_svg(data, t, top=5):
    langs = sorted(data["languages"].items(), key=lambda kv: kv[1], reverse=True)
    total = sum(v for _, v in langs) or 1
    langs = langs[:top]
    row_h = 32
    h = 150 + row_h * len(langs)
    out = [frame(t, h, "s")]
    out.append(text(56, 76, "Language Stack", 25, t["title"], t["font_title"], "bold"))
    out.append(text(57, 99, "Repository-weighted technologies", 13, t["sub"], t["font_body"], "600"))
    out.append(text(W - 92, 72, "> stack.scan", 13, t["accent"], "'Cascadia Code', Consolas, monospace", "bold",
                    anchor="end"))

    bar_x, bar_w = 340, W - 340 - 92
    for i, (name, val) in enumerate(langs):
        pct = val * 100 / total
        y = 122 + i * row_h
        col = t["bars"][i % len(t["bars"])]
        pct_txt = f"{pct:.0f}%" if pct >= 1 else "<1%"
        out.append(f'<circle cx="62" cy="{y-4}" r="4.5" fill="{col}"/>')
        out.append(text(82, y, name, 14, t["text"], t["font_body"], "bold"))
        out.append(text(312, y, pct_txt, 14, col, t["font_body"], "bold", anchor="end"))
        out.append(f'<rect x="{bar_x}" y="{y-9}" width="{bar_w}" height="8" rx="4" fill="{t["track"]}"/>')
        fill_w = max(8, bar_w * pct / 100)
        out.append(f'<rect x="{bar_x}" y="{y-9}" width="{fill_w:.1f}" height="8" rx="4" fill="{col}"/>')

    out.append(text(W - 30, h - 20, f'@{data["owner"]}', 10, t["muted"], t["font_body"], anchor="end"))
    return svg_wrap(h, "".join(out))


def svg_wrap(h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" '
            f'role="img">{body}</svg>\n')


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--theme", default="midnight", choices=THEMES.keys())
    p.add_argument("--data", required=True)
    p.add_argument("--out", default="assets")
    a = p.parse_args()
    data = json.load(open(a.data, encoding="utf-8"))
    t = THEMES[a.theme]
    os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, "activity.svg"), "w", encoding="utf-8").write(activity_svg(data, t))
    open(os.path.join(a.out, "stack.svg"), "w", encoding="utf-8").write(stack_svg(data, t))
    print(f"OK -> {a.out}/activity.svg, {a.out}/stack.svg ({a.theme})")


if __name__ == "__main__":
    main()
