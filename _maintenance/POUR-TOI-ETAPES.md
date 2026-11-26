# Ce qu’il te reste à faire — dans l’ordre

## Ce qui est déjà fait

- Le guide a été réécrit pour **Ollama en local**, avec Python et Flask, sans GitHub Models.
- Le nouveau PDF et sa copie à l’ancienne adresse sont générés depuis le même HTML.
- Le kit téléchargeable contient les vrais fichiers du guide, leurs tests et un démarrage rapide.
- L’accueil, la fiche du guide, le catalogue, les liens, les aperçus, les mentions et la confidentialité sont synchronisés.
- Les tests automatiques du programme et du navigateur utilisent un **moteur simulé**. Ils ne prétendent pas avoir téléchargé et fait tourner un modèle réel.
- Rien n’a été déployé sur ton site public pendant cette intervention.

**Tu n’as pas à réécrire le PDF ni à créer de clé API.** Il te reste un essai sur ton ordinateur, une relecture, puis la publication du site.

## 1. Récupérer les deux livrables

Depuis les fichiers de cette session :

1. Le guide : `guide-assistant-ia.pdf` (également dans `assets/pdf/assistant-ia-guide.pdf`).
2. Le code : `assets/code/assistant-ia-kit.zip`.

Garde ton ancien PDF comme archive personnelle si tu le souhaites, mais ne le diffuse plus comme guide fonctionnel. Décompresse le nouveau ZIP **dans un dossier neuf sur ton ordinateur**. Ouvre le dossier intérieur `assistant-ia`, celui qui contient `serveur.py` et `LIRE-MOI.md`. N’essaie pas de lancer directement un fichier depuis la fenêtre du ZIP.

Le kit est un atelier distinct : tu n’as pas besoin de recopier son contenu à la racine du dépôt de ton site. Les fichiers de publication sont déjà préparés à leur bonne place dans cette branche.

## 2. Installer ou vérifier Python et Ollama

1. Installe Python 3.11 ou plus récent depuis https://www.python.org/downloads/.
2. Installe Ollama depuis https://ollama.com/download et ouvre l’application.
3. Vérifie ses conditions et le système supporté : Windows 10 22H2+, macOS 14+ ou Linux compatible selon sa documentation actuelle.
4. Prévois de la place : le petit modèle représente environ 1,3 Go, en plus des logiciels. Recommandation de départ de l’atelier : 8 Go de RAM et 10 Go de disque libres, sans garantie de vitesse.
5. Ouvre un nouveau terminal et lance :

```text
ollama --version
ollama pull llama3.2:1b
ollama list
```

Attends la fin du téléchargement. La liste doit afficher **llama3.2:1b**, pas seulement un autre modèle. Si Ollama n’est pas lancé, démarre son application ou son service ; pour un lancement manuel, `ollama serve` se garde dans un terminal séparé. Si le port est déjà occupé, une instance tourne peut-être déjà.

Lis les conditions du modèle : https://ollama.com/library/llama3.2:1b. Son utilisation n’est pas couverte par la licence MIT du code de notre kit. Aucun compte ni carte bancaire n’est requis pour le modèle local choisi.

## 3. Confirmer le choix local, sans exposer de serveur

- Ne règle pas `OLLAMA_HOST` sur `0.0.0.0` et ne crée pas de tunnel public.
- N’ouvre pas le port 11434 dans ton routeur.
- Pour désactiver les fonctions cloud : ajoute `"disable_ollama_cloud": true` dans le fichier de configuration d’Ollama, puis quitte et redémarre Ollama.

Emplacement : `%USERPROFILE%\.ollama\server.json` sous Windows ; `~/.ollama/server.json` sous macOS/Linux. S’il n’existe pas, crée un fichier JSON contenant :

```json
{
  "disable_ollama_cloud": true
}
```

S’il existe déjà, conserve ses autres propriétés et ajoute celle-ci avec une syntaxe JSON valide. Ce fichier se trouve dans le dossier **Ollama**, pas dans le kit. La méthode et l’alternative `OLLAMA_NO_CLOUD=1` sont décrites dans https://docs.ollama.com/faq et au chapitre 4 du guide.

## 4. Installer l’atelier et lancer les tests

Dans le terminal, place-toi dans le dossier décompressé qui contient `serveur.py`.

### Windows — PowerShell

```powershell
py -3 --version
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest -v
```

### macOS / Linux

```sh
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest -v
```

Vérifie que la version Python indiquée est au moins 3.11. Attends le résultat **OK** des tests. Ils simulent le moteur : ce n’est pas encore le test de ton modèle. Il n’est pas nécessaire d’activer l’environnement ou de changer la politique de sécurité de PowerShell.

## 5. Effectuer la vraie validation du modèle

### Windows

