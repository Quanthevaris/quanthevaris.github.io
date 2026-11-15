"""Applique les retouches éditoriales au PDF Pygame, sans toucher au code.

L’original ne possède pas de source éditable dans le dépôt. On repart du PDF
conservé dans Git (pas du fichier joint à une conversation). Une autre copie de
cet original peut être passée avec --source. Aucune page n’est rasterisée.
Usage : .venv/bin/python _maintenance/relire-guide-jeu.py
"""
import argparse
from io import BytesIO
import json
from pathlib import Path
import subprocess

from fontTools.ttLib import TTFont
import pymupdf as fitz

ROOT = Path(__file__).resolve().parents[1]
SOURCE_GIT = '4fe4e50e2b37a8c2d20f136fde23c8194b124520:assets/pdf/esquive-en-pixels-guide.pdf'
DEST = ROOT / 'assets/pdf/esquive-en-pixels-guide.pdf'
DOSSIER = ROOT / '_maintenance/guide-jeu'


def police(gras=False):
    chemin = ROOT / ('assets/fonts/inter-bold.woff2' if gras else 'assets/fonts/inter-regular.woff2')
    ttf = TTFont(BytesIO(chemin.read_bytes()))
    ttf.flavor = None
    sortie = BytesIO()
    ttf.save(sortie)
    return sortie.getvalue()


def lignes(texte, fonte, taille, largeur):
    resultat = []
    for paragraphe in texte.split('\n'):
        ligne = ''
        for mot in paragraphe.split():
            essai = (ligne + ' ' + mot).strip()
            if ligne and fonte.text_length(essai, fontsize=taille) > largeur:
                resultat.append(ligne)
                ligne = mot
            else:
                ligne = essai
        resultat.append(ligne)
    return resultat


