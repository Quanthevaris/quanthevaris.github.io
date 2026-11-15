# Audit de sécurité et nettoyage des branches

Date de référence : 14 novembre 2026. Code examiné : `10d21ab1086871ec6182f6ae8f33f25a7af0e611`.

> **Audit initial, avant corrections.** Sur demande « publie et sécurise », Pillow a depuis été mis à jour vers 13.0.0 (nouvel audit Python sans alerte), les pages ont reçu une CSP et les workflows ont été renforcés. Le bilan courant, les tests et les limites restantes sont dans [SECURISATION.md](SECURISATION.md). Les constats et mentions de non-publication ci-dessous décrivent l’état initial, pas l’état après cette intervention.

## Verdict en langage simple

**Aucun chemin de compromission évident du site public n’a été identifié dans le périmètre examiné.** Sa surface d’attaque applicative est réduite : GitHub Pages sert des fichiers statiques, sans connexion visiteur, base de données, formulaire de réception ni serveur Python public. Cela ne constitue ni une garantie d’inviolabilité, ni un test d’intrusion complet.

Le scénario le plus préoccupant est la compromission du compte GitHub, d’une autorisation d’application ou de la chaîne de publication : un attaquant disposant du droit d’écrire dans la source publiée pourrait remplacer les pages et les téléchargements. La double authentification, le contrôle des accès et la protection de la branche de publication sont donc prioritaires.

Un problème concret a été identifié dans les **outils de maintenance** : Pillow 12.1.1 comporte des vulnérabilités connues selon l’audit PyPI. Ce paquet n’est pas exécuté par GitHub Pages et aucun téléversement de fichier public ne lui est transmis par le site. L’exposition concerne l’environnement de génération des images/PDF lorsqu’il traite des fichiers ou polices malveillants.

## Périmètre et limites

Examinés : pages HTML à la racine, JavaScript du site, script de mesure d’audience, workflows GitHub Actions, dépendances de maintenance et du kit IA, protections du serveur local du kit IA, métadonnées GitHub Pages et branches distantes.

Méthode : revue du code, parsing HTML, recherche indicative de secrets dans 80 fichiers texte suivis, tests automatisés existants, `npm audit`, `pip-audit` avec la base PyPI et lecture des réglages GitHub accessibles. Les bibliothèques transitives Python ont été résolues au moment de l’audit ; cela ne représente pas nécessairement un ancien environnement de compilation.

Non réalisés : exploitation, scan agressif, test de charge, audit des infrastructures GitHub ou GoatCounter, analyse antivirus ou rétro-ingénierie de l’EXE, vérification de signature Authenticode, audit exhaustif de tous les scripts de génération, recherche exhaustive de secrets dans l’historique, contrôle du poste de l’éditeur ou de sa messagerie, audit des réglages privés Google/GoatCounter, vrai appel à un modèle Ollama.

La récupération directe des en-têtes HTTPS depuis le terminal a échoué dans cet environnement. Leur présence ou absence sur le site publié n’est donc pas établie. Les en-têtes de l’API GitHub ne doivent pas être confondus avec ceux du site. Certaines API administrateur ont répondu 403 : protection classique de branche et activation des alertes de vulnérabilité non confirmées. L’état de la double authentification et les sessions du compte ne sont pas connus.

## Constats positifs vérifiés

- API Pages : site construit, source `main:/`, HTTPS forcé (`https_enforced: true`). Aucun domaine personnalisé n’est configuré dans les éléments examinés.
- Aucun formulaire dans les HTML à la racine ; le contact utilise `mailto:`. Aucun serveur de réception ni base SQL dans l’architecture publique examinée.
- Seuls scripts externes au document dans ces pages : `/js/script.js` et `/js/audience.js`, servis localement. Aucun script JavaScript chargé depuis un CDN dans ces pages. Les blocs JSON-LD ne sont pas du code JavaScript exécutable.
- Pas de mécanisme `eval`, `new Function`, `document.write` ou d’injection `innerHTML` identifié dans les scripts publics examinés. Les interfaces du kit IA et d’ELIZA affichent les conversations avec `textContent`.
- Tous les liens `target="_blank"` des pages à la racine portent `noopener noreferrer`.
- Mesure d’audience : destination HTTPS restreinte à GoatCounter, chemins canoniques autorisés, pas de paramètres de recherche ni fragment transmis, `credentials: omit`, `referrerPolicy: no-referrer`. Aucun chargement du script tiers de GoatCounter.
- Recherche indicative : aucun motif de clé privée, jeton GitHub, clé AWS, clé API Google ou clé OpenAI trouvé dans les 80 fichiers texte suivis contrôlés. Ce n’est pas une preuve d’absence de tout secret, notamment dans l’historique ou les binaires.
- Un seul collaborateur direct renvoyé par l’API : le propriétaire `Quanthevaris`. Cela ne couvre pas les applications autorisées, jetons, clés de déploiement ou sessions.
- Le workflow de vérification a `contents: read` et n’utilise pas `pull_request_target`.
- Le kit IA n’est pas un backend public : écoute sur `127.0.0.1`, débogage désactivé, contrôle Host et Origin, rejet cross-site, taille des requêtes limitée, routes de fichiers explicites, destination Ollama fixe sans proxy ni redirection, limite de réponse et verrou de génération. Des tests vérifient ces comportements sans vrai modèle. Les instructions données au modèle ne sont pas une barrière de sécurité contre les prompt injections.

