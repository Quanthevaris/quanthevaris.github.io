# quanthevaris.github.io

Site statique de **Quanthevaris** : guides pédagogiques gratuits pour apprendre à coder des jeux vidéo.
Aucune dépendance, aucun traceur, aucun cookie — publié via GitHub Pages.

## Structure

```
├── index.html                  Accueil
├── guides.html                 Liste des guides
├── esquive-en-pixels.html      Page du guide « Esquive en Pixels »
├── contact.html                Contact
├── mentions-legales.html       Mentions légales
├── confidentialite.html        Politique de confidentialité
├── 404.html                    Page introuvable (gérée par GitHub Pages)
├── site.webmanifest            Manifeste (icônes / thème)
├── robots.txt · sitemap.xml    Référencement
├── css/style.css               Styles du site (design system complet)
├── js/script.js                Menu mobile + année du pied de page
└── assets/
    ├── fonts/                  Inter (WOFF2, subset latin) + licence OFL
    ├── img/                    Favicons, image de partage (Open Graph), aperçus
    └── pdf/                    Guides téléchargeables
```

## Conventions

- **Chemins absolus** (`/css/style.css`) : les pages fonctionnent aussi bien depuis
  `quanthevaris.github.io/` que depuis n'importe quelle sous-adresse.
- **Images** : toujours renseigner `width`, `height`, `alt` et `loading="lazy"`
  (sauf image du hero). Formats : PNG/WebP, favicons en ICO + PNG.
- **Polices** : auto-hébergées dans `assets/fonts/`, aucune requête vers un domaine tiers
  (cohérent avec la politique de confidentialité).
- **Accessibilité** : lien d'évitement, focus visible, contrastes AA, `aria-current`
  sur l'onglet actif, menu mobile refermable avec Échap.

## Ajouter un guide

1. Déposer le PDF dans `assets/pdf/`.
2. Créer une page dédiée sur le modèle de `esquive-en-pixels.html`.
3. Ajouter une carte dans `guides.html` et, si besoin, une entrée dans `sitemap.xml`.

## Développement local

```bash
python3 -m http.server 8000
# puis ouvrir http://localhost:8000
```
