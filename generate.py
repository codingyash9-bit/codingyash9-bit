"""Generate the light and dark SVGs used by this GitHub profile README.

Place a private ``profile.jpg`` beside this file, then run ``python generate.py``.
The photograph is converted to text and is never embedded in the SVG output.
"""

from __future__ import annotations

import html
from pathlib import Path

try:
    from PIL import Image, ImageEnhance, ImageOps
except ImportError as exc:
    raise SystemExit("Pillow is required. Install it with: python -m pip install Pillow") from exc


ROOT = Path(__file__).resolve().parent
SOURCE_IMAGE = ROOT / "profile.jpg"
ASCII_ART = ROOT / "portrait.txt"

# Portrait controls: adjust these and rerun the script to tune the result.
ASCII_WIDTH = 84
ASCII_HEIGHT = 58
CONTRAST = 1.30
BRIGHTNESS = 1.12
CHARACTER_RAMP = "@%#*+=-:. "  # darkest to lightest
ASCII_FONT_SIZE = 8.4
CHARACTER_ASPECT = 0.55  # approximate monospace glyph width / line height

VIEWBOX_WIDTH = 1500
VIEWBOX_HEIGHT = 700

THEMES = {
    "dark_mode.svg": {
        "bg": "#080b0d",
        "panel": "#0d1117",
        "text": "#e6edf3",
        "muted": "#8b949e",
        "accent": "#7ee787",
        "accent2": "#e3b341",
        "border": "#30363d",
        "portrait": "#b1bac4",
    },
    "light_mode.svg": {
        "bg": "#fffdf5",
        "panel": "#fffaf0",
        "text": "#24292f",
        "muted": "#57606a",
        "accent": "#0969da",
        "accent2": "#9a6700",
        "border": "#d0d7de",
        "portrait": "#424a53",
    },
}


def image_to_ascii(path: Path) -> list[str]:
    """Return a contrast-enhanced, aspect-corrected ASCII portrait."""
    with Image.open(path) as source:
        image = ImageOps.exif_transpose(source).convert("L")
        image = ImageOps.autocontrast(image, cutoff=1)
        image = ImageEnhance.Contrast(image).enhance(CONTRAST)
        image = ImageEnhance.Brightness(image).enhance(BRIGHTNESS)

        # Compensate for characters being taller than they are wide. Fit instead
        # of stretching so the face and silhouette keep their proportions.
        corrected_height = round(ASCII_WIDTH * image.height / image.width * CHARACTER_ASPECT)
        target_height = min(ASCII_HEIGHT, max(1, corrected_height))
        image.thumbnail((ASCII_WIDTH, target_height), Image.Resampling.LANCZOS)
        canvas = Image.new("L", (ASCII_WIDTH, ASCII_HEIGHT), 255)
        x = (ASCII_WIDTH - image.width) // 2
        y = (ASCII_HEIGHT - image.height) // 2
        canvas.paste(image, (x, y))

        # Grayscale images encode one brightness byte per pixel.
        pixels = canvas.tobytes()
        last = len(CHARACTER_RAMP) - 1
        rows: list[str] = []
        for row_start in range(0, len(pixels), ASCII_WIDTH):
            row = pixels[row_start : row_start + ASCII_WIDTH]
            chars = "".join(CHARACTER_RAMP[round(value / 255 * last)] for value in row)
            rows.append(chars.rstrip())
        return rows


def load_portrait() -> list[str] | None:
    """Prefer the hand-tuned canonical artwork, with photo conversion as fallback."""
    if ASCII_ART.exists():
        return ASCII_ART.read_text(encoding="utf-8").splitlines()
    if SOURCE_IMAGE.exists():
        return image_to_ascii(SOURCE_IMAGE)
    return None


def text(x: int, y: int, value: str, css_class: str = "body", anchor: str = "start") -> str:
    return (
        f'<text x="{x}" y="{y}" class="{css_class}" text-anchor="{anchor}">'
        f"{html.escape(value)}</text>"
    )


def render_portrait(rows: list[str] | None) -> str:
    if rows is None:
        return "\n".join(
            [
                text(274, 305, "[ portrait source missing ]", "placeholder", "middle"),
                text(274, 335, "add profile.jpg + run python generate.py", "tiny", "middle"),
            ]
        )

    line_height = 9.55
    top = 68
    rendered = []
    for index, row in enumerate(rows):
        rendered.append(
            f'<text x="50" y="{top + index * line_height:.1f}" class="ascii" '
            f'xml:space="preserve">{html.escape(row, quote=False)}</text>'
        )
    return "\n".join(rendered)


