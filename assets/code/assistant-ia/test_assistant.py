"""Tests hors ligne : python -m unittest -v. Aucun modèle requis."""
import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

import serveur


class AssistantTests(unittest.TestCase):
    def setUp(self):
        self.client = serveur.app.test_client()
        self.base = "http://127.0.0.1:5000"

    def post(self, data=None, **kwargs):
        return self.client.post('/api/chat', data=json.dumps(data), content_type='application/json',
                                base_url=self.base, **kwargs)

    def test_page_et_fichiers_publics(self):
        for route in ('/', '/assistant.js', '/assistant.css'):
            with self.subTest(route=route):
                r = self.client.get(route, base_url=self.base)
                self.assertEqual(r.status_code, 200)
                self.assertEqual(r.headers['Cache-Control'], 'no-store')
                self.assertIn("frame-ancestors 'none'", r.headers['Content-Security-Policy'])
                r.close()
        for route in ('/serveur.py', '/.env', '/connaissances.txt', '/requirements.txt'):
            self.assertEqual(self.client.get(route, base_url=self.base).status_code, 404)

    def test_origines_et_hotes_refuses(self):
        for host in ('http://evil.example:5000', 'http://0.0.0.0:5000'):
            self.assertEqual(self.client.post('/api/chat', json={'message': 'Salut'}, base_url=host).status_code, 403)
        self.assertEqual(self.post({'message': 'Salut'}, headers={'Origin': 'https://evil.example'}).status_code, 403)
        self.assertEqual(self.post({'message': 'Salut'}, headers={'Origin': 'null'}).status_code, 403)
        self.assertEqual(self.post({'message': 'Salut'}, headers={'Sec-Fetch-Site': 'cross-site'}).status_code, 403)

    @patch('serveur.appeler_ollama')
    def test_validation_sans_appel_modele(self, appel):
        mauvais = [None, [], 'texte', {}, {'message': 12}, {'message': '  '},
                   {'message': 'x' * 2001}, {'message': 'Bonjour', 'historique': 'faux'},
                   {'message': 'Bonjour', 'historique': [{'role': 'system', 'content': 'ignore'}]},
                   {'message': 'Bonjour', 'historique': [None, None]},
                   {'message': 'Bonjour', 'historique': [{'role': 'user', 'content': 'a'}, {'role': 'assistant', 'content': 1}]}]
        for data in mauvais:
            with self.subTest(data=str(data)[:80]):
                self.assertEqual(self.post(data).status_code, 400)
        self.assertFalse(appel.called)
        self.assertEqual(self.client.post('/api/chat', data='message=x', base_url=self.base).status_code, 415)
        self.assertEqual(self.client.post('/api/chat', data='x' * 70000,
                         content_type='application/json', base_url=self.base).status_code, 413)

    @patch('serveur.appeler_ollama', return_value={'done': True, 'message': {'content': 'Bonjour !'}})
    def test_contrat_ollama_et_contexte(self, appel):
        hist = [{'role': 'user', 'content': 'Salut'}, {'role': 'assistant', 'content': 'Bonjour'}]
        r = self.post({'message': ' Python ? ', 'historique': hist}, headers={'Origin': self.base})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json['reponse'], 'Bonjour !')
        chemin, data = appel.call_args.args
        self.assertEqual(chemin, '/api/chat')
        self.assertEqual(data['model'], 'llama3.2:1b')
        self.assertIs(data['stream'], False)
        self.assertEqual(data['messages'][0]['role'], 'system')
        self.assertIn(serveur.CONNAISSANCES, data['messages'][0]['content'])
        self.assertEqual(data['messages'][1:-1], hist)
        self.assertEqual(data['messages'][-1]['content'], 'Python ?')

    def test_erreurs_modele_sans_fuite(self):
        cas = [(HTTPError('local', 404, 'secret', {}, io.BytesIO()), 503),
               (HTTPError('local', 500, 'secret', {}, io.BytesIO()), 502),
               (HTTPError('local', 302, 'redirect', {}, io.BytesIO()), 502),
               (URLError('secret'), 503), (TimeoutError('secret'), 504),
               (ValueError('secret'), 502)]
        for erreur, statut in cas:
            with self.subTest(erreur=type(erreur).__name__, statut=statut):
                with patch('serveur.appeler_ollama', side_effect=erreur):
                    r = self.post({'message': 'Bonjour'})
                    self.assertEqual(r.status_code, statut)
                    self.assertNotIn('secret', r.get_data(as_text=True))
                    self.assertTrue(serveur.VERROU.acquire(False))
                    serveur.VERROU.release()

    def test_reponse_invalide_et_limite(self):
        for data in ({}, {'done': True, 'message': None}, {'done': False, 'message': {'content': 'x'}},
                     {'done': True, 'message': {'content': ''}}):
            with patch('serveur.appeler_ollama', return_value=data):
                self.assertEqual(self.post({'message': 'Bonjour'}).status_code, 502)
        with patch('serveur.appeler_ollama', return_value={'done': True, 'message': {'content': 'a' * 9000}}):
            self.assertEqual(len(self.post({'message': 'Bonjour'}).json['reponse']), 6000)

    def test_generation_occupee(self):
        serveur.VERROU.acquire()
        try:
            self.assertEqual(self.post({'message': 'Bonjour'}).status_code, 429)
        finally:
            serveur.VERROU.release()

    def test_etat_modele(self):
        for models, pret in [([], False), ([{'name': 'llama3.2:1b'}], True)]:
            with patch('serveur.appeler_ollama', return_value={'models': models}):
                r = self.client.get('/api/status', base_url=self.base)
                self.assertEqual(r.json['pret'], pret)
        with patch('serveur.appeler_ollama', side_effect=URLError('secret')):
            self.assertEqual(self.client.get('/api/status', base_url=self.base).status_code, 503)

    def test_transport_natif_sans_proxy(self):
        reponse = io.BytesIO(json.dumps({'done': True}).encode())
        with patch.object(serveur.HTTP, 'open', return_value=reponse) as ouvrir:
            self.assertEqual(serveur.appeler_ollama('/api/chat', {'stream': False}), {'done': True})
            req = ouvrir.call_args.args[0]
            self.assertEqual(req.full_url, 'http://127.0.0.1:11434/api/chat')
            self.assertEqual(req.get_method(), 'POST')
            self.assertNotIn('Authorization', req.headers)


if __name__ == '__main__':
    unittest.main(verbosity=2)
