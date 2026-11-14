# Suite de l’audit du 14 novembre 2026 — état final de travail

## Évolution de la correction

1. Mesure immédiate : l’ancienne édition avait été signalée comme obsolète, avec des
   avertissements HTML/PDF, après confirmation du retrait de GitHub Models.
2. À la demande de l’éditeur : **réécriture complète de l’édition locale 2.0** autour
   de Flask et de l’API native Ollama, avec un kit de sources unique et une nouvelle
   génération HTML/PDF. Les anciens bandeaux d’archive ne décrivent plus les fichiers
   livrés : ils ont été remplacés par l’explication du nouveau parcours et de ses limites.

Le PDF joint par l’éditeur (49 pages) a été consulté. Sa structure ELIZA → assistant
moderne est conservée ; les instructions dépendantes du service retiré ne sont pas
présentées comme fonctionnelles dans la nouvelle édition. L’ancien contenu reste
accessible dans l’historique du dépôt, pas dans le parcours principal à télécharger.

## P0 — Migration du guide

- [x] Reconfirmer le retrait de GitHub Models dans son annonce et sa documentation.
- [x] Choisir Ollama et un tag local explicite `llama3.2:1b`, dont la documentation,
  l’API, les conditions locales, la taille et les licences ont été consultées.
- [x] Réécrire installation, configuration, architecture, serveur, interface,
  personnalisation, publication, dépannage, glossaire et mentions du guide.
- [x] Conserver GitHub pour le versionnement, les tests et une démo ELIZA statique,
  sans promettre d’inférence ou de serveur Python sur GitHub Pages.
- [x] Supprimer du parcours les jetons d’inférence, anciennes URL et dépendances
  OpenAI/CORS/dotenv. Aucun secret n’est requis dans la nouvelle architecture.
- [x] Fournir les fichiers réels dans un ZIP, avec README, licence, tests et
  `verifier_installation.py` pour l’inférence réelle chez le lecteur.
- [x] Corriger les tests ELIZA pour maîtriser l’aléatoire et isoler la mémoire.
- [x] Ajouter validation des entrées, limites de taille, host/origin, absence de CORS,
  boucle locale, erreurs propres, rendu texte brut, absence de stockage des discussions.
- [x] Tester le programme dans un environnement Python neuf sans anciennes dépendances.
- [x] Tester la chaîne HTTP et l’interface avec un **faux moteur Ollama** : protocole
  natif, six échanges au maximum, échec de modèle absent, réinitialisation, absence
  de scripts externes, absence de stockage et rendu non exécutable des réponses.
- [x] Régénérer les deux PDF identiques avec une pagination mesurée, et synchroniser
  tous les listings, le ZIP, les images et les métadonnées publiques.
- [ ] **Valider l’installation d’Ollama, le téléchargement des poids, une véritable
  inférence et la qualité/vitesse sur un ordinateur réel compatible.** Les poids
  ne sont pas téléchargés dans cet environnement. Aucun test simulé n’est présenté
  comme cette validation réelle. Procédure : `POUR-TOI-ETAPES.md`, étapes 2 à 6.
- [ ] Relecture éditoriale et décision de diffusion par l’éditeur, puis publication.

Le site et le PDF indiquent explicitement la portée des tests. La version locale est
livrée pour être essayée, pas certifiée compatible avec tous les matériels.

## P1 — Cohérence et transparence

- [x] Clarifier l’accueil : pas de compte ni de publicité, mais audience agrégée et
  journaux GitHub Pages, notamment les adresses IP ; pas de promesse « zéro donnée ».
- [x] Distinguer la lecture d’un PDF hors ligne du fonctionnement des programmes.
- [x] Corriger « aucune donnée collectée » dans les métadonnées de contact.
- [x] Harmoniser accueil, catalogue, fiche, contact, mentions et confidentialité avec
  le nouveau parcours local et les traitements propres aux téléchargements.
- [x] Ne pas présenter « sans cookie » ou l’intérêt légitime RGPD comme une preuve
  automatique d’exemption de consentement ou une certification CNIL.
- [x] Vérifier le script local d’audience et ses tests : chemins canoniques limités,
  pas de stockage navigateur, DNT/GPC, requête sans cookies/provenance. Aucune extension
  de la collecte n’est ajoutée ; les pages IA restent exclues du comptage existant.
