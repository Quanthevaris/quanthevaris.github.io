"""Source unique HTML/ZIP : .venv/bin/python _maintenance/generer-guide-ia.py.
Après génération, exporter le PDF avec exporter-guide-ia.mjs puis synchroniser les pages.
"""
from html import escape
from pathlib import Path
import re
from zipfile import ZipFile, ZIP_DEFLATED, ZipInfo
import markdown

ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / 'assets/code/assistant-ia'
SOURCE = ROOT / '_maintenance/guide-ia'
FICHIERS = [
    'eliza.py', 'eliza-web.html', 'serveur.py', 'assistant.html', 'assistant.js',
    'assistant.css', 'connaissances.txt', 'requirements.txt', 'test_eliza.py',
    'test_assistant.py', 'verifier_installation.py', 'LICENCE-MIT.txt',
    'LIRE-MOI.md', '.gitignore', '.github/workflows/tests.yml',
]


def code(match):
    name = match[1]
    if name not in FICHIERS:
        raise ValueError('Fichier non autorisé : ' + name)
    texte = (KIT / name).read_text(encoding='utf-8').rstrip()
    return '\n```text\n' + texte + '\n```\n'


def generer():
    contenu = re.sub(r'\{\{code:([^}]+)}}', code, (SOURCE / 'contenu.md').read_text())
    morceaux = re.split(r'<!-- section:([\w-]+) -->', contenu)
    sections, titres = [], []
    for identifiant, texte in zip(morceaux[1::2], morceaux[2::2]):
        titre = re.search(r'^# (.+)$', texte, re.M)[1]
        titres.append((identifiant, titre))
        html = markdown.markdown(texte, extensions=['fenced_code', 'tables', 'sane_lists'])
        # Un seul h1 sur la couverture, chapitres h2, sous-titres h3.
        html = re.sub(r'<(/?)h2>', r'<\1h3>', html)
        html = re.sub(r'<(/?)h1>', r'<\1h2>', html)
        sections.append(f'<section class="chapitre" id="{identifiant}">{html}</section>')
    sommaire = '<nav class="chapitre sommaire" id="sommaire" aria-label="Sommaire"><p class="eyebrow">SE REPÉRER</p><h2>Ton parcours</h2><ol>'
    sommaire += ''.join(f'<li><a href="#{identifiant}">{escape(titre)}</a></li>' for identifiant, titre in titres)
    sommaire += '</ol><p>Sommaire cliquable dans le HTML et le PDF. La pagination est générée à partir de cette édition, sans reprendre celle de l’ancien document.</p></nav>'
    css = (SOURCE / 'style.css').read_text()
    template = (SOURCE / 'template.html').read_text()
    resultat = template.replace('{{STYLE}}', css).replace('{{SOMMAIRE}}', sommaire).replace('{{CONTENU}}', '\n'.join(sections))
    assert not re.search(r'\{\{(?:STYLE|SOMMAIRE|CONTENU|code:)', resultat)
    (ROOT / 'guide-assistant-ia.html').write_text(resultat, encoding='utf-8')
    destination = ROOT / 'assets/code/assistant-ia-kit.zip'
    with ZipFile(destination, 'w', compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for nom in FICHIERS:
            info = ZipInfo('assistant-ia/' + nom, date_time=(2026, 11, 14, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, (KIT / nom).read_bytes())
    print('Guide HTML et kit ZIP générés depuis les mêmes fichiers de code.')
    import runpy
    runpy.run_path(str(ROOT / '_maintenance/securiser-pages.py'))['synchroniser']()


if __name__ == '__main__':
    generer()
