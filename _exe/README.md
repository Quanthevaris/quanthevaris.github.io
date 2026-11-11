# Transformer `FISSION_ARENA.py` en `FISSION_ARENA.exe`

Note pour la prochaine fois : comment refaire le `.exe` quand le code du jeu change.
Ce dossier `_exe/` contient tout le nécessaire ; il n'est pas publié sur le site
(GitHub Pages ignore les dossiers dont le nom commence par `_`).

| Fichier | Rôle |
|---|---|
| `construire_exe.bat` | À double-cliquer sous Windows : installe les outils si besoin, fabrique le `.exe`, le teste. |
| `fabriquer_exe.py` | Le script qui fait le travail (utilisé par le `.bat` **et** par GitHub). |
| `fission-arena.ico` | L'icône du `.exe` (la même que celle de la fenêtre du jeu). |

Le code du jeu et le `.exe` publiés sont dans [`assets/jeux/`](../assets/jeux/).

---

## Méthode 1 — automatique, rien à installer (recommandée)

GitHub fabrique le `.exe` sur une vraie machine Windows, le teste, puis le range sur le site.

1. Sur GitHub, ouvre le dossier `assets/jeux/`.
2. **Add file → Upload files**, dépose ton nouveau `FISSION_ARENA.py` (même nom de fichier), puis **Commit changes**.
3. Attends environ 5 minutes. Onglet **Actions** → « FISSION ARENA - fabriquer le .exe » :
   - coche verte : le nouveau `FISSION_ARENA.exe` et sa fiche `FISSION_ARENA-fiche.txt` ont été rangés
     dans `assets/jeux/` par le robot, et le site est à jour une minute plus tard ;
   - croix rouge : rien n'a été publié, l'ancien `.exe` reste en place. Ouvre l'exécution : le message
     « FISSION ARENA » en haut de la page explique ce qui a échoué.

Avant de publier, le robot vérifie chaque fois que :

- le code démarre avec Python 3.13 (pygame) et Python 3.14 (pygame-ce) ;
- le `.exe` se lance dans un profil vide et qu'**un nouveau joueur part bien de zéro** ;
- la notice de santé s'affiche au premier lancement, et plus d'office ensuite ;
- une partie se joue (le programme joue tout seul dix secondes) et l'image n'est pas noire ;
- au second lancement, la sauvegarde et le record sont retrouvés ;
- les 15 sons et la musique sont bien fabriqués ;
- les bibliothèques contenues dans le `.exe` sont bien celles décrites dans `LICENCES-TIERS.txt`
  (sinon un avertissement jaune le signale).

Pour relancer la fabrication sans rien modifier : onglet **Actions** → ce workflow → **Run workflow**.
Le `.exe` obtenu est alors téléchargeable en bas de la page de l'exécution (« Artifacts »).

## Méthode 2 — sur ton PC Windows

1. Télécharge le dépôt (**Code → Download ZIP**) et décompresse-le, ou copie simplement les trois fichiers
   de ce dossier à côté de ton `FISSION_ARENA.py`.
2. Double-clique sur **`construire_exe.bat`**.
3. Patiente 2 à 4 minutes. Une fenêtre du jeu s'ouvre et joue toute seule, deux fois : c'est le test,
   il ne touche pas à ta sauvegarde.
4. `FISSION_ARENA.exe` apparaît à côté de `FISSION_ARENA.py`, avec sa fiche `FISSION_ARENA-fiche.txt`.

