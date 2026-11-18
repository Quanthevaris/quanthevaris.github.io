# À finaliser avant publication officielle

Ce dossier est un **site autonome livré comme prototype**. Il ne dépend pas du design ni de la marque du dépôt qui l’héberge pendant les travaux. Plusieurs éléments restent volontairement provisoires : ils sont listés ici pour être traités « juste après », sans inventer une identité juridique ou une adresse qui n’existe pas.

## 1. Pseudonyme et marque

- Nom de travail actuel : **Semaine Claire**.
- Couleurs actuelles : blanc, bleu `#135BEA`, marine `#10233F`.
- Remplacer le nom, le dossier, le logo SVG, les favicons, le titre de l’image de partage et les métadonnées une fois le pseudonyme choisi.
- Repérer toutes les occurrences :

```bash
grep -RIn "Semaine Claire\|semaine-claire\|semaineclaire" semaine-claire
```

- Le slogan actuel (« 10 minutes le dimanche… ») peut être conservé même si le nom change : il décrit la promesse, pas la marque.

## 2. Adresse de contact dédiée

État actuel : adresse fournie par l’éditeur, **semaineclaire@gmail.com**, déjà branchée dans `contact.html` (lien `mailto:` avec objet pré-rempli), `README.md`, ce fichier et le dossier de relance.

Un libellé Gmail `Projet / Semaine Claire` a été créé pour organiser le travail en interne. Il ne remplace pas la vérification de réception sur la boîte `semaineclaire@gmail.com`.

À faire avant publication officielle :

1. Envoyer un message de test à `semaineclaire@gmail.com` et vérifier qu’il arrive bien dans la boîte.
2. Ajouter cette adresse dans les mentions légales et la politique de confidentialité définitive.
3. Décider si elle reste l’adresse publique ou si elle sera remplacée par une adresse sur le futur domaine (`contact@<domaine>`).

## 3. Domaine, indexation et SEO

Le site utilise uniquement des chemins relatifs : le dossier peut être copié à la racine d’un nouveau dépôt ou d’un nouveau domaine sans réécrire les liens.

Actuellement :

- `noindex, nofollow` sur toutes les pages : volontaire, pour ne pas indexer un nom de travail ;
- ni URL canonique ni `sitemap.xml`, car le domaine n’est pas choisi ;
- métadonnées Open Graph et Twitter avec images relatives.

À faire après choix du domaine :

1. Ajouter `<link rel="canonical" href="https://<domaine>/...">` à chaque page.
2. Ajouter `og:url` avec l’URL absolue correspondante.
3. Créer `sitemap.xml` et `robots.txt` avec l’URL absolue du sitemap.
4. Retirer `noindex, nofollow`.
5. Vérifier le rendu des aperçus sociaux avec l’image `assets/img/og-image.png`.

## 4. Juridique et public mineur

La page `confidentialite.html` est une page de **transparence**, pas une politique définitive. Aucun éditeur, aucun hébergeur et aucune licence définitive ne sont inventés.

À trancher avant publication :

- statut et nom de l’éditeur ou du pseudonyme ;
- adresse de contact à publier (`semaineclaire@gmail.com`, réception à confirmer par message de test) ;
- hébergeur et traitement réel des journaux techniques ;
- conditions d’utilisation ;
- politique de confidentialité adaptée à un public de collégiens et lycéens ;
- information claire sur le stockage local et son effacement ;
- licence du site, des textes, du PDF et des visuels ;
- crédits et droits des images générées ;
- politique concernant d’éventuels retours par e-mail contenant des données personnelles.

Les pages actuelles évitent délibérément les formulations absolues du type « aucune donnée collectée » : l’hébergement d’un site produit des journaux techniques même lorsque le planner n’envoie aucune donnée de semaine.

## 5. Mesure et validation

Aucun outil d’audience n’est installé. Les indicateurs du dossier de relance sont donc des **hypothèses à mesurer** par entretiens, tests utilisateurs et, plus tard, une mesure agrégée compatible avec la politique de confidentialité.

Si une mesure est ajoutée :

1. mettre à jour la CSP (`connect-src`) ;
2. mettre à jour `confidentialite.html` ;
3. éviter les identifiants persistants et le suivi individuel ;
4. documenter la finalité, la durée de conservation et le mode de désactivation.

## 6. Dernière vérification technique

```bash
cd semaine-claire
npm test
python3 -m venv .venv
.venv/bin/pip install -r outils/requirements.txt
.venv/bin/python outils/generer-kit.py
python3 -m http.server 8000
```

Puis vérifier à la main : ajout de tâches, trois priorités, déplacement, export/import, impression A4, téléchargement PDF, responsive mobile, navigation clavier et suppression des données.

Ne publier officiellement qu’après les points 1 à 4.
