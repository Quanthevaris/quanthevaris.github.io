"""Après test-parcours-ia.py : met à jour les aperçus sans simuler une vraie conversation."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
source = Image.open(ROOT / '.cache/pixel-interface.png').convert('RGB')
preview = ImageOps.fit(source, (800, 600), method=Image.Resampling.LANCZOS)
preview.save(ROOT / 'assets/img/assistant-ia-preview.png', optimize=True)
preview.save(ROOT / 'assets/img/assistant-ia-preview.webp', quality=88, method=6)

regular = Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
bold = Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
if not regular.is_file() or not bold.is_file():
    raise SystemExit('Installer les polices DejaVu pour régénérer l’image Open Graph.')


def font(size, gras=False):
    return ImageFont.truetype(str(bold if gras else regular), size)


image = Image.new('RGB', (1200, 630), '#070d19')
draw = ImageDraw.Draw(image)
draw.rounded_rectangle((48, 42, 88, 82), radius=10, fill='#061321', outline='#19415b')
draw.ellipse((57, 49, 80, 72), outline='#00d2ff', width=3)
draw.rounded_rectangle((75, 68, 82, 75), radius=2, fill='#ff5a5a')
draw.text((102, 45), 'Quanthevaris', font=font(25, True), fill='#f8fafc')
draw.text((64, 122), 'GUIDE PRATIQUE · ÉDITION LOCALE 2.0', font=font(16), fill='#00d2ff')
for y, text, color in [(168, 'Crée ton', '#f8fafc'), (245, 'assistant IA', '#f8fafc'), (322, 'local.', '#00d2ff')]:
    draw.text((60, y), text, font=font(62, True), fill=color)
draw.text((65, 438), 'Python · Ollama · GitHub', font=font(24), fill='#a3b4cc')
draw.rounded_rectangle((64, 508, 453, 559), radius=25, fill='#08212f', outline='#126079')
draw.text((88, 523), 'PDF + CODE · SANS CLÉ API', font=font(18, True), fill='#00d2ff')
thumb = ImageOps.fit(source, (540, 420), method=Image.Resampling.LANCZOS)
mask = Image.new('L', thumb.size, 0)
ImageDraw.Draw(mask).rounded_rectangle((0, 0, 539, 419), radius=18, fill=255)
image.paste(thumb, (610, 145), mask)
draw = ImageDraw.Draw(image)
draw.rounded_rectangle((609, 144, 1151, 566), radius=18, outline='#243d56', width=2)
draw.text((65, 594), 'quanthevaris.github.io', font=font(14), fill='#92a3bb')
image.save(ROOT / 'assets/img/og-assistant-ia.png', optimize=True)
print('Aperçus et image Open Graph synchronisés avec l’édition locale.')
