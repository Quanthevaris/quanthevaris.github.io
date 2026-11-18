# Dossier de relance — Semaine Claire

**Décisions retenues avec l’utilisateur** : cible collégiens/lycéens, produit entièrement gratuit, MVP complet, identité blanc et bleu scolaire, nouveau site autonome sans marque Quanthevaris. Cause principale de l’échec identifiée : **pas assez désirable**. Adresse de contact fournie : `semaineclaire@gmail.com` (réception à vérifier par message de test). Pseudonyme et juridique restent à régler avant publication officielle.

**Statut** : prototype complet et testable. « Semaine Claire » est un nom de travail. Voir [`../A-FINALISER.md`](../A-FINALISER.md).

---

## 1. Résumé de la reprise

L’ancien produit était un PDF de 15 pages : propre dans l’intention, mais interchangeable avec n’importe quel agenda gratuit. Il ne disait pas à qui il s’adressait, quelle décision il aidait à prendre, ni pourquoi on devait l’utiliser plutôt qu’une feuille blanche.

La version reconstruite part d’un seul moment : **le dimanche, quand plusieurs devoirs, contrôles et projets arrivent en même temps**. Elle ne vend pas « plus d’organisation » ; elle aide à produire une décision en dix minutes : quoi faire en premier, quand le faire, et quoi regarder en fin de semaine.

Le produit n’est plus un document isolé. C’est un ensemble cohérent :

1. une page d’atterrissage qui clarifie le problème et la méthode ;
2. un planner web local, sans compte ;
3. un PDF A4 de 8 pages, refait de zéro ;
4. une page de transparence sur les données ;
5. une page de contact de travail ;
6. un plan de lancement, une copy pack et des indicateurs de validation.

---

## 2. Positionnement

### Cible prioritaire

**Collégiens et lycéens**, environ 11–18 ans, qui ont plusieurs matières, des devoirs à dates différentes et une impression de « trop de choses à retenir ». Ils n’ont pas besoin d’un outil de productivité professionnel, ni d’un système de gamification, ni d’un discours culpabilisant.

**Prescripteurs secondaires** : parents, professeurs, documentalistes, associations de parents d’élèves. Ils peuvent faire découvrir le produit, mais le copy principal parle à l’élève, pas à l’adulte qui achèterait à sa place.

### Job to be done

> « Quand je rentre le dimanche avec plusieurs devoirs et contrôles, je veux savoir quoi faire en premier et quand le faire, sans avoir à tenir un système compliqué. »

### Promesse

> **10 minutes le dimanche. Une semaine de devoirs enfin lisible.**

Cette promesse est volontairement plus étroite que « réussir son année scolaire » ou « ne plus jamais oublier ». Elle est située dans le temps, actionnable et vérifiable par l’utilisateur dès la première semaine.

### Mécanisme différenciant : les quatre gestes

| Geste | Décision produite | Traduction dans le produit |
| --- | --- | --- |
| **Vider** | Tout ce qui occupe la tête est écrit | Formulaire simple : tâche, matière, date, durée, priorité, jour |
| **Choisir** | Trois priorités maximum | Sélection automatique ou manuelle, limite stricte à 3 |
| **Placer** | Chaque tâche reçoit un jour | Planning 7 colonnes, déplacement sans ressaisie |
| **Vérifier** | Ce qui est fait et ce qui change | Cases, progression, bilan court, archivage de semaine |

Le mécanisme est la vraie réponse à « pas assez désirable » : on n’achète pas quinze grilles, on adopte une décision répétable.

### Anti-promesses

Pour rester crédible auprès d’un public scolaire, le produit refuse explicitement :

- « De meilleures notes garanties » ;
- « Zéro oubli » ;
- les streaks, classements et notifications culpabilisantes ;
- les tableaux de bord complexes ;
- les faux témoignages et les chiffres d’usage inventés ;
- l’idée qu’il faut utiliser l’outil tous les jours pour que ça marche.

### Ton

Direct, calme, non infantilisant. On dit « tu », on évite le jargon entrepreneur, on reconnaît que certaines semaines ne se passent pas comme prévu. La phrase « Une petite amélioration chaque semaine » remplace la logique de performance.