- [ ] Vérifier dans le compte privé GoatCounter les réglages réels : Sessions seul,
  autres dimensions désactivées, tableau privé, conservation 365 jours. Le dépôt
  contient une confirmation antérieure de l’éditeur, pas un accès utilisé ici au compte.
- [ ] Documenter les garanties fournisseur et réexaminer l’éventuelle exemption CNIL.
  Si elle ne peut pas être justifiée, désactiver la mesure ou recueillir un consentement
  préalable valable. Aucun réglage de compte ou contact fournisseur n’est exécuté ici.

## P2 — Présentation

- [x] Mettre en avant l’édition locale, son public, son kit et ses prérequis.
- [x] Remplacer l’image d’accueil par une illustration 3D légère, distincte d’une capture.
- [x] Mettre à jour les aperçus de Pixel et l’image de partage avec la vraie nouvelle
  interface au repos ; le diagnostic montré est explicitement simulé.
- [x] Conserver les anciens chemins PDF et les ancres de fiche utilisées précédemment.

## Reproduire les contrôles

Voir README à la racine pour l’ordre de génération HTML → ZIP → PDF → synchronisation.

- `python3 _maintenance/test-site.py` : liens, ancres, métadonnées, compteurs et transparence.
- `node --test _audience/test-audience.mjs` : comptage et exclusions existantes.
- `.venv/bin/python -m unittest discover -s assets/code/assistant-ia -v` : code des projets.
- `.venv/bin/python _maintenance/test-parcours-ia.py` : serveur HTTP + navigateur + faux Ollama.
- `.venv/bin/python _maintenance/test-livraison-ia.py` : PDF, ZIP, empreintes, listings identiques.
- `node --check js/audience.js`, `node --check js/script.js`, `git diff --check`.

### Résultats de la livraison du 14 novembre

- 14 tests du kit réussis dans un environnement Python neuf, puis depuis le ZIP
  décompressé dans un dossier neuf (seules les dépendances déclarées installées).
- 7 tests statiques, 14 tests d’audience et 4 tests de livraison réussis.
- PDF et captures remplacés aux chemins historiques ; les liens publics portent
  une empreinte de contenu pour éviter le réemploi des anciennes versions en cache.
  Le navigateur a chargé le nouvel aperçu sur les trois pages et vérifié que le
  bouton de téléchargement renvoie exactement les octets du nouveau PDF.
- Test HTTP + navigateur réussi : 9 appels au moteur **simulé**, dont un échec attendu.
- Accueil, catalogue, fiche IA et guide HTML vérifiés à 390, 768 et 1327 pixels :
  pas de débordement horizontal, d’image cassée après chargement ni d’erreur JavaScript.
- PDF : 49 pages, copies identiques, signets imbriqués présents, aucune page vide,
  aucun texte hors des marges contrôlées ; couverture, prérequis, lancement et une
  page d’annexe inspectés visuellement. Image Open Graph et fiche mobile inspectées.
- Sans Ollama installé, le vérificateur réel échoue explicitement : aucun rapport
  de réussite artificiel n’est produit.
- Workflow `verifier-site.yml` ajouté pour les tests hors navigateur ; son exécution
  distante reste à confirmer après publication de la branche.

Ces tests ne valident ni une véritable inférence dans cet environnement, ni les réglages
privés de GoatCounter, ni une conformité juridique ou un audit de sécurité exhaustif.

## Sources relues

- GitHub Models : <https://docs.github.com/en/github-models> et
  <https://github.blog/changelog/2026-07-30-github-models-is-now-retired/>.
- Ollama : <https://docs.ollama.com/api/chat>, <https://docs.ollama.com/api/tags>,
  <https://docs.ollama.com/faq>, <https://docs.ollama.com/windows>,
  <https://docs.ollama.com/macos>, <https://ollama.com/library/llama3.2:1b>.
- GitHub Pages / journaux IP :
  <https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages#data-collection>.
- GoatCounter : <https://www.goatcounter.com/help/privacy>.
- CNIL : <https://www.cnil.fr/fr/cookies-solutions-pour-les-outils-de-mesure-daudience>.

## Publication

Travail préparé sur la branche de cette session, sans intégration ni déploiement exécutés.
Les étapes restantes sont expliquées dans `POUR-TOI-ETAPES.md`, y compris contrôle public
après GitHub Pages et vérification privée de GoatCounter. Le jeu FISSION ARENA, ses binaires
et ses conditions ne sont pas modifiés par la migration du guide.
