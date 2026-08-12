from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter


COLORS = {
    'bg': '#050816',
    'panel': '#0b1224',
    'cyan': '#58e6ff',
    'blue': '#3f7cff',
    'violet': '#9b6cff',
    'pink': '#f05cff',
    'muted': '#7d91b8',
    'text': '#e8f1ff',
    'green': '#45e0a8',
}


def hex_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip('#')
    return tuple(int(value[index:index + 2], 16) for index in (0, 2, 4))


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def svg_escape(text: str) -> str:
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def write_glow_divider(out: Path) -> None:
    out.write_text('''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="32" viewBox="0 0 1600 32" role="img" aria-label="Cyan violet gradient divider">
  <defs>
    <linearGradient id="line" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#58e6ff" stop-opacity="0"/>
      <stop offset="0.18" stop-color="#58e6ff"/>
      <stop offset="0.5" stop-color="#9b6cff"/>
      <stop offset="0.82" stop-color="#f05cff"/>
      <stop offset="1" stop-color="#f05cff" stop-opacity="0"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-400%" width="140%" height="900%">
      <feGaussianBlur stdDeviation="5" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <path d="M40 16 H1560" stroke="url(#line)" stroke-width="2" filter="url(#glow)"/>
  <circle cx="800" cy="16" r="3" fill="#e8f1ff" filter="url(#glow)"/>
</svg>
''', encoding='utf-8')


def write_tech_strip(out: Path) -> None:
    labels = [
        ('PYTHON', '#3776ab'),
        ('AIOGRAM 3.X', '#2aabee'),
        ('SQLITE / WAL', '#6cc24a'),
        ('UV', '#e8f1ff'),
        ('TELEGRAM SYSTEMS', '#58e6ff'),
        ('AI AUTOMATION', '#9b6cff'),
    ]
    width = 1500
    chip_width = 224
    gap = 18
    height = 96
    chips = []
    for index, (label, color) in enumerate(labels):
        x = 22 + index * (chip_width + gap)
        text_color = '#050816' if color in {'#e8f1ff', '#6cc24a'} else '#ffffff'
        chips.append(f'''<g transform="translate({x},12)">
  <rect width="{chip_width}" height="{height - 24}" rx="18" fill="#0b1224" stroke="{color}" stroke-opacity="0.72"/>
  <rect x="1" y="1" width="{chip_width - 2}" height="{height - 26}" rx="17" fill="{color}" fill-opacity="0.10"/>
  <circle cx="26" cy="36" r="7" fill="{color}"/>
  <text x="48" y="42" fill="#e8f1ff" font-family="Arial, Helvetica, sans-serif" font-size="16" font-weight="700" letter-spacing="1">{svg_escape(label)}</text>
</g>''')
    out.write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Verified technology focus strip">
  <rect width="100%" height="100%" rx="24" fill="#050816"/>
  {''.join(chips)}
