<!-- section:avant-propos -->
# Avant de commencer

**Crée ton assistant IA personnalisé · Édition locale 2.0 · 14 novembre 2026**

Ce guide remplace l’ancienne édition « avec GitHub ». Il conserve ses deux projets : découvrir un chatbot à règles inspiré d’ELIZA, puis construire Pixel, un assistant à modèle de langage. Le second projet fonctionne désormais **sur ton ordinateur avec Ollama**, sans API d’inférence GitHub et sans clé à créer.

GitHub Models a été retiré le 30 juillet 2026. Ses anciens liens, jetons, quotas et exemples d’API ne font plus partie du parcours. GitHub reste utile pour versionner le code, exécuter des tests et publier **une démonstration statique d’ELIZA**, pas pour héberger le modèle local.

## Ce que tu vas obtenir

- Un fichier `eliza.py`, sans dépendance, qui reformule des phrases **en anglais** à l’aide de règles.
- Une petite variante `eliza-web.html`, utilisable dans un navigateur, sans serveur.
- Pixel : une interface web, un serveur Python Flask et un modèle local `llama3.2:1b` exécuté par Ollama.
- Un kit complet : sources, styles, tests hors ligne, vérificateur d’inférence réelle et licence du code.
- Des explications sur le rôle du programme, du modèle et du serveur.

**Tests et installation.** Les tests fournis utilisent des réponses simulées pour vérifier le code. Pour essayer le modèle sur ton ordinateur, lance `verifier_installation.py`, puis teste l’interface (chapitre 6). La vitesse et la qualité des réponses dépendent de ta configuration. Le modèle se télécharge séparément ; les captures du guide ne montrent pas de réponse réellement générée.

## Ce qu’il te faut

| Élément | Ce qu’il faut |
| --- | --- |
| Bases | Savoir créer un fichier et ouvrir un terminal ; les notions sont expliquées progressivement. |
| Python | Version 3.11 ou plus récente. Vérifie la version réellement utilisée. |
| Système | Windows 10 22H2 ou plus récent, macOS 14 ou plus récent, ou Linux compatible avec Ollama ; consulter ses exigences actuelles. |
| Matériel | Prévois environ 8 Go de RAM et 10 Go de disque libres pour cet exercice. Ces valeurs sont indicatives ; les besoins et la vitesse dépendent de ta configuration. |
| Modèle | `llama3.2:1b`, environ 1,3 Go de téléchargement au 14 novembre 2026. La mémoire utilisée en exécution s’ajoute au fichier téléchargé. |
| Réseau | Internet pour les logiciels, les paquets et le téléchargement initial du modèle. L’inférence choisie ensuite est locale. |
| Comptes | Aucun compte GitHub ou Ollama nécessaire pour les deux projets locaux. Un compte GitHub est facultatif pour le chapitre de publication. |
| Coût | Pas de facturation d’API pour l’inférence locale ; ordinateur, électricité, stockage et accès Internet restent à ta charge. |

Commence par ELIZA même si ton ordinateur ne peut pas faire tourner Ollama : tu peux terminer le premier projet sans modèle. Télécharge les logiciels sur leurs sites officiels, évite les installateurs tiers. Pour un mineur, associe un adulte à l’installation et à la lecture des conditions du modèle.

## Kit et méthode de lecture

