# Mesure d'audience GoatCounter — mode d'emploi

## État de cette version

Le compte `quanthevaris` a été créé et ses réglages minimaux ont été confirmés par l'éditeur.
Le code est maintenant relié à :

```text
https://quanthevaris.goatcounter.com/count
```

**L'activation est effective sur le site public après déploiement de cette version sur `main`.**
GitHub Pages publie ce dépôt depuis la racine de `main`. Un commit sur la branche de travail ou
un aperçu technique ne suffit pas à mettre le comptage en ligne.

La promesse tenue est : **pas de cookie, pas de stockage navigateur, pas de profil individuel,
des statistiques agrégées**. Ce n'est pas « zéro donnée traitée » : toute requête transmet une IP
et un user-agent ; GoatCounter les utilise temporairement pour regrouper les visites. GitHub
Pages conserve par ailleurs ses propres journaux de sécurité. Voir l'analyse dans
[`ANALYSE-CONFIDENTIALITE.md`](ANALYSE-CONFIDENTIALITE.md).

## 1. Réglages du compte — confirmés par l'éditeur

Dans <https://quanthevaris.goatcounter.com/settings/main> :

- **Your site** : `quanthevaris.github.io` ;
- **Dashboard viewable by** : **Only logged in users** ;
- **Allow adding visitor counts on your website** : décoché ;
- **Data retention in days** : `365` ;
- **Data collection** : **Sessions** uniquement ;
- décochés : **Individual pageviews**, **Referrer**, **User-Agent**, **Size**, **Country**,
  **Region**, **Language**.

**Ignore IPs** est une exclusion optionnelle de l'éditeur, distincte de la collecte des visiteurs.
Ne pas publier une capture contenant des informations privées. Aucun mot de passe, jeton d'API
ou secret de tableau de bord ne doit être ajouté au dépôt.

Si ces réglages changent, mettre à jour la politique et l'analyse **avant** de publier le changement.
Le code ne peut pas vérifier les réglages internes du compte à distance.

## 2. Ce que fait le code

`js/audience.js` est chargé par toutes les pages. Il :

- n'utilise ni cookie, ni localStorage, ni sessionStorage ;
- respecte **Global Privacy Control** et **Do Not Track** ;
- ne compte que sur `https://quanthevaris.github.io`, dans un onglet visible et hors iframe ;
- ignore localhost, les aperçus techniques, les fichiers locaux, la 404 et les chemins inconnus ;
- envoie une seule requête par chargement de page connue, avec uniquement `p=<chemin canonique>` ;
- omet les identifiants/cookies et le referrer de la requête ;
- ne charge pas `gc.zgo.at/count.js` et ne collecte pas les clics, téléchargements ou paramètres d'URL ;
- échoue silencieusement si le navigateur bloque la requête, sans tentative de contournement.

Ne pas remplacer ce module par le snippet générique GoatCounter sans refaire l'analyse de
confidentialité : le script officiel lit notamment localStorage et transmet davantage de paramètres.

## 3. Publier

1. Relire `confidentialite.html`, `mentions-legales.html`, `index.html`, `contact.html` et les pieds
   de page : ils décrivent la mesure et ne promettent plus « aucune mesure d'audience ».
2. Exécuter les vérifications :

   ```bash
   node --check js/audience.js
   node --test _audience/test-audience.mjs
   git diff --check
   ```

3. Intégrer la branche de travail à `main` par une pull request relue, puis attendre le déploiement
   GitHub Pages. Ne pas pousser directement sur une autre branche depuis cette session.
4. Ouvrir <https://quanthevaris.github.io/> après le déploiement. Si l'ancienne version apparaît,
   recharger sans cache ; ne pas conclure à une panne avant la fin du déploiement.

## 4. Première visite de test

Pour un test destiné à apparaître dans le tableau de bord, utiliser un appareil/une connexion non
exclus par **Ignore IPs**, sans signal DNT/GPC actif et sans bloqueur qui bloque GoatCounter.
Ne pas désactiver durablement les protections des visiteurs pour obtenir des chiffres.

1. Ouvrir l'accueil du site public.
2. Attendre quelques secondes, puis ouvrir <https://quanthevaris.goatcounter.com/>.
3. Choisir **Last day** ou la période incluant aujourd'hui.
4. Une ligne `/` doit apparaître dans **Pages**. Ouvrir ensuite `/guides.html` pour voir une seconde
   page. Les rechargements d'une même page pendant la fenêtre de session ne créent pas chacun une
   nouvelle visite.

Si l'IP de l'éditeur est dans **Ignore IPs**, il est normal que ses visites ne figurent pas au
tableau de bord. Pour vérifier le branchement sans changer cette exclusion : ouvrir les outils de
développement du navigateur (**F12**), onglet **Network / Réseau**, recharger l'accueil et filtrer
`count`. Une requête vers `quanthevaris.goatcounter.com/count?p=%2F` doit partir. Avec
`mode: no-cors`, le navigateur peut masquer le statut/contenu de la réponse : cela ne prouve pas à
soit seul que le tableau de bord a enregistré la visite.

## 5. Lire les chiffres sans les surinterpréter

- **Pages** : les pages consultées et leurs comptages de visites.
- **Totals** : une estimation des visites sur la période, pas un nombre exact de personnes.
- Une personne qui revient après la fenêtre de regroupement peut être comptée à nouveau.
- Plusieurs personnes partageant une IP et un user-agent peuvent être regroupées.
- Les bloqueurs, DNT/GPC, erreurs réseau et visiteurs exclus ne sont pas comptés.
- Les téléchargements directs et le jeu hors ligne ne sont pas des événements d'audience du site.

## 6. Désactiver ou changer de compte

Pour désactiver, remettre `endpoint: ""` dans `js/audience.js`, restaurer une politique et des
mentions sans audience, puis déployer. Supprimer les données ou le compte GoatCounter séparément
si souhaité : vider l'endpoint ne supprime pas les statistiques déjà reçues.

Pour changer de code GoatCounter, modifier l'endpoint et vérifier les réglages du nouveau compte.
Pour utiliser un domaine personnalisé ou une instance auto-hébergée, adapter aussi `CONFIG.origin`,
les canoniques, la validation d'endpoint, les tests et l'analyse du prestataire avant publication.
