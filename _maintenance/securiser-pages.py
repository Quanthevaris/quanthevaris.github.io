"""CSP du site statique : python3 _maintenance/securiser-pages.py [--check].

Ne touche jamais au fichier de validation Google. Les empreintes autorisent
uniquement les blocs JSON-LD exacts ; aucun JavaScript inline exécutable.
Une CSP meta ne peut pas fournir frame-ancestors ni les en-têtes HTTP serveur.
"""
import argparse
import base64
import hashlib
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = re.compile(r'<script\b([^>]*)>(.*?)</script>', re.S | re.I)
META = re.compile(r'<meta\s+(?:http-equiv="Content-Security-Policy"|name="referrer")\s+content="[^"]*">\n?', re.I)


def securiser(texte):
    if not re.search(r'<html\b', texte, re.I):
        return texte
    hashes = []
    for attrs, contenu in SCRIPT.findall(texte):
        if re.search(r'\bsrc\s*=', attrs, re.I):
            continue
        if not re.search(r'\btype="application/ld\+json"', attrs, re.I):
            raise ValueError('JavaScript inline interdit : utiliser un fichier local.')
        empreinte = base64.b64encode(hashlib.sha256(contenu.encode()).digest()).decode()
        hashes.append("'sha256-" + empreinte + "'")
    politique = (
        "default-src 'none'; base-uri 'none'; object-src 'none'; "
        "script-src 'self'" + ''.join(' ' + h for h in sorted(set(hashes))) + "; "
        "script-src-attr 'none'; style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; font-src 'self'; "
        "connect-src 'self' https://quanthevaris.goatcounter.com; "
        "form-action 'none'; frame-src 'none'"
    )
    texte = META.sub('', texte)
    balises = ('<meta http-equiv="Content-Security-Policy" content="' + politique + '">\n'
               '<meta name="referrer" content="no-referrer">\n')
    texte, n = re.subn(r'(<meta charset="utf-8">\n)', lambda m: m[1] + balises,
                       texte, count=1, flags=re.I)
    if n != 1:
        raise ValueError('Placer une déclaration UTF-8 au début du head.')
    return texte


def synchroniser(check=False):
    chemins = list(ROOT.glob('*.html')) + [ROOT / '_maintenance/guide-ia/template.html']
    ecarts = []
    for p in chemins:
        texte = p.read_text()
        nouveau = securiser(texte)
        if texte != nouveau:
            ecarts.append(str(p.relative_to(ROOT)))
            if not check:
                p.write_text(nouveau)
    if check and ecarts:
        raise SystemExit('CSP à synchroniser : ' + ', '.join(ecarts))
    print('Politiques de sécurité ' + ('vérifiées.' if check else 'synchronisées.'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    synchroniser(parser.parse_args().check)
