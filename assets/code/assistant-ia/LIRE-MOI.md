# Pixel — atelier local 2.0 (14 novembre 2026)

Deux projets : une adaptation pédagogique d’ELIZA (règles en anglais), puis Pixel
(Flask + Ollama + modèle local `llama3.2:1b`). Aucun service GitHub Models ni clé API.
Le guide complet est sur https://quanthevaris.github.io/guide-assistant-ia.html.

## 1. Préparer

- Python 3.11 ou plus récent : https://www.python.org/downloads/.
- Ollama officiel : https://ollama.com/download. Windows 10 22H2+ / macOS 14+ / Linux
  compatible selon sa documentation. Prévoir, à titre de recommandation de l’atelier,
  8 Go de RAM et 10 Go de disque libres ; ce n’est pas une garantie de vitesse.
- Modèle : environ 1,3 Go de téléchargement à la date de rédaction, plus la mémoire
  d’exécution. Un petit modèle est limité ; il peut mal répondre en français.
- Internet pour les installations et le téléchargement initial ; pas pour les
  conversations une fois le modèle local installé. Pas de carte bancaire ni de compte
  Ollama pour le modèle local de cet atelier. Respecter la licence Llama 3.2 et sa
  politique d’utilisation : https://ollama.com/library/llama3.2:1b.

Décompresse entièrement le ZIP dans un nouveau dossier personnel. N’installe pas
cet atelier dans le dépôt de ton site si tu veux simplement l’utiliser.

## 2. Installer le modèle

Démarre l’application Ollama, puis ouvre un terminal :

```text
ollama --version
ollama pull llama3.2:1b
ollama list
```

Si le service n’est pas lancé (notamment sous Linux), lance `ollama serve` dans un
terminal séparé. S’il répond « address already in use », il est probablement déjà
lancé : ne démarre pas une deuxième instance. Garde son écoute locale par défaut.
Ne règle pas `OLLAMA_HOST` sur `0.0.0.0` et n’ouvre pas le port dans le routeur.

Pour désactiver les fonctions cloud d’Ollama : ajoute la propriété
`"disable_ollama_cloud": true` à son fichier `~/.ollama/server.json` (sous Windows :
`%USERPROFILE%\.ollama\server.json`), en conservant ses autres propriétés JSON,
puis quitte et redémarre Ollama. Voir https://docs.ollama.com/faq. Ce réglage se fait
sur Ollama, pas dans ce dossier. L’atelier ne choisit que des modèles locaux.

## 3. Installer Python dans un environnement isolé

Depuis le dossier décompressé, **PowerShell Windows** :

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest -v
.\.venv\Scripts\python.exe verifier_installation.py --rapport validation-locale.json
.\.venv\Scripts\python.exe serveur.py
```

Depuis le dossier décompressé, **macOS / Linux** :

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest -v
.venv/bin/python verifier_installation.py --rapport validation-locale.json
.venv/bin/python serveur.py
```

Sur certaines distributions Linux, installe d’abord le paquet système `python3-venv`.
La première commande Windows utilise la version Python 3 par défaut : vérifie
`py -3 --version` (3.11 minimum). Pas besoin d’activer l’environnement ni de changer
la politique d’exécution de PowerShell. Ne copie pas les balises de code du guide.

## 4. Utiliser

Ouvre **http://127.0.0.1:5000** sur ce même ordinateur. Ne double-clique pas
`assistant.html`. Le serveur sert l’interface ET l’API : aucun CORS à configurer.
Pose deux questions, clique sur « Nouvelle discussion », puis essaie encore.
Arrêt de Flask : `Ctrl+C` dans son terminal. Fermer la page efface son contexte ;
Ollama peut garder le modèle en RAM quelques minutes. `ollama stop llama3.2:1b`
le décharge. `ollama rm llama3.2:1b` supprime son téléchargement si souhaité.

- Personnalité : modifier `PERSONA` dans `serveur.py`, puis relancer le serveur.
- Repères : modifier `connaissances.txt`, puis relancer. Ce n’est pas un vrai RAG.
- Modèle plus grand, facultatif : `ollama pull llama3.2:3b`, puis définir
  `PIXEL_MODEL=llama3.2:3b` pour le processus Python (instructions dans le guide).
  La RAM et l’espace disque nécessaires augmentent.
- ELIZA : lancer `python eliza.py` avec le Python de l’environnement, ou ouvrir
  `eliza-web.html`. La version web est volontairement plus petite que la version Python.

## 5. Comprendre les limites

Les tests `unittest` sont **sans modèle** : ils simulent les réponses et vérifient le
programme. Seul `verifier_installation.py` exécute une vraie inférence sur ton poste.
La qualité et la vitesse du modèle ne sont pas garanties sur un matériel donné.
Le code ne stocke pas les conversations, n’utilise aucun cookie et ne charge aucune
ressource distante. L’historique est gardé dans l’onglet (six échanges), puis renvoyé
au modèle local. Ollama, le navigateur et le système ont leurs propres journaux.
Ne saisis pas de données sensibles. Les consignes système ne sont pas une protection
infaillible contre les instructions malveillantes. Aucun accès aux fichiers, aucune
commande système et aucun outil exécuté par le modèle n’est implémenté.

**GitHub Pages ne fait pas tourner Flask ou Ollama.** Publie seulement une présentation
et éventuellement `eliza-web.html`, pas une interface faisant croire à un assistant
public fonctionnel. Ne rends pas ce serveur de développement accessible sur Internet.
Un vrai service public demande une autre architecture, une authentification, TLS,
un contrôle des coûts/ressources et une nouvelle analyse de confidentialité.

## Licence

Le code des projets est sous MIT (LICENCE-MIT.txt). Le texte et la maquette du guide
restent © 2026 Quanthevaris, tous droits réservés, usage personnel et éducatif autorisé.
Flask, Python, Ollama et les poids de Llama conservent leurs propres licences ; aucun
poids de modèle, installateur ou bibliothèque n’est redistribué dans ce kit.
