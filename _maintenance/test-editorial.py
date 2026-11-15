"""Contrôles des retouches des deux guides : pas de réseau ni de modèle."""
import hashlib
import json
from pathlib import Path
import re
import unittest

import pymupdf
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]


def normaliser(texte):
    return ' '.join(texte.split())


class EditorialTests(unittest.TestCase):
    def test_mentions_ia_completes(self):
        guide = (ROOT / 'guide-assistant-ia.html').read_text()
        mentions = guide.split('id="mentions">', 1)[1].split('</section>', 1)[0]
        for texte in ('Informations d’édition', 'Autoéditeur', 'ISBN',
                      'Texte, illustrations et maquette', 'Code source : licence MIT',
                      'Logiciels, modèles et marques', 'Données personnelles et fonctionnement local',
                      'Usage pédagogique et responsabilité', 'Llama 3.2 Community License',
                      'sous réserve des exceptions prévues par la loi',
                      'mailto:contact.quanthevaris@gmail.com',
                      'https://quanthevaris.github.io/confidentialite.html',
                      'https://quanthevaris.github.io/mentions-legales.html'):
            self.assertIn(texte, mentions)

    def test_licences_jointes_aux_pdf(self):
        licence = (ROOT / 'assets/pdf/LICENCE-MIT.txt').read_bytes()
        for nom in ('guide-assistant-ia.pdf', 'assets/pdf/assistant-ia-guide.pdf',
                    'assets/pdf/esquive-en-pixels-guide.pdf'):
            with self.subTest(pdf=nom):
                r = PdfReader(ROOT / nom)
                self.assertEqual(list(r.attachments), ['LICENCE-MIT.txt'])
                self.assertEqual(r.attachments['LICENCE-MIT.txt'], [licence])

    def test_retouches_pygame_presentes(self):
        with pymupdf.open(ROOT / 'assets/pdf/esquive-en-pixels-guide.pdf') as doc:
            self.assertEqual(len(doc), 25)
            for retouche in json.loads((ROOT / '_maintenance/guide-jeu/retouches.json').read_text()):
                with self.subTest(page=retouche['page'], texte=retouche['apres']):
                    self.assertIn(normaliser(retouche['apres']),
                                  normaliser(doc[retouche['page'] - 1].get_text()))
            for texte in ('Code source : licence MIT', 'Logiciels et marques',
                          'Usage pédagogique et responsabilité', 'confidentialite.html',
                          'ne pourrait légalement l’être'):
                self.assertIn(texte, normaliser(doc[-1].get_text()))
            self.assertNotIn('décline toute responsabilité', doc[-1].get_text())

    def test_code_pygame_reference_inchange(self):
        controle = json.loads((ROOT / '_maintenance/guide-jeu/controle.json').read_text())
        with pymupdf.open(ROOT / 'assets/pdf/esquive-en-pixels-guide.pdf') as doc:
            for numero, empreinte in controle['code_reference_pages'].items():
                self.assertEqual(hashlib.sha256(doc[int(numero) - 1].get_text().encode()).hexdigest(),
                                 empreinte, 'Code de référence page ' + numero)

    def test_formulations_retirees(self):
        fichiers = list(ROOT.glob('*.html')) + [ROOT / '_maintenance/guide-ia/contenu.md',
                                               ROOT / '_maintenance/guide-ia/template.html',
                                               ROOT / '_maintenance/guide-ia/fiche-main.html']
        expressions = ('Les possibilités, elles, s’ouvrent', 'Moins de magie.',
                       'Plus de compréhension.', 'sans jamais se sentir perdu',
                       'Aucune question n\'est bête', 'Un cadre clair', 'Statut honnête de cette édition')
        for fichier in fichiers:
            texte = fichier.read_text()
            for expression in expressions:
                self.assertNotIn(expression, texte, str(fichier))

    def test_taille_et_liens_pdf_pygame(self):
        pdf = ROOT / 'assets/pdf/esquive-en-pixels-guide.pdf'
        taille = f'{pdf.stat().st_size / 1_000_000:.2f}'.replace('.', ',')
        page = (ROOT / 'esquive-en-pixels.html').read_text()
        self.assertEqual(re.findall(r'data-jeu-size>([\d,]+)', page), [taille, taille])
        empreinte = hashlib.sha256(pdf.read_bytes()).hexdigest()[:12]
        for fichier in ROOT.glob('*.html'):
            liens = re.findall(r'/assets/pdf/esquive-en-pixels-guide\.pdf[^"\s<]*', fichier.read_text())
            for lien in liens:
                self.assertEqual(lien, '/assets/pdf/esquive-en-pixels-guide.pdf?v=' + empreinte)


if __name__ == '__main__':
    unittest.main(verbosity=2)