## Risques et actions classées

### Priorité 1 — Protéger le compte et la publication

**Impact potentiel élevé ; absence de protection non démontrée.** Le site et ses téléchargements dépendent des écritures dans GitHub. Vérifier manuellement :

1. Compte GitHub → Settings → Password and authentication : activer une passkey ou une clé de sécurité/2FA et conserver les codes de secours hors ligne. Protéger aussi la messagerie de récupération.
2. Settings → Sessions / Applications / Developer settings : supprimer sessions, applications, jetons et clés devenus inutiles ; appliquer les permissions minimales.
3. Dépôt → Settings → Rules → Rulesets : protéger `main`, bloquer suppression et force-push et exiger une PR et les contrôles de vérification avant fusion, selon les possibilités du compte. Pour un éditeur seul, une approbation obligatoire par une deuxième personne peut bloquer le travail : adapter la règle plutôt que l’activer aveuglément.
4. Garder une sauvegarde indépendante du code et des publications. Une branche supplémentaire n’est pas à elle seule une sauvegarde contre un compte compromis.

Attention : le workflow de fabrication de l’EXE écrit automatiquement sur sa branche et demande un build Pages. Une règle exigeant une PR pour toute écriture peut bloquer cette automatisation sur `main`. Tester et adapter la livraison (par exemple artefact puis PR dédiée), sans créer une large exemption qui annulerait la protection.

### Priorité 2 — Mettre à jour Pillow dans la maintenance

**Risque pour le poste/CI qui transforme des fichiers non fiables ; pas de point d’entrée distant identifié sur le site public.**

`_maintenance/requirements.txt` fixe `Pillow==12.1.1`. `pip-audit` signale des vulnérabilités dans ce paquet, notamment déni de service par consommation de mémoire, corruption mémoire et problèmes de traitement de formats/polices. Exemples : CVE-2026-40192 et CVE-2026-42311. Certaines corrections proposées sont dans 12.2.0, d’autres dans 12.3.0 ou 13.0.0 selon l’avis.

Action : choisir une version corrigée compatible, refaire l’audit puis les tests de génération et de rendu. Ne pas supposer qu’un simple passage à 12.2.0 corrige tous les avis actuels. En attendant, ne pas traiter d’images, PDF ou polices de provenance inconnue dans ces outils. Les alertes de la base ne démontrent pas une exploitation possible avec les fichiers actuels.

L’outil a renvoyé 77 entrées pour Pillow, dont des doublons et alias (60 identifiants principaux distincts, 37 alias CVE distincts). Ce ne sont pas « 77 failles du site ». Les 22 autres paquets Python résolus n’avaient pas d’avis renvoyé lors de ce contrôle, ce qui n’exclut pas des vulnérabilités inconnues ou hors base.

Aucune dépendance ni aucun PDF n’a été modifié dans cette analyse.

### Priorité 2 — Réduire le risque de chaîne d’approvisionnement CI

Les actions GitHub sont référencées par tags majeurs (`@v7`, `@v6`), pas par SHA complet. Les versions directes pip sont fixées, mais sans verrouillage complet des dépendances transitives ni hashes de distributions. Le job EXE installe et exécute du code de dépendances tout en disposant de `contents: write` et `pages: write`.

Améliorations : épingler les actions à des SHA vérifiés et entretenir ces références, séparer autant que possible compilation et publication avec droits d’écriture, revoir les permissions, et verrouiller/auditer les dépendances. Le fait qu’un job dispose de droits d’écriture est un risque de confiance, pas une preuve de compromission. Aucun workflow `pull_request_target` exécutant le code d’une PR externe n’a été identifié.

### Priorité 3 — Défense en profondeur navigateur

Aucune CSP sous forme de balise meta dans les pages publiques à la racine. Les en-têtes HTTP réellement servis n’ont pas été vérifiés : on ne conclut pas qu’ils sont absents.