</svg>
''', encoding='utf-8')


def contribution_level(count: int) -> tuple[str, int]:
    if count <= 0:
        return '#101a32', 0
    if count == 1:
        return '#1f6f78', 1
    if count == 2:
        return '#2db7bb', 2
    if count <= 4:
        return '#58e6ff', 3
    return '#d5fbff', 4


def write_contribution_svg(out: Path, contribution_json: Path) -> None:
    data = json.loads(contribution_json.read_text(encoding='utf-8'))
    days = data.get('days') or []
    if len(days) > 364:
        days = days[-364:]
    while len(days) < 364:
        days.insert(0, {'date': '', 'count': 0, 'level': 'NONE'})
    weeks = [days[index:index + 7] for index in range(0, 364, 7)]
    cell_w = 24
    cell_d = 13
    origin_x = 810
    origin_y = 64
    cubes = []
    for week_index, week in enumerate(weeks):
        for day_index, day in enumerate(week):
            count = int(day.get('count') or 0)
            color, level = contribution_level(count)
            x = origin_x + (week_index - day_index) * cell_w
            y = origin_y + (week_index + day_index) * cell_d
            height = 3 + level * 8
            top = f'{x},{y - height} {x + cell_w},{y - height - cell_d} {x + 2 * cell_w},{y - height} {x + cell_w},{y - height + cell_d}'
            left = f'{x},{y - height} {x + cell_w},{y - height + cell_d} {x + cell_w},{y + cell_d} {x},{y}'
            right = f'{x + cell_w},{y - height + cell_d} {x + 2 * cell_w},{y - height} {x + 2 * cell_w},{y} {x + cell_w},{y + cell_d}'
            opacity = '1' if level else '0.62'
            cubes.append(f'<g opacity="{opacity}"><polygon points="{top}" fill="{color}" stroke="#b9f7ff" stroke-opacity="0.18"/><polygon points="{left}" fill="#0b6472" stroke="#b9f7ff" stroke-opacity="0.12"/><polygon points="{right}" fill="#15506f" stroke="#b9f7ff" stroke-opacity="0.12"/></g>')
    total = data.get('total_contributions', 0)
    active = data.get('active_day_count', 0)
    out.write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="520" viewBox="0 0 1600 520" role="img" aria-label="Isometric contribution activity snapshot for AhmedFayala">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#050816"/><stop offset="1" stop-color="#101b36"/></linearGradient>
    <radialGradient id="halo"><stop offset="0" stop-color="#58e6ff" stop-opacity="0.18"/><stop offset="1" stop-color="#58e6ff" stop-opacity="0"/></radialGradient>
    <filter id="blur"><feGaussianBlur stdDeviation="18"/></filter>
  </defs>
  <rect width="1600" height="520" rx="30" fill="url(#bg)"/>
  <ellipse cx="820" cy="260" rx="580" ry="230" fill="url(#halo)" filter="url(#blur)"/>
  <g opacity="0.25" stroke="#58e6ff" stroke-width="1"><path d="M70 420 H1530"/><path d="M130 452 H1470"/><path d="M190 484 H1410"/></g>
  <g>{''.join(cubes)}</g>
  <g font-family="Arial, Helvetica, sans-serif">
    <text x="86" y="108" fill="#58e6ff" font-size="16" letter-spacing="4">CONTRIBUTION FIELD / VERIFIED SNAPSHOT</text>
    <text x="86" y="162" fill="#e8f1ff" font-size="40" font-weight="700">AhmedFayala</text>
    <text x="86" y="202" fill="#9bb0d6" font-size="18">Local isometric rendering generated from the GitHub contribution calendar.</text>
    <text x="86" y="258" fill="#58e6ff" font-size="18">{svg_escape(str(total))} contributions</text>
    <text x="86" y="288" fill="#9bb0d6" font-size="16">{svg_escape(str(active))} active days in the retrieved window</text>
    <text x="86" y="438" fill="#7d91b8" font-size="14" letter-spacing="2">DATA SNAPSHOT · REGENERATE LOCALLY WITH THE REFRESH SCRIPT</text>
  </g>
</svg>
''', encoding='utf-8')


def write_typing_gif(out: Path) -> None:
    width, height = 1400, 220
    bg = hex_rgb(COLORS['bg'])
    frames = []
    lines = ['AHMED SALEH', 'PYTHON  /  AUTOMATION  /  TELEGRAM SYSTEMS', 'BUILDING PRACTICAL SOFTWARE, ONE LINE AT A TIME.']
    for frame_index in range(18):
        image = Image.new('RGB', (width, height), bg)
        glow = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow)
        for radius, alpha in [(24, 24), (10, 42), (3, 90)]:
            glow_draw.rounded_rectangle((34 - radius, 32 - radius, width - 34 + radius, 188 + radius), radius=28 + radius, outline=(*hex_rgb(COLORS['cyan']), alpha), width=3)
        glow = glow.filter(ImageFilter.GaussianBlur(8))
        image = Image.alpha_composite(image.convert('RGBA'), glow).convert('RGB')
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((34, 32, width - 34, 188), radius=28, outline=hex_rgb(COLORS['cyan']), width=2)
        draw.rounded_rectangle((52, 50, 80, 78), radius=8, fill=hex_rgb(COLORS['violet']))
        draw.ellipse((60, 58, 72, 70), fill=hex_rgb(COLORS['bg']))
        reveal = min(frame_index * 4, len(lines[1]))
        headline = lines[0] if frame_index % 18 != 17 else lines[0] + '  /'
        draw.text((110, 48), headline, font=font(42, True), fill=hex_rgb(COLORS['text']))
        draw.text((110, 106), lines[1][:reveal] + ('▌' if frame_index % 2 == 0 else ' '), font=font(24, True), fill=hex_rgb(COLORS['cyan']))
        draw.text((110, 146), lines[2], font=font(18), fill=hex_rgb(COLORS['muted']))
        draw.line((110, 184, 1110 + (frame_index % 5) * 38, 184), fill=hex_rgb(COLORS['pink']), width=2)
        frames.append(image)
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=115, loop=0, optimize=True)


def write_tech_strip_png(out: Path) -> None:
    width, height = 1500, 96
    image = Image.new('RGB', (width, height), hex_rgb(COLORS['bg']))
    draw = ImageDraw.Draw(image)
    labels = [
        ('PYTHON', COLORS['blue']),
        ('AIOGRAM 3.X', COLORS['cyan']),
        ('SQLITE / WAL', COLORS['green']),
        ('UV', COLORS['text']),
        ('TELEGRAM SYSTEMS', COLORS['cyan']),
        ('AI AUTOMATION', COLORS['violet']),
    ]
    chip_width, gap = 224, 18
    label_font = font(16, True)
    for index, (label, color) in enumerate(labels):
        x = 22 + index * (chip_width + gap)
        draw.rounded_rectangle((x, 12, x + chip_width, height - 12), radius=18, fill=hex_rgb(COLORS['panel']), outline=hex_rgb(color), width=2)
        draw.ellipse((x + 18, 29, x + 32, 43), fill=hex_rgb(color))
        draw.text((x + 48, 28), label, font=label_font, fill=hex_rgb(COLORS['text']))
    image.save(out, optimize=True)