Télécharge le [kit de l’édition locale](https://quanthevaris.github.io/assets/code/assistant-ia-kit.zip), puis **décompresse-le entièrement dans un nouveau dossier**. Il ne suffit pas d’ouvrir un fichier à l’intérieur du ZIP. Le dossier obtenu contient `serveur.py`, `assistant.html`, `assistant.js`, `assistant.css`, `connaissances.txt` et les autres fichiers des annexes.

Les chapitres 1 et 2 se lisent sans ordinateur. Les chapitres 3 à 6 se suivent dans l’ordre. Les chapitres 7 à 10 permettent de comprendre, personnaliser et partager sans publier accidentellement un serveur local. Les annexes présentent les fichiers effectivement livrés ; le ZIP évite les erreurs de copier-coller depuis un PDF.

**Convention terminal :** copie seulement les commandes, pas les balises `powershell`, `sh` ou les explications. Chaque chemin est relatif au dossier décompressé, sauf indication contraire. Aucune commande ne demande ton mot de passe GitHub ou une clé API.

<!-- section:ch1 -->
# 1. ELIZA : comprendre l’illusion

## 1.1 Un programme qui reformule

Au MIT, Joseph Weizenbaum développe ELIZA au milieu des années 1960. Son article de janvier 1966, publié dans *Communications of the ACM*, décrit un programme de dialogue en langage naturel. Son script le plus connu, DOCTOR, simule certaines reformulations d’un psychothérapeute rogérien.

ELIZA repère des mots-clés, découpe la phrase, remplace certains pronoms et compose une réponse à partir d’un modèle de phrase.

> Utilisateur : My boyfriend made me come here.  
> ELIZA : Your boyfriend made you come here?

Le programme remplace « my » par « your » et « me » par « you ». Il ne connaît pas la situation de la personne : cet exemple illustre une règle de transformation, pas un accompagnement psychologique.

## 1.2 L’effet ELIZA

L’**effet ELIZA** désigne notre tendance à attribuer de la compréhension ou de l’empathie à un système qui produit des échanges convaincants. Weizenbaum s’inquiétait déjà de la confiance que les utilisateurs accordaient à son programme. Son livre *Computer Power and Human Reason* (1976) développera cette critique.

Cette mise en garde est toujours utile. Un ton chaleureux ne garantit ni une intention, ni une compréhension comparable à la nôtre, ni l’exactitude d’une réponse. Un assistant n’est pas une personne et ne remplace pas un professionnel de santé.

## 1.3 De règles explicites aux modèles appris

| Repère | Idée à retenir |
| --- | --- |
| ELIZA, 1966 | Des règles écrites à la main produisent l’apparence d’une conversation. |
| Systèmes à règles ultérieurs | On multiplie les motifs et les réponses, sans résoudre toute la diversité du langage. |
| Transformer, 2017 | Une architecture d’apprentissage devient centrale dans de nombreux modèles de langage modernes. |
| Assistants génératifs actuels | Un modèle appris génère des suites de tokens plausibles à partir d’un contexte. |

Le deuxième projet utilise un modèle de langage plutôt que des règles écrites à la main. Son comportement est plus difficile à prévoir que celui d’ELIZA.

## 1.4 Notre version d’ELIZA

Le programme de ce guide est **une adaptation pédagogique simplifiée**, pas une reproduction intégrale du code MAD-SLIP de 1966. Il reprend les idées de règles, de réflexion et de petite mémoire. Les dialogues de l’adaptation sont en anglais parce que ses motifs le sont ; Pixel, lui, recevra une consigne de réponse en français.

**Exercice.** Écris deux phrases auxquelles un programme à règles pourrait répondre sans en comprendre le sens. Puis imagine une question factuelle qui mettrait ses limites en évidence. L’objectif n’est pas de tromper les utilisateurs, mais de rendre le mécanisme visible.

<!-- section:ch2 -->
# 2. Règles, modèle et contexte

## 2.1 Mots-clés et expressions régulières

Une expression régulière décrit une famille de textes. Dans `r".*\bi need\b(.*)"`, le groupe `(.*)` capture ce qui suit « i need ». Le préfixe `r` empêche Python d’interpréter les antislashs comme des échappements ordinaires. `\b` désigne une frontière de mot.

Pour « I need help with my computer », le programme capture « help with my computer », transforme les pronoms puis insère le résultat dans un gabarit comme « Why do you need {0}? ». Le programme ne sait pas réparer l’ordinateur : il manipule du texte.

L’ordre des règles compte. On essaie les règles précises avant une règle très large, sinon celle-ci capture tout. Une réponse par défaut permet de répondre même lorsqu’aucun motif ne correspond.

## 2.2 Un modèle de langage ne fonctionne pas par simple liste de réponses

Un LLM (*Large Language Model*) contient des paramètres appris sur de grandes quantités de données. À partir d’un contexte, il produit une suite de **tokens** : des fragments de texte, pas nécessairement des mots entiers. Sa réponse peut être pertinente, mais aussi plausible et fausse.

- Le **modèle** est l’ensemble des poids chargés pour produire des réponses.
- **Ollama** est le logiciel qui télécharge et exécute le modèle choisi, et offre une API locale.
- **Flask** reçoit les requêtes de notre interface et prépare le contexte.
- Le **navigateur** affiche la discussion et garde quelques tours en mémoire.
- **GitHub** n’est nécessaire à aucune de ces quatre opérations locales.

## 2.3 Contexte, personnalité et mémoire

Un message de rôle `system` fournit un cadre : langue, ton, objectif et limites. Un message `user` représente une demande ; un message `assistant` représente une réponse antérieure. Le serveur recompose ces messages à chaque appel.

Dans l’atelier, la conversation n’est pas apprise par le modèle. Elle est simplement renvoyée avec la question suivante. Fermer ou recharger l’onglet fait perdre son contexte. Il n’y a pas de mémoire persistante, de compte ou de base de conversations.

L’interface conserve au plus six paires question/réponse. Elle peut en envoyer moins pour rester sous la limite de taille. La fenêtre de contexte du modèle reste limitée à 4 096 tokens dans notre requête ; de longs échanges peuvent donc perdre des détails, même si six tours sont affichés.

## 2.4 Les limites du modèle choisi

`llama3.2:1b` est choisi pour la légèreté, pas parce qu’il serait le meilleur modèle en toutes circonstances. Sa fiche annonce le français parmi les langues prises en charge. Il peut néanmoins produire des erreurs de langue, mal suivre une consigne et inventer des faits. Les performances dépendent du processeur, de la RAM, du GPU et des autres logiciels ouverts.

La **température** règle une partie de l’aléatoire ; elle ne mesure pas l’intelligence et ne garantit pas le déterminisme. `num_predict` limite le nombre de tokens de réponse, pas le nombre exact de mots ou de caractères. Aucune consigne système n’offre une garantie de sécurité absolue.

**À retenir.** Comprendre où s’exécute chaque composant permet de mieux interpréter une erreur, une promesse de confidentialité ou une limite matérielle.

<!-- section:ch3 -->
# 3. Préparer le projet

## 3.1 Vérifier Python

Installe Python depuis [python.org/downloads](https://www.python.org/downloads/). Sous Windows, le lanceur `py` est utilisé ci-dessous ; s’il n’est pas disponible, répare l’installation officielle ou adapte les commandes à un Python 3.11+ vérifié. Sous macOS/Linux, utilise `python3`.

**PowerShell Windows :**

```powershell
py -3 --version
```

**macOS/Linux :**

```sh
python3 --version
```

Le résultat doit indiquer au moins Python 3.11. Ne suppose pas que le `python` d’une vieille installation et celui du nouvel environnement désignent le même interpréteur.

## 3.2 Créer l’environnement, sans modifier PowerShell

Ouvre un terminal **dans le dossier du kit décompressé**. Dans l’Explorateur Windows, tu peux ouvrir le dossier puis choisir l’ouverture d’un terminal ; vérifie que `serveur.py` est visible avec `dir`. Sous macOS/Linux, vérifie avec `ls`.

**PowerShell Windows :**

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**macOS/Linux :**

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Pas besoin d’activer l’environnement virtuel : on appelle directement son Python. Il n’est donc pas nécessaire de désactiver une protection de PowerShell. Si Linux signale que `venv` est absent, installe le paquet `python3-venv` via le gestionnaire de paquets de ta distribution, puis recommence.

Le kit a une seule dépendance directe : `Flask==3.1.3`. Ses dépendances transitives sont installées par pip. Cette version est celle utilisée pour la vérification de l’atelier ; lors d’une mise à jour future, examine les correctifs de sécurité et relance les tests. **Ollama ne s’installe pas avec pip dans ce projet.**

## 3.3 L’éditeur et les fichiers

Tu peux utiliser Visual Studio Code ou un autre éditeur de texte. Enregistre en UTF-8. Sous Windows, affiche les extensions connues pour ne pas créer `serveur.py.txt`. Ne renomme pas les fichiers du kit au hasard : le serveur sert trois noms précis à l’interface.

```text
assistant-ia/
  eliza.py                  chatbot à règles en anglais
  eliza-web.html            petite variante statique
  serveur.py                serveur Flask local
  assistant.html            structure de l’interface
  assistant.css             présentation, sans ressources distantes
  assistant.js              requêtes et historique dans l’onglet
  connaissances.txt         repères ajoutés au prompt
  requirements.txt          dépendance Flask
  test_eliza.py              tests déterministes d’ELIZA
  test_assistant.py          tests de Pixel, sans vrai modèle
  verifier_installation.py  test d’inférence locale réelle
  LICENCE-MIT.txt            licence du code
  LIRE-MOI.md                démarrage rapide
  .gitignore                exclusions Git
  .github/workflows/tests.yml tests optionnels sur GitHub
```

## 3.4 Tester l’installation Python

**PowerShell Windows :**

```powershell
.\.venv\Scripts\python.exe -m unittest -v
```

**macOS/Linux :**

```sh
.venv/bin/python -m unittest -v
```

Ces tests ne téléchargent rien et ne démarrent pas de modèle. Ils vérifient les règles, le contrat de requête et les erreurs avec des réponses simulées. Un résultat `OK` ici **ne valide pas encore une conversation réelle**. La vérification du modèle est au chapitre 6.

<!-- section:ch4 -->
# 4. Installer Ollama et choisir le mode local

## 4.1 Installer le logiciel officiel

Télécharge Ollama sur [ollama.com/download](https://ollama.com/download). Consulte les notices [Windows](https://docs.ollama.com/windows), [macOS](https://docs.ollama.com/macos) ou [Linux](https://docs.ollama.com/linux) avant l’installation : systèmes et accélérations GPU supportés peuvent évoluer.

Sous Windows, installe et ouvre l’application Ollama, puis rouvre le terminal pour prendre en compte son chemin. Sous macOS, installe l’application dans Applications et ouvre-la. Sous Linux, suis la procédure officielle de ta distribution et vérifie le service. Ne colle pas un script d’installation obtenu sur un site inconnu.

```text
ollama --version
```

Si la commande est inconnue, ne poursuis pas : vérifie l’installation et le PATH, puis rouvre le terminal. Si la version s’affiche, continue.

## 4.2 Télécharger le modèle

```text
ollama pull llama3.2:1b
ollama list
```

Attends la fin du téléchargement. `ollama list` doit contenir **exactement** `llama3.2:1b`. La fiche consultée indique environ 1,3 Go ; garde une marge pour Ollama, Python, les fichiers temporaires et la mémoire d’exécution. Le tag peut évoluer : le vérificateur enregistre le digest du modèle pour identifier ce qui a été essayé.

La licence des poids est la **Llama 3.2 Community License**, avec une politique d’utilisation acceptable, et non la licence MIT du code de l’atelier. Consulte [la fiche du modèle et ses licences](https://ollama.com/library/llama3.2:1b). Le kit ne redistribue aucun poids et n’accorde aucun droit supplémentaire sur eux.

## 4.3 Démarrer le service si nécessaire

L’application Windows/macOS démarre généralement le service. Si l’API est injoignable, ouvre Ollama. Sous Linux, vérifie son service ; si tu lances le binaire manuellement, garde un terminal séparé ouvert avec :

```text
ollama serve
```

Si tu obtiens « address already in use » sur le port 11434, une instance tourne peut-être déjà. Ne lance pas une boucle de redémarrage et ne change pas le port de l’atelier : vérifie d’abord l’instance existante.

**Sécurité :** conserve l’écoute locale par défaut. Ne configure pas `OLLAMA_HOST=0.0.0.0`, ne crée pas de tunnel public et n’ouvre pas le port 11434 dans ton routeur pour suivre ce guide. L’API locale n’est pas une API publique authentifiée.

## 4.4 Désactiver les fonctionnalités cloud

Ollama propose aussi des fonctionnalités distantes. Le présent parcours utilise seulement les modèles locaux autorisés dans `MODELES` du serveur. Pour renforcer ce choix, la [FAQ officielle](https://docs.ollama.com/faq) décrit le mode local uniquement.

Dans `~/.ollama/server.json` — sous Windows, `%USERPROFILE%\.ollama\server.json` — ajoute la propriété suivante en **conservant les autres propriétés** du fichier JSON, puis quitte et redémarre complètement Ollama :

```json
{
  "disable_ollama_cloud": true
}
```

Si le fichier n’existe pas, crée-le à cet emplacement avec ce contenu. Ne crée pas `server.json` dans le dossier du kit : ce n’est pas le même logiciel qui le lit. Si le fichier existe déjà, un objet JSON ne doit contenir qu’une occurrence de chaque propriété ; ajoute une virgule correctement si nécessaire. La variable d’environnement `OLLAMA_NO_CLOUD=1`, appliquée **au processus Ollama puis suivie d’un redémarrage**, est une autre méthode documentée.

Ce réglage ne signifie pas que l’installation ne contactera jamais Internet : téléchargements de modèles et mises à jour restent des opérations réseau. Dans notre parcours, les conversations sont envoyées à l’API locale du modèle téléchargé, pas à un compte cloud.

<!-- section:ch5 -->
# 5. Projet n° 1 — programmer une petite ELIZA

## 5.1 Lancer avant de modifier

Avec le Python de l’environnement, exécute `eliza.py` :

```powershell
.\.venv\Scripts\python.exe eliza.py
```

```sh
.venv/bin/python eliza.py
```

Essaie **en anglais** : `I need help with my computer`, `I'm sad`, `My boyfriend made me come here`. Tape `au revoir` pour quitter. Les réponses peuvent varier : plusieurs gabarits sont choisis au hasard. Ce programme n’est pas un modèle génératif et ne fait aucun appel réseau.

## 5.2 Retourner les pronoms

La fonction `reflechir` coupe un texte en mots, puis remplace ceux présents dans le dictionnaire `REFLEXION`. Une clé absente conserve sa valeur d’origine grâce au deuxième argument de `get`.

```python
# Petit exemple explicatif, pas un remplacement du fichier complet.
reflets = {"my": "your", "me": "you"}
mots = "help me with my computer".split()
print(" ".join(reflets.get(mot, mot) for mot in mots))
# help you with your computer
```

C’est une technique volontairement limitée. Elle ne résout ni toute la grammaire anglaise, ni les ambiguïtés de « you », ni les accords d’une autre langue. Pour ajouter le français, il faut des règles et une réflexion adaptées, pas seulement traduire les réponses.

## 5.3 La liste des règles

Dans `REGLES`, chaque élément contient un motif et une liste de réponses. `re.match` cherche une correspondance ; les groupes capturés sont réfléchis, puis insérés dans les gabarits par `format`.

```python
# Exemple de règle, déjà présente dans le code complet.
(r".*\bi need\b(.*)", [
    "Why do you need {0}?",
    "Would it really help you to get {0}?",
])
```

Les accolades `{0}` désignent le premier groupe capturé. Si tu veux une accolade littérale dans un gabarit formaté, écris `{{` ou `}}`. Teste une nouvelle règle avant de l’ajouter : un motif trop large masque ceux qui suivent.

## 5.4 Mémoriser une phrase

Quand une phrase correspond à « I remember… », le programme stocke le fragment réfléchi dans `MEMOIRE`. Il peut le ressortir plus tard avec une probabilité de 25 %. Cette liste est limitée à 20 éléments ; elle disparaît à l’arrêt du programme. Elle ne contient aucun apprentissage persistant.

Exemple **possible**, non garanti à chaque exécution :

> Toi : I remember my first video game.  
> ELIZA : Do you often think of your first video game?  
> Toi : Hello.  
> ELIZA : Earlier you said you remembered your first video game. Does that have anything to do with now?

Cet exemple montre comment une variable peut modifier une réponse ultérieure. N’utilise pas cet exemple comme outil thérapeutique.

## 5.5 Des tests qui ne dépendent pas du hasard

Les tests du kit utilisent `unittest.mock.patch` pour choisir une réponse déterminée et contrôler le tirage de mémoire. Ils vident `MEMOIRE` avant et après chaque test. On ne peut pas exiger une réponse aléatoire précise sans maîtriser le hasard : ce serait un test intermittent.

```python
from unittest.mock import patch
import eliza

eliza.MEMOIRE.clear()
with patch("eliza.random.choice", side_effect=lambda choix: choix[0]):
    assert eliza.repondre("I need help") == "Why do you need help?"
```

Le fichier complet `test_eliza.py` figure dans l’annexe A et dans le kit. Lance l’ensemble des tests après chaque modification. Si un test échoue, cherche quel comportement a changé avant de modifier le test.

## 5.6 Variante dans le navigateur

Ouvre `eliza-web.html` par double-clic. Cette variante statique reprend le principe avec moins de règles et des choix de réponses plus courts ; elle n’est **pas strictement identique** à la version Python. Aucun serveur ni modèle n’est nécessaire. C’est cette page que tu pourras publier sur GitHub Pages, avec une explication de ses limites.

**Exercice.** Ajoute une règle sur « I like… » dans une copie du projet. Écris un test qui impose le premier gabarit, puis vérifie le comportement avant de changer les autres règles.

<!-- section:ch6 -->
# 6. Projet n° 2 — Pixel avec un modèle local

## 6.1 L’architecture complète

```text
Navigateur sur TON ordinateur
  http://127.0.0.1:5000
       | GET /, /assistant.js, /assistant.css
       | POST /api/chat (URL relative)
       v
Flask — serveur.py — 127.0.0.1:5000
       | POST http://127.0.0.1:11434/api/chat
       v
Ollama — modèle local llama3.2:1b
       | réponse JSON, stream: false
       v
Flask renvoie {"reponse": "…", "modele": "llama3.2:1b"}
```

Le navigateur ne contacte pas directement Ollama. La page et l’API de Pixel partagent la même origine. **Pas de Flask-CORS, pas d’adresse d’API distante à coller dans le JavaScript.** Un navigateur sur un autre appareil ne viserait pas ton ordinateur en utilisant `127.0.0.1` : la boucle locale désigne toujours l’appareil qui fait la requête.

Le modèle est limité à deux tags locaux autorisés. Le nom par défaut, `llama3.2:1b`, ne requiert pas de clé API. Ne crée pas de jeton GitHub pour ce projet.

## 6.2 Tester le modèle avant d’ouvrir l’interface

Dans le dossier du kit, Ollama étant démarré et le modèle téléchargé :

**PowerShell Windows :**

```powershell
.\.venv\Scripts\python.exe verifier_installation.py --rapport validation-locale.json
```

**macOS/Linux :**

```sh
.venv/bin/python verifier_installation.py --rapport validation-locale.json
```

Ce script contacte réellement l’API Ollama locale. Il vérifie la présence du modèle puis demande une courte salutation en français. Il n’utilise pas les réponses simulées des tests. En cas de réussite, il affiche `INFERENCE LOCALE REELLE OK` et crée, si demandé, un rapport avec version Python, version Ollama, système, digest du modèle et réponse à la question de test.

Si le script échoue, consulte le dépannage avant de continuer. Lis aussi la réponse obtenue : une réponse non vide peut être fausse. Un petit modèle peut être imprécis. Le fichier `validation-locale.json` est ignoré par Git ; il ne contient que le test fixe, pas tes conversations personnelles. Tu peux le garder pour identifier la configuration essayée.

## 6.3 Lancer le serveur de l’atelier

**PowerShell Windows :**

```powershell
.\.venv\Scripts\python.exe serveur.py
```

**macOS/Linux :**

```sh
.venv/bin/python serveur.py
```

Laisse ce terminal ouvert et visite **http://127.0.0.1:5000** dans le navigateur du même ordinateur. Ne double-clique pas `assistant.html` ; ce fichier attend le serveur. Si le navigateur indique une adresse refusée, utilise bien cette URL exacte ou `http://localhost:5000` et ne change pas seulement le port.

Le diagnostic en haut de la conversation consulte `/api/status`, qui vérifie l’existence du modèle via l’API `/api/tags` d’Ollama. « Prêt » indique que le modèle est installé. Pour vérifier qu’il répond correctement, essaie quelques questions.

## 6.4 Ce qu’envoie le serveur

Extrait explicatif ; le fichier complet est en annexe C :

```python
resultat = appeler_ollama("/api/chat", {
    "model": MODELE,
    "messages": [
        {"role": "system", "content": PERSONA + "\nRepères :\n" + CONNAISSANCES},
        *historique,
        {"role": "user", "content": message},
    ],
    "stream": False,
    "options": {"temperature": 0.5, "num_predict": 400, "num_ctx": 4096},
    "keep_alive": "5m",
})
```

L’API native d’Ollama renvoie le texte dans `message.content`, pas dans le format d’un ancien client OpenAI. `stream: false` demande une seule réponse JSON plutôt qu’un flux de fragments. La longueur de la réponse et de l’historique est limitée. Un échange trop long peut dépasser le contexte du modèle.

Le programme n’effectue pas de téléchargement automatique, ne lit aucun chemin fourni par le navigateur, ne suit pas les redirections de l’API locale et n’utilise pas de proxy système pour lui parler. Les modèles et le fichier de connaissances sont choisis côté serveur.

## 6.5 Essai dans l’interface

1. Demande : « Explique une boucle Python à un débutant en trois phrases. »
2. Demande : « Donne un exemple avec les nombres de 1 à 3. » Vérifie si le contexte est repris.
3. Clique **Nouvelle discussion**, puis demande à quoi correspond « cet exemple ». Le contexte précédent ne devrait plus être fourni.
4. Pose une question dont tu connais la réponse. Vérifie les faits et le code proposé.
5. Arrête Ollama, envoie une question et vérifie le message d’erreur ; redémarre-le ensuite.

Le premier calcul peut être lent, car les poids sont chargés en mémoire. Le serveur attend jusqu’à 180 secondes et l’interface jusqu’à 200 secondes. Un abandon du navigateur n’arrête pas nécessairement le calcul déjà lancé dans Ollama. Attends, puis utilise au besoin `ollama stop llama3.2:1b` avant de réessayer.

## 6.6 Arrêter et redémarrer

- `Ctrl+C` dans le terminal de Flask arrête l’atelier, pas forcément Ollama.
- Fermer l’onglet efface l’historique de l’interface ; ne le confonds pas avec la mémoire de ton navigateur ou les journaux d’autres logiciels.
- `ollama ps` montre les modèles chargés ; `ollama stop llama3.2:1b` décharge celui-ci.
- `ollama rm llama3.2:1b` supprime son téléchargement si tu veux libérer de l’espace. Tu devras le retélécharger pour le réutiliser.

Le serveur intégré à Flask est ici un outil d’atelier local. Il n’a ni authentification utilisateur ni infrastructure de production. **Ne le rends pas accessible sur Internet.**

<!-- section:ch7 -->
# 7. Personnaliser Pixel

## 7.1 Choisir un rôle et un ton

La constante `PERSONA` dans `serveur.py` définit Pixel : assistant pédagogique, réponse française et brève, limites clairement formulées. Modifie ce texte dans une copie, enregistre, puis **arrête et relance Flask**. Le mode debug et le rechargement automatique sont désactivés volontairement.

Une bonne consigne précise : le rôle, le public, le domaine, le format et les limites. Par exemple :

```text
Tu aides un débutant à comprendre Python.
Réponds en français avec des phrases courtes.
Donne un exemple simple quand il est utile.
Si tu n’es pas sûr d’un fait, dis-le.
N’affirme pas avoir exécuté le code ou consulté Internet.
```

Le modèle peut ne pas suivre la consigne parfaitement. Ce n’est ni une vérification des faits ni une barrière contre toutes les instructions malveillantes. Compare plusieurs réponses avec une petite liste de questions identiques avant et après modification.

## 7.2 Ajouter des informations au contexte

`connaissances.txt` contient quelques faits sur le projet. Le serveur lit les 4 000 premiers caractères au démarrage et les ajoute au prompt. Modifie ce fichier en UTF-8 et relance Flask. N’y mets ni mots de passe ni informations personnelles.

Ce mécanisme n’est **pas un système de recherche documentaire (RAG)** : il n’effectue ni recherche documentaire ni sélection par pertinence, et ne cite pas automatiquement des sources vérifiées. Un système RAG recherche des extraits, les associe à des sources et les fournit au modèle ; il exige ses propres tests et protections contre les instructions contenues dans les documents.

Ajoute des informations courtes que tu peux vérifier. Vérifie ensuite si le modèle les utilise correctement, sans inventer de lien ni omettre un élément important.

## 7.3 Limiter l’historique

Les six derniers échanges au maximum sont conservés dans une variable JavaScript, pas dans `localStorage`, un cookie ou un fichier. Le serveur vérifie l’alternance `user`, `assistant` et refuse un rôle `system` envoyé par le client. Il impose aussi 2 000 caractères à la question et 64 Kio au corps HTTP.

L’interface peut retirer des paires plus anciennes pour rester sous la limite d’octets. Une réponse encore visible à l’écran n’est donc pas forcément envoyée au modèle. « Nouvelle discussion » remet le contexte de l’onglet à zéro ; une requête en cours doit se terminer avant d’en démarrer une autre.

## 7.4 Choisir un modèle plus grand, facultativement

Reste avec `llama3.2:1b` jusqu’à ce que le projet fonctionne. Pour essayer `llama3.2:3b`, vérifie d’abord sa fiche, sa licence, sa taille et ta mémoire disponible. Puis :

```text
ollama pull llama3.2:3b
```

**PowerShell, seulement pour ce terminal :**

```powershell
$env:PIXEL_MODEL="llama3.2:3b"
.\.venv\Scripts\python.exe serveur.py
```

**macOS/Linux, seulement pour ce lancement :**

```sh
PIXEL_MODEL=llama3.2:3b .venv/bin/python serveur.py
```

Pour revenir au petit modèle sous PowerShell, arrête Flask puis exécute `Remove-Item Env:PIXEL_MODEL -ErrorAction SilentlyContinue` avant de relancer. Sous macOS/Linux, relance simplement sans le préfixe. Le vérificateur fourni teste toujours le modèle de référence `llama3.2:1b` ; vérifie séparément tes essais avec le 3b dans l’interface.

Aucun tag cloud n’est autorisé dans le serveur. Pour ajouter un autre modèle local, il faut modifier et revalider le programme, ses ressources, sa licence et la documentation. Un modèle plus gros ne rend pas automatiquement toutes les réponses fiables.

## 7.5 Fonctions non incluses : outils, agents et voix

Le modèle ne peut ni parcourir tes fichiers ni lancer des commandes. Le serveur ne lui donne aucun outil. N’ajoute pas `eval`, `exec` ou un appel shell basé sur une réponse de modèle. Toute extension d’agent doit avoir des actions autorisées explicitement, une validation des paramètres et une confirmation humaine avant des effets réels.

La voix n’est pas implémentée non plus. Certaines fonctions vocales de navigateurs ou de fournisseurs envoient l’audio à un service distant : vérifie leur fonctionnement avant de promettre un usage local. Ici, le parcours livré est textuel, sans micro ni outil autonome.

<!-- section:ch8 -->
# 8. Partager le code et publier la démo ELIZA

## 8.1 GitHub est facultatif pour l’exécution

Git enregistre l’histoire d’un dossier ; GitHub héberge des dépôts et des services autour de ce code. Aucun compte n’est nécessaire pour lancer ELIZA ou Pixel sur ton ordinateur. Pour partager le projet, crée un compte GitHub, sécurise-le avec une authentification à deux facteurs et suis la procédure officielle d’authentification de Git ou de GitHub Desktop. Ce guide ne te demande pas de créer un jeton d’inférence.

Si tu as déjà suivi l’ancienne édition, le jeton créé pour GitHub Models n’est plus utile à cet atelier. Tu peux le révoquer dans les paramètres GitHub. Vérifie d’abord qu’aucun autre projet légitime ne l’utilise ; ne copie pas sa valeur dans une capture, un message ou un dépôt.

## 8.2 Préparer le dépôt

Travaille dans un nouveau dépôt personnel, distinct du dépôt du site Quanthevaris. Le kit inclut un `.gitignore` pour exclure `.venv`, les caches, les fichiers `.env` et le rapport local de validation. Ces exclusions n’effacent pas un fichier déjà versionné.

Si tu utilises Git en ligne de commande après l’avoir installé :

```sh
git init
git status
# Après vérification qu’aucun secret ni dossier .venv n’apparaît :
git add .
git commit -m "Premier atelier ELIZA et Pixel local"
```

Configure ton identité Git si l’outil le demande. Relis les fichiers proposés à l’enregistrement avant de publier. Un secret exposé doit être révoqué ; l’effacer du dernier fichier ne le retire pas de l’historique.

## 8.3 Tester sans télécharger un modèle dans Actions

Le kit contient `.github/workflows/tests.yml`. Si tu publies **le contenu du kit à la racine de ton nouveau dépôt**, le workflow installe Flask puis lance `python -m unittest -v` sur Python 3.11 et 3.13. Ces tests ne demandent ni GPU, ni poids de modèle, ni secret. Les droits du workflow sont limités à la lecture du contenu.

Si tu places le kit dans un sous-dossier d’un autre dépôt, les chemins de ce workflow doivent être adaptés : ne suppose pas qu’un fichier `.github` imbriqué sera exécuté. Les tests GitHub peuvent consommer le quota de ton offre ; consulte ses conditions en vigueur. Ces tests automatisés ne remplacent pas un essai du modèle sur ton ordinateur.

## 8.4 Publier uniquement la démo statique d’ELIZA

Crée un dossier `docs` dans ton dépôt personnel. Copie `eliza-web.html` dedans **sous le nom `index.html`**. Ajoute un texte expliquant qu’il s’agit d’une adaptation à règles en anglais, sans IA générative. Enregistre et publie ces fichiers.

Dans les paramètres du dépôt, section Pages, choisis le mode de publication depuis une branche, puis la branche qui contient ta démo et le dossier `/docs`. Les libellés de l’interface GitHub peuvent évoluer. Attends la fin du déploiement avant de tester l’adresse publique donnée par GitHub. La disponibilité dépend de ton offre et de la visibilité du dépôt.

**La page `assistant.html` ne fonctionne pas seule sur GitHub Pages.** Il attend `/api/chat` sur le serveur local. GitHub Pages ne lance ni Python, ni Flask, ni Ollama. Remplacer une URL par `localhost` dans une page publique ne lui donne pas accès à ton ordinateur : cela vise l’appareil de chaque visiteur et peut être bloqué par le navigateur.

## 8.5 Héberger un assistant public

Un service accessible aux autres nécessiterait un serveur adapté, TLS, authentification, contrôle des ressources et des abus, politique de conservation, conditions du modèle et étude des données traitées. Le kit n’est pas conçu pour cet hébergement. Ne remplace pas l’écoute `127.0.0.1` par `0.0.0.0` et ne crée pas de tunnel public pour contourner ce travail.

Pour garder ton dépôt simple, conserve une branche principale et une branche de travail seulement lorsque nécessaire. Avant de supprimer une branche, vérifie que ses commits sont conservés ailleurs. Une pull request sert à relire un changement avant de l’intégrer ; elle n’est pas requise pour exécuter le projet local.

<!-- section:ch9 -->
# 9. Confidentialité, sécurité et limites

## 9.1 Ce qui reste local et ce qui utilise le réseau

| Opération | Où passent les données ? |
| --- | --- |
| Lire ou télécharger le guide | Le site et son hébergeur traitent les requêtes ; consulter la politique de confidentialité du site. |
| Installer Python, Flask et Ollama | Les fournisseurs de logiciels et registres reçoivent des requêtes de téléchargement. |
| `ollama pull` et mises à jour | Téléchargements réseau ; les fournisseurs ont leurs propres conditions et journaux. |
| Discuter dans le kit avec le modèle local choisi | Navigateur → Flask sur la boucle locale → Ollama sur la boucle locale. Aucun service de conversation Quanthevaris n’est contacté par le code. |
| Publier une démo sur GitHub Pages | Le visiteur contacte GitHub Pages ; ce service journalise notamment les adresses IP pour la sécurité. |

Le code fourni n’enregistre pas les conversations, n’utilise ni cookie ni stockage navigateur et ne charge pas de script distant. Le navigateur, le système, les sauvegardes et Ollama peuvent toutefois conserver des données techniques. N’utilise pas ce projet pour manipuler des données sensibles. Si tu ajoutes un journal ou un service externe, cette description doit être revue.

## 9.2 Les protections du serveur local

Le serveur refuse les hôtes et origines externes, les types de requêtes incorrects, les messages trop longs et les historiques mal formés. Il sert trois ressources déterminées et pas tout le dossier. Il ne retourne pas les exceptions détaillées du moteur au navigateur, désactive le mode debug et ne traite qu’une génération à la fois.

L’interface affiche les réponses avec `textContent`, jamais comme HTML exécutable. Une réponse contenant `<script>` doit rester du texte. Les en-têtes limitent les ressources à la même origine et interdisent l’intégration dans un cadre. Ces mesures ne constituent pas un audit de sécurité ni une infrastructure de production.

## 9.3 Vérifier les réponses

Un modèle peut inventer une fonction ou une URL, ou donner avec assurance une explication fausse. Pour du code, lis-le avant exécution, utilise un environnement isolé et ne lance jamais une commande destructrice simplement parce que Pixel la propose. Pour une affirmation factuelle, ouvre une source fiable et compare.

Le petit modèle n’est pas approprié à une décision médicale, juridique, financière ou de sécurité. Les limites mentionnées dans le prompt ne suffisent pas à le rendre sûr pour ces usages. En cas de détresse ou de besoin de conseil professionnel, adresse-toi à une personne qualifiée.

## 9.4 Ressources et énergie

Le mode local supprime la dépendance à une facturation d’API, pas le coût d’exécution. Ferme les applications lourdes, commence avec le modèle 1b et des questions courtes. Un portable peut chauffer et utiliser sa batterie. Un GPU compatible peut accélérer le calcul ; consulte la liste du matériel pris en charge par Ollama.

Ne rends pas ce serveur accessible au public pour tester ses performances. Ses limites de longueur et de requêtes simultanées ne remplacent pas l’authentification et les protections nécessaires à un service public.

## 9.5 Respecter les licences

Le code écrit pour les projets est sous MIT, avec sa notice dans le kit. Le texte et la maquette de ce guide restent © 2026 Quanthevaris, tous droits réservés ; usage personnel et éducatif autorisé. Python, Flask, Ollama et Llama gardent leurs licences et conditions respectives. Aucun poids ni logiciel tiers n’est inclus dans le ZIP. Le nom des marques ne signifie aucune affiliation.

<!-- section:ch10 -->
# 10. Valider et continuer

## 10.1 Les vérifications de fin

- [ ] Je peux expliquer la différence entre règles, modèle, serveur et interface.
- [ ] J’ai lancé ELIZA et ses tests déterministes.
- [ ] J’ai installé Python 3.11+, Flask et Ollama depuis les sources officielles.
- [ ] `ollama list` affiche le modèle local de référence `llama3.2:1b`.
- [ ] J’ai conservé une écoute locale et vérifié le choix sans fonctionnalités cloud.
- [ ] `python -m unittest -v`, avec le Python de l’environnement, se termine par `OK`.
- [ ] `verifier_installation.py` valide une **inférence réelle** sur ma machine.
- [ ] L’interface sur `http://127.0.0.1:5000` répond à deux questions successives.
- [ ] « Nouvelle discussion » efface le contexte de l’onglet.
- [ ] J’ai vérifié qu’un message d’erreur s’affiche quand Ollama est arrêté, puis réessayé après redémarrage.
- [ ] J’ai vérifié les réponses à des questions dont je connais la solution.
- [ ] Je sais arrêter Flask et décharger le modèle.
- [ ] Si je partage une démo, je ne publie que la variante statique d’ELIZA, pas ce serveur local.

Ces vérifications peuvent aussi servir avant de diffuser une nouvelle version du projet. Les tests simulés et l’essai réel du modèle doivent être distingués.

## 10.2 Améliorer progressivement

Choisis un seul changement à la fois : reformuler la personnalité, ajouter un repère vérifié ou comparer les deux modèles locaux autorisés. Note tes questions d’essai, les versions et les réponses obtenues. Garde aussi les réponses erronées pour comparer les résultats après une modification.

Pour ajouter une recherche documentaire, une mémoire persistante, des outils ou la voix, pars d’une nouvelle branche de travail et d’un besoin explicite. Définis quelles données seraient stockées ou envoyées, ce que le programme pourrait faire et comment l’utilisateur pourrait s’y opposer. Le projet fourni ne contient pas ces fonctions.

## 10.3 Ressources officielles à reconsulter

Documentation relue le 14 novembre 2026 ; logiciels, modèles et conditions évoluent.

- [Python : installation et documentation](https://www.python.org/downloads/).
- [Flask : documentation](https://flask.palletsprojects.com/en/stable/).
- [Ollama : téléchargement](https://ollama.com/download).
- [Ollama : API de conversation](https://docs.ollama.com/api/chat) et [liste des modèles locaux](https://docs.ollama.com/api/tags).
- [Ollama : fonctionnement local, cloud et configuration](https://docs.ollama.com/faq).
- [Llama 3.2:1b : fiche et licences](https://ollama.com/library/llama3.2:1b).
- [GitHub Pages : ce que le service héberge](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages).
- [GitHub Actions : documentation](https://docs.github.com/en/actions).
- [GitHub Models : statut de retrait](https://docs.github.com/en/github-models).
- Weizenbaum, J. (1966), *ELIZA — A Computer Program for the Study of Natural Language Communication Between Man and Machine*, Communications of the ACM, 9(1), 36–45, DOI : 10.1145/365153.365168.

**Fin du parcours principal.** Les annexes suivantes contiennent les fichiers réellement utilisés pour construire le kit de cette édition. Pour éviter les retours à la ligne et caractères altérés par un lecteur PDF, utilise de préférence les fichiers du ZIP.

<!-- section:annexe-a -->
# Annexe A — ELIZA en Python et ses tests

`eliza.py` : adaptation simplifiée, sans dépendance tierce. Les entrées de dialogue attendues sont en anglais. Pour un projet partagé, ajoute la notice `LICENCE-MIT.txt` fournie au code.

{{code:eliza.py}}

## Tests déterministes : test_eliza.py

Ils sont lancés par `python -m unittest -v` depuis le dossier du kit. Les tests contrôlent explicitement les tirages aléatoires et isolent la mémoire entre les cas.

{{code:test_eliza.py}}

<!-- section:annexe-b -->
# Annexe B — ELIZA dans le navigateur

`eliza-web.html` : variante statique plus courte, sans API. Pour une publication Pages, copie ce fichier dans `docs/index.html` de ton dépôt personnel, puis publie seulement ce dossier. Cette version ne charge pas de ressource distante.

{{code:eliza-web.html}}

<!-- section:annexe-c -->
# Annexe C — Le serveur local complet

Les quatre fichiers de configuration suivants sont à la racine du kit. Aucun fichier `.env` n’est requis. Ne crée pas de clé API. Le seul modèle de référence est le tag local explicitement téléchargé au chapitre 4.

## requirements.txt

{{code:requirements.txt}}

## .gitignore

{{code:.gitignore}}

## connaissances.txt

{{code:connaissances.txt}}

## serveur.py

Le serveur écoute seulement sur `127.0.0.1:5000`, conserve le mode debug désactivé et contacte Ollama sur `127.0.0.1:11434`. Le code est pédagogique, pas un service public prêt à déployer.

{{code:serveur.py}}

<!-- section:annexe-interface -->
# Annexe D — L’interface complète

Les trois fichiers ci-dessous sont servis par Flask sur la même origine que `/api/chat`. Les chemins absolus commencent par `/` parce que le serveur local sert l’atelier à sa racine. Ce choix n’est pas une recette d’hébergement GitHub Pages pour Pixel.

## assistant.html

{{code:assistant.html}}

## assistant.js

{{code:assistant.js}}

## assistant.css

Le style utilise uniquement les polices système et des règles locales. Il peut être modifié sans changer le contrat d’API. Conserve les libellés accessibles, le focus visible et l’affichage des réponses en texte brut.

{{code:assistant.css}}

<!-- section:annexe-tests -->
# Annexe E — Tester le code et le modèle installé

## test_assistant.py : tests sans modèle

Ce fichier fait partie de `python -m unittest -v`. Les appels à Ollama sont remplacés par des simulations pour vérifier les cas de réussite et d’échec de manière reproductible. Il n’évalue pas la qualité d’un modèle de langage.

{{code:test_assistant.py}}

## verifier_installation.py : inférence réelle sur ton poste

Ce script ne simule pas Ollama : il envoie une vraie question de test fixe au modèle local de référence. Il doit être exécuté après l’installation. Un échec renvoie un code non nul et ne doit pas être assimilé à une validation.

{{code:verifier_installation.py}}

## Workflow facultatif : .github/workflows/tests.yml

Cette recette suppose que le kit constitue la racine de ton dépôt personnel. Elle ne lance aucune inférence, ne télécharge aucun modèle et ne demande aucun secret.

{{code:.github/workflows/tests.yml}}

<!-- section:depannage -->
# Annexe F — Dépannage

| Symptôme | Vérification et action |
| --- | --- |
| `py`, `python3` ou `ollama` inconnu | Vérifie l’installation officielle et le PATH ; rouvre le terminal. Ne poursuis pas avec une version Python non identifiée. |
| `No module named flask` | Depuis le kit, installe `requirements.txt` avec le même Python `.venv` que celui utilisé pour lancer le serveur. |
| `.venv` n’existe pas | Reprends la création de l’environnement dans le bon dossier. Sous Linux, vérifie `python3-venv`. |
| `ollama list` ne montre pas `llama3.2:1b` | Termine `ollama pull llama3.2:1b`. Un modèle de nom voisin ne suffit pas. |
| Le diagnostic dit qu’Ollama est injoignable | Démarre l’application ou son service. Vérifie le port local 11434. Sous Linux, consulte sa documentation de service. |
| `address already in use`, port 11434 | Ollama est peut-être déjà lancé ; vérifie avant de démarrer une autre instance. |
| Le port 5000 est occupé | Arrête l’ancien atelier. Sur macOS, vérifie aussi les fonctions système qui utilisent ce port. Ne change pas seulement `app.run` : les protections d’hôte devraient être adaptées et retestées ensemble. |
| La page ouverte en double-clic ne fonctionne pas | Lance `serveur.py`, puis ouvre `http://127.0.0.1:5000`, pas `assistant.html` en fichier local. |
| Erreur 403 | Utilise l’URL locale exacte. N’intègre pas l’atelier dans un cadre, une page publique ou un tunnel ; l’origine ou l’hôte est refusé. |
| Erreur 400 ou 415 | Corps JSON ou historique invalide, ou type incorrect. Utilise l’interface fournie ; ne contourne pas les validations. |
| Erreur 413 | Corps de requête trop gros. Démarre une nouvelle discussion et envoie un message plus court. |
| Erreur 429 | Une génération est déjà en cours dans le serveur local. Attends sa fin ; ce n’est pas un quota d’API payante. |
| Erreur 503, modèle absent | Installe le tag local exact avec `ollama pull llama3.2:1b`, ou celui que tu as explicitement configuré. |
| Erreur 502 | Ollama a refusé la requête ou renvoyé un format inattendu ; vérifie sa version et ses journaux locaux. Ne publie pas de journal sans le relire. |
| Erreur 504 ou délai dépassé | Premier chargement trop lent, manque de ressources ou génération longue. Attends, ferme les logiciels lourds, essaie une question courte ; ne martèle pas Envoyer. |
| La réponse est fausse ou mal écrite | Une requête réussie ne garantit pas l’exactitude de la réponse. Vérifie les sources, simplifie la question et garde à l’esprit les limites du modèle 1b. |
| Une modification n’apparaît pas | Enregistre, arrête Flask avec Ctrl+C puis relance. Recharge le navigateur. Pour le mode cloud d’Ollama, redémarre bien Ollama lui-même. |
| Les tests passent mais aucune conversation ne marche | Les tests hors ligne simulent le modèle. Lance `verifier_installation.py` et résous son erreur avant de conclure. |
| ELIZA répond « à côté » en français | Ses règles sont en anglais. Utilise les exemples anglais ou écris des règles françaises adaptées. |
| Pixel ne fonctionne pas sur GitHub Pages | C’est attendu : Pages ne lance pas Flask ni Ollama. Publie uniquement la démo ELIZA et une présentation du projet local. |

## Si tu venais de l’ancienne édition

Repars du nouveau kit dans un dossier neuf, sans réutiliser les anciennes dépendances `openai`, `flask-cors` ou `python-dotenv`. Ne cherche pas à réparer l’ancienne API en changeant uniquement le nom du modèle. Révoque l’ancien jeton devenu inutile si aucun autre usage ne le nécessite ; s’il a été exposé, révoque-le sans attendre et traite aussi l’historique où il figure.

<!-- section:glossaire -->
# Glossaire

| Mot | Définition dans cet atelier |
| --- | --- |
| API | Interface par laquelle un programme communique avec un autre. Celle d’Ollama est ici locale. |
| Boucle locale | Adresse `127.0.0.1` ou `localhost` : l’ordinateur qui émet la requête, pas un serveur public. |
| Commit | Enregistrement d’un état du projet dans Git. Un commit n’est pas forcément signé cryptographiquement. |
| Contexte | Instructions et échanges fournis au modèle pour l’appel en cours. |
| Digest | Empreinte identifiant la version de poids effectivement installée, utile pour la reproductibilité. |
| ELIZA | Programme historique de dialogue ; notre adaptation simplifiée repose sur des règles en anglais. |
| Flask | Bibliothèque Python qui reçoit les requêtes HTTP et sert ici l’interface locale. |
| GitHub Actions | Exécution de workflows, par exemple les tests sans modèle du kit. |
| GitHub Pages | Hébergement de fichiers statiques, pas d’un serveur Python ou d’un modèle. |
| Hallucination | Réponse plausible mais erronée ou inventée. |
| Historique | Messages récents renvoyés au modèle, sans apprentissage permanent dans cet atelier. |
| Inférence | Calcul d’une réponse à partir de poids déjà appris et du contexte fourni. |
| LLM | Modèle de langage qui génère des tokens à partir d’un contexte. |
| Modèle local | Poids téléchargés et exécutés sur l’ordinateur, distincts des fonctionnalités cloud d’un fournisseur. |
| Ollama | Logiciel d’exécution de modèles et API ; ses conditions sont distinctes de la licence des poids. |
| Origine | Ensemble protocole, hôte et port d’une page ; le serveur vérifie celle des requêtes. |
| Persona | Consigne décrivant le rôle et le style de l’assistant, sans garantie de respect parfait. |
| Prompt injection | Instruction malveillante cherchant à détourner le modèle via un texte fourni. |
| RAG | Recherche d’extraits documentaires puis génération avec ces extraits ; non implémenté ici. |
| Regex | Motif qui décrit une famille de textes et peut capturer des fragments. |
| Simulation de test | Réponse préparée pour tester le programme, sans exécuter de modèle. |
| Température | Paramètre influençant l’aléatoire du calcul, sans garantir la vérité ni un déterminisme parfait. |
| Token | Fragment de texte manipulé par le modèle ; ne pas confondre avec une clé d’authentification. |
| Environnement virtuel | Dossier Python isolant les paquets d’un projet de ceux des autres projets. |

<!-- section:mentions -->
# Mentions légales et droits d’usage

## Informations d’édition

- **Titre :** Crée ton assistant IA personnalisé — Python et Ollama.
- **Autoéditeur :** Quanthevaris, France. Publication sous pseudonyme, à titre non professionnel.
- **Diffusion :** publication numérique gratuite et non périodique, édition locale 2.0 du 14 novembre 2026.
- **Contact :** [contact.quanthevaris@gmail.com](mailto:contact.quanthevaris@gmail.com).
- **ISBN :** aucun numéro attribué à cette édition.
- **Mentions légales du site :** [quanthevaris.github.io/mentions-legales.html](https://quanthevaris.github.io/mentions-legales.html).
- **Politique de confidentialité :** [quanthevaris.github.io/confidentialite.html](https://quanthevaris.github.io/confidentialite.html).

Cette édition remplace le projet fondé sur GitHub Models par un assistant exécuté en local avec Ollama. La version à jour est disponible sur [la fiche du guide](https://quanthevaris.github.io/assistant-ia.html).

## Texte, illustrations et maquette

© 2026 Quanthevaris. Tous droits réservés, sauf éléments de tiers signalés comme tels. La lecture et l’usage personnel ou éducatif du guide sont autorisés. Sa redistribution, sa modification ou sa vente nécessitent l’accord préalable de l’éditeur, sous réserve des exceptions prévues par la loi. La gratuité du téléchargement ne vaut pas autorisation de redistribution.

## Code source : licence MIT

Le code écrit pour les projets du guide est distribué sous licence MIT. Tu peux l’utiliser, le copier, le modifier et le redistribuer, y compris à des fins commerciales, à condition de conserver la notice de copyright et le texte de la licence. Cette autorisation concerne le code, pas le texte ni la maquette du guide.

Le texte officiel anglais de la licence figure dans `LICENCE-MIT.txt`, fourni dans le kit et en pièce jointe de ce PDF (volet « Pièces jointes » des lecteurs compatibles). Il est aussi [téléchargeable sur le site](https://quanthevaris.github.io/assets/pdf/LICENCE-MIT.txt). Ce texte fait foi ; le paragraphe ci-dessus en est un résumé.

## Logiciels, modèles et marques

Python, Flask, Ollama et les autres composants tiers conservent leurs licences. Les poids de `llama3.2` relèvent de la **Llama 3.2 Community License** et de sa politique d’utilisation, et non de la licence MIT du code. Consulte [la fiche du modèle et les conditions associées](https://ollama.com/library/llama3.2:1b) avant de le télécharger ou de le redistribuer. Le kit ne contient ni poids de modèle ni installateur tiers.

Les noms Python, Flask, Ollama, Llama, GitHub, Microsoft, Windows et Visual Studio Code sont cités pour identifier les outils utilisés. Ils appartiennent à leurs titulaires respectifs. Ce guide est indépendant et n’est ni affilié à ces éditeurs ni approuvé par eux. Notre version d’ELIZA est une adaptation pédagogique ; la référence au travail de Joseph Weizenbaum figure au chapitre 10.

## Données personnelles et fonctionnement local

Le PDF se lit hors ligne une fois téléchargé. Sa consultation sur le site et son téléchargement restent soumis aux traitements décrits dans la politique de confidentialité, notamment aux journaux techniques de GitHub Pages.

Dans la configuration décrite, les messages de Pixel passent du navigateur au serveur Flask, puis au modèle local d’Ollama sur le même ordinateur. Le code fourni n’enregistre pas les conversations et ne les transmet pas à Quanthevaris. L’installation et les téléchargements utilisent Internet ; le navigateur, le système et les logiciels tiers peuvent conserver leurs propres données techniques. N’utilise pas d’informations sensibles pour les exercices. Tout ajout d’un service distant ou d’un stockage nécessite de réexaminer ces conditions.

## Usage pédagogique et responsabilité

Le guide et le code sont fournis en l’état, à des fins d’apprentissage. Les tests automatisés vérifient le code avec des réponses simulées ; ils ne certifient ni le fonctionnement du modèle sur chaque ordinateur, ni la qualité de ses réponses. Utilise `verifier_installation.py`, puis essaie l’interface sur ton matériel.

Les logiciels, liens, licences et prérequis peuvent évoluer. Lis les commandes avant de les exécuter, sauvegarde tes fichiers et vérifie les réponses du modèle. Cet assistant ne remplace pas un avis médical, juridique, financier ou de sécurité. Le serveur est prévu pour un usage local : il ne doit pas être exposé sur Internet en l’état.

L’éditeur ne garantit pas l’absence d’erreur ni la compatibilité avec toutes les configurations. Ces limites s’appliquent dans la mesure permise par la loi et n’excluent aucune responsabilité qui ne pourrait légalement l’être. Pour signaler une erreur, utilise l’adresse de contact en précisant la version du guide et la page concernée, sans transmettre de donnée sensible.
