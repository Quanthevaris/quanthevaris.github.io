# Faire vérifier l’indexation du site par Google

## Ce qui a été contrôlé

- Le site public, `robots.txt` et `sitemap.xml` sont accessibles lors de la vérification.
- `robots.txt` autorise l’exploration et déclare le sitemap.
- Le sitemap contient 10 pages publiques, avec des adresses sur `https://quanthevaris.github.io/`.
- Dans les fichiers du dépôt, ces pages ont une URL canonique cohérente et aucune directive `noindex` pour les robots ou Googlebot.
- La page 404 porte volontairement `noindex` et n’est pas dans le sitemap.

Ces vérifications ne donnent pas accès à l’état de l’index Google, à ses décisions de classement, à ses journaux d’exploration ni aux rapports privés Search Console. Elles ne contrôlent pas tous les en-têtes HTTP servis à Googlebot. Une page accessible n’est pas forcément indexée, et une page indexée peut ne pas apparaître en bonne position pour une recherche donnée.

Le commentaire ancien « 8 pages publiques » de `robots.txt` a été retiré. C’était un commentaire sans effet sur les robots, pas un blocage d’indexation.

## Fichier de validation fourni par l’éditeur

Le fichier `google4068430e1e1eeb11.html` est conservé sans modification à la racine du dépôt et doit rester publié à cette adresse :
<https://quanthevaris.github.io/google4068430e1e1eeb11.html>.

Il ne contient ni script ni mesure d’audience. Ce fichier public prouve le contrôle du site à Google ; il n’effectue pas lui-même la validation dans Search Console et ne garantit pas l’indexation. L’éditeur doit cliquer sur **Valider** après sa mise en ligne. Ne pas le supprimer une fois la propriété validée.

## Étapes à faire dans Google Search Console

1. Ouvre <https://search.google.com/search-console> avec ton compte Google.
2. Si elle n’existe pas déjà, ajoute une propriété **Préfixe de l’URL** avec exactement `https://quanthevaris.github.io/`. N’utilise pas la propriété Domaine pour `github.io` : ce domaine appartient à GitHub et tu n’en contrôles pas les DNS.
3. Valide la propriété avec le **fichier HTML** ou la **balise HTML** que Google fournit. Le fichier doit être publié à la racine du site, ou la balise placée dans le `<head>` de l’accueil. Si une intervention sur le dépôt est nécessaire, transmets seulement ce fichier de vérification public ou la balise fournie, jamais ton mot de passe ni un jeton d’accès. Conserve la preuve de validation sur le site après validation.
4. Dans **Sitemaps**, envoie `https://quanthevaris.github.io/sitemap.xml`.
5. Dans **Inspection de l’URL**, inspecte `https://quanthevaris.github.io/` (sans paramètre `?v=...`). Lis le statut d’indexation et le motif si la page n’est pas indexée.
6. Utilise **Tester l’URL publiée** si nécessaire, puis **Demander une indexation** si l’outil le permet. Fais de même pour les fiches des deux guides et la page du jeu, sans multiplier les demandes pour la même URL.
7. Consulte ensuite le rapport **Indexation des pages**. Si Google signale une exclusion, une erreur ou une autre URL canonique, transmets le libellé exact pour que la correction corresponde au diagnostic réel.

Google indique que l’exploration peut prendre de quelques jours à quelques semaines. Envoyer un sitemap ou demander une indexation ne garantit ni inclusion ni position, et répéter une demande ne l’accélère pas. Search Console est gratuit et utile au diagnostic, mais l’inscription n’est pas obligatoire pour apparaître dans Google.

## Pour aider les visiteurs à trouver le site

- Garde le nom Quanthevaris cohérent dans les titres et les profils publics.
- Ajoute un lien vers le site depuis tes profils ou pages publiques pertinents, sans acheter de liens ni en publier en masse.
- Continue à publier des pages utiles, accessibles par les liens internes. Les titres, descriptions et données structurées ne remplacent pas l’indexation.
- La recherche `site:quanthevaris.github.io` donne une indication, pas une liste complète ni un diagnostic certain. L’inspection d’URL dans Search Console est plus utile pour une page précise.

Aucun outil Google Analytics, script tiers ou collecte supplémentaire n’a été ajouté au site pour cette vérification.

## Documentation officielle

- Search Console : <https://support.google.com/webmasters/answer/9128668?hl=fr>.
- Demander une nouvelle exploration : <https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl?hl=fr>.
- Inspection d’URL : <https://support.google.com/webmasters/answer/9012289?hl=fr>.
