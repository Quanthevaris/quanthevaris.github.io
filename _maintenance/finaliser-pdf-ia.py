"""Ajoute la licence MIT au PDF exporté et conserve deux copies identiques."""
from io import BytesIO
from pathlib import Path
from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parents[1]
pdf = ROOT / 'guide-assistant-ia.pdf'
reader = PdfReader(BytesIO(pdf.read_bytes()))
writer = PdfWriter(clone_from=reader)
licence = (ROOT / 'assets/pdf/LICENCE-MIT.txt').read_bytes()
if 'LICENCE-MIT.txt' in reader.attachments:
    if reader.attachments['LICENCE-MIT.txt'] != [licence]:
        raise ValueError('Licence jointe différente : refaire l’export HTML vers PDF.')
else:
    writer.add_attachment('LICENCE-MIT.txt', licence)
sortie = BytesIO()
writer.write(sortie)
for chemin in (pdf, ROOT / 'assets/pdf/assistant-ia-guide.pdf'):
    chemin.write_bytes(sortie.getvalue())
print('Licence MIT jointe aux deux copies PDF identiques.')
