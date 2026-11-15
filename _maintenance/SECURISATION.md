# Bilan de sécurisation

Intervention du 14 novembre 2026, sur demande « publie et sécurise ».

## Corrections appliquées

1. **Pillow 12.1.1 → 13.0.0** dans les dépendances de maintenance. Le nouvel audit PyPI des dépendances déclarées de maintenance et du kit IA, transitives résolues incluses, ne renvoie plus de vulnérabilité connue. L’audit npm des outils de maintenance ne renvoie pas d’alerte non plus. Ce résultat est daté et limité à ces périmètres, pas une garantie générale.
2. **CSP dans les 11 pages HTML publiques** (404 comprise, fichier de validation Google exclu). Par défaut les ressources sont refusées, puis les ressources nécessaires du site sont autorisées. Pas de JavaScript inline exécutable ni d’évaluation dynamique autorisés ; scripts uniquement sur la même origine ; blocs JSON-LD autorisés par empreinte SHA-256 exacte. Les connexions sont limitées à l’origine du site et au compte GoatCounter déjà utilisé. Objets, frames, soumission de formulaires et modification de base URL sont interdits. Les styles inline restent autorisés pour préserver les mises en page existantes, notamment le guide ; ce n’est pas une autorisation de scripts inline.
3. **Politique de référent `no-referrer`** dans ces mêmes pages : ne pas transmettre l’adresse de la page lors des navigations et chargements soumis à cette politique.
4. Le bouton **Imprimer / PDF** du guide utilise désormais un script local externe plutôt qu’un `onclick` inline. Son fonctionnement est testé. Le template canonique a été mis à jour et la génération/synchronisation des guides réapplique les politiques pour ne pas perdre la protection ou conserver des empreintes JSON-LD périmées.
5. Les **actions des trois workflows du dépôt** sont épinglées à des SHA complets vérifiés via l’API GitHub, au lieu de tags majeurs mobiles. La configuration d’exemple livrée dans le kit pédagogique n’a pas été modifiée ; les ZIP et PDF existants restent identiques.
6. La **compilation et les tests du jeu** tournent désormais avec des droits en lecture seule et sans conservation des identifiants Git dans les étapes de checkout. Un job isolé télécharge l’artefact du même workflow et le publie ; lui seul a les droits d’écriture. Il n’installe pas de paquets et n’exécute pas le jeu ou l’EXE. Il vérifie que la fiche de l’artefact correspond encore à l’empreinte du code courant. Si la branche change entre-temps, le push échoue plutôt que rebaser automatiquement un ancien résultat. Cela réduit l’exposition du jeton ; cela ne certifie pas qu’une dépendance de compilation ne peut jamais altérer un binaire.
7. Ajout d’un **audit automatique hebdomadaire** Python/npm, également déclenché lors des modifications des manifestes concernés. Droits en lecture seule ; aucune création de branche ni mise à jour aveugle. Les échecs restent visibles dans Actions et les notifications configurées par le propriétaire. Les dépendances spécifiques de PyInstaller/pygame ne sont pas incluses dans ce nouveau scan ; leurs mises à jour et la confiance dans le binaire restent à suivre séparément.
8. Ajout de tests statiques de sécurité à la CI et de tests navigateur dédiés utilisables en maintenance.

## Vérifications effectuées avant publication

- 4 tests de sécurité statiques ; contrôle de synchronisation des CSP.
- 11 tests du site ; 14 tests d’audience ; 14 tests du code pédagogique sans vrai modèle.
- 4 tests de livraison et 6 tests éditoriaux, y compris les licences attachées, listings et empreintes des PDF et du ZIP.
- Navigateur : 11 pages sans violation CSP en utilisation normale ; menu mobile et impression fonctionnels ; essais locaux d’injection d’un script inline et d’un gestionnaire inline effectivement bloqués par le navigateur.
- Interface : 10 pages × 3 largeurs, images, absence de débordement et d’erreur JavaScript, téléchargements des PDF identiques aux fichiers attendus.
- Audits Python et npm : aucune vulnérabilité connue renvoyée dans les périmètres ci-dessus après mise à jour.
- Test de compatibilité Pillow : ouverture et redimensionnement en mémoire des images PNG/JPEG/WebP du site, décodage de la police locale et rendu d’une page de chacun des deux PDF, sans réexporter les livrables.
- Parsing des trois workflows YAML et validation des actions épinglées. La chaîne Windows est également lancée par GitHub pour valider le découpage compilation/publication.

Un contrôle sans alerte ne prouve ni absence de faille ni absence de compromission passée. Aucune attaque ni test de charge n’a été lancé sur les services publics.

## Entretien

Après modification d’un bloc JSON-LD ou d’un HTML, lancer :

```bash
python3 _maintenance/securiser-pages.py
python3 _maintenance/securiser-pages.py --check
python3 _maintenance/test-securite.py
node _maintenance/test-securite-navigateur.mjs
```

Les appels normaux de `generer-guide-ia.py` et `synchroniser-ia.py` réappliquent les politiques automatiquement. Le fichier de validation Google reste inchangé. Ne pas ajouter `unsafe-inline` ou `unsafe-eval` à `script-src` pour contourner un échec de test : déplacer le code exécutable dans un fichier local et réviser les permissions nécessaires.

Relancer les audits avant chaque changement de dépendances :

```bash
.venv/bin/pip-audit --vulnerability-service pypi -r _maintenance/requirements.txt -r assets/code/assistant-ia/requirements.txt
npm audit --prefix _maintenance
```

Pour consulter le scan récurrent : dépôt → Actions → **Auditer les dépendances**. Les versions épinglées des actions doivent également être entretenues ; le scan pip/npm ne couvre pas les actions GitHub elles-mêmes.

## Ce qui reste à faire par le propriétaire

L’intégration GitHub ne dispose pas des droits administrateur pour certains réglages. Aucun changement de mot de passe, 2FA, session, jeton ou compte Gmail n’a été effectué.

- **Activer une passkey ou la double authentification** sur GitHub et sur la messagerie de récupération ; conserver les codes de secours hors ligne.
- Vérifier les sessions, applications autorisées, jetons personnels et clés de déploiement ; révoquer les accès inutiles.
- Configurer une règle adaptée sur **main** : pas de force-push ni suppression, contrôles requis et PR avant fusion si possible. Attention au job qui range l’EXE : une interdiction complète d’écriture directe nécessitera d’adapter la livraison vers une PR dédiée ; ne pas donner une large exemption à tous les workflows.
- Activer manuellement **Settings → General → Pull Requests → Automatically delete head branches**. Les huit anciennes branches fusionnées sont déjà supprimées ; la branche du cours de français non fusionné reste conservée.
- Garder une sauvegarde indépendante. Maintenir aussi Windows, navigateurs et lecteurs PDF à jour ; une signature et un contrôle antivirus de l’EXE ne sont pas remplacés par ces tests.

## Limites des protections navigateur

La CSP est une balise meta, compatible avec GitHub Pages. Elle ne peut pas fournir `frame-ancestors` : aucune protection anti-encadrement par cet en-tête n’est revendiquée. De même, aucun `X-Content-Type-Options` ou `Permissions-Policy` HTTP personnalisé n’est prétendu ajouté. Il faudrait un hébergement ou une couche serveur permettant ces en-têtes pour compléter ce point. Aucun proxy, outil de suivi, service payant ou domaine supplémentaire n’a été ajouté.

La CSP limite une partie des injections, mais ne protège pas contre un attaquant pouvant modifier le dépôt : celui-ci pourrait aussi modifier la politique. Le contrôle des comptes et des droits de publication reste donc essentiel.