def write_contribution_png(out: Path, contribution_json: Path) -> None:
    data = json.loads(contribution_json.read_text(encoding='utf-8'))
    days = data.get('days') or []
    if len(days) > 364:
        days = days[-364:]
    while len(days) < 364:
        days.insert(0, {'date': '', 'count': 0, 'level': 'NONE'})
    weeks = [days[index:index + 7] for index in range(0, 364, 7)]
    width, height = 1600, 520
    image = Image.new('RGB', (width, height), hex_rgb(COLORS['bg']))
    draw = ImageDraw.Draw(image)
    for x in range(width):
        blend = x / max(width - 1, 1)
        color = tuple(int(hex_rgb(COLORS['bg'])[i] * (1 - blend * 0.15) + hex_rgb('#101b36')[i] * (blend * 0.15)) for i in range(3))
        draw.line((x, 0, x, height), fill=color)
    glow = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((160, 40, 1240, 480), fill=(*hex_rgb(COLORS['blue']), 36))
    glow = glow.filter(ImageFilter.GaussianBlur(42))
    image = Image.alpha_composite(image.convert('RGBA'), glow).convert('RGB')
    draw = ImageDraw.Draw(image)
    origin_x, origin_y = 820, 64
    cell_w, cell_d = 24, 13
    for week_index, week in enumerate(weeks):
        for day_index, day in enumerate(week):
            count = int(day.get('count') or 0)
            color, level = contribution_level(count)
            x = origin_x + (week_index - day_index) * cell_w
            y = origin_y + (week_index + day_index) * cell_d
            height_delta = 3 + level * 8
            top = [(x, y - height_delta), (x + cell_w, y - height_delta - cell_d), (x + 2 * cell_w, y - height_delta), (x + cell_w, y - height_delta + cell_d)]
            left = [(x, y - height_delta), (x + cell_w, y - height_delta + cell_d), (x + cell_w, y + cell_d), (x, y)]
            right = [(x + cell_w, y - height_delta + cell_d), (x + 2 * cell_w, y - height_delta), (x + 2 * cell_w, y), (x + cell_w, y + cell_d)]
            draw.polygon(top, fill=hex_rgb(color), outline=hex_rgb('#b9f7ff'))
            draw.polygon(left, fill=hex_rgb('#0b6472'), outline=hex_rgb('#1f8c99'))
            draw.polygon(right, fill=hex_rgb('#15506f'), outline=hex_rgb('#1f8c99'))
    label_font = font(16, True)
    title_font = font(40, True)
    body_font = font(18)
    small_font = font(14)
    draw.text((86, 78), 'CONTRIBUTION FIELD / VERIFIED SNAPSHOT', font=label_font, fill=hex_rgb(COLORS['cyan']))
    draw.text((86, 132), 'AhmedFayala', font=title_font, fill=hex_rgb(COLORS['text']))
    draw.text((86, 188), 'Local isometric rendering generated from the GitHub contribution calendar.', font=body_font, fill=hex_rgb('#9bb0d6'))
    draw.text((86, 236), f"{data.get('total_contributions', 0)} contributions", font=body_font, fill=hex_rgb(COLORS['cyan']))
    draw.text((86, 270), f"{data.get('active_day_count', 0)} active days in the retrieved window", font=body_font, fill=hex_rgb('#9bb0d6'))
    draw.text((86, 438), 'DATA SNAPSHOT · REGENERATE LOCALLY WITH THE REFRESH SCRIPT', font=small_font, fill=hex_rgb(COLORS['muted']))
    draw.line((70, 420, 1530, 420), fill=hex_rgb('#214c66'), width=1)
    draw.line((130, 452, 1470, 452), fill=hex_rgb('#214c66'), width=1)
    draw.line((190, 484, 1410, 484), fill=hex_rgb('#214c66'), width=1)
    image.save(out, optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', required=True, type=Path)
    parser.add_argument('--contributions-json', required=True, type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_glow_divider(args.output_dir / 'glow-divider.svg')
    write_tech_strip(args.output_dir / 'tech-strip.svg')
    write_tech_strip_png(args.output_dir / 'tech-strip.png')
    write_contribution_svg(args.output_dir / 'contribution-isometric.svg', args.contributions_json)
    write_contribution_png(args.output_dir / 'contribution-isometric.png', args.contributions_json)
    write_typing_gif(args.output_dir / 'profile-typing.gif')
    print(f'Generated profile assets in {args.output_dir}')


if __name__ == '__main__':
    main()
