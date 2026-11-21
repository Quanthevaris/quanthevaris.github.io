# quanthevaris.github.io

Site statique de **Quanthevaris** : guides gratuits pour débuter en Python — jeu avec
Pygame, assistant IA local avec Ollama et Flask — et jeux Windows à télécharger, sans publicité.
Aucune dépendance à l'exécution du site, aucun cookie — publié via GitHub Pages.
Une mesure d'audience agrégée GoatCounter est configurée, sans profil individuel (voir plus bas).

## Structure

```
├── index.html                  Accueil
├── guides.html                 Liste des guides
├── jeux.html                   Catalogue des jeux (à enrichir lors de chaque sortie)
├── assistant-ia.html           Page du guide « Crée ton assistant IA personnalisé — Python et Ollama »
├── esquive-en-pixels.html      Page du guide « Esquive en Pixels »
├── fission-arena.html          Page du jeu FISSION ARENA (téléchargement, notice de santé, licence)
├── contact.html                Contact
├── mentions-legales.html       Mentions légales
├── confidentialite.html        Politique de confidentialité
├── 404.html                    Page introuvable (gérée par GitHub Pages)
├── site.webmanifest            Manifeste (icônes / thème)
├── LICENCES-TIERS.txt          Notices du site (Inter, Lucide / Feather)
├── LICENSE                     Licence MIT du code, avec son périmètre (texte intégral : assets/pdf/LICENCE-MIT.txt)
├── robots.txt · sitemap.xml    Référencement
├── css/style.css               Styles du site (design system complet)
├── js/script.js                Menu mobile + année du pied de page
├── js/audience.js              Mesure d'audience GoatCounter minimale
├── assets/
│   ├── fonts/                  Inter (WOFF2, subset latin) + licence OFL
│   ├── img/                    Favicons, images de partage (Open Graph), aperçus, captures du jeu
│   ├── jeux/                   FISSION ARENA : .exe, code source .py, fiche du .exe, licences des tiers
│   └── pdf/                    Guides téléchargeables
├── _exe/                       Kit qui fabrique le .exe (non publié sur le site : dossier en « _ »)
├── _audience/                  Mode d'emploi, analyse de confidentialité et tests (non publié : dossier en « _ »)
└── .github/workflows/          Fabrication et test automatiques du .exe (GitHub Actions)
```

## Licences

La licence MIT du code est résumée ici et détaillée dans [`LICENSE`](LICENSE), à la racine du dépôt
(périmètre explicite). Le texte intégral joint aux guides reste `assets/pdf/LICENCE-MIT.txt`.

- **Code du site** (HTML, CSS, JavaScript) et programmes des guides « Esquive en Pixels » et « Crée ton assistant IA personnalisé — Python et Ollama » : licence MIT.
- **Texte et maquette des guides** « Esquive en Pixels » et « Crée ton assistant IA personnalisé — Python et Ollama » : © 2026 Quanthevaris, tous droits réservés.
- **Jeu FISSION ARENA** (`assets/jeux/FISSION_ARENA.py`, `FISSION_ARENA.exe`, nom, images, sons) :
  © 2026 Quanthevaris, tous droits réservés. Jeu gratuit, mais **pas sous licence MIT** : usage personnel
  libre, redistribution ou diffusion d'une version modifiée seulement avec l'accord de l'auteur.
  Conditions complètes : <https://quanthevaris.github.io/fission-arena.html#licence>.
- **Logiciels de tiers contenus dans le `.exe`** (Python, pygame, SDL…) : leurs propres licences,
  reproduites dans `assets/jeux/LICENCES-TIERS.txt`.
- **Police Inter** : SIL Open Font License (`assets/fonts/Inter-LICENSE.txt`).
- **Icônes Lucide / Feather** : notices ISC et MIT dans `LICENCES-TIERS.txt`.