Il faut seulement que Python soit installé ([python.org](https://www.python.org/downloads/), case
« Add python.exe to PATH » cochée). Le `.bat` installe lui-même `pygame` et `pyinstaller` s'ils manquent.

## Méthode 3 — à la main, pour comprendre

Dans un terminal ouvert dans le dossier qui contient `FISSION_ARENA.py` et `fission-arena.ico` :

```bat
py -m pip install pygame pyinstaller
py -m PyInstaller --onefile --windowed --noupx --name FISSION_ARENA --icon fission-arena.ico FISSION_ARENA.py
```

Le résultat est `dist\FISSION_ARENA.exe` (les dossiers `build\` et `dist\` et le fichier `.spec` créés au
passage peuvent être supprimés).

| Option | Effet |
|---|---|
| `--onefile` | Un seul fichier `.exe` qui contient Python, pygame et le jeu. |
| `--windowed` | Pas de fenêtre noire (console) derrière le jeu. |
| `--noupx` | Pas de compression UPX, qui déclenche de fausses alertes antivirus. |
| `--name` | Nom du fichier obtenu. |
| `--icon` | Icône du `.exe` dans l'Explorateur Windows. |

`fabriquer_exe.py` lance cette même commande, y ajoute les informations de version affichées par
Windows (clic droit → Propriétés → Détails) et fait les tests.

---

## À faire à chaque nouvelle version

1. Dans `FISSION_ARENA.py`, changer `VERSION = "1.0"` (début du fichier) : le numéro s'affiche dans la barre
   de titre du jeu, dans les propriétés du `.exe` et dans la fiche.
2. Refaire le `.exe` (méthode 1 ou 2).
3. Dans `fission-arena.html`, mettre à jour le numéro de version (chercher « 1.0 » : il apparaît dans le
   texte de la page et dans le bloc `softwareVersion`) et, si besoin, la taille du fichier. Faire de même
   dans la carte du jeu de `index.html` et de `guides.html`.
   L'empreinte SHA-256 n'est pas à recopier : la page renvoie vers la fiche, refaite avec chaque `.exe`.

## Bon à savoir

- **Un nouveau joueur part toujours de zéro.** La progression n'est jamais dans le `.exe` : elle est écrite
  sur l'ordinateur de chaque joueur, dans `%APPDATA%\FissionArena\save.json`. Ta propre sauvegarde ne part
  donc pas avec le fichier que tu distribues.
- **Windows affiche un avertissement au premier lancement** (« Windows a protégé votre ordinateur ») parce
  que le fichier n'est pas signé par un éditeur reconnu. C'est normal pour un jeu amateur : un certificat de
  signature est payant. La page du jeu l'explique aux joueurs et donne l'empreinte SHA-256 du fichier.
- **Un antivirus peut se tromper** sur un `.exe` fabriqué avec PyInstaller. Ne pas utiliser UPX réduit ce
  risque ; fournir aussi le code `.py`, comme sur le site, permet à chacun de vérifier.
- **Le `.exe` pèse une quinzaine de Mo** : il contient Python et pygame. Il met deux ou trois secondes à
  s'ouvrir, le temps de se décompresser dans un dossier temporaire.
- **Un `.exe` Windows ne se fabrique que sous Windows** (d'où la méthode 1, qui utilise une machine Windows
  de GitHub). Le fichier obtenu fonctionne sur Windows 10 et 11 en 64 bits.
- **Le jeu tient dans un seul fichier** : images, sons et musique sont fabriqués par le programme. Si un jour
  tu ajoutes des fichiers (images, sons…), il faudra les déclarer avec l'option `--add-data` de PyInstaller
  et les ouvrir à partir de `sys._MEIPASS` ; tant que tout reste dans le `.py`, rien à faire.
- **Python 3.14 et plus récent** : `pygame` ne s'y installe pas ; utiliser `pygame-ce`
  (`py -m pip install pygame-ce`), qui se comporte de la même façon. Le `.bat` s'en occupe tout seul
  (vérifié sur une machine Windows avec Python 3.15).
- **Essayer sans publier** : si le message du commit contient `[test]`, GitHub fabrique et teste le `.exe`
  mais ne le range pas sur le site. Avec `[kit]`, il essaie en plus `construire_exe.bat` comme sur un PC.
- **La notice de santé du premier lancement est à garder.** Elle reproduit mot pour mot le texte officiel de
  mise en garde sur l'épilepsie (décret n° 96-360 du 23 avril 1996) : ne pas la reformuler ni la retirer.
  Elle s'affiche d'office une seule fois par ordinateur, puis à la demande (bouton « NOTICE SANTÉ »).
- **Les logiciels libres contenus dans le `.exe`** (Python, pygame, SDL…) doivent être cités avec leurs
  licences : c'est le rôle de `assets/jeux/LICENCES-TIERS.txt`, proposé sur la page du jeu. Ce fichier décrit
  le `.exe` fabriqué par la méthode 1 (Python 3.13 + pygame 2.6.1). Si une fabrication contient d'autres
  bibliothèques (autre version de Python, pygame-ce…), le script affiche « ATTENTION » avec leur liste :
  pour ton usage personnel, rien à faire ; pour **publier** ce `.exe`-là, il faut d'abord compléter
  `LICENCES-TIERS.txt`. Le plus simple est donc de toujours publier le `.exe` de la méthode 1.
- **pygame est sous licence LGPL** : en échange du droit de le distribuer dans le `.exe`, le site fournit le
  code source du jeu (`FISSION_ARENA.py`) et ce kit, et `LICENCES-TIERS.txt` promet d'envoyer le code source
  de pygame à qui le demande par e-mail (il suffit alors de répondre avec le lien
  <https://pypi.org/project/pygame/2.6.1/#files>).
