"""Contrôles statiques sans réseau : python3 _maintenance/test-site.py."""
import hashlib
import json
import re
import unittest
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
from urllib.robotparser import RobotFileParser
from zipfile import ZipFile
import xml.etree.ElementTree as ET

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

    def test_boutons_edition_locale_et_guide(self):
        for nom in ('index.html', 'guides.html'):
            self.assertRegex(self.texts[nom],
                             r'<a href="/assistant-ia\.html"[^>]*>Découvrir l’édition locale et le guide ')

    def test_fichier_validation_google_inchange(self):
        nom = 'google4068430e1e1eeb11.html'
        self.assertEqual((ROOT / nom).read_bytes(),
                         ('google-site-verification: ' + nom).encode('ascii'))
        self.assertNotIn(nom, (ROOT / 'sitemap.xml').read_text())

    def test_indexabilite_statique_pages_du_sitemap(self):
        robots = RobotFileParser()
        robots.parse((ROOT / 'robots.txt').read_text().splitlines())
        self.assertIn(ORIGIN + '/sitemap.xml', robots.site_maps())
        sitemap = ET.parse(ROOT / 'sitemap.xml')
        urls = [element.text for element in sitemap.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
        self.assertEqual(len(urls), len(set(urls)))
        self.assertIn(ORIGIN + '/', urls)
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(urlsplit(url).netloc, 'quanthevaris.github.io')
                nom = urlsplit(url).path.lstrip('/') or 'index.html'
                self.assertIn(nom, self.texts)
                self.assertTrue(robots.can_fetch('Googlebot', url))
                self.assertNotRegex(self.pages[nom].meta.get('robots', '').lower(), r'\b(noindex|none)\b')
                self.assertNotRegex(self.pages[nom].meta.get('googlebot', '').lower(), r'\b(noindex|none)\b')
                self.assertIn(f'<link rel="canonical" href="{url}">', self.texts[nom])
        self.assertNotIn(ORIGIN + '/404.html', urls)

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

    def test_licence_du_code_et_lien_vers_le_depot(self):
        # GitHub ne détecte « MIT » que si LICENSE contient le texte MIT standard,
        # sans ajout : tout commentaire de périmètre irait dans la documentation.
        licence = (ROOT / 'LICENSE').read_text()
        standard = (ROOT / 'assets/pdf/LICENSE-MIT-CODE.txt').read_text()
        self.assertEqual(licence, standard, 'LICENSE doit rester le texte MIT exact')
        self.assertTrue(licence.startswith('MIT License\n\nCopyright (c) 2026 Quanthevaris\n'))
        self.assertNotIn('Périmètre', licence)
        self.assertLess(len(licence.encode()), 1200, 'trop long pour la détection GitHub')
        # Le texte joint aux PDF commencent par une note de périmètre, puis le texte exact.
        jointe = (ROOT / 'assets/pdf/LICENCE-MIT.txt').read_text()
        self.assertTrue(jointe.endswith(licence))
        self.assertIn('FISSION ARENA', jointe.split('MIT License\n', 1)[0])
        self.assertEqual((ROOT / 'assets/pdf/LICENCE-MIT.txt').read_bytes(),
                         (ROOT / 'assets/code/assistant-ia/LICENCE-MIT.txt').read_bytes())
        depot = 'https://github.com/Quanthevaris/quanthevaris.github.io'
        for name in ('index.html', 'guides.html', 'assistant-ia.html', 'esquive-en-pixels.html',
                     'jeux.html', 'fission-arena.html', 'contact.html', 'confidentialite.html',
                     'mentions-legales.html', '404.html'):
            with self.subTest(page=name):
                self.assertIn(f'<a href="{depot}">Code source du site sur GitHub</a>',
                              self.texts[name])
        # La portée de la licence est expliquée sur la page des mentions légales.
        self.assertIn('id="propriete-intellectuelle"', self.texts['mentions-legales.html'])
        self.assertIn(f'<a href="{depot}/blob/main/LICENSE">LICENSE</a>',
                      self.texts['mentions-legales.html'])
        self.assertIn('[`LICENSE`](LICENSE)', (ROOT / 'README.md').read_text())

    def test_coherence_des_licences_du_depot(self):
        """Une seule formulation par périmètre : code, guides, jeu, composants tiers."""
        jeu = (ROOT / 'assets/jeux/LICENCE-FISSION-ARENA.txt').read_text()
        for extrait in ("FISSION ARENA est un jeu gratuit, mais ce n'est pas un logiciel libre",
                        'Copyright (c) 2026 Quanthevaris. Tous droits réservés.',
                        'CE QUE TU PEUX FAIRE, GRATUITEMENT ET SANS AUTORISATION',
                        "CE QUI DEMANDE L'ACCORD ÉCRIT DE L'AUTEUR",
                        'pygame (GNU LGPL 2.1)', 'FreeSansBold (GPL)',
                        'trois ans', 'jeu gratuit'):
            self.assertIn(extrait, jeu)
        # Le jeu n'est cité dans aucun document sous licence MIT.
        for nom in ('LICENSE', 'assets/pdf/LICENCE-MIT.txt', 'assets/code/assistant-ia/LICENCE-MIT.txt'):
            texte = (ROOT / nom).read_text()
            section_mit = texte[texte.index('MIT License'):]
            self.assertNotIn('FISSION ARENA', section_mit, nom)
        # Le code du site n'est jamais annoncé sous une autre licence que MIT.
        for nom, texte in self.texts.items():
            if 'FISSION ARENA' not in texte:
                continue
            for phrase in re.findall(r'[^.]*MIT[^.]*\.', texte):
                if 'FISSION ARENA' in phrase:
                    self.assertRegex(phrase, r"n'est pas sous licence MIT|ne couvre ni|ni le jeu",
                                     (nom, phrase))
        # La page du jeu renvoie vers le fichier de licence et vers le kit.
        page = self.texts['fission-arena.html']
        self.assertIn('/assets/jeux/LICENCE-FISSION-ARENA.txt', page)
        self.assertIn('/assets/jeux/FISSION_ARENA-kit.zip', page)
        self.assertIn('/assets/jeux/LICENCE-FISSION-ARENA.txt', self.texts['mentions-legales.html'])
        # Le kit du jeu contient sa licence, identique au fichier publié.
        with ZipFile(ROOT / 'assets/jeux/FISSION_ARENA-kit.zip') as archive:
            self.assertEqual(archive.read('FISSION_ARENA-kit/LICENCE-FISSION-ARENA.txt'),
                             (ROOT / 'assets/jeux/LICENCE-FISSION-ARENA.txt').read_bytes())
            for nom in ('fabriquer_exe.py', 'construire_exe.bat', 'fission-arena.ico', 'LIRE-MOI.txt'):
                self.assertEqual(archive.read('FISSION_ARENA-kit/' + nom),
                                 (ROOT / '_exe' / nom).read_bytes(), nom)


if __name__ == '__main__':
    unittest.main(verbosity=2)
