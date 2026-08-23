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

# Portrait controls: adjust these and rerun the script to tune the result.
ASCII_WIDTH = 84
ASCII_HEIGHT = 58
CONTRAST = 1.30
BRIGHTNESS = 1.12
CHARACTER_RAMP = "@%#*+=-:. "  # darkest to lightest
ASCII_FONT_SIZE = 9.2
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

    line_height = 9.6
    top = 70
    rendered = []
    for index, row in enumerate(rows):
        rendered.append(
            f'<text x="46" y="{top + index * line_height:.1f}" class="ascii" '
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


def main() -> None:
    portrait = image_to_ascii(SOURCE_IMAGE) if SOURCE_IMAGE.exists() else None
    for filename, colors in THEMES.items():
        (ROOT / filename).write_text(build_svg(colors, portrait), encoding="utf-8")
        print(f"generated {filename}")
    if portrait is None:
        print("profile.jpg was not found; generated a labeled placeholder instead.")
        print("Add profile.jpg to this directory and rerun: python generate.py")


if __name__ == "__main__":
    main()
