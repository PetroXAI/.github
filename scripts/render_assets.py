#!/usr/bin/env python3
"""Render Retina visual assets for the PetroXAI GitHub Organization profile.

Generates:
  - profile/assets/banner-dark.png        (2560x760, 2x Retina)
  - profile/assets/banner-light.png       (2560x760, 2x Retina)
  - profile/assets/affiliation-dark.png   (2560x248, 2x Retina)
  - profile/assets/affiliation-light.png  (2560x248, 2x Retina)
  - profile/assets/icons/{simhelm,labtrace,fieldmind,logscope,specmind}.png (96x96)

Usage:
  python3 scripts/render_assets.py \\
    --brand-dir ../home/public/brand \\
    --font-file ../home/src/assets/fonts/saira-latin-standard-normal.woff2 \\
    --chrome /path/to/chrome-headless-shell
"""

from __future__ import annotations

import argparse
import base64
import math
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image


def b64_file(path: Path, mime: str) -> str:
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def recolor_svg(svg_text: str, new_fill: str) -> str:
    """Recolor white-monochrome official SVGs for light-mode rendering."""
    out = re.sub(r'fill="#(?:fff|ffffff|FFF|FFFFFF)"', f'fill="{new_fill}"', svg_text)
    out = re.sub(r'fill="white"', f'fill="{new_fill}"', out)
    return out


