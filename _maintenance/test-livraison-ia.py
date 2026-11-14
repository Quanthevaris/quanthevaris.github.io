"""Vérifie les livrables, pas une vraie inférence. Dépendance : pypdf."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unittest
from zipfile import ZipFile

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / 'assets/code/assistant-ia'


class Listings(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.pre = False
        self.capture = None
        self.blocs = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        if tag == 'pre':
            self.pre = True
        if tag == 'code' and self.pre:
            self.capture = ''

    def handle_data(self, data):
        if self.capture is not None:
            self.capture += data

    def handle_endtag(self, tag):
        if tag == 'code' and self.capture is not None:
            self.blocs.append(self.capture.rstrip())
            self.capture = None
        if tag == 'pre':
            self.pre = False


class LivraisonTests(unittest.TestCase):
    def test_pdf_et_metadonnees(self):
        data = (ROOT / 'guide-assistant-ia.pdf').read_bytes()
        self.assertEqual(data, (ROOT / 'assets/pdf/assistant-ia-guide.pdf').read_bytes())
        version = json.loads((ROOT / 'assets/pdf/assistant-ia-version.json').read_text())
        self.assertEqual(version['pdf_sha256'], hashlib.sha256(data).hexdigest())
        self.assertEqual(version['pdf_octets'], len(data))
        r = PdfReader(ROOT / 'guide-assistant-ia.pdf')
        self.assertEqual(version['pages'], len(r.pages))
        self.assertGreaterEqual(len(r.pages), 30)
        self.assertIn('Python et Ollama', r.metadata.title)
        self.assertNotIn('GitHub', r.metadata.title)
        def compter(signets):
            return sum(compter(s) if isinstance(s, list) else 1 for s in signets)
        self.assertGreater(compter(r.outline), 15)
        textes = [p.extract_text() for p in r.pages]
        self.assertTrue(all(len(t) > 150 for t in textes), 'Page vide ou presque')
        texte = '\n'.join(textes)
        self.assertNotRegex(texte, r'models\.github\.ai|GITHUB_TOKEN|Models: Read|openai/gpt|from openai')
        self.assertIn('verifier_installation.py', texte)
        self.assertIn('llama3.2:1b', texte)
        self.assertIn('stream', texte)
        self.assertFalse(version['inference_reelle_effectuee_dans_cet_environnement'])

    def test_zip_exact_et_sans_dechets(self):
        version = json.loads((ROOT / 'assets/pdf/assistant-ia-version.json').read_text())
        p = ROOT / 'assets/code/assistant-ia-kit.zip'
        self.assertEqual(version['kit_sha256'], hashlib.sha256(p.read_bytes()).hexdigest())
        with ZipFile(p) as archive:
            self.assertIsNone(archive.testzip())
            self.assertGreaterEqual(len(archive.namelist()), 15)
            for name in archive.namelist():
                self.assertTrue(name.startswith('assistant-ia/'))
                rel = name.removeprefix('assistant-ia/')
                self.assertNotRegex(rel, r'(^|/)(\.venv|__pycache__|node_modules|validation-locale\.json)(/|$)')
                self.assertNotIn('..', Path(rel).parts)
                self.assertEqual(archive.read(name), (KIT / rel).read_bytes(), rel)
            for required in ('serveur.py', 'assistant.js', 'assistant.html', 'assistant.css',
                             'test_eliza.py', 'test_assistant.py', 'verifier_installation.py',
                             '.gitignore', '.github/workflows/tests.yml', 'LICENCE-MIT.txt'):
                self.assertIn('assistant-ia/' + required, archive.namelist())

    def test_listings_du_guide_identiques_aux_sources(self):
        source = (ROOT / 'guide-assistant-ia.html').read_text()
        blocs = Listings(source).blocs
        for nom in ('eliza.py', 'eliza-web.html', 'test_eliza.py', 'serveur.py', 'assistant.html',
                    'assistant.js', 'assistant.css', 'test_assistant.py', 'verifier_installation.py',
                    'connaissances.txt', 'requirements.txt', '.gitignore', '.github/workflows/tests.yml'):
            with self.subTest(fichier=nom):
                self.assertIn((KIT / nom).read_text().rstrip(), blocs)

    def test_parcours_ne_depend_pas_de_l_ancien_service(self):
        for p in KIT.rglob('*'):
            if not p.is_file() or '__pycache__' in p.parts:
                continue
            if p.suffix in ('.py', '.js', '.html'):
                self.assertNotRegex(p.read_text(), r'models\.github\.ai|GITHUB_TOKEN|from openai|api_key')
        serveur = (KIT / 'serveur.py').read_text()
        self.assertIn('host="127.0.0.1"', serveur)
        self.assertIn('debug=False', serveur)
        self.assertIn('static_folder=None', serveur)
        interface = (KIT / 'assistant.js').read_text()
        self.assertIn("fetch('/api/chat'", interface)
        self.assertNotIn('innerHTML =', interface)
        self.assertNotRegex(interface, r'localStorage\.|sessionStorage\.')
        self.assertEqual((KIT / 'LICENCE-MIT.txt').read_bytes(), (ROOT / 'assets/pdf/LICENCE-MIT.txt').read_bytes())


if __name__ == '__main__':
    unittest.main(verbosity=2)