def build_svg(colors: dict[str, str], portrait: list[str] | None) -> str:
    items = [
        '<svg xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-labelledby="title desc" viewBox="0 0 {VIEWBOX_WIDTH} {VIEWBOX_HEIGHT}">',
        '<title id="title">Yash Mahadeshvar — AI and Data Science student</title>',
        '<desc id="desc">A terminal-inspired GitHub profile with an ASCII portrait, skills, projects, and current focus.</desc>',
        "<style>",
        f".bg{{fill:{colors['bg']}}}.panel{{fill:{colors['panel']};stroke:{colors['border']};stroke-width:1}}",
        f"text{{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,'Liberation Mono',monospace;fill:{colors['text']}}}",
        ".body{font-size:15px}.small{font-size:13px}.tiny{font-size:11px}",
        f".muted{{fill:{colors['muted']}}}.accent{{fill:{colors['accent']}}}.warm{{fill:{colors['accent2']}}}",
        ".heading{font-size:15px;font-weight:700;letter-spacing:.6px}.name{font-size:45px;font-weight:700;letter-spacing:6px}",
        f".ascii{{font-size:{ASCII_FONT_SIZE}px;fill:{colors['portrait']}}}.placeholder{{font-size:14px;fill:{colors['muted']}}}",
        "</style>",
        f'<rect class="bg" width="{VIEWBOX_WIDTH}" height="{VIEWBOX_HEIGHT}" rx="14"/>',
        '<rect class="panel" x="24" y="24" width="525" height="620" rx="10"/>',
        '<rect class="panel" x="573" y="24" width="903" height="620" rx="10"/>',
        render_portrait(portrait),
        text(600, 57, "codingyash9-bit@github:~$ whoami", "small accent"),
        text(600, 112, "Yash Mahadeshvar", "name warm"),
        text(602, 144, "AI & Data Science Student", "heading accent"),
        text(602, 170, "Developer • AI Builder • DSA Explorer", "body"),
        text(602, 211, "> about", "heading accent"),
        text(622, 238, "VESIT  •  Mumbai, India", "body"),
        text(622, 262, "B.Tech — Artificial Intelligence & Data Science", "small muted"),
        '<rect class="panel" x="600" y="286" width="404" height="116" rx="7"/>',
        text(620, 315, "> cat stack.txt", "heading accent"),
        text(620, 344, "Java • Python • JavaScript • SQL", "small"),
        text(620, 368, "React • Next.js • Firebase", "small"),
        text(620, 392, "Git • GitHub • VS Code • HTML • CSS", "small muted"),
        '<rect class="panel" x="1021" y="286" width="426" height="116" rx="7"/>',
        text(1041, 315, "> current_focus", "heading accent"),
        text(1041, 344, "DSA in Java  •  AI / ML", "small"),
        text(1041, 368, "Backend Systems", "small"),
        text(1041, 392, "Building AI Products", "small muted"),
        text(600, 442, "> ls projects/", "heading accent"),
    ]

    projects = [
        ("VESTA", "AI-powered social platform"),
        ("TradingRocket", "AI market intelligence & stock analysis"),
        ("IPOP", "IPO prediction & analysis engine"),
        ("Nostalgia AI", "Memory and nostalgia exploration"),
        ("fixIT", "Autonomous incident-to-fix system"),
        ("ParsIT", "Reddit sentiment analysis"),
        ("Escape Galaxy", "Browser-based vertical space shooter"),
    ]
    for index, (name, description) in enumerate(projects):
        y = 472 + index * 24
        items.append(text(622, y, name, "small warm"))
        items.append(text(785, y, description, "small"))

    items.extend(
        [
            text(44, 672, "codingyash9-bit@github:~$ ./future.sh", "tiny accent"),
            text(330, 672, "Building products. Solving problems. Creating impact.", "tiny muted"),
            text(1150, 672, "codingyash9-bit@github:~$ █", "tiny accent"),
            "</svg>",
        ]
    )
    return "\n".join(items) + "\n"