À évaluer : politique CSP compatible avec JSON-LD, styles et mesure d’audience, `Referrer-Policy`, `X-Content-Type-Options`, protection contre l’encadrement et permissions navigateur. GitHub Pages ne permet pas de définir arbitrairement tous les en-têtes d’une réponse via un fichier HTML ou un fichier `_headers`. Une CSP meta ne remplace pas un en-tête pour `frame-ancestors`. Ne pas ajouter une fausse protection ou un hébergeur intermédiaire sans nécessité ; l’architecture actuelle limite déjà les entrées non fiables.

### Priorité 3 — Téléchargements et services publics

- L’EXE constitue une chaîne de confiance distincte : sa compilation et ses empreintes ne remplacent pas un antivirus, un audit du binaire ni une signature de l’éditeur. Évaluer signature, traçabilité des versions et publication d’empreintes ; un attaquant pouvant changer à la fois le fichier et son empreinte peut falsifier les deux.
- L’adresse de contact publique peut recevoir spam et hameçonnage. Cela ne permet pas de modifier le site ; ne pas ouvrir aveuglément les pièces jointes reçues.
- L’endpoint de comptage GoatCounter est public par nature et peut recevoir de fausses visites. Ce risque d’intégrité des statistiques n’équivaut pas à un accès au dépôt.
- Le fichier Google de validation est destiné à être public ; ce n’est ni un mot de passe ni une clé API. Le conserver sur le site.
- Le code du dépôt est public : il ne faut jamais y placer des secrets, même dans un fichier ignoré par le sitemap ou interdit par `robots.txt`. Supprimer un fichier du dernier commit ne le retire pas de l’historique.

## Contrôles exécutés

| Contrôle | Résultat |
| --- | --- |
| `python3 _maintenance/test-site.py` | 11 tests réussis |
| `node --test _audience/test-audience.mjs` | 14 tests réussis |
| `.venv/bin/python -m unittest discover -s assets/code/assistant-ia -v` | 14 tests réussis, sans vrai modèle |
| `npm ci --prefix _maintenance --no-fund --no-audit` puis `npm audit --prefix _maintenance --json` | 0 vulnérabilité signalée ; outils Node de maintenance uniquement |
| `.venv/bin/pip-audit --vulnerability-service pypi -r assets/code/assistant-ia/requirements.txt -r _maintenance/requirements.txt --format json` | Alertes Pillow 12.1.1 ; 23 paquets résolus au total |
| Parsing HTML et recherche ciblée de secrets | Constats décrits ci-dessus ; pas un scanner exhaustif |

Les sorties brutes volumineuses d’audit sont temporaires dans `.cache/securite/` (ignoré par Git). Les résultats de bases de vulnérabilités évoluent ; les relancer avant une mise à jour. Un audit sans alerte ne prouve jamais l’absence de faille.

## Nettoyage des branches effectué

Aucune PR ouverte lors du contrôle. Avant chaque suppression, l’API de comparaison a confirmé que le commit de la branche était ancêtre de `main` (`behind_by: 0` dans la comparaison branche…main). Huit anciennes branches entièrement intégrées ont été supprimées sur GitHub :

- `arena/b0a9382c-quanthevaris-github-io`
- `arena/cfe7536e-quanthevaris-github-io`
- `arena/0c8c90ae-quanthevaris-github-io`
- `arena/2a1eae6a-quanthevaris-github-io`
- `arena/8b1ddbf4-quanthevaris-github-io`
- `arena/55b4bd4a-quanthevaris-github-io`
- `arena/145162de-quanthevaris-github-io`
- `arena/244229b1-quanthevaris-github-io`

Branches distantes restantes au dernier contrôle :

- `main`, branche publiée ;
- `arena/2f0940aa-quanthevaris-github-io`, **conservée car non intégrée** : commit `6756b9cd025cb6de54984a5e3c0525b9130417ae`, ajout d’un PDF de français 3e et de trois illustrations. Aucune suppression sans décision de conserver autrement ou d’abandonner ce travail.

La branche active de cette session, `arena/1fbc2c6e-quanthevaris-github-io`, est conservée localement, sans changement de branche. Le rapport n’a pas été poussé ni publié.

L’activation de la suppression automatique des branches fusionnées a été refusée par l’API (403, droit administrateur non accordé). À faire manuellement : dépôt → Settings → General → Pull Requests → **Automatically delete head branches**. Cette option ne supprime pas un travail non fusionné et ne change pas la branche `main`.

## Conclusion

**Pas de signe identifié d’un site « facile à pirater » par ses pages publiques, mais des points de renforcement réels.** Priorités : sécuriser les comptes et la publication, corriger Pillow côté maintenance, puis durcir la chaîne de compilation. Ce rapport n’est pas une certification de sécurité et ne permet pas d’attester l’absence de compromission passée.
