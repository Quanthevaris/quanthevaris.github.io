# quanthevaris.github.io

Site statique de **Quanthevaris** : guides pédagogiques et jeux gratuits à télécharger.
Aucune dépendance, aucun traceur, aucun cookie — publié via GitHub Pages.

## Structure

```
├── index.html                  Accueil
├── guides.html                 Liste des guides
├── jeux.html                   Catalogue des jeux (à enrichir lors de chaque sortie)
├── esquive-en-pixels.html      Page du guide « Esquive en Pixels »
├── fission-arena.html          Page du jeu FISSION ARENA (téléchargement, notice de santé, licence)
├── contact.html                Contact
├── mentions-legales.html       Mentions légales
├── confidentialite.html        Politique de confidentialité
├── 404.html                    Page introuvable (gérée par GitHub Pages)
├── site.webmanifest            Manifeste (icônes / thème)
├── LICENCES-TIERS.txt          Notices du site (Inter, Lucide / Feather)
├── robots.txt · sitemap.xml    Référencement
├── css/style.css               Styles du site (design system complet)
├── js/script.js                Menu mobile + année du pied de page
├── assets/
│   ├── fonts/                  Inter (WOFF2, subset latin) + licence OFL
│   ├── img/                    Favicons, images de partage (Open Graph), aperçus, captures du jeu
│   ├── jeux/                   FISSION ARENA : .exe, code source .py, fiche du .exe, licences des tiers
│   └── pdf/                    Guides téléchargeables
├── _exe/                       Kit qui fabrique le .exe (non publié sur le site : dossier en « _ »)
└── .github/workflows/          Fabrication et test automatiques du .exe (GitHub Actions)
```

## Licences

- **Code du site** (HTML, CSS, JavaScript) et programme du guide « Esquive en Pixels » : licence MIT.
- **Texte et maquette du guide** « Esquive en Pixels » : © 2026 Quanthevaris, tous droits réservés.
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
- **Polices** : auto-hébergées dans `assets/fonts/`, aucune requête vers un domaine tiers
  (cohérent avec la politique de confidentialité).
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

## Visibilité

Aucun lien vers le dépôt depuis les pages publiques. Ne pas rendre ce dépôt privé sans vérifier la compatibilité de GitHub Pages avec l’abonnement : cela peut interrompre le site. Les mentions de l’hébergeur et les attributions des composants tiers restent nécessaires.