def build_motion_svg() -> str:
    """Create a restrained animated systems diagram for the README."""
    return '''<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc" viewBox="0 0 1500 250">
<title id="title">Yash Mahadeshvar development loop</title>
<desc id="desc">An animated terminal pipeline moving from learning through building to impact.</desc>
<style>
  :root { color-scheme: light dark; }
  .bg { fill:#fffdf5; } .panel { fill:#fffaf0; stroke:#d0d7de; }
  .line { stroke:#0969da; } .muted-line { stroke:#afb8c1; }
  .txt { fill:#24292f; } .muted { fill:#57606a; } .accent { fill:#0969da; }
  text { font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,'Liberation Mono',monospace; }
  .flow { stroke-dasharray:8 14; animation:flow 2.8s linear infinite; }
  .pulse { animation:pulse 2.4s ease-in-out infinite; transform-box:fill-box; transform-origin:center; }
  .pulse.b { animation-delay:.6s } .pulse.c { animation-delay:1.2s } .pulse.d { animation-delay:1.8s }
  .cursor { animation:blink 1s steps(1,end) infinite; }
  .scanner { animation:scan 4.5s ease-in-out infinite; }
  @keyframes flow { to { stroke-dashoffset:-44; } }
  @keyframes pulse { 0%,100% { opacity:.45; transform:scale(.82) } 45% { opacity:1; transform:scale(1.18) } }
  @keyframes blink { 0%,48% { opacity:1 } 49%,100% { opacity:0 } }
  @keyframes scan { 0%,100% { transform:translateX(0); opacity:.15 } 50% { transform:translateX(1370px); opacity:.75 } }
  @media (prefers-color-scheme: dark) {
    .bg { fill:#080b0d; } .panel { fill:#0d1117; stroke:#30363d; }
    .line { stroke:#7ee787; } .muted-line { stroke:#30363d; }
    .txt { fill:#e6edf3; } .muted { fill:#8b949e; } .accent { fill:#7ee787; }
  }
  @media (prefers-reduced-motion: reduce) { * { animation:none!important } }
</style>
<rect class="bg" width="1500" height="250" rx="14"/>
<rect class="panel" x="24" y="24" width="1452" height="202" rx="10"/>
<text x="52" y="57" class="accent" font-size="14" font-weight="700">codingyash9-bit@github:~$ ./build-loop --observe</text>
<text x="52" y="84" class="muted" font-size="12">continuous development pipeline</text>
<line x1="84" y1="145" x2="1416" y2="145" class="muted-line" stroke-width="2"/>
<line x1="84" y1="145" x2="1416" y2="145" class="line flow" stroke-width="2"/>
<line x1="64" y1="104" x2="64" y2="194" class="line scanner" stroke-width="2"/>
<g text-anchor="middle">
  <circle cx="150" cy="145" r="9" class="accent pulse"/><text x="150" y="181" class="txt" font-size="13">LEARN</text><text x="150" y="201" class="muted" font-size="10">DSA / AI / ML</text>
  <circle cx="550" cy="145" r="9" class="accent pulse b"/><text x="550" y="181" class="txt" font-size="13">MODEL</text><text x="550" y="201" class="muted" font-size="10">reason about systems</text>
  <circle cx="950" cy="145" r="9" class="accent pulse c"/><text x="950" y="181" class="txt" font-size="13">BUILD</text><text x="950" y="201" class="muted" font-size="10">backend / products</text>
  <circle cx="1350" cy="145" r="9" class="accent pulse d"/><text x="1350" y="181" class="txt" font-size="13">IMPACT</text><text x="1350" y="201" class="muted" font-size="10">measure / improve</text>
</g>
<text x="1408" y="57" class="accent cursor" font-size="16">█</text>
</svg>
'''


def main() -> None:
    portrait = load_portrait()
    for filename, colors in THEMES.items():
        (ROOT / filename).write_text(build_svg(colors, portrait), encoding="utf-8")
        print(f"generated {filename}")
    (ROOT / "motion.svg").write_text(build_motion_svg(), encoding="utf-8")
    print("generated motion.svg")
    if portrait is None:
        print("profile.jpg was not found; generated a labeled placeholder instead.")
        print("Add profile.jpg to this directory and rerun: python generate.py")


if __name__ == "__main__":
    main()