def svg_to_data_uri(svg_text: str) -> str:
    data = base64.b64encode(svg_text.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{data}"


def font_face_css(font_file: Path | None) -> str:
    if not font_file or not font_file.exists():
        return ""
    uri = b64_file(font_file, "font/woff2")
    return f"""
@font-face {{
  font-family: "Saira";
  font-style: normal;
  font-weight: 100 900;
  font-stretch: 50% 125%;
  src: url("{uri}") format("woff2-variations");
}}
"""


def build_hero_html(theme: str, brand_dir: Path, font_css: str) -> str:
    is_dark = theme == "dark"

    # Official PetroXAI wordmark & icon
    wordmark_path = brand_dir / "petroxai" / (
        "petroxai-logo-reverse.svg" if is_dark else "petroxai-logo-color.svg"
    )
    wordmark_uri = svg_to_data_uri(wordmark_path.read_text(encoding="utf-8"))
    core_icon_uri = svg_to_data_uri(
        (brand_dir / "petroxai" / "petroxai-icon.svg").read_text(encoding="utf-8")
    )

    # Five publicly released products (official order matching petroxai.com)
    products = [
        (
            "SimHelm",
            svg_to_data_uri((brand_dir / "simhelm" / "simhelm-favicon-full.svg").read_text(encoding="utf-8")),
            False,
        ),
        (
            "LabTrace",
            svg_to_data_uri((brand_dir / "labtrace" / "labtrace-mark.svg").read_text(encoding="utf-8")),
            True,  # Needs crisp white tile backing
        ),
        (
            "FieldMind",
            svg_to_data_uri((brand_dir / "fieldmind" / "fieldmind-appicon.svg").read_text(encoding="utf-8")),
            False,
        ),
        (
            "LogScope",
            b64_file(brand_dir / "logscope" / "logscope-app-icon-512.png", "image/png"),
            False,
        ),
        (
            "SpecMind",
            svg_to_data_uri((brand_dir / "specmind" / "specmind-tile.svg").read_text(encoding="utf-8")),
            False,
        ),
    ]

    # Hub geometry inside 440x360 right container
    cx, cy, r = 220.0, 190.0, 108.0
    hub_lines = []
    hub_nodes_html = []
    for idx, (name, uri, white_tile) in enumerate(products):
        angle = -math.pi / 2 + (2 * math.pi * idx) / len(products)
        nx = cx + r * math.cos(angle)
        ny = cy + r * math.sin(angle)
        hub_lines.append(
            f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{nx:.1f}" y2="{ny:.1f}" '
            f'stroke="{"rgba(92,142,255,0.56)" if is_dark else "rgba(0,47,167,0.28)"}" '
            f'stroke-width="1.5" stroke-dasharray="4 5" />'
        )
        tile_cls = "node-tile white-tile" if white_tile else "node-tile"
        label_pos = "label-top" if idx == 0 else "label-bottom"
        hub_nodes_html.append(
            f"""
            <div class="hub-node {label_pos}" style="left:{nx:.1f}px; top:{ny:.1f}px;">
              {'<span class="node-label">' + name + '</span>' if idx == 0 else ''}
              <div class="{tile_cls}">
                <img src="{uri}" alt="{name}" />
              </div>
              {'<span class="node-label">' + name + '</span>' if idx != 0 else ''}
            </div>
            """
        )

    if is_dark:
        bg_css = """
          background:
            radial-gradient(640px 440px at 81% 48%, rgba(0, 47, 167, 0.72), transparent 68%),
            radial-gradient(500px 320px at 8% 12%, rgba(43, 89, 224, 0.24), transparent 65%),
            linear-gradient(135deg, #000719 0%, #001038 56%, #001549 100%);
        """
        border_color = "rgba(166, 188, 225, 0.22)"
        grid_stroke = "rgba(130, 162, 235, 0.085)"
        wave1 = "rgba(43, 89, 224, 0.42)"
        wave2 = "rgba(0, 150, 214, 0.30)"
        wave3 = "rgba(166, 188, 225, 0.18)"
        kicker_color = "rgba(166, 188, 225, 0.72)"
        kicker_hi = "#F42434"
        h1_color = "#FFFFFF"
        zh_color = "#A7B7D9"
        meta_color = "#DCE7FF"
        meta_muted = "rgba(166, 188, 225, 0.50)"
        meta_dot_blue = "#5B8BFF"
        divider_color = "rgba(166, 188, 225, 0.20)"
        ring_stroke = "rgba(166, 188, 225, 0.14)"
        ring_inner = "rgba(43, 89, 224, 0.28)"
        node_label_color = "#DCE7FF"
        node_tile_border = "1px solid rgba(166, 188, 225, 0.24)"
        node_shadow = "0 10px 24px -6px rgba(0, 5, 22, 0.78)"
        core_shadow = "0 0 0 8px rgba(0, 47, 167, 0.28), 0 18px 42px -10px rgba(0, 47, 167, 0.9)"
        pill_bg = "rgba(255, 255, 255, 0.06)"
        pill_border = "rgba(166, 188, 225, 0.22)"
    else:
        bg_css = """
          background:
            radial-gradient(600px 420px at 81% 50%, rgba(0, 47, 167, 0.095), transparent 70%),
            radial-gradient(460px 300px at 6% 10%, rgba(43, 89, 224, 0.055), transparent 65%),
            linear-gradient(135deg, #FFFFFF 0%, #F5F8FE 58%, #EBF1FC 100%);
        """
        border_color = "rgba(0, 47, 167, 0.16)"
        grid_stroke = "rgba(0, 47, 167, 0.055)"
        wave1 = "rgba(0, 47, 167, 0.16)"
        wave2 = "rgba(0, 150, 214, 0.14)"
        wave3 = "rgba(0, 47, 167, 0.08)"
        kicker_color = "#566785"
        kicker_hi = "#E30613"
        h1_color = "#0A1330"
        zh_color = "#465572"
        meta_color = "#1B2B4B"
        meta_muted = "rgba(10, 19, 48, 0.32)"
        meta_dot_blue = "#002FA7"
        divider_color = "rgba(0, 47, 167, 0.13)"
        ring_stroke = "rgba(0, 47, 167, 0.11)"
        ring_inner = "rgba(0, 47, 167, 0.18)"
        node_label_color = "#182848"
        node_tile_border = "1px solid rgba(10, 19, 48, 0.10)"
        node_shadow = "0 8px 20px -6px rgba(10, 19, 48, 0.18)"
        core_shadow = "0 0 0 8px rgba(0, 47, 167, 0.09), 0 14px 32px -10px rgba(0, 47, 167, 0.28)"
        pill_bg = "rgba(0, 47, 167, 0.05)"
        pill_border = "rgba(0, 47, 167, 0.16)"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<style>
{font_css}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{
  width: 1280px;
  height: 380px;
  overflow: hidden;
  font-family: "Saira", "Noto Sans CJK SC", system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
}}
.canvas {{
  position: relative;
  width: 1280px;
  height: 380px;
  {bg_css}
  border: 1px solid {border_color};
  overflow: hidden;
}}
/* Subtle top brand accent bar */
.top-accent {{
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #002FA7 0%, #002FA7 78%, #E30613 78%, #E30613 100%);
  z-index: 5;
}}
.bg-svg {{
  position: absolute;
  inset: 0;
  width: 1280px;
  height: 380px;
  z-index: 0;
}}
.content {{
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  height: 100%;
  padding: 0 58px 0 64px;
}}
.left {{
  width: 660px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  gap: 0;
}}
.kicker {{
  display: inline-flex;
  align-items: center;
  gap: 12px;
  font-family: "Saira", sans-serif;
  font-size: 15.5px;
  font-weight: 400;
  letter-spacing: 0.08em;
  color: {kicker_color};
  margin-bottom: 18px;
}}
.kicker-bar {{
  width: 24px;
  height: 2.5px;
  background: #E30613;
  flex-shrink: 0;
}}
.kicker-hi {{
  color: {kicker_hi};
  font-weight: 700;
}}
.kicker-sep {{
  opacity: 0.48;
  margin: 0 5px;
}}
.wordmark {{
  height: 44px;
  width: 489px;
  display: block;
  align-self: flex-start;
  margin-bottom: 22px;
}}
.headline {{
  font-family: "Saira", sans-serif;
  font-size: 25px;
  font-weight: 500;
  letter-spacing: 0.025em;
  color: {h1_color};
  line-height: 1.24;
  margin-bottom: 8px;
}}
.sub-zh {{
  font-family: "Noto Sans CJK SC", sans-serif;
  font-size: 15.5px;
  font-weight: 400;
  letter-spacing: 0.08em;
  color: {zh_color};
  margin-bottom: 26px;
}}
.meta-row {{
  width: 100%;
  display: flex;
  align-items: center;
  gap: 14px;
  padding-top: 18px;
  border-top: 1px solid {divider_color};
}}
.meta-tag {{
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 5px 12px;
  border-radius: 3px;
  background: {pill_bg};
  border: 1px solid {pill_border};
  font-family: "Saira", "Noto Sans CJK SC", sans-serif;
  font-size: 13px;
  font-weight: 500;
  letter-spacing: 0.05em;
  color: {meta_color};
}}
.meta-dot {{
  width: 6px;
  height: 6px;
  border-radius: 1px;
  background: {meta_dot_blue};
}}
.meta-dot.red {{
  background: #E30613;
}}
.meta-sep {{
  color: {meta_muted};
  font-size: 13px;
}}
.meta-inst {{
  font-family: "Saira", "Noto Sans CJK SC", sans-serif;
  font-size: 13px;
  font-weight: 400;
  letter-spacing: 0.03em;
  color: {zh_color};
}}