### Identité visuelle

Blanc dominant, bleu `#135BEA`, marine `#10233F`, lignes fines, beaucoup d’espace, géométrie de carnet. Le bleu scolaire de l’ancien visuel est conservé comme signal ; les filets roses, les grilles noires et les cases cassées sont supprimés.

---

## 3. Offre et parcours

### Offre

Produit **gratuit**, sans compte, sans paiement, sans version premium.

L’absence de transaction est un choix stratégique ici : elle supprime la friction, évite de construire un tunnel de paiement factice et permet de valider d’abord l’usage. Le « prix » demandé est un rituel de dix minutes, pas une carte bancaire.

### Objets livrés

| Objet | Valeur perçue | Preuve visible |
| --- | --- | --- |
| Planner web | « Je vois ma semaine sans créer de compte » | Aperçu, bouton d’essai, exemple chargeable |
| Kit PDF | « Je peux l’imprimer ou le remplir sur ordinateur » | Aperçu 3 pages, 8 pages A4, champs remplissables |
| Méthode | « Je sais par où commencer » | Quatre gestes, trois priorités maximum |
| Transparence | « Je ne confie pas mes devoirs à un serveur » | CSP stricte, stockage local, page dédiée |

### Parcours d’activation

1. L’utilisateur arrive sur la page d’accueil et comprend le moment d’usage en une phrase.
2. Il voit la méthode en quatre gestes, puis un aperçu du planner.
3. Il clique sur **« Commencer ma semaine »**.
4. Dans le planner, il ajoute un premier devoir, ou charge l’exemple.
5. Il sélectionne trois priorités, déplace une tâche, coche une case.
6. Il imprime sa feuille ou télécharge le kit PDF.
7. En fin de semaine, il remplit un bilan court et lance une nouvelle semaine.

**Événement d’activation retenu** : au moins trois tâches ajoutées et une priorité sélectionnée. Ce n’est pas une mesure déjà collectée ; c’est la définition à utiliser lors des tests.

### CTA principal

Partout : **« Commencer ma semaine »** ou **« Ouvrir le planner »**.

CTA secondaire : **« Télécharger le kit A4 »**.

Aucun CTA vers une liste d’attente, un paiement ou une inscription : ils seraient incohérents avec le modèle gratuit et l’absence de backend.

---

## 4. Copy pack

### Accroches courtes

1. « Un agenda vierge ne dit pas quoi faire en premier. »
2. « 10 minutes le dimanche. Une semaine de devoirs enfin lisible. »
3. « Trois priorités. Sept jours. Zéro compte à créer. »

### Hero principal

> **10 minutes le dimanche. Une semaine de devoirs enfin lisible.**
>
> Semaine Claire transforme la pile de devoirs, de contrôles et de projets en un plan simple. Tu vides ta tête, tu choisis l’essentiel, tu places chaque tâche et tu vois ce qu’il reste. Rien à installer, aucun compte à créer.

### Section problème

> 15 pages ne suffisent pas à décider quoi faire en premier.
>
> Un agenda vierge demande déjà de savoir s’organiser. Le vrai blocage n’est pas le manque de cases : c’est la charge mentale, la priorité floue et le devoir découvert la veille au soir. On a donc repris le produit à l’envers : d’abord la décision, ensuite la page.

### Publications courtes

**Post 1 — diagnostic**

> Ton problème n’est pas d’avoir trop de cases à remplir. C’est de ne pas savoir laquelle regarder en premier. On a reconstruit un kit de rentrée autour d’une seule question : quelles sont mes trois priorités de la semaine ? Gratuit, sans compte.

**Post 2 — démonstration**

> Vider. Choisir. Placer. Vérifier. Quatre gestes, dix minutes le dimanche. Le planner garde tes devoirs dans le navigateur, imprime une feuille A4 propre et ne t’envoie aucune notification.

**Post 3 — papier**

> Le PDF fait 8 pages, pas 15. Chaque page correspond à une décision : inventaire, priorités, semaine, vérification, révisions, routine, bilan, relance. Remplissable à l’écran ou après impression.

