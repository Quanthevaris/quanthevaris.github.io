"""Régressions de sécurité statiques : python3 _maintenance/test-securite.py."""
from html.parser import HTMLParser
from pathlib import Path
import re
import runpy
import unittest

ROOT = Path(__file__).resolve().parents[1]
securiser = runpy.run_path(str(ROOT / '_maintenance/securiser-pages.py'))['securiser']


class Page(HTMLParser):
    def __init__(self, texte):
        super().__init__()
        self.tags = []
        self.feed(texte)

    def handle_starttag(self, nom, attrs):
        self.tags.append((nom, dict(attrs)))


class SecuriteTests(unittest.TestCase):
    def test_politiques_et_absence_gestionnaires_inline(self):
        for p in ROOT.glob('*.html'):
            texte = p.read_text()
            if not texte.lstrip().lower().startswith('<!doctype'):
                continue  # Fichier Google : doit rester strictement inchangé.
            with self.subTest(page=p.name):
                self.assertEqual(securiser(texte), texte, 'Resynchroniser la CSP')
                tags = Page(texte).tags
                politiques = [a['content'] for n, a in tags if n == 'meta'
                              and a.get('http-equiv') == 'Content-Security-Policy']
                self.assertEqual(len(politiques), 1)
                csp = politiques[0]
                for regle in ("default-src 'none'", "base-uri 'none'", "object-src 'none'",
                              "script-src-attr 'none'", "form-action 'none'", "frame-src 'none'"):
                    self.assertIn(regle, csp)
                script_src = next(r for r in csp.split(';') if r.strip().startswith('script-src '))
                self.assertNotIn('unsafe-inline', script_src)
                self.assertNotIn('unsafe-eval', csp)
                self.assertLess(texte.index('Content-Security-Policy'), texte.index('<title>'))
                self.assertIn(('meta', {'name': 'referrer', 'content': 'no-referrer'}), tags)
                for nom, attrs in tags:
                    self.assertFalse(any(k.lower().startswith('on') for k in attrs), (nom, attrs))
                    if nom == 'script' and 'src' in attrs:
                        self.assertTrue(attrs['src'].startswith('/js/'), attrs)
                    if nom == 'a' and attrs.get('target') == '_blank':
                        self.assertTrue({'noopener', 'noreferrer'} <= set(attrs.get('rel', '').split()))

    def test_empreinte_jsonld_et_rejet_js_inline(self):
        texte = '<!DOCTYPE html><html><head>\n<meta charset="utf-8">\n<title>Test</title>\n'
        avec_schema = texte + '<script type="application/ld+json">{"name":"test"}</script></head></html>'
        avant = securiser(avec_schema)
        apres = securiser(avec_schema.replace('"test"', '"autre"'))
        self.assertNotEqual(re.search(r"sha256-[^']+", avant)[0], re.search(r"sha256-[^']+", apres)[0])
        with self.assertRaises(ValueError):
            securiser(texte + '<script>alert(1)</script></head></html>')

    def test_actions_epinglees_et_separation_publication(self):
        for p in (ROOT / '.github/workflows').glob('*.yml'):
            texte = p.read_text()
            for action in re.findall(r'^\s*- uses: (\S+)', texte, re.M):
                self.assertRegex(action, r'^[\w-]+/[\w-]+@[0-9a-f]{40}$')
            self.assertNotIn('pull_request_target', texte)
        workflow = (ROOT / '.github/workflows/fission-arena-exe.yml').read_text()
        compilation, publication = workflow.split('\n  publier:\n', 1)
        self.assertNotIn('contents: write', compilation)
        self.assertNotIn('pages: write', compilation)
        self.assertIn('persist-credentials: false', compilation)
        self.assertNotIn('pip install', publication)
        self.assertNotIn('run: python', publication)
        self.assertIn('needs: exe', publication)
        self.assertIn('sha256sum assets/jeux/FISSION_ARENA.py', publication)
        self.assertNotIn('git pull --rebase', publication)

    def test_bouton_impression_externe_et_source_canonique(self):
        for p in ('guide-assistant-ia.html', '_maintenance/guide-ia/template.html'):
            texte = (ROOT / p).read_text()
            self.assertIn('id="imprimer-guide"', texte)
            self.assertIn('<script src="/js/impression-guide.js" defer></script>', texte)
        for p in ('generer-guide-ia.py', 'synchroniser-ia.py'):
            self.assertIn('securiser-pages.py', (ROOT / '_maintenance' / p).read_text())


if __name__ == '__main__':
    unittest.main(verbosity=2)
