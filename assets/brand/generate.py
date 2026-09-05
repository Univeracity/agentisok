"""Rebuild the AgentIsOK vector identity and PNG exports.

Requires Inkscape (to outline Inter lettering) and rsvg-convert (PNG export).
The monogram is original path geometry; installed Inter is needed only to rebuild
the wordmark and specimen. Distributed SVGs have no font dependency.
"""
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
PALETTES = {
    "light": ("#B8892E", "#172B24", "#087F5B", "#FCFBF7"),
    "dark": ("#E7C46F", "#F4F2EA", "#43C995", "#10241D"),
    "mono": ("#172B24", "#172B24", "#172B24", "#FCFBF7"),
}


def mark(theme="light"):
    gold, ink, green, _ = PALETTES[theme]
    return f'''
    <g fill="{gold}">
      <path fill-rule="evenodd" d="M26 116 58 30H84L116 116H93L87 98H54L48 116ZM60 80H81L70.5 49Z"/>
      <path d="M143 30H166V116H143Z"/>
    </g>
    <g fill="{ink}">
      <path fill-rule="evenodd" d="M70 163C42 163 26 180 26 207S42 251 70 251 114 234 114 207 98 163 70 163ZM70 184C84 184 92 192 92 207S84 230 70 230 48 222 48 207 56 184 70 184Z"/>
      <path d="M143 165H166V199L194 165H223L188 206 225 249H195L166 214V249H143Z"/>
    </g>
    <path d="M94 128 127 153 220 72" fill="none" stroke="{green}"
          stroke-width="19" stroke-linecap="square" stroke-linejoin="miter"/>
    '''


def svg(width, height, content, title, description):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title description">
  <title id="title">{title}</title>
  <desc id="description">{description}</desc>
  {content.strip()}
</svg>
'''


def lettering(text, x, y, size, color, weight=600, spacing=-1.5):
    return f'<text x="{x}" y="{y}" font-family="Inter" font-weight="{weight}" font-size="{size}" letter-spacing="{spacing}" fill="{color}">{text}</text>'


def save(name, document, png_width=None, outline=False):
    target = ROOT / f"{name}.svg"
    if outline:
        with tempfile.TemporaryDirectory(prefix="agentisok-brand-") as temp:
            source = Path(temp) / "source.svg"
            source.write_text(document, encoding="utf-8")
            subprocess.run([
                "inkscape", str(source), "--export-text-to-path", "--export-plain-svg",
                f"--export-filename={target}",
            ], check=True, stdout=subprocess.DEVNULL)
    else:
        target.write_text(document, encoding="utf-8")
    if png_width:
        subprocess.run([
            "rsvg-convert", "--width", str(png_width),
            "--output", str(ROOT / f"{name}.png"), str(target),
        ], check=True)


def main():
    description = "Gold AI above OK, with a green checkmark crossing the space between the two lines."
    for theme in PALETTES:
        save(f"agentisok-mark-{theme}", svg(256, 280, mark(theme), "AgentIsOK", description), 512 if theme != "mono" else None)
        _, ink, _, _ = PALETTES[theme]
        lockup = f'<g transform="translate(10 4) scale(.52)">{mark(theme)}</g>'
        lockup += lettering("AgentIsOK", 170, 99, 68, ink)
        save(f"agentisok-logo-{theme}", svg(570, 156, lockup, "AgentIsOK", description), outline=True)

    avatar = '<rect width="512" height="512" rx="112" fill="#10241D"/>'
    avatar += f'<g transform="translate(64 42) scale(1.5)">{mark("dark")}</g>'
    save("agentisok-avatar", svg(512, 512, avatar, "AgentIsOK", description), 512)

    # A distinct, simplified favicon preserves AI + check at 16–32 pixels.
    favicon = '''<rect width="64" height="64" rx="14" fill="#10241D"/>
    <path fill="#E7C46F" fill-rule="evenodd" d="M7 39 17 10H25L35 39H27L25 33H17L15 39ZM19 27H23L21 19Z"/>
    <path fill="#E7C46F" d="M39 10H47V35H39Z"/>
    <path d="M29 44 38 51 56 33" fill="none" stroke="#43C995" stroke-width="7"/>'''
    save("agentisok-favicon", svg(64, 64, favicon, "AgentIsOK", "Gold AI and a green check on deep green."), 64)

    social = '<rect width="1280" height="640" fill="#10241D"/>'
    social += '<path d="M72 64H1208" stroke="#E7C46F" stroke-width="2"/>'
    social += f'<g transform="translate(72 137) scale(1.05)">{mark("dark")}</g>'
    social += lettering("AgentIsOK", 403, 268, 102, "#F4F2EA")
    social += lettering("Evidence travels. The origin decides.", 407, 332, 32, "#E7C46F", 400, -.5)
    social += lettering("Open clearance for authorized agents", 407, 387, 25, "#BACDC3", 400, 0)
    social += lettering("PRE-ALPHA  /  APACHE-2.0", 76, 565, 17, "#BACDC3", 500, 2)
    social += lettering("github.com/Univeracity/agentisok", 751, 565, 19, "#BACDC3", 400, 0)
    save("agentisok-social", svg(1280, 640, social, "AgentIsOK", "Open clearance for authorized agents. Evidence travels. The origin decides. Pre-alpha."), 1280, True)

    specimen = '<rect width="1440" height="940" fill="#FCFBF7"/>'
    specimen += lettering("AgentIsOK / Visual identity", 64, 74, 24, "#172B24", 500, -.3)
    specimen += lettering("01", 1330, 74, 18, "#087F5B", 500, 0)
    specimen += '<path d="M64 102H1376" stroke="#DCDDD3"/>'
    specimen += f'<g transform="translate(94 158) scale(1.25)">{mark()}</g>'
    specimen += lettering("AgentIsOK", 500, 295, 108, "#172B24")
    specimen += lettering("Evidence travels. The origin decides.", 505, 359, 30, "#087F5B", 400, -.5)
    specimen += lettering("AI / OK", 97, 556, 17, "#172B24", 600, 1)
    specimen += lettering("An open path for authorized agents.", 500, 482, 23, "#172B24", 400, 0)
    specimen += lettering("Gold for AI. Green for a contextual OK.", 500, 521, 23, "#172B24", 400, 0)
    specimen += '<rect x="64" y="606" width="856" height="270" rx="16" fill="#10241D"/>'
    specimen += f'<g transform="translate(96 639) scale(.7)">{mark("dark")}</g>'
    specimen += lettering("AgentIsOK", 330, 741, 72, "#F4F2EA")
    specimen += lettering("For this action. Under this origin’s policy.", 334, 793, 21, "#E7C46F", 400, -.2)
    for x, color, label in [(958, "#B8892E", "GOLD"), (1099, "#087F5B", "GREEN"), (1240, "#172B24", "INK")]:
        specimen += f'<rect x="{x}" y="606" width="136" height="182" rx="12" fill="{color}"/>'
        specimen += lettering(label, x, 823, 14, "#172B24", 600, 1)
        specimen += lettering(color, x, 855, 16, "#172B24", 400, 0)
    save("agentisok-specimen", svg(1440, 940, specimen, "AgentIsOK visual identity", description), 1440, True)


if __name__ == "__main__":
    main()
