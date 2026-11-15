"""Synchronise fiche, compteurs publics et métadonnées après l’export PDF."""
import hashlib
import html
import json
from pathlib import Path
import re
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]


def synchroniser():
    pdf = (ROOT / 'assets/pdf/assistant-ia-guide.pdf').read_bytes()
    assert pdf == (ROOT / 'guide-assistant-ia.pdf').read_bytes()
    pages = len(PdfReader(ROOT / 'guide-assistant-ia.pdf').pages)
    taille = f'{len(pdf) / 1_000_000:.2f}'.replace('.', ',')
    taille_jeu = f'{(ROOT / "assets/pdf/esquive-en-pixels-guide.pdf").stat().st_size / 1_000_000:.2f}'.replace('.', ',')
    p = ROOT / 'assistant-ia.html'
    fiche = p.read_text()
    principal = (ROOT / '_maintenance/guide-ia/fiche-main.html').read_text()
    fiche, n = re.subn(r'<main id="contenu">.*?</main>', lambda m: principal, fiche, count=1, flags=re.S)
    assert n == 1
    titre = 'Crée ton assistant IA local — Python et Ollama | Quanthevaris'
    description = 'Édition locale 2.0 : ELIZA puis Pixel avec Python et Ollama. PDF et kit gratuits, sans clé API. Tests du code inclus ; modèle à valider sur ton ordinateur.'
    fiche = re.sub(r'<title>.*?</title>', lambda m: '<title>' + titre + '</title>', fiche, count=1)
    for key in ('description', 'og:description', 'twitter:description'):
        fiche, n = re.subn(r'(<meta (?:name|property)="' + key + r'" content=")[^"]*(">)',
                          lambda m: m[1] + html.escape(description, quote=True) + m[2], fiche)
        assert n == 1
    for key in ('og:title', 'twitter:title'):
        fiche = re.sub(r'(<meta (?:name|property)="' + key + r'" content=")[^"]*(">)',
                       lambda m: m[1] + titre + m[2], fiche)
    fiche = re.sub(r'(<meta property="og:image:alt" content=")[^"]*(">)',
                   lambda m: m[1] + 'Pixel, atelier local Python et Ollama — édition 2.0.' + m[2], fiche)
    schema = re.search(r'<script type="application/ld\+json">(.*?)</script>', fiche, re.S)
    donnees = json.loads(schema[1])
    donnees.update(name='Crée ton assistant IA personnalisé — Python et Ollama',
                   description=description, numberOfPages=pages, dateModified='2026-11-14',
                   version='2.0', keywords='assistant IA local, ollama, python, flask, eliza, tutoriel')
    fiche = fiche[:schema.start(1)] + '\n' + json.dumps(donnees, ensure_ascii=False, indent=2) + '\n' + fiche[schema.end(1):]
    p.write_text(fiche)
    # Une URL différente force le rechargement après remplacement d’un ancien fichier.
    # Les chemins historiques sans paramètre restent disponibles pour les anciens liens.
    ressources = (
        'assets/pdf/assistant-ia-guide.pdf', 'guide-assistant-ia.pdf',
        'assets/pdf/esquive-en-pixels-guide.pdf',
        'assets/img/assistant-ia-preview.png', 'assets/img/assistant-ia-preview.webp',
        'assets/img/og-assistant-ia.png',
    )
    empreintes = {nom: hashlib.sha256((ROOT / nom).read_bytes()).hexdigest()[:12]
                  for nom in ressources}
    for p in ROOT.glob('*.html'):
        texte = p.read_text()
        texte = re.sub(r'(data-ia-pages>)\d+(</span>)', lambda m: m[1] + str(pages) + m[2], texte)
        texte = re.sub(r'(data-ia-size>)[\d,]+(</span>)', lambda m: m[1] + taille + m[2], texte)
        texte = re.sub(r'(data-jeu-size>)[\d,]+(</span>)', lambda m: m[1] + taille_jeu + m[2], texte)
        texte = texte.replace('Guide Assistant IA — en actualisation', 'Guide Assistant IA — édition locale')
        for nom, empreinte in empreintes.items():
            texte = re.sub(re.escape('/' + nom) + r'(?:\?v=[\w.-]+)?(?=["\s>])',
                           lambda m: '/' + nom + '?v=' + empreinte, texte)
        p.write_text(texte)
    kit = (ROOT / 'assets/code/assistant-ia-kit.zip').read_bytes()
    version = {'version': '2.0', 'date': '2026-11-14', 'pages': pages, 'pdf_octets': len(pdf),
               'pdf_sha256': hashlib.sha256(pdf).hexdigest(), 'kit_octets': len(kit),
               'kit_sha256': hashlib.sha256(kit).hexdigest(), 'modele_reference': 'llama3.2:1b',
               'inference_reelle_effectuee_dans_cet_environnement': False,
               'validation_restante': 'Installer le modèle et tester une vraie conversation sur le matériel du lecteur.'}
    (ROOT / 'assets/pdf/assistant-ia-version.json').write_text(json.dumps(version, ensure_ascii=False, indent=2) + '\n')
    print(f'Fiche et compteurs synchronisés : {pages} pages, {taille} Mo, kit {len(kit)} octets.')


if __name__ == '__main__':
    synchroniser()
