"""Vrai test local Ollama (pas une simulation). Sans dépendance Python.
Usage : python verifier_installation.py [--rapport validation-locale.json]
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import subprocess
import sys
from urllib.request import ProxyHandler, Request, build_opener

MODELE = 'llama3.2:1b'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rapport', type=Path)
    args = parser.parse_args()
    try:
        version = subprocess.run(['ollama', '--version'], text=True, capture_output=True,
                                 timeout=10, check=True)
        http = build_opener(ProxyHandler({}))
        with http.open('http://127.0.0.1:11434/api/tags', timeout=10) as r:
            modeles = json.load(r)['models']
        modele = next((m for m in modeles if m.get('name') == MODELE), None)
        if not modele:
            raise RuntimeError(f'Modèle absent. Exécute : ollama pull {MODELE}')
        donnees = {'model': MODELE, 'messages': [
            {'role': 'user', 'content': 'Dis bonjour en français en une phrase.'}],
            'stream': False, 'options': {'num_predict': 60, 'num_ctx': 4096}}
        req = Request('http://127.0.0.1:11434/api/chat', data=json.dumps(donnees).encode(),
                      headers={'Content-Type': 'application/json'})
        with http.open(req, timeout=180) as r:
            resultat = json.load(r)
        texte = resultat.get('message', {}).get('content', '')
        if resultat.get('done') is not True or not isinstance(texte, str) or not texte.strip():
            raise RuntimeError('Ollama n’a pas renvoyé de réponse complète.')
        rapport = {'date_utc': datetime.now(timezone.utc).isoformat(), 'python': platform.python_version(),
                   'systeme': platform.system(), 'ollama': (version.stdout + version.stderr).strip(),
                   'modele': MODELE, 'digest_modele': modele.get('digest'),
                   'reponse_test': texte, 'inference_locale_reelle': True}
        print('INFERENCE LOCALE REELLE OK :', texte)
        print('Il reste à tester l’interface et la qualité des réponses à tes questions.')
        if args.rapport:
            args.rapport.write_text(json.dumps(rapport, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            print('Rapport enregistré :', args.rapport)
        return 0
    except (OSError, ValueError, KeyError, TypeError, AttributeError, RuntimeError,
            subprocess.SubprocessError) as erreur:
        print('TEST NON VALIDE :', erreur, file=sys.stderr)
        print('Installe et démarre Ollama, puis lance ollama pull llama3.2:1b.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
