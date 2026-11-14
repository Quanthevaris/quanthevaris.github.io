"""Test d'intégration HTTP réel + navigateur, avec moteur Ollama SIMULÉ.
.venv/bin/python _maintenance/test-parcours-ia.py
Ne télécharge aucun modèle et ne prouve pas une vraie inférence.
"""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import subprocess
import sys
from threading import Thread

from werkzeug.serving import make_server

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'assets/code/assistant-ia'))
import serveur

APPELS = []


class FauxOllama(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def repondre(self, statut, data):
        self.send_response(statut)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        if self.path != '/api/tags':
            self.repondre(404, {'error': 'route inconnue'})
        else:
            self.repondre(200, {'models': [{'name': 'llama3.2:1b'}]})

    def do_POST(self):
        data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        APPELS.append(data)
        assert self.path == '/api/chat'
        assert data['model'] == 'llama3.2:1b' and data['stream'] is False
        message = data['messages'][-1]['content']
        if message == 'erreur simulée':
            self.repondre(404, {'error': 'model not found'})
        else:
            self.repondre(200, {'done': True, 'message': {'role': 'assistant',
                'content': 'Réponse SIMULÉE de test : <img src=x onerror=alert(1)> ' + message}})


def main():
    faux = ThreadingHTTPServer(('127.0.0.1', 0), FauxOllama)
    # Ce remplacement n'existe que dans le processus de test, jamais dans le ZIP livré.
    serveur.OLLAMA = 'http://127.0.0.1:' + str(faux.server_port)
    atelier = make_server('127.0.0.1', 5000, serveur.app, threaded=True)
    threads = [Thread(target=faux.serve_forever, daemon=True), Thread(target=atelier.serve_forever, daemon=True)]
    for thread in threads:
        thread.start()
    try:
        subprocess.run(['node', '_maintenance/test-interface-ia.mjs'], cwd=ROOT, check=True)
        assert APPELS
        assert all(a['messages'][0]['role'] == 'system' for a in APPELS)
        assert max(len(a['messages']) for a in APPELS) <= 14  # 12 antérieurs + système + demande
        print(f'Intégration OK : {len(APPELS)} appels HTTP au moteur SIMULÉ. Aucune vraie inférence.')
    finally:
        atelier.shutdown()
        faux.shutdown()
        atelier.server_close()
        faux.server_close()
        for thread in threads:
            thread.join(timeout=5)


if __name__ == '__main__':
    main()
