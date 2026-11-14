"""Pixel 2.0 — atelier local Flask + Ollama. © 2026 Quanthevaris, MIT.
Lancer : python serveur.py ; ouvrir http://127.0.0.1:5000
Pas de clé API, pas de téléchargement automatique, pas de serveur public.
"""
import json
import os
import socket
from pathlib import Path
from threading import Lock
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from flask import Flask, jsonify, request, send_file
from werkzeug.exceptions import HTTPException

DOSSIER = Path(__file__).resolve().parent
MODELES = ("llama3.2:1b", "llama3.2:3b")
MODELE = os.environ.get("PIXEL_MODEL", MODELES[0])
if MODELE not in MODELES:
    raise ValueError("PIXEL_MODEL doit être llama3.2:1b ou llama3.2:3b (modèle local).")
OLLAMA = "http://127.0.0.1:11434"
PERSONA = """Tu es Pixel, un assistant pédagogique, pas un être humain.
Réponds en français, brièvement, avec un exemple simple si utile.
Aide à comprendre Python et les jeux vidéo. Reconnais tes incertitudes.
Ne prétends pas avoir accès aux fichiers, au Web ou aux outils de l'ordinateur.
Ne donne pas de conseil médical, juridique ou financier personnalisé."""
# Le texte de connaissances est chargé au démarrage, jamais fourni comme chemin par le visiteur.
CONNAISSANCES = (DOSSIER / "connaissances.txt").read_text(encoding="utf-8")[:4000]
HISTORIQUE_MAX = 12  # six paires question/réponse, en mémoire dans l'onglet
MESSAGE_MAX = 2000
REPONSE_MAX = 6000
VERROU = Lock()
# Aucun proxy système pour les appels à la boucle locale ; aucune redirection HTTP suivie.
class SansRedirection(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


HTTP = build_opener(ProxyHandler({}), SansRedirection())
app = Flask(__name__, static_folder=None)
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024


def appeler_ollama(chemin, donnees=None, delai=180):
    """API native Ollama. Une seule destination, toujours 127.0.0.1."""
    corps = None if donnees is None else json.dumps(donnees).encode("utf-8")
    req = Request(OLLAMA + chemin, data=corps,
                  headers={"Content-Type": "application/json"})
    with HTTP.open(req, timeout=delai) as reponse:
        brut = reponse.read(1024 * 1024 + 1)
    if len(brut) > 1024 * 1024:
        raise ValueError("Réponse trop volumineuse")
    resultat = json.loads(brut)
    if not isinstance(resultat, dict) or "error" in resultat:
        raise ValueError("Réponse Ollama inattendue")
    return resultat


@app.before_request
def origine_locale():
    # Protection locale contre les origines tierces et le DNS rebinding.
    if request.host not in ("127.0.0.1:5000", "localhost:5000"):
        return jsonify(erreur="Adresse refusée. Ouvre http://127.0.0.1:5000."), 403
    origine = request.headers.get("Origin")
    if origine and origine != request.host_url.rstrip("/"):
        return jsonify(erreur="Origine refusée."), 403
    if request.headers.get("Sec-Fetch-Site") == "cross-site":
        return jsonify(erreur="Requête externe refusée."), 403


@app.after_request
def entetes(reponse):
    reponse.headers["Cache-Control"] = "no-store"
    reponse.headers["X-Content-Type-Options"] = "nosniff"
    reponse.headers["Referrer-Policy"] = "no-referrer"
    reponse.headers["Content-Security-Policy"] = (
        "default-src 'none'; script-src 'self'; style-src 'self'; "
        "connect-src 'self'; img-src 'self'; frame-ancestors 'none'; "
        "base-uri 'none'; form-action 'self'"
    )
    return reponse


@app.get("/")
def accueil():
    return send_file(DOSSIER / "assistant.html")


@app.get("/assistant.js")
def javascript():
    return send_file(DOSSIER / "assistant.js", mimetype="text/javascript")


@app.get("/assistant.css")
def styles():
    return send_file(DOSSIER / "assistant.css", mimetype="text/css")


@app.get("/api/status")
def etat():
    try:
        resultat = appeler_ollama("/api/tags", delai=5)
        presents = {m.get("name") for m in resultat.get("models", []) if isinstance(m, dict)}
        pret = MODELE in presents
        return jsonify(pret=pret, modele=MODELE, information=(
            "Modèle local installé." if pret else f"Exécute : ollama pull {MODELE}"))
    except (URLError, OSError, ValueError, TypeError):
        return jsonify(pret=False, modele=MODELE,
                       information="Ollama est injoignable. Démarre l’application Ollama."), 503


def valider(donnees):
    if not isinstance(donnees, dict):
        raise ValueError("Un objet JSON est attendu.")
    message = donnees.get("message")
    if not isinstance(message, str) or not message.strip() or len(message) > MESSAGE_MAX:
        raise ValueError("Écris un message de 1 à 2 000 caractères.")
    historique = donnees.get("historique", [])
    if not isinstance(historique, list) or len(historique) > HISTORIQUE_MAX or len(historique) % 2:
        raise ValueError("Historique invalide : six paires question/réponse au maximum.")
    nettoye = []
    for i, tour in enumerate(historique):
        if not isinstance(tour, dict):
            raise ValueError("Tour de conversation invalide.")
        role = "user" if i % 2 == 0 else "assistant"
        texte = tour.get("content")
        limite = MESSAGE_MAX if role == "user" else REPONSE_MAX
        if tour.get("role") != role or not isinstance(texte, str) or not texte.strip() or len(texte) > limite:
            raise ValueError("Rôle ou contenu de l’historique invalide.")
        nettoye.append({"role": role, "content": texte})
    # Le client ne peut pas injecter un rôle system. Cela n'élimine pas les prompt injections.
    return message.strip(), nettoye


@app.post("/api/chat")
def chat():
    if not request.is_json:
        return jsonify(erreur="Content-Type application/json requis."), 415
    try:
        message, historique = valider(request.get_json(silent=True))
    except ValueError as erreur:
        return jsonify(erreur=str(erreur)), 400
    if not VERROU.acquire(blocking=False):
        return jsonify(erreur="Pixel répond déjà. Réessaie dans un instant."), 429
    try:
        resultat = appeler_ollama("/api/chat", {
            "model": MODELE,
            "messages": [{"role": "system", "content": PERSONA + "\nRepères :\n" + CONNAISSANCES},
                         *historique, {"role": "user", "content": message}],
            "stream": False,
            "options": {"temperature": 0.5, "num_predict": 400, "num_ctx": 4096},
            "keep_alive": "5m",
        })
        texte = resultat.get("message", {}).get("content")
        if resultat.get("done") is not True or not isinstance(texte, str) or not texte.strip():
            raise ValueError("Réponse de modèle vide ou incomplète")
        return jsonify(reponse=texte.strip()[:REPONSE_MAX], modele=MODELE)
    except HTTPError as erreur:
        if erreur.code == 404:
            return jsonify(erreur=f"Modèle absent. Exécute : ollama pull {MODELE}"), 503
        return jsonify(erreur="Ollama a refusé la requête. Consulte ses journaux locaux."), 502
    except (TimeoutError, socket.timeout):
        return jsonify(erreur="Réponse trop lente (180 s). Réduis la conversation et réessaie."), 504
    except (URLError, OSError):
        return jsonify(erreur="Ollama est injoignable. Démarre l’application Ollama."), 503
    except (ValueError, TypeError, AttributeError):
        return jsonify(erreur="Ollama a renvoyé une réponse inattendue."), 502
    finally:
        VERROU.release()


@app.errorhandler(HTTPException)
def erreur_http(erreur):
    return jsonify(erreur="Requête trop volumineuse." if erreur.code == 413
                   else "Adresse ou méthode non disponible."), erreur.code


if __name__ == "__main__":
    print("Pixel local : http://127.0.0.1:5000 — Ctrl+C pour arrêter.")
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
