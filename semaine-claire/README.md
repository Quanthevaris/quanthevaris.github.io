# Semaine Claire — prototype autonome

> **Nom de travail.** Ce dossier est un nouveau site complet, sans identité Quanthevaris dans les pages visibles. Le pseudonyme, le domaine et le juridique seront fixés ensuite : voir [`A-FINALISER.md`](./A-FINALISER.md).

Semaine Claire est la reprise de A à Z d’un ancien « Kit de rentrée » : un produit gratuit pour aider les **collégiens et lycéens** à transformer une pile de devoirs en une semaine lisible. Le cœur du produit n’est plus un empilement de pages à remplir, mais un rituel guidé en quatre gestes : **vider, choisir, placer, vérifier**.

## Ce qui est livré

| Élément | Fichier | Rôle |
| --- | --- | --- |
| Page d’atterrissage | `index.html` | Diagnostic, promesse, méthode, aperçu, objections, CTA |
| Planner local | `planner.html` | Ajout de tâches, trois priorités, semaine, bilan, impression, export |
| Kit A4 remplissable | `assets/pdf/kit-semaine-claire.pdf` | 8 pages cohérentes, champs PDF et impression propre |
| Transparence | `confidentialite.html` | Données locales, limites, éléments juridiques restants |
| Contact | `contact.html` | Adresse `semaineclaire@gmail.com` et consignes |
| Dossier de relance | `docs/DOSSIER-RELANCE.md` | Positionnement, offre, copy, lancement, indicateurs |
| Audit de départ | `docs/AUDIT-DEPART.md` | Ce qui a été conservé, supprimé et reconstruit |
| Générateur PDF | `outils/generer-kit.py` | Régénère le kit sans dépendre d’un ancien Canva |
| Tests | `tests/*.test.mjs` | Logique du planner, liens, CSP, absence d’appels externes |

## Principes produit

- **Gratuit**, sans essai limité, sans paiement et sans version premium cachée.
- **Aucun compte, aucun traceur publicitaire, aucun script tiers.**
- Les données du planner restent dans `localStorage` du navigateur.
- Le planner ne fait aucun appel réseau ; `connect-src 'none'` dans la CSP.
- Export/import JSON, impression A4 et archivage local d’un résumé de semaine.
- Pages en `noindex` tant que le nom, le domaine et les mentions légales ne sont pas fixés.
- Aucun chiffre de vente, témoignage ou résultat scolaire inventé.

## Démarrer

Depuis ce dossier :

```bash
python3 -m http.server 8000
# puis ouvrir http://localhost:8000/
```

Depuis la racine du dépôt de travail, l’aperçu est accessible à `/semaine-claire/`. Tous les liens du site sont relatifs : le dossier peut être déplacé à la racine d’un autre dépôt ou d’un domaine définitif.

## Tester

```bash
cd semaine-claire
npm test
```

Les tests Node couvrent :

- le calcul de semaine, la validation, le tri, les trois priorités, l’archivage et l’import ;
- les liens et ancres locaux ;
- l’absence de scripts inline, de gestionnaires `on*`, de styles inline et d’URL externes ;
- la présence de tous les identifiants DOM attendus par le planner ;
- la présence du PDF, des visuels et du dossier stratégique.

## Régénérer le kit PDF

```bash
cd semaine-claire
python3 -m venv .venv
.venv/bin/pip install -r outils/requirements.txt
.venv/bin/python outils/generer-kit.py
```

Le script écrit `assets/pdf/kit-semaine-claire.pdf`. Il produit 8 pages A4 avec des champs de formulaire et des cases à cocher. Aucun ancien PDF source n’est réutilisé.

## Structure

```text
semaine-claire/
├── index.html · planner.html · contact.html · confidentialite.html
├── A-FINALISER.md · README.md · package.json
├── assets/
│   ├── css/       site.css + planner.css
│   ├── js/        planner-core.mjs + planner.mjs
│   ├── img/       hero, aperçu PDF, OG image, favicons
│   ├── fonts/     Inter WOFF2 + licence OFL
│   └── pdf/       kit-semaine-claire.pdf
├── docs/          dossier de relance + audit de départ
├── outils/        générateur du PDF
└── tests/         tests Node sans dépendance
```

## Contact

Adresse de contact du projet : **semaineclaire@gmail.com** (fournie par l’éditeur). La page [`contact.html`](./contact.html) contient le lien `mailto:` correspondant ; voir [`A-FINALISER.md`](./A-FINALISER.md#2-adresse-de-contact-dédiée) pour la vérification par message de test avant publication officielle.

## Crédits et licence

- Police **Inter** : SIL Open Font License, notice dans `assets/fonts/Inter-LICENSE.txt`.
- Visuel hero et image de partage : illustrations générées pour ce prototype, sans texte de marque lisible.
- Icônes : SVG dessinés dans le dossier.
- Code, textes, PDF et identité définitive : licence à fixer avant publication officielle.
