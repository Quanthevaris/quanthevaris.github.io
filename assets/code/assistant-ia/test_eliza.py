"""Tests déterministes de l'adaptation pédagogique d'ELIZA (sans pytest)."""
import unittest
from unittest.mock import patch
import eliza


class ElizaTests(unittest.TestCase):
    def setUp(self):
        eliza.MEMOIRE.clear()

    def tearDown(self):
        eliza.MEMOIRE.clear()

    def test_reflexion(self):
        self.assertEqual(eliza.reflechir('my friend'), 'your friend')
        self.assertEqual(eliza.reflechir('i am sad'), 'you are sad')
        self.assertEqual(eliza.reflechir(''), '')

    @patch('eliza.random.choice', side_effect=lambda choix: choix[0])
    def test_regles(self, choix):
        self.assertEqual(eliza.repondre('My boyfriend made me come here'), 'Your boyfriend made you come here?')
        self.assertEqual(eliza.repondre("I'm sad"), 'I am sorry to hear you are sad.')
        self.assertEqual(eliza.repondre('I need help with my computer'), 'Why do you need help with your computer?')
        self.assertEqual(eliza.repondre('You never listen'), 'Why do you say I never listen?')

    @patch('eliza.random.random', return_value=0.9)
    def test_memoire_remplie_et_bornee(self, hasard):
        for i in range(25):
            eliza.repondre(f'I remember my childhood {i}')
        self.assertEqual(len(eliza.MEMOIRE), 20)
        self.assertEqual(eliza.MEMOIRE[-1], 'your childhood 24')

    def test_memoire_restituee(self):
        eliza.MEMOIRE.append('your first game')
        with patch('eliza.random.random', return_value=0.0):
            self.assertIn('your first game', eliza.repondre('Hello'))
        self.assertEqual(eliza.MEMOIRE, [])

    @patch('eliza.random.choice', side_effect=lambda choix: choix[0])
    def test_defaut(self, choix):
        self.assertEqual(eliza.repondre('bliblou'), eliza.REPONSES_DEFAUT[0])


if __name__ == '__main__':
    unittest.main(verbosity=2)