Le détail fait foi dans les [mentions légales](https://quanthevaris.github.io/mentions-legales.html#propriete-intellectuelle).

## Conventions

- **Chemins absolus** (`/css/style.css`) : les pages fonctionnent aussi bien depuis
  `quanthevaris.github.io/` que depuis n'importe quelle sous-adresse.
- **Images** : toujours renseigner `width`, `height`, `alt` et `loading="lazy"`
  (sauf image du hero). Formats : PNG/WebP, favicons en ICO + PNG.
- **Polices et scripts** : auto-hébergés dans `assets/fonts/` et `js/`, sans chargement de script tiers.
  La requête de comptage GoatCounter est le seul appel tiers ajouté au chargement des pages.
- **Accessibilité** : lien d'évitement, focus visible, contrastes AA, `aria-current`
  sur l'onglet actif, menu mobile refermable avec Échap.

## Ajouter un jeu

Créer une page dédiée, ajouter une carte à `jeux.html`, une URL au sitemap et les fichiers dans `assets/jeux/`. Garder les licences de chaque jeu distinctes.

## Ajouter un guide

1. Déposer le PDF dans `assets/pdf/`.
2. Créer une page dédiée sur le modèle de `esquive-en-pixels.html`.
3. Ajouter une carte dans `guides.html` et, si besoin, une entrée dans `sitemap.xml`.

## Mettre à jour FISSION ARENA

1. Modifier `assets/jeux/FISSION_ARENA.py` (et son numéro `VERSION`), puis pousser sur `main`.
2. GitHub Actions teste le code, fabrique `FISSION_ARENA.exe` sous Windows, le teste, puis range
   le nouveau `.exe` et sa fiche dans `assets/jeux/` (commit automatique). Ne jamais modifier ces
   deux fichiers à la main.
3. Reporter le nouveau numéro de version et la taille du fichier dans `fission-arena.html`,
   `index.html` et `jeux.html`.
4. Si la fabrication signale une bibliothèque non décrite, compléter `assets/jeux/LICENCES-TIERS.txt`.

Le détail est dans [`_exe/README.md`](_exe/README.md).

## Développement local

```bash
python3 -m http.server 8000
# puis ouvrir http://localhost:8000
```

## Mesure d'audience

`js/audience.js` est chargé par les pages du site (hors guide HTML imprimable) et configuré pour
`https://quanthevaris.goatcounter.com/count`. Il ne lit ni n'écrit de stockage navigateur,
respecte Do Not Track et Global Privacy Control, ignore les aperçus/localhost/iframes et ne
transmet que le chemin canonique des pages connues. Les chiffres sont des estimations de visites,
pas un nombre exact de personnes. Les pages IA restent exclues de la liste des chemins comptés.
La promesse est « sans cookie ni profil individuel », pas « zéro donnée traitée ».

Le compte est réglé au minimum (Sessions uniquement, conservation 365 jours, tableau privé).
La politique publique décrit ce traitement ; le mode d'emploi et l'analyse sont dans
[`_audience/ACTIVATION.md`](_audience/ACTIVATION.md) et
[`_audience/ANALYSE-CONFIDENTIALITE.md`](_audience/ANALYSE-CONFIDENTIALITE.md).
Pour désactiver, remettre `CONFIG.endpoint` à `""` et restaurer les textes sans audience avant
de déployer. Tests sans dépendance ni envoi réel : `node --test _audience/test-audience.mjs`.

## Illustration de l’accueil

Le hero utilise `assets/img/code-to-play-hero.webp` (environ 51 Ko), avec repli JPEG.
Cette illustration d’ambiance 3D générée par IA est affichée seule, sans titre ni légende.
Son texte alternatif précise qu’il ne s’agit pas d’une capture du jeu, qui reste en 2D.
Les véritables aperçus d’Esquive en Pixels sont
conservés dans les cartes et sur la page du guide. Aucun script tiers n’est ajouté.

## Assistant IA — édition locale 2.0

Le parcours GitHub Models est remplacé par **Flask + API native Ollama + modèle local
`llama3.2:1b`**. GitHub sert au versionnement, aux tests et à une démo ELIZA statique,
pas à l’hébergement d’un assistant public. Aucun jeton ni service de conversation
Quanthevaris n’est utilisé. ELIZA fonctionne indépendamment du modèle.

- Source éditoriale : `_maintenance/guide-ia/contenu.md`, template et style voisins.
- Sources réellement livrées : `assets/code/assistant-ia/` ; kit téléchargeable
  `assets/code/assistant-ia-kit.zip` (sans environnement, cache, modèle ni logiciel tiers).
- `guide-assistant-ia.html` est généré avec les listings de ces mêmes fichiers.
- Les mentions légales sont dans la section `mentions` de la source éditoriale.
  L’export joint automatiquement `assets/pdf/LICENCE-MIT.txt` au PDF, comme pour le guide Pygame.
- Les deux PDF sont identiques ; `assets/pdf/assistant-ia-version.json` fournit le
  nombre de pages, les tailles et les empreintes PDF/ZIP. Ne pas les modifier à la main.
- Tests du programme et du navigateur avec **moteur simulé**, pas une inférence réelle.
  Le modèle, ses performances et la qualité des réponses doivent être essayés sur le
  matériel du lecteur. `verifier_installation.py` dans le kit effectue ce vrai test.

### Régénérer le guide (maintenance, pas installation du lecteur)

Python 3.11+, Node 22+ et Linux pour le Chromium embarqué ; sur un autre système,
définir `CHROME_EXECUTABLE` vers une installation Chrome/Chromium compatible.

```bash
python3 -m venv .venv
.venv/bin/pip install -r _maintenance/requirements.txt
npm ci --prefix _maintenance
.venv/bin/python _maintenance/generer-guide-ia.py
node _maintenance/exporter-guide-ia.mjs
.venv/bin/python _maintenance/synchroniser-ia.py
```

Les outils Node sont dans `_maintenance/`, sans impact sur le site statique.
L’ancien script d’estampillage d’archive est retiré : il ne faut pas le réappliquer
à la nouvelle édition. Le workflow PDF ne télécharge aucun poids de modèle.

### Vérifier

```bash
python3 _maintenance/test-site.py
python3 _maintenance/securiser-pages.py --check
python3 _maintenance/test-securite.py
node _maintenance/test-securite-navigateur.mjs
node --test _audience/test-audience.mjs
.venv/bin/pip install -r assets/code/assistant-ia/requirements.txt
.venv/bin/python -m unittest discover -s assets/code/assistant-ia -v
.venv/bin/python _maintenance/test-livraison-ia.py
.venv/bin/python _maintenance/test-editorial.py
# Site statique : affichage responsive et téléchargement des deux PDF :
node _maintenance/test-interface-site.mjs
# Test HTTP et navigateur avec un faux moteur, nécessite les outils npm ci-dessus :
.venv/bin/python _maintenance/test-parcours-ia.py
# Mettre à jour les miniatures après une modification de l’interface (Linux + polices DejaVu) :
.venv/bin/python _maintenance/miniatures-ia.py
node --check js/audience.js
node --check js/script.js
git diff --check
```

Le workflow `.github/workflows/verifier-site.yml` rejoue les tests Python, statiques,
de livraison et d’audience sur les pull requests, sans télécharger de modèle. Le contrôle
navigateur reste une commande de maintenance distincte ; il n’est pas exécuté par ce workflow.

Les commandes de validation **avec un vrai modèle**, les étapes restantes de l’éditeur
et les précautions de publication figurent dans
[`_maintenance/POUR-TOI-ETAPES.md`](_maintenance/POUR-TOI-ETAPES.md).
Le suivi de l’audit, y compris les vérifications privées de GoatCounter encore à faire,
est dans [`_maintenance/SUIVI-AUDIT.md`](_maintenance/SUIVI-AUDIT.md).

## Relecture du guide Esquive en Pixels

Le dépôt ne contient pas la source de mise en page du premier guide. Les retouches
sont donc appliquées au PDF original conservé dans Git, sans rasteriser les pages
ni modifier les deux pages de code complet (empreintes contrôlées).

- `_maintenance/guide-jeu/retouches.json` : passages à remplacer et nouveaux textes.
- `_maintenance/guide-jeu/mentions.txt` : texte de la dernière page.
- `_maintenance/relire-guide-jeu.py` : application des retouches, liens et licence jointe.

```bash
.venv/bin/python _maintenance/relire-guide-jeu.py
.venv/bin/python _maintenance/synchroniser-ia.py
.venv/bin/python _maintenance/test-editorial.py
```

Le script repart toujours du même original, pas du PDF déjà modifié. Il nécessite
l’objet Git indiqué dans le script (commit `4fe4e50e2b37a8c2d20f136fde23c8194b124520`).
Avec un clone sans cet historique, fournir une copie de cet original via `--source chemin.pdf`.
Le fichier livré reste `assets/pdf/esquive-en-pixels-guide.pdf`. La synchronisation
met à jour les tailles et les liens versionnés des deux guides. Ces outils et leurs
dépendances ne sont pas nécessaires pour lire les guides ou lancer leurs projets.

## Sécurité et maintenance

Le bilan des protections appliquées, des contrôles et des réglages privés restant
à vérifier est dans [`_maintenance/SECURISATION.md`](_maintenance/SECURISATION.md).
Après modification d’un HTML ou d’un bloc JSON-LD, lancer
`python3 _maintenance/securiser-pages.py` pour actualiser sa CSP ; les générateurs
du guide le font automatiquement. Le fichier Google de validation ne doit pas être modifié.

Les workflows du dépôt utilisent des actions épinglées à des SHA complets. Le job
de compilation du jeu ne possède plus de droit d’écriture ; un job séparé publie
l’artefact sans l’exécuter. Le workflow **Auditer les dépendances** contrôle
hebdomadairement les paquets Python de maintenance/du kit IA et les outils npm,
sans créer de branche. Réviser régulièrement les résultats dans l’onglet Actions.
Ces protections ne remplacent pas la double authentification ni le contrôle des accès GitHub.

## Visibilité

Aucun lien vers le dépôt depuis les pages publiques. Ne pas rendre ce dépôt privé sans vérifier la compatibilité de GitHub Pages avec l’abonnement : cela peut interrompre le site. Les mentions de l’hébergeur et les attributions des composants tiers restent nécessaires.