def ecrire(page, rect, texte, taille, fonte, nom, couleur):
    """Même corps si possible ; échec explicite si le texte ne tient pas."""
    initiale = taille
    while taille >= min(initiale, 7.5):
        contenu = lignes(texte, fonte, taille, rect.width)
        hauteur = (fonte.ascender - fonte.descender + (len(contenu) - 1) * 1.4) * taille
        if hauteur <= rect.height:
            page.insert_text((rect.x0, rect.y0 + fonte.ascender * taille), contenu,
                             fontsize=taille, fontname=nom, color=couleur, lineheight=1.4)
            return rect.y0 + hauteur
        taille = round(taille - .1, 3)
    raise ValueError(f'Texte trop long en page {page.number + 1} : {texte}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path)
    args = parser.parse_args()
    original = args.source.read_bytes() if args.source else subprocess.check_output(
        ['git', 'show', SOURCE_GIT], cwd=ROOT)
    doc = fitz.open(stream=original, filetype='pdf')
    buffers = [police(), police(True)]
    fontes = [fitz.Font(fontbuffer=b) for b in buffers]
    retouches = json.loads((DOSSIER / 'retouches.json').read_text())
    for page in doc:
        insertions = []
        for retouche in (r for r in retouches if r['page'] == page.number + 1):
            rects = page.search_for(retouche['avant'])
            if not rects:
                raise ValueError(f'Passage introuvable : {retouche}')
            rect = fitz.Rect(rects[0])
            for r in rects[1:]:
                rect |= r
            spans = [s for b in page.get_text('dict')['blocks'] if 'lines' in b
                     for l in b['lines'] for s in l['spans']
                     if fitz.Rect(s['bbox']).intersects(rect) and s['text'].strip()]
            taille = max(s['size'] for s in spans)
            couleur = fitz.sRGB_to_pdf(spans[0]['color'])
            gras = taille >= 9.9
            # Effacer seulement les glyphes, pas les fonds, schémas ou cadres.
            for r in rects:
                page.add_redact_annot(r, fill=False, cross_out=False)
            insertions.append((rect + (0, 0, 2, 2), retouche['apres'], taille, gras, couleur))
        if page.number == 24:
            page.add_redact_annot(fitz.Rect(60, 242, 535, 750), fill=False, cross_out=False)
            for lien in page.get_links():
                if lien['from'].y0 > 236:
                    page.delete_link(lien)
            for annotation in list(page.annots() or []):
                if annotation.rect.y0 > 236 and annotation.type[0] != fitz.PDF_ANNOT_REDACT:
                    page.delete_annot(annotation)
        page.apply_redactions(images=0, graphics=0)
        if page.number == 24:
            # Refaire le fond du bloc pour retirer les anciens traits de liens et
            # prolonger le cadre sous les mentions, sans toucher aux ressources.
            page.draw_rect(fitz.Rect(50, 235, 546, 752), color=None,
                           fill=fitz.sRGB_to_pdf(0x070d19), overlay=True)
            page.draw_rect(fitz.Rect(51, 237, 544, 660), color=fitz.sRGB_to_pdf(0x26384e),
                           fill=fitz.sRGB_to_pdf(0x101827), width=.6, overlay=True)
            page.draw_line((52, 238), (52, 659), color=(0, .82, 1), width=2)
        for nom, buffer in zip(('qtexte', 'qtitre'), buffers):
            page.insert_font(fontname=nom, fontbuffer=buffer)
        for rect, texte, taille, gras, couleur in insertions:
            ecrire(page, rect, texte, taille, fontes[gras], 'qtitre' if gras else 'qtexte', couleur)
        if page.number == 24:
            y = 250
            for i, bloc in enumerate((DOSSIER / 'mentions.txt').read_text().strip().split('\n\n')):
                titre = i == 0 or bloc.startswith('## ')
                if bloc.startswith('## '):
                    entete, corps = bloc[3:].split('\n', 1)
                    y = ecrire(page, fitz.Rect(67.5, y, 527, 750), entete, 9.5,
                               fontes[1], 'qtitre', (.0, .82, 1.0)) + 5
                    bloc, titre = corps, False
                y = ecrire(page, fitz.Rect(67.5, y, 527, 750), bloc, 9.5 if titre else 8.5,
                           fontes[titre], 'qtitre' if titre else 'qtexte',
                           (.94, .97, 1.) if titre else (.80, .85, .91)) + 12
            assert y < 750, y
            # Des liens utilisables aussi dans un lecteur PDF hors navigateur.
            for texte, uri in (
                ('contact.quanthevaris@gmail.com', 'mailto:contact.quanthevaris@gmail.com'),
                ('quanthevaris.github.io/mentions-legales.html', 'https://quanthevaris.github.io/mentions-legales.html'),
                ('quanthevaris.github.io/confidentialite.html', 'https://quanthevaris.github.io/confidentialite.html'),
                ('LICENCE-MIT.txt', 'https://quanthevaris.github.io/assets/pdf/LICENCE-MIT.txt'),
            ):
                for r in page.search_for(texte):
                    page.insert_link({'kind': fitz.LINK_URI, 'from': r, 'uri': uri})
    licence = (ROOT / 'assets/pdf/LICENCE-MIT.txt').read_bytes()
    if 'LICENCE-MIT.txt' in doc.embfile_names():
        doc.embfile_del('LICENCE-MIT.txt')
    doc.embfile_add('LICENCE-MIT.txt', licence)
    metadata = doc.metadata
    metadata['modDate'] = "D:20261114000000+00'00'"
    doc.set_metadata(metadata)
    # Les deux pages du code de référence doivent rester strictement identiques.
    avant = fitz.open(stream=original, filetype='pdf')
    for n in (16, 17):
        assert avant[n].get_text() == doc[n].get_text(), f'Code modifié page {n + 1}'
    data = doc.tobytes(garbage=4, deflate=True)
    DEST.write_bytes(data)
    print(f'Guide Pygame : {len(retouches)} retouches, mentions relues, 25 pages, {len(data)} octets.')


if __name__ == '__main__':
    main()
