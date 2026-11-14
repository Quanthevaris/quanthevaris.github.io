# Analyse de la mesure d'audience — 14 novembre 2026

Document de travail de l'éditeur, non publié par GitHub Pages. Il documente le choix de
configuration ; ce n'est ni une certification CNIL ni une consultation juridique personnalisée.

## Périmètre et configuration

- Site : `https://quanthevaris.github.io/`, hébergé par GitHub Pages.
- Prestataire : GoatCounter.com, code `quanthevaris`.
- Responsable : l'éditeur du site, contact `contact.quanthevaris@gmail.com`.
- Finalité : fréquentation et pages consultées, pour le seul éditeur ; pas de publicité,
  prospection, test A/B, profilage, mesure des clics ou des téléchargements.
- Réglages confirmés par l'éditeur le 14 novembre 2026 : Sessions seul parmi les options de
  collecte ; pas de pages vues individuelles, provenance, navigateur/système, pays, région,
  langue ou taille d'écran ; conservation 365 jours ; tableau de bord privé.
- Code client : `js/audience.js`, chemin canonique issu d'une liste fermée, un POST sans corps,
  `credentials: omit`, `referrerPolicy: no-referrer`, pas de stockage navigateur.
- Exclusions : DNT/GPC, iframes, aperçus/localhost, fichiers locaux, pages non visibles,
  chemins inconnus et 404. Pas de repli destiné à contourner un blocage.

Les réglages du compte sont déclarés par l'éditeur, pas lus par le code à distance. Toute évolution
doit déclencher une revue de cette analyse et de la politique publique.

## Données et durée

Le script ne fournit que le chemin de page comme paramètre. Le transport HTTP implique néanmoins
IP, user-agent et métadonnées réseau. L'IP et le user-agent sont des données à caractère personnel
lorsqu'ils permettent d'individualiser une connexion ; les dire « non stockés dans les statistiques »
ne revient pas à dire « jamais traités ». La politique publique emploie donc « statistiques
agrégées », pas une promesse absolue de « zéro donnée » ou d'anonymisation juridique inconditionnelle.

D'après la documentation GoatCounter, la correspondance site + IP + user-agent servant aux sessions
reste en mémoire jusqu'à huit heures ; les valeurs brutes ne sont pas conservées dans la base de
statistiques. Avec l'option Individual pageviews désactivée, les résultats conservés sont des
comptages séparés par page/période. Le réglage de conservation du compte est fixé à 365 jours.
Les journaux de sécurité de GitHub Pages constituent un traitement distinct, non maîtrisé par
l'éditeur.

## Base légale et article 82

Base envisagée : intérêt légitime de l'éditeur (article 6, 1, f, RGPD) à connaître la fréquentation
d'un site gratuit, avec collecte minimale, absence de publicité et de recoupement, information
claire et opposition. Les attentes des visiteurs sont prises en compte par la limitation des
données, le respect des signaux de confidentialité et l'absence d'identifiant persistant.

Pour l'article 82 de la loi Informatique et Libertés, vérifier les garanties suivantes :

| Garantie CNIL | Mise en œuvre / limite |
| --- | --- |
| Finalité limitée à l'audience, pour le compte exclusif de l'éditeur | Comptages de pages uniquement ; tableau privé ; pas de réutilisation publicitaire ou autre traitement. |
| Statistiques anonymes, pas de suivi individuel | Agrégats, pas de lignes de visites individuelles ; IP/UA seulement temporairement traités pour les sessions. Ne pas assimiler automatiquement pseudonymisation et anonymisation. |
| Pas de suivi global sur plusieurs sites/applications | Aucun cookie ou identifiant persistant ; pas de recoupement intersites ; session propre au code de site. |
| Pas de recoupement ou transmission à des tiers au-delà du prestataire | Pas de croisement avec emails, GitHub ou autre outil ; prestataire limité au service d'audience, qui indique ne pas partager les informations avec d'autres tiers. |
| Information et opposition | Section Audience de la politique, mentions et pieds de page ; DNT/GPC et contact éditeur. |
| Durée limitée et réexamen | 365 jours, inférieur à la recommandation de 25 mois ; réexamen au moins annuel et à chaque changement. |

Le fournisseur n'a pas remis à l'éditeur, à cette date, une auto-évaluation CNIL signée ou une
« certification ». L'absence de cookie ne suffit pas à établir l'exemption. L'éditeur doit pouvoir
justifier l'analyse ci-dessus à partir de la configuration réelle et des engagements du prestataire.
Si cette justification ne peut plus être maintenue, mettre en place un consentement préalable
valable ou désactiver la mesure.

## Sources officielles consultées

- GoatCounter, politique de confidentialité (version indiquée : 8 juin 2025) :
  <https://www.goatcounter.com/help/privacy> — agrégats, options de collecte, session en mémoire,
  hébergement Finlande/Allemagne, exploitant en Irlande, suppression du compte et sauvegardes.
- GoatCounter, sessions : <https://www.goatcounter.com/help/sessions> — fenêtre de huit heures,
  IP/UA non enregistrés dans la base, comportement des rechargements.
- GoatCounter, consentement : <https://www.goatcounter.com/help/gdpr> — position de l'auteur,
  formulée avec réserve ; ne remplace pas l'analyse du responsable.
- CNIL, mesure d'audience (4 juillet 2025) :
  <https://www.cnil.fr/fr/cookies-solutions-pour-les-outils-de-mesure-daudience> — conditions
  d'exemption, information, durées recommandées, absence de certification automatique.
- CNIL, FAQ cookies :
  <https://www.cnil.fr/fr/cookies-et-autres-traceurs/regles/cookies/FAQ> — démonstration des
  garanties et mécanisme d'opposition.
- GitHub Pages :
  <https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages#data-collection>
  — journalisation des IP par l'hébergeur.

## Vérifications techniques

Commandes sans dépendance :

```bash
node --check js/audience.js
node --test _audience/test-audience.mjs
git diff --check
```

Les tests simulent le navigateur et n'envoient aucune visite réelle au compte. Ils vérifient
notamment l'endpoint, les chemins autorisés, l'absence de paramètres privés, l'absence d'accès au
stockage, DNT/GPC, les environnements exclus, les erreurs réseau et la cohérence des pages publiques.
Après déploiement, effectuer une visite réelle de contrôle et vérifier le tableau de bord ; une
requête partie du navigateur ne suffit pas à prouver son enregistrement côté prestataire.

## Réexamen

À réexaminer au plus tard le 14 novembre 2027, et immédiatement en cas de changement de
prestataire, domaine, réglages, script, finalité, durée, partage des données ou doctrine CNIL.
Conserver une version datée de cette analyse lors de chaque changement.