```powershell
.\.venv\Scripts\python.exe verifier_installation.py --rapport validation-locale.json
```

### macOS / Linux

```sh
.venv/bin/python verifier_installation.py --rapport validation-locale.json
```

Résultat attendu : **INFERENCE LOCALE REELLE OK**, suivi d’une salutation réellement générée. Le script enregistre les versions et le digest du modèle dans le rapport local. Lis la réponse : un résultat techniquement valide peut rester médiocre.

**Si cette étape échoue, ne conclus pas que le guide fonctionne sur ta machine.** Consulte l’annexe Dépannage et transmets le message d’erreur, ton système, les versions Python/Ollama et le nom du modèle, sans donnée sensible. Ne joins jamais d’ancien jeton ou de clé.

## 6. Essayer l’interface de bout en bout

### Windows

```powershell
.\.venv\Scripts\python.exe serveur.py
```

### macOS / Linux

```sh
.venv/bin/python serveur.py
```

1. Garde le terminal ouvert.
2. Ouvre **http://127.0.0.1:5000** sur le même ordinateur ; ne double-clique pas `assistant.html`.
3. Demande une explication d’une boucle Python, puis un exemple lié à la réponse précédente.
4. Clique **Nouvelle discussion** et vérifie que le contexte précédent n’est plus repris.
5. Pose une question dont tu connais la réponse et vérifie la qualité, pas seulement l’apparence du texte.
6. Arrête Ollama et vérifie que l’interface affiche une erreur claire ; redémarre-le et réessaie.
7. Termine avec **Ctrl+C** dans le terminal de Flask. Si besoin, `ollama stop llama3.2:1b` décharge le modèle.

Si tout passe, tu disposes d’un parcours réellement essayé sur ton matériel. Garde le rapport pour connaître les versions utilisées. Les performances sur les ordinateurs des lecteurs peuvent varier.

## 7. Relire le nouveau guide et supprimer la confusion avec l’ancien

- Relis la couverture, les prérequis et les chapitres 4, 6 et 8.
- Vérifie que la mention **édition locale 2.0** est celle que tu souhaites diffuser.
- Il n’y a plus de parcours d’inférence GitHub ni de clé à créer.
- Les exemples ELIZA sont en anglais ; Pixel reçoit une consigne française.
- Le guide ne promet pas un assistant public sur GitHub Pages.
- Les captures de l’interface sont étiquetées comme aperçus avec diagnostic simulé, pas comme preuve de ta validation réelle.
- Si tu avais créé un jeton pour l’ancienne édition et qu’il n’a plus d’autre usage, révoque-le dans tes paramètres GitHub. S’il a été divulgué, révoque-le immédiatement et traite aussi l’historique concerné.

Si tu changes le code du kit ou la source du guide après relecture, régénère ensemble HTML, ZIP, PDF et métadonnées selon le README du dépôt. Ne retouche pas séparément le PDF téléchargé, sinon les versions divergeront.

## 8. Publier les changements du site

Pour publier de futures corrections, après l’essai réel et la relecture :

1. Fais enregistrer et publier cette branche de travail, puis ouvrir une pull request vers `main`. Il n’est pas nécessaire de créer une autre branche.
2. Relis le différentiel : le site, le nouveau guide, les deux copies PDF, le kit et les images doivent être inclus ensemble. Les dossiers `.venv`, `node_modules`, `.cache` et les modèles ne doivent pas être publiés.
3. Après vérifications, fusionne la pull request dans `main`.
4. Attends la réussite du déploiement **GitHub Pages** dans l’onglet Actions.
5. Ouvre le site public sans cache. Vérifie l’accueil, la fiche Assistant IA, le PDF, le ZIP et le guide HTML. Les deux anciennes adresses PDF doivent servir la nouvelle édition.
6. Ne supprime la branche de cette session qu’une fois son travail intégré et la session terminée ; tu pourras alors revenir à une seule branche distante `main`.

Vérifie l’état de la pull request et du déploiement avant de considérer une modification comme publiée.

## 9. Vérification restante issue de l’audit : GoatCounter

Cette partie est distincte de l’atelier IA. La configuration du script n’a pas été étendue ni remplacée.

- Dans ton compte privé, confirme Sessions uniquement, autres dimensions désactivées, tableau privé, conservation 365 jours.
- Conserve les informations du fournisseur justifiant le traitement et l’analyse d’une éventuelle exemption de consentement ; l’absence de cookie ne suffit pas.
- Si l’exemption ne peut pas être justifiée, désactive la mesure ou fais mettre en place un consentement préalable valable avant son activation.

Le détail est dans `_audience/ACTIVATION.md` et `_maintenance/SUIVI-AUDIT.md`. Je n’ai pas accès à ces réglages privés et ne peux pas les certifier depuis le dépôt.