/* Right Hub Constellation */
.right {{
  position: relative;
  width: 440px;
  height: 360px;
  flex-shrink: 0;
}}
.hub-svg {{
  position: absolute;
  inset: 0;
  width: 440px;
  height: 360px;
}}
.hub-core {{
  position: absolute;
  left: {cx:.1f}px;
  top: {cy:.1f}px;
  width: 76px;
  height: 76px;
  transform: translate(-50%, -50%);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: {core_shadow};
  z-index: 3;
}}
.hub-core img {{
  width: 100%;
  height: 100%;
  display: block;
}}
.hub-node {{
  position: absolute;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  z-index: 3;
}}
.hub-node.label-top {{
  transform: translate(-50%, calc(-50% - 10px));
}}
.hub-node.label-bottom {{
  transform: translate(-50%, calc(-50% + 10px));
}}
.node-tile {{
  width: 48px;
  height: 48px;
  border-radius: 12px;
  overflow: hidden;
  border: {node_tile_border};
  box-shadow: {node_shadow};
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
}}
.node-tile.white-tile {{
  background: #FFFFFF;
  border: 1px solid rgba(10, 19, 48, 0.14);
  padding: 6px;
}}
.node-tile img {{
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}}
.node-tile.white-tile img {{
  object-fit: contain;
}}
.node-label {{
  font-family: "Saira", sans-serif;
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0.04em;
  color: {node_label_color};
  white-space: nowrap;
  line-height: 1;
}}
</style>
</head>
<body>
  <div class="canvas">
    <div class="top-accent"></div>
    <svg class="bg-svg" viewBox="0 0 1280 380" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
          <path d="M 40 0 L 0 0 0 40" fill="none" stroke="{grid_stroke}" stroke-width="1" />
        </pattern>
        <linearGradient id="fadeGrid" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="white" stop-opacity="0.95" />
          <stop offset="70%" stop-color="white" stop-opacity="0.65" />
          <stop offset="100%" stop-color="white" stop-opacity="0.25" />
        </linearGradient>
        <mask id="gridMask">
          <rect width="1280" height="380" fill="url(#fadeGrid)" />
        </mask>
      </defs>
      <rect width="1280" height="380" fill="url(#grid)" mask="url(#gridMask)" />
      <!-- Subsurface seismic horizon lines -->
      <g fill="none" stroke-linecap="round">
        <path d="M -40 278 Q 190 236 420 282 T 880 276 T 1340 264" stroke="{wave1}" stroke-width="1.35" />
        <path d="M -40 318 Q 210 288 440 322 T 900 314 T 1340 306" stroke="{wave2}" stroke-width="1.05" />
        <path d="M -40 236 Q 170 198 400 240 T 860 234 T 1340 222" stroke="{wave3}" stroke-width="0.85" />
      </g>
    </svg>

    <div class="content">
      <div class="left">
        <div class="kicker">
          <span class="kicker-bar"></span>
          <span><span class="kicker-hi">PETRO</span>leum<span class="kicker-sep">·</span>e<span class="kicker-hi">X</span>plainable<span class="kicker-sep">·</span><span class="kicker-hi">A</span>rtificial <span class="kicker-hi">I</span>ntelligence</span>
        </div>
        <img class="wordmark" src="{wordmark_uri}" alt="PetroXAI" />
        <div class="headline">Explainable AI Platform for Petroleum Engineering</div>
        <div class="sub-zh">油气工程可解释智能平台</div>
        <div class="meta-row">
          <span class="meta-tag"><span class="meta-dot"></span>petroxai.com</span>
          <span class="meta-tag"><span class="meta-dot red"></span>5 Live Products</span>
          <span class="meta-sep">·</span>
          <span class="meta-inst">China University of Petroleum, Beijing</span>
        </div>
      </div>

      <div class="right">
        <svg class="hub-svg" viewBox="0 0 440 360" xmlns="http://www.w3.org/2000/svg">
          <circle cx="{cx:.1f}" cy="{cy:.1f}" r="108" fill="none" stroke="{ring_stroke}" stroke-width="1" />
          <circle cx="{cx:.1f}" cy="{cy:.1f}" r="70" fill="none" stroke="{ring_inner}" stroke-width="1" stroke-dasharray="3 5" />
          {''.join(hub_lines)}
        </svg>
        <div class="hub-core">
          <img src="{core_icon_uri}" alt="PetroXAI" />
        </div>
        {''.join(hub_nodes_html)}
      </div>
    </div>
  </div>
