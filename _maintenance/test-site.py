"""Contrôles statiques sans réseau : python3 _maintenance/test-site.py."""
import hashlib
import json
import re
import unittest
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://quanthevaris.github.io'


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.links = []
        self.meta = {}
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        for key in ('href', 'src'):
            if key in attrs:
                self.links.append(attrs[key])
        if 'srcset' in attrs:
            self.links.extend(item.strip().split()[0] for item in attrs['srcset'].split(','))
        if tag == 'meta':
            self.meta[attrs.get('name', attrs.get('property'))] = attrs.get('content', '')


class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.texts = {p.name: p.read_text() for p in ROOT.glob('*.html')}
        cls.pages = {name: Page(text) for name, text in cls.texts.items()}

    def test_liens_et_ancres_internes(self):
        for name, page in self.pages.items():
            for link in page.links:
                url = urlsplit(urljoin(f'{ORIGIN}/{name}', link))
                if url.scheme not in ('http', 'https') or url.netloc != 'quanthevaris.github.io':
                    continue
                target_name = unquote(url.path).lstrip('/') or 'index.html'
                with self.subTest(page=name, link=link):
                    self.assertTrue((ROOT / target_name).is_file(), target_name)
                    if url.fragment and target_name in self.pages:
                        self.assertIn(unquote(url.fragment), self.pages[target_name].ids)

    def test_nouvelle_illustration_accueil(self):
        text = self.texts['index.html']
        hero = text.split('<section class="hero">', 1)[1].split('</section>', 1)[0]
        self.assertIn('class="hero-artwork"', hero)
        self.assertIn('/assets/img/code-to-play-hero.webp', hero)
        self.assertIn('width="1200" height="896"', hero)
        self.assertIn('fetchpriority="high"', hero)
        self.assertIn('Illustration d’ambiance 3D', hero)
        self.assertIn('qui se joue en 2D', hero)
        artwork = hero.split('<figure class="hero-artwork">', 1)[1].split('</figure>', 1)[0]
        self.assertNotIn('<figcaption', artwork)
        self.assertNotIn('hero-artwork-label', artwork)
        # Le visuel n’a ni titre ni légende visibles ; l’alternative reste accessible.
        self.assertEqual(re.sub(r'<[^>]+>', '', artwork).strip(), '')
        self.assertNotIn('/assets/img/esquive-preview', hero)
        # Les vraies captures du guide sont conservées plus bas dans la page.
        self.assertIn('/assets/img/esquive-preview.png', text.split('</section>', 1)[1])
        self.assertLess((ROOT / 'assets/img/code-to-play-hero.webp').stat().st_size, 100_000)

    def test_accueil_distingue_les_deux_pdf(self):
        version = json.loads((ROOT / 'assets/pdf/assistant-ia-version.json').read_text())
        hero = self.texts['index.html'].split('<section class="hero">', 1)[1].split('</section>', 1)[0]
        self.assertNotIn('PDF de 25 pages', hero)
        self.assertIn('PDF jeu : 25 pages', hero)
        self.assertIn(f'PDF IA : <span data-ia-pages>{version["pages"]}</span> pages', hero)
        self.assertIn('Code des guides sous licence MIT', hero)

    def test_identifiants_uniques(self):
        for name, page in self.pages.items():
            with self.subTest(page=name):
                self.assertEqual([key for key, n in Counter(page.ids).items() if n > 1], [])

    def test_edition_locale_et_metadonnees(self):
        version = json.loads((ROOT / 'assets/pdf/assistant-ia-version.json').read_text())
        for name in ('index.html', 'guides.html', 'assistant-ia.html', 'guide-assistant-ia.html'):
            with self.subTest(page=name):
                self.assertIn('Ollama', self.texts[name])
                self.assertIn('local', self.pages[name].meta['description'])
                self.assertNotIn('en cours d’actualisation', self.texts[name])
                self.assertNotIn('archive-notice', self.texts[name])
        page = self.texts['assistant-ia.html']
        self.assertIn('id="actualisation"', page)  # anciens liens conservés
        self.assertNotIn('Ce qui est vérifié', page)
        self.assertNotIn('Ce qui reste à valider sur ton matériel', page)
        source = (ROOT / '_maintenance/guide-ia/fiche-main.html').read_text()
        self.assertNotIn('Ce qui est vérifié', source)
        self.assertNotIn('Ce qui reste à valider sur ton matériel', source)
        for script in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S):
            data = json.loads(script)
            self.assertEqual(data['numberOfPages'], version['pages'])
            self.assertIn('Ollama', data['description'])
            self.assertEqual(data['name'], 'Crée ton assistant IA personnalisé — Python et Ollama')
            self.assertIn('ollama', data['keywords'].lower())
            self.assertNotIn('github', data['keywords'].lower())
        guide = self.texts['guide-assistant-ia.html']
        titre = re.search(r'<title>(.*?)</title>', guide)[1]
        self.assertIn('Python et Ollama', titre)
        self.assertNotIn('GitHub', titre)
        for nom in ('README.md', 'mentions-legales.html', 'assets/pdf/LICENCE-MIT.txt',
                    'assets/code/assistant-ia/LICENCE-MIT.txt'):
            texte = (ROOT / nom).read_text()
            self.assertIn('Crée ton assistant IA personnalisé — Python et Ollama', texte)
            self.assertNotIn('Python, Ollama et GitHub', texte)
        for name in ('index.html', 'guides.html', 'assistant-ia.html'):
            for number in re.findall(r'data-ia-pages>(\d+)', self.texts[name]):
                self.assertEqual(int(number), version['pages'])

    def test_telechargements_et_guide_imprimable(self):
        for link in ('/assets/pdf/assistant-ia-guide.pdf', '/assets/code/assistant-ia-kit.zip', '/guide-assistant-ia.html'):
            self.assertIn(link, [urlsplit(url).path for url in self.pages['assistant-ia.html'].links])
        guide = self.texts['guide-assistant-ia.html']
        self.assertNotIn('noindex', self.pages['guide-assistant-ia.html'].meta.get('robots', ''))
        self.assertNotIn('/js/audience.js', guide)
        self.assertNotRegex(guide, r'models\.github\.ai|GITHUB_TOKEN|Models: Read|openai/gpt|from openai')
        self.assertIn('stream', guide)
        self.assertIn('verifier_installation.py', guide)
        self.assertIn('ne lance ni Python, ni Flask, ni Ollama', guide)

    def test_pdf_et_apercus_remplaces_sans_ancien_cache(self):
        for name in ('index.html', 'guides.html', 'assistant-ia.html'):
            page = self.pages[name]
            liens = page.links + [page.meta.get('og:image', ''), page.meta.get('twitter:image', '')]
            apercus = [url for url in liens if 'assistant-ia-preview.' in url]
            self.assertTrue(apercus, name)
            for url in liens:
                if not any(nom in url for nom in ('assistant-ia-preview.', 'og-assistant-ia.png', 'assistant-ia-guide.pdf')):
                    continue
                fichier = ROOT / urlsplit(url).path.lstrip('/')
                empreinte = hashlib.sha256(fichier.read_bytes()).hexdigest()[:12]
                self.assertEqual(urlsplit(url).query, 'v=' + empreinte, (name, url))
            self.assertNotIn('ÉDITION GITHUB', self.texts[name])

    def test_confidentialite_sans_promesse_absolue(self):
        for name, page in self.pages.items():
            for key, value in page.meta.items():
                if key and 'description' in key:
                    self.assertNotRegex(value.lower(), r'aucune donnée collectée|aucune trace|pas de collecte de données')
        for name in ('index.html', 'contact.html', 'confidentialite.html', 'mentions-legales.html'):
            self.assertIn('GitHub Pages', self.texts[name])
            self.assertRegex(self.texts[name], r'audience agrégée|audience</h2>')
        policy = self.texts['confidentialite.html']
        self.assertIn('ne signifie pas automatiquement exempté de consentement', policy)
        self.assertIn('consentement préalable valable', policy)


if __name__ == '__main__':
    unittest.main(verbosity=2)