### Message de test à cinq élèves

> Objet : 10 minutes pour tester un planner de devoirs
>
> Bonjour, je teste une version gratuite d’un organisateur de semaine pour collégiens/lycéens. L’objectif n’est pas de juger tes notes ni ton organisation : je veux voir si l’outil t’aide à répondre à une seule question — « qu’est-ce que je fais en premier ? ».
>
> Essaie pendant une semaine, avec trois devoirs seulement. Dis-moi précisément le moment où tu as hésité, et une chose que tu supprimerais. Pas besoin d’envoyer tes vrais devoirs ni des informations personnelles.
>
> Merci.

### Objections et réponses

| Objection | Réponse |
| --- | --- |
| « Encore un planner ? » | Ce n’est pas une collection de grilles : une méthode en quatre gestes et une limite de trois priorités. |
| « Je vais oublier de l’ouvrir. » | Le rituel est fait une fois, puis la feuille imprimée suffit. L’outil ne demande pas d’usage quotidien. |
| « Mes données vont où ? » | Dans le navigateur, sans compte ni API distante. La page de transparence détaille aussi les limites liées à l’hébergement. |
| « Pourquoi gratuit ? » | Pour supprimer toute friction et valider l’usage avant d’envisager un modèle économique. Aucune version cachée. |
| « Le nom est définitif ? » | Non. C’est un nom de travail, clairement indiqué, en attendant le pseudonyme et le juridique. |

---

## 5. Plan de lancement sur 7 jours

Il s’agit d’un **plan de validation**, pas d’une campagne de croissance. Aucun trafic n’est supposé.

| Jour | Objectif | Action | Sortie attendue |
| --- | --- | --- | --- |
| J1 | Confronter au réel | 5 entretiens courts avec des collégiens/lycéens ; faire ajouter 3 devoirs sans aide | Liste des hésitations, verbatims |
| J2 | Corriger l’activation | Ajuster les libellés, l’ordre des champs et l’exemple si le premier ajout bloque | Planner modifié, tests rejoués |
| J3 | Fixer l’identité | Choisir pseudonyme, domaine, adresse de contact, statut de l’éditeur | `A-FINALISER.md` soldé |
| J4 | Sécuriser la publication | Rédiger mentions légales, confidentialité définitive, conditions, licence ; vérifier l’hébergeur | Pages juridiques prêtes |
| J5 | Préparer la distribution | 3 visuels courts, 3 posts, 1 message de test, 1 fiche pour parents/enseignants | Copy pack validé |
| J6 | Contrôle technique | Tests Node, PDF, responsive, clavier, impression, liens, aperçus sociaux | Checklist verte |
| J7 | Publication douce | Retirer `noindex`, publier sur le domaine, envoyer à 20 testeurs, demander un seul retour | Premiers usages qualitatifs |

### J+7 : décision

Trois issues possibles, à trancher sur des observations et non sur l’enthousiasme :

1. **Continuer** : les testeurs ajoutent trois tâches sans aide et comprennent les quatre gestes.
2. **Réduire encore** : le planner reste trop présent ; garder surtout le PDF et la méthode.
3. **Changer de cible** : les parents s’approprient mieux l’outil que les élèves ; réécrire le copy autour du foyer, sans prétendre que c’était la cible initiale.

---

## 6. Indicateurs

Aucun outil d’audience n’est installé dans le prototype. Les indicateurs ci-dessous sont donc soit **observables en test utilisateur**, soit à instrumenter plus tard avec une mesure respectueuse de la vie privée.

| Indicateur | Définition | Méthode actuelle | Seuil hypothétique |
| --- | --- | --- | --- |
| Compréhension de la promesse | La personne reformule le rituel sans aide | Entretien J1 | 4/5 personnes |
| Temps jusqu’à la première tâche | Durée entre l’ouverture du planner et le premier ajout | Observation chronométrée | < 60 s |
| Activation | 3 tâches ajoutées + 1 priorité choisie | Observation ou mesure locale déclarée | 60 % des testeurs |
| Usage du tri | Au moins une tâche déplacée ou une priorité retirée | Observation | 50 % des testeurs |
| Sortie papier | Impression ou téléchargement du PDF | Observation / compte de fichier servi plus tard | 30 % des testeurs |
| Retour semaine suivante | La personne sait expliquer comment relancer le rituel | Entretien J+7 | 3/5 personnes |
| Friction dominante | Moment précis d’hésitation le plus fréquent | Verbatims | 1 friction claire à corriger |