</body>
</html>
"""


def build_affiliation_html(theme: str, brand_dir: Path, font_css: str) -> str:
    is_dark = theme == "dark"
    cupb_dir = brand_dir / "cupb"

    emblem_svg = (cupb_dir / "cupb-emblem-white.svg").read_text(encoding="utf-8")
    wordmark_svg = (cupb_dir / "cupb-wordmark-white.svg").read_text(encoding="utf-8")
    if not is_dark:
        # Official CUPB dark red for emblem, deep ink for calligraphy wordmark
        emblem_svg = recolor_svg(emblem_svg, "#8C1515")
        wordmark_svg = recolor_svg(wordmark_svg, "#0A1330")

    emblem_uri = svg_to_data_uri(emblem_svg)
    wordmark_uri = svg_to_data_uri(wordmark_svg)
    rock_uri = svg_to_data_uri(
        (cupb_dir / ("rock-mechanics-lab-white.svg" if is_dark else "rock-mechanics-lab.svg")).read_text(encoding="utf-8")
    )
    smart_uri = b64_file(cupb_dir / "smart-energy-lab.webp", "image/webp")

    if is_dark:
        bg = "linear-gradient(135deg, #000B24 0%, #00123A 100%)"
        border = "rgba(166, 188, 225, 0.18)"
        lab_zh_color = "#F0F4FF"
        lab_en_color = "#8FA3CC"
        sep_color = "rgba(166, 188, 225, 0.30)"
        cupb_en_color = "#A6BCE1"
        right_badge_bg = "rgba(255, 255, 255, 0.05)"
        right_badge_border = "rgba(166, 188, 225, 0.18)"
    else:
        bg = "linear-gradient(135deg, #FFFFFF 0%, #F5F8FE 100%)"
        border = "rgba(0, 47, 167, 0.14)"
        lab_zh_color = "#0A1330"
        lab_en_color = "#546585"
        sep_color = "rgba(0, 47, 167, 0.22)"
        cupb_en_color = "#4B5D82"
        right_badge_bg = "rgba(0, 47, 167, 0.04)"
        right_badge_border = "rgba(0, 47, 167, 0.14)"

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<style>
{font_css}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{
  width: 1280px;
  height: 116px;
  overflow: hidden;
  font-family: "Saira", "Noto Sans CJK SC", system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
}}
.bar {{
  width: 1280px;
  height: 116px;
  background: {bg};
  border: 1px solid {border};
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 44px;
  position: relative;
}}
.left-accent {{
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: linear-gradient(180deg, #002FA7 0%, #002FA7 68%, #E30613 68%, #E30613 100%);
}}
.lockup {{
  display: flex;
  align-items: center;
  gap: 16px;
}}
.emblems {{
  display: flex;
  align-items: center;
  gap: 12px;
}}
.emblem {{
  height: 60px;
  width: auto;
  display: block;
}}
.emblem.round {{
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
}}
.org-text {{
  margin-left: 10px;
  display: flex;
  flex-direction: column;
  gap: 5px;
}}
.row-univ {{
  display: flex;
  align-items: center;
  gap: 14px;
}}
.cupb-wm {{
  height: 24px;
  width: auto;
  display: block;
}}
.univ-en {{
  font-family: "Saira", sans-serif;
  font-size: 13px;
  font-weight: 500;
  letter-spacing: 0.06em;
  color: {cupb_en_color};
  padding-left: 12px;
  border-left: 1px solid {sep_color};
}}
.row-labs-zh {{
  display: flex;
  align-items: center;
  gap: 14px;
  font-family: "Noto Sans CJK SC", sans-serif;
  font-size: 15.5px;
  font-weight: 600;
  letter-spacing: 0.08em;
  color: {lab_zh_color};
}}
.row-labs-zh span + span {{
  padding-left: 14px;
  border-left: 1px solid {sep_color};
}}
.row-labs-en {{
  font-family: "Saira", sans-serif;
  font-size: 12px;
  font-weight: 400;
  letter-spacing: 0.03em;
  color: {lab_en_color};
}}
</style>
</head>
<body>
  <div class="bar">
    <div class="left-accent"></div>
    <div class="lockup">
      <div class="emblems">
        <img class="emblem" src="{emblem_uri}" alt="CUPB" />
        <img class="emblem" src="{rock_uri}" alt="Rock Mechanics Lab" />
        <img class="emblem round" src="{smart_uri}" alt="Smart Energy Systems Lab" />
      </div>
      <div class="org-text">
        <div class="row-univ">
          <img class="cupb-wm" src="{wordmark_uri}" alt="中国石油大学(北京)" />
          <span class="univ-en">China University of Petroleum, Beijing</span>
        </div>
        <div class="row-labs-zh">
          <span>岩石力学实验室</span>
          <span>智慧能源系统与工程实验室</span>
        </div>
        <div class="row-labs-en">Rock Mechanics Laboratory &nbsp;·&nbsp; Laboratory of Smart Energy Systems and Engineering</div>
      </div>
    </div>
  </div>
</body>
</html>
"""


def build_icon_html(uri: str, white_tile: bool) -> str:
    tile_style = (
        "background:#FFFFFF; border:2px solid rgba(10,19,48,0.14); padding:10px;"
        if white_tile
        else "background:transparent;"
    )
    fit = "contain" if white_tile else "cover"
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8" />
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ width: 96px; height: 96px; background: transparent; overflow: hidden; }}
.tile {{
  width: 96px; height: 96px;
  border-radius: 22px;
  overflow: hidden;
  display: flex; align-items: center; justify-content: center;
  {tile_style}
}}
img {{ width: 100%; height: 100%; object-fit: {fit}; display: block; }}
</style>
</head>
<body><div class="tile"><img src="{uri}" /></div></body>
</html>
"""


def render_html(
    chrome: str,
    html: str,
    out_png: Path,
    width: int,
    height: int,
    scale: float = 2.0,
    out_size: tuple[int, int] | None = None,
    transparent: bool = False,
) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        html_path = Path(tmp) / "page.html"
        html_path.write_text(html, encoding="utf-8")
        cmd = [
            chrome,
            "--headless",
            "--no-sandbox",
            "--disable-gpu",
            "--hide-scrollbars",
            f"--force-device-scale-factor={scale}",
            f"--window-size={width},{height}",
            f"--screenshot={out_png}",
        ]
        if transparent:
            cmd.append("--default-background-color=00000000")
        cmd.append(html_path.as_uri())
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    im = Image.open(out_png)
    if out_size and im.size != out_size:
        im = im.resize(out_size, Image.Resampling.LANCZOS)
    im.save(out_png, format="PNG", optimize=True)


def detect_chrome(explicit: str | None) -> str:
    if explicit:
        return explicit
    for cand in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
        found = shutil.which(cand)
        if found:
            return found
    cache = Path.home() / ".cache" / "ms-playwright"
    if cache.exists():
        for pattern in ("chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell",
                        "chromium-*/chrome-linux64/chrome"):
            matches = sorted(cache.glob(pattern), reverse=True)
            if matches:
                return str(matches[0])
    raise RuntimeError("No Chromium/Chrome binary found. Pass --chrome /path/to/chrome.")


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="Render PetroXAI GitHub profile visual assets.")
    parser.add_argument("--brand-dir", type=Path, default=repo_root.parent / "home" / "public" / "brand")
    parser.add_argument(
        "--font-file",
        type=Path,
        default=repo_root.parent / "home" / "src" / "assets" / "fonts" / "saira-latin-standard-normal.woff2",
    )
    parser.add_argument("--chrome", type=str, default=None)
    args = parser.parse_args()

    chrome = detect_chrome(args.chrome)
    brand_dir = args.brand_dir.resolve()
    font_css = font_face_css(args.font_file.resolve() if args.font_file else None)

    assets_dir = repo_root / "profile" / "assets"
    icons_dir = assets_dir / "icons"
    icons_dir.mkdir(parents=True, exist_ok=True)

    # 1. Hero Banners (Dark & Light) — render at 2x, downsample to crisp 1920x570 (>2x on GitHub)
    for theme in ("dark", "light"):
        html = build_hero_html(theme, brand_dir, font_css)
        out = assets_dir / f"banner-{theme}.png"
        render_html(chrome, html, out, 1280, 380, scale=2, out_size=(1920, 570))
        print(f"Rendered {out.relative_to(repo_root)} ({out.stat().st_size // 1024} KB)")

    # 2. Affiliation Bars (Dark & Light) — render at 2x, downsample to crisp 1920x174
    for theme in ("dark", "light"):
        html = build_affiliation_html(theme, brand_dir, font_css)
        out = assets_dir / f"affiliation-{theme}.png"
        render_html(chrome, html, out, 1280, 116, scale=2, out_size=(1920, 174))
        print(f"Rendered {out.relative_to(repo_root)} ({out.stat().st_size // 1024} KB)")

    # 3. Uniform Rounded Product Icons (96x96)
    icon_specs = [
        ("simhelm", svg_to_data_uri((brand_dir / "simhelm" / "simhelm-favicon-full.svg").read_text(encoding="utf-8")), False),
        ("labtrace", svg_to_data_uri((brand_dir / "labtrace" / "labtrace-mark.svg").read_text(encoding="utf-8")), True),
        ("fieldmind", svg_to_data_uri((brand_dir / "fieldmind" / "fieldmind-appicon.svg").read_text(encoding="utf-8")), False),
        ("logscope", b64_file(brand_dir / "logscope" / "logscope-app-icon-512.png", "image/png"), False),
        ("specmind", svg_to_data_uri((brand_dir / "specmind" / "specmind-tile.svg").read_text(encoding="utf-8")), False),
    ]
    for key, uri, white_tile in icon_specs:
        out = icons_dir / f"{key}.png"
        render_html(chrome, build_icon_html(uri, white_tile), out, 96, 96, scale=1, transparent=True)
        print(f"Rendered {out.relative_to(repo_root)} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