Ces seuils sont des **hypothèses de travail**, pas des résultats. Ils doivent être remplacés par des observations réelles avant toute communication chiffrée.

---

## 7. Canaux prioritaires

Ordre recommandé, du plus qualitatif au plus large :

1. **Tests directs** : 5 élèves, puis 20 testeurs. Le plus utile au début.
2. **Prescripteurs de proximité** : parents, enseignants, documentalistes, associations de parents d’élèves, avec une fiche d’une page.
3. **Démonstrations courtes** : 20 secondes d’écran montrant « trois devoirs → trois priorités → une semaine placée ».
4. **Recherche naturelle** : pages méthode, FAQ et kit PDF une fois le domaine définitif et indexable.
5. **Partage du PDF** : le fichier peut circuler seul ; sa dernière page renvoie à la méthode numérique sans exiger un lien tracké.

À éviter au lancement : publicité payante, partenariats massifs, promesse de notes, collecte d’e-mails sans finalité claire.

---

## 8. Risques et arbitrages

| Risque | Pourquoi c’est risqué | Arbitrage actuel |
| --- | --- | --- |
| Catégorie saturée | Les planners gratuits sont partout | Promesse étroite + mécanisme en 4 gestes, pas « encore un agenda » |
| Public mineur | Données, consentement, ton | Aucun compte, aucune API de semaine, transparence explicite, juridique à finaliser |
| Stockage local | Données perdues si le navigateur est nettoyé | Export JSON, PDF autonome, avertissement si `localStorage` indisponible |
| Nom provisoire | Crédibilité et mémorisation | `noindex`, mention visible, liste exacte des remplacements |
| Absence de backend | Pas de mesure, pas de contact automatique | Mesure qualitative d’abord, page contact sans lien tant qu’aucune adresse vérifiée n’existe, aucun faux formulaire |
| Outil trop ambitieux | L’élève abandonne | Pas de drag-and-drop, pas de comptes, pas de gamification, 3 priorités max |
| PDF trop long | Pages redondantes | 8 pages, chacune liée à une décision |
| Juridique incomplet | Publication prématurée | Pages en `noindex` et avertissement explicite |

---

## 9. Ce qui a été appliqué dans le code

- Site autonome avec chemins relatifs, sans CSS/JS du dépôt hôte.
- CSP stricte : aucune connexion sortante, aucun script inline, aucun gestionnaire `on*`, aucun style inline.
- Polices Inter auto-hébergées avec licence OFL.
- Images optimisées : hero WebP + JPEG, aperçu PDF WebP, image OG, favicons.
- Planner en modules ES : logique métier séparée du DOM, tests Node sans dépendance.
- `localStorage`, export/import JSON, impression A4, archivage de semaine.
- PDF généré par script reproductible, avec 155 champs et cases remplissables.
- Aucun script tiers, aucun cookie applicatif, aucun traceur publicitaire.
- Pages `noindex` tant que l’identité définitive n’est pas fixée.

---

## 10. Prochaines décisions

1. Valider le pseudonyme et le domaine.
2. Envoyer un message de test à `semaineclaire@gmail.com`, vérifier sa réception, puis décider si cette adresse reste publique ou sera remplacée par une adresse sur le futur domaine.
3. Finaliser le juridique avant de retirer `noindex`.
4. Tester avec cinq élèves, puis corriger une seule friction dominante.
5. Décider, à J+7, si le produit doit rester gratuit comme outil d’audience ou devenir une offre plus large.

La reprise est volontairement terminée à un stade **démontrable et honnête** : tout est utilisable, rien n’est présenté comme déjà validé par le marché.
