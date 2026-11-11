"""Fabrique FISSION_ARENA.exe a partir de FISSION_ARENA.py, puis le teste.

Le plus simple sous Windows : double-cliquer sur construire_exe.bat (meme dossier).
Sinon :  python fabriquer_exe.py [--source chemin/FISSION_ARENA.py] [--sortie dossier]

Ce que fait ce script, dans l'ordre :
  1. il lit le nom et la version du jeu dans le fichier .py ;
  2. il verifie que le jeu demarre (10 secondes de jeu automatique, sans fenetre ni son) ;
  3. il fabrique le .exe avec PyInstaller : un seul fichier, sans console, avec l'icone ;
  4. il lance le .exe deux fois dans un profil vide : un nouveau joueur doit partir de zero et voir
     la notice de sante, puis la sauvegarde de la premiere partie doit etre retrouvee ;
  5. il compare les bibliotheques contenues dans le .exe a celles decrites dans LICENCES-TIERS.txt ;
  6. il range le .exe et sa fiche (taille, empreinte SHA-256) dans le dossier de sortie.

Rien n'est installe par ce script. Il faut avoir fait une fois :
    python -m pip install pygame pyinstaller
(construire_exe.bat le fait tout seul.)
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap

ICI = os.path.dirname(os.path.abspath(__file__))
NOM_SOURCE = "FISSION_ARENA.py"
NOM_FICHE = "FISSION_ARENA-fiche.txt"
SOUS_WINDOWS = sys.platform.startswith("win")
NOM_PROGRAMME = "FISSION_ARENA.exe" if SOUS_WINDOWS else "FISSION_ARENA"
DEPART_A_ZERO = {
    "best": 0, "best_wave": 0, "coins": 0, "weapons": ["PULSE"], "arenas": ["NEON"],
    "melee_styles": ["BLADE"], "nova_styles": ["NOVA"],
    "upgrades": {"melee": 0, "shot": 0, "health": 0, "speed": 0},
}


# Bibliotheques contenues dans le .exe publie et decrites (auteur, licence) dans
# assets/jeux/LICENCES-TIERS.txt. Si la fabrication en embarque d'autres, un avertissement
# demande de completer ce fichier avant de publier le nouveau .exe.
COMPOSANTS_DECRITS = frozenset({
    # Python et ses modules
    "python313.dll", "_bz2.pyd", "_ctypes.pyd", "_decimal.pyd", "_hashlib.pyd", "_lzma.pyd", "_queue.pyd",
    "_socket.pyd", "_wmi.pyd", "select.pyd", "unicodedata.pyd", "libcrypto-3.dll", "libffi-8.dll",
    # Microsoft Visual C++ / Universal C Runtime
    "vcruntime140.dll", "vcruntime140_1.dll", "ucrtbase.dll",
    # pygame et les bibliotheques SDL
    "sdl2.dll", "sdl2_image.dll", "sdl2_mixer.dll", "sdl2_ttf.dll", "freetype.dll", "libjpeg-9.dll",
    "libmodplug-1.dll", "libogg-0.dll", "libopus-0.dll", "libopusfile-0.dll", "libpng16-16.dll",
    "libtiff-5.dll", "libwebp-7.dll", "portmidi.dll", "zlib1.dll", "freesansbold.ttf",
})


class Echec(Exception):
    """Erreur expliquee en clair a l'utilisateur."""


def dire(message: str = "") -> None:
    try:
        print(message, flush=True)
    except UnicodeEncodeError:              # console ancienne : on remplace les caracteres inconnus
        print(message.encode("ascii", "replace").decode("ascii"), flush=True)


def annoter(niveau: str, message: str) -> None:
    """Sur GitHub Actions, affiche le message dans le resume de l'execution."""
    if os.environ.get("GITHUB_ACTIONS") == "true":
        propre = message.replace("%", "%25").replace("\r", "").replace("\n", "%0A")
        print(f"::{niveau} title=FISSION ARENA::{propre}", flush=True)


def trouver_source(demande: str | None) -> str:
    candidats = [demande] if demande else [
        os.path.join(ICI, NOM_SOURCE),
        os.path.join(os.getcwd(), NOM_SOURCE),
        os.path.join(ICI, "..", "assets", "jeux", NOM_SOURCE),
    ]
    for chemin in candidats:
        if chemin and os.path.isfile(chemin):
            return os.path.abspath(chemin)
    raise Echec("Fichier du jeu introuvable. Mets FISSION_ARENA.py dans le meme dossier que ce script,\n"
                "ou indique son emplacement :  python fabriquer_exe.py --source chemin/FISSION_ARENA.py")


def lire_constante(texte: str, nom: str) -> str:
    trouve = re.search(rf'^{nom}\s*=\s*"([^"]+)"', texte, re.MULTILINE)
    if not trouve:
        raise Echec(f'La ligne  {nom} = "..."  est introuvable dans le fichier du jeu.')
    return trouve.group(1)


def empreinte(donnees: bytes) -> str:
    return hashlib.sha256(donnees).hexdigest()


def empreinte_source(chemin: str) -> str:
    """Empreinte du code, identique que les fins de ligne soient celles de Windows ou non."""
    with open(chemin, "rb") as f:
        return empreinte(f.read().replace(b"\r\n", b"\n"))


def version_modules() -> dict[str, str]:
    versions = {"Python": platform.python_version()}
    try:
        from importlib.metadata import PackageNotFoundError, version
    except ImportError:                                   # Python tres ancien
        return versions
    for nom in ("pygame", "pygame-ce", "pyinstaller"):
        try:
            versions[nom] = version(nom)
        except PackageNotFoundError:
            pass
    return versions


def verifier_outils() -> dict[str, str]:
    versions = version_modules()
    manquants = []
    if "pygame" not in versions and "pygame-ce" not in versions:
        manquants.append("pygame")
    if "pyinstaller" not in versions:
        manquants.append("pyinstaller")
    if manquants:
        raise Echec("Il manque : " + ", ".join(manquants) + ".\nInstalle-les avec :\n    "
                    + os.path.basename(sys.executable) + " -m pip install " + " ".join(manquants))
    return versions


def fichier_version(dossier: str, nom_jeu: str, version: str) -> str:
    """Informations affichees par Windows dans Proprietes > Details du .exe."""
    nombres = [int(n) for n in re.findall(r"\d+", version)][:4]
    nombres += [0] * (4 - len(nombres))
    quad = tuple(nombres)
    annee = datetime.date.today().year
    contenu = f"""# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(filevers={quad}, prodvers={quad}, mask=0x3f, flags=0x0, OS=0x40004,
                    fileType=0x1, subtype=0x0, date=(0, 0)),
  kids=[
    StringFileInfo([StringTable('040C04B0', [
      StringStruct('CompanyName', 'Quanthevaris'),
      StringStruct('FileDescription', '{nom_jeu}'),
      StringStruct('FileVersion', '{".".join(str(n) for n in quad)}'),
      StringStruct('InternalName', 'FISSION_ARENA'),
      StringStruct('LegalCopyright', '(c) {annee} Quanthevaris. Tous droits reserves.'),
      StringStruct('OriginalFilename', 'FISSION_ARENA.exe'),
      StringStruct('ProductName', '{nom_jeu}'),
      StringStruct('ProductVersion', '{version}')])]),
    VarFileInfo([VarStruct('Translation', [0x040C, 1200])])
  ]
)
"""
    chemin = os.path.join(dossier, "version_exe.txt")
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)
    return chemin


def lancer_jeu(commande: list[str], dossier: str, nom: str, profil: str, sans_fenetre: bool,
               sans_son: bool) -> dict:
    """Lance le jeu en mode verification automatique et renvoie son rapport."""
    rapport = os.path.join(dossier, f"rapport_{nom}.json")
    image = os.path.join(dossier, f"image_{nom}.png")
    env = dict(os.environ)
    env.update({
        "FISSION_ARENA_AUTOTEST": rapport, "FISSION_ARENA_AUTOTEST_SHOT": image,
        # profil vide et isole : le test ne touche jamais a la vraie sauvegarde du joueur
        "APPDATA": os.path.join(profil, "AppData", "Roaming"), "USERPROFILE": profil, "HOME": profil,
        "XDG_DATA_HOME": os.path.join(profil, "donnees"),
    })
    env.pop("SDL_VIDEODRIVER", None)
    env.pop("SDL_AUDIODRIVER", None)
    if sans_fenetre:
        env["SDL_VIDEODRIVER"] = "dummy"
    if sans_son:
        env["SDL_AUDIODRIVER"] = "dummy"
    try:
        resultat = subprocess.run(commande, env=env, timeout=300, capture_output=True, text=True, errors="replace")
    except subprocess.TimeoutExpired:
        raise Echec(f"Test '{nom}' : le jeu ne s'est pas ferme tout seul apres 5 minutes.")
    try:
        with open(rapport, encoding="utf-8") as f:
            donnees = json.load(f)
    except (OSError, ValueError):
        raise Echec(f"Test '{nom}' : le jeu n'a pas ecrit son rapport (code de sortie {resultat.returncode}).\n"
                    + (resultat.stderr or resultat.stdout or "")[-1500:])
    if resultat.returncode != 0 or not donnees.get("ok"):
        raise Echec(f"Test '{nom}' : le jeu signale un probleme (code de sortie {resultat.returncode}).\n"
                    + str(donnees.get("error") or donnees)[-1500:])
    if sum(donnees.get("picture", [0])) < 30 or sum(donnees.get("window_picture", [0])) < 30:
        raise Echec(f"Test '{nom}' : l'image du jeu est noire ({donnees.get('picture')}, {donnees.get('window_picture')}).")
    if not os.path.isfile(image) or os.path.getsize(image) < 5000:
        raise Echec(f"Test '{nom}' : la capture d'ecran du jeu est absente ou vide.")
    return donnees


def exiger(condition: bool, message: str) -> None:
    if not condition:
        raise Echec(message)


def tester(commande: list[str], dossier: str, nom: str, sans_fenetre: bool, programme_final: bool) -> list[dict]:
    """Deux lancements dans un profil vide : depart a zero, puis sauvegarde retrouvee."""
    profil = os.path.join(dossier, f"profil_{nom}")
    os.makedirs(profil, exist_ok=True)
    un = lancer_jeu(commande, dossier, nom + "_1", profil, sans_fenetre, sans_son=sans_fenetre)
    exiger(un["save_existed"] is False, f"Test '{nom}' : une sauvegarde existait deja dans un profil vide.")
    exiger(un["start"] == DEPART_A_ZERO,
           f"Test '{nom}' : un nouveau joueur ne part pas de zero : {un['start']}")
    exiger(os.path.abspath(un["save_file"]).startswith(os.path.abspath(profil)),
           f"Test '{nom}' : la sauvegarde n'est pas rangee dans le profil de l'utilisateur : {un['save_file']}")
    exiger(un["save_written"] is True and un["score"] > 0 and un["kills"] > 0,
           f"Test '{nom}' : la partie automatique n'a rien enregistre : {un}")
    exiger(bool(un["frozen"]) == programme_final, f"Test '{nom}' : type de programme inattendu (frozen={un['frozen']}).")
    exiger(un.get("notice_seen") is False and "notice" in un["states"],
           f"Test '{nom}' : la notice de sante ne s'est pas affichee au premier lancement ({un['states']}).")
    # second lancement, cette fois avec le pilote audio muet : la fabrication des sons est verifiee meme sans haut-parleur
    deux = lancer_jeu(commande, dossier, nom + "_2", profil, sans_fenetre, sans_son=True)
    exiger(deux["save_existed"] is True, f"Test '{nom}' : la sauvegarde du premier lancement est introuvable.")
    exiger(deux["start"]["best"] == un["score"] and deux["start"]["best_wave"] == un["wave"],
           f"Test '{nom}' : record non retrouve ({deux['start']} au lieu de {un['score']} / vague {un['wave']}).")
    exiger(deux.get("notice_seen") is True and "notice" not in deux["states"],
           f"Test '{nom}' : la notice de sante est encore imposee au second lancement ({deux['states']}).")
    exiger(deux["audio"] is True and deux["sfx"] == 15 and deux["music"] is True,
           f"Test '{nom}' : sons ou musique non fabriques (audio={deux['audio']}, sons={deux['sfx']}, musique={deux['music']}).")
    return [un, deux]


def fabriquer(source: str, travail: str, nom_jeu: str, version: str) -> str:
    commande = [
        sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--log-level", "WARN",
        "--onefile",                    # un seul fichier .exe
        "--windowed",                   # pas de fenetre noire (console) derriere le jeu
        "--noupx",                      # pas de compression UPX : elle declenche de fausses alertes antivirus
        "--name", "FISSION_ARENA",
        "--distpath", os.path.join(travail, "sortie"),
        "--workpath", os.path.join(travail, "construction"),
        "--specpath", travail,
        # modules inutiles au jeu : les ecarter allege le .exe s'ils sont installes sur l'ordinateur
        "--exclude-module", "numpy", "--exclude-module", "tkinter", "--exclude-module", "unittest",
        "--exclude-module", "pydoc", "--exclude-module", "doctest",
    ]
    if SOUS_WINDOWS:
        commande += ["--icon", os.path.join(ICI, "fission-arena.ico"),
                     "--version-file", fichier_version(travail, nom_jeu, version)]
    commande.append(source)
    resultat = subprocess.run(commande, capture_output=True, text=True, errors="replace")
    programme = os.path.join(travail, "sortie", NOM_PROGRAMME)
    if resultat.returncode != 0 or not os.path.isfile(programme):
        raise Echec("PyInstaller n'a pas reussi a fabriquer le programme :\n" + (resultat.stderr or resultat.stdout)[-3000:])
    return programme


def composants_du_programme(programme: str) -> list[str]:
    """Bibliotheques (.dll, .pyd, polices) rangees dans le programme fabrique, sans les fichiers de Windows."""
    try:
        from PyInstaller.archive.readers import CArchiveReader
        noms = list(CArchiveReader(programme).toc)
    except Exception:                                   # format inattendu : on n'empeche pas la fabrication
        return []
    fichiers = {nom.replace("\\", "/").rsplit("/", 1)[-1].lower() for nom in noms}
    return sorted(f for f in fichiers
                  if f.endswith((".dll", ".pyd", ".ttf", ".so", ".dylib")) and not f.startswith("api-ms-win-")
                  and ".cp3" not in f)                  # modules de pygame lui-meme (pygame/xxx.cp313-win_amd64.pyd)


def ecrire_fiche(chemin: str, nom_jeu: str, version: str, programme: str, source: str,
                 versions: dict[str, str], rapports: list[dict], composants: list[str]) -> str:
    with open(programme, "rb") as f:
        donnees = f.read()
    taille = len(donnees)
    moteur = "pygame-ce " + versions["pygame-ce"] if "pygame-ce" in versions else "pygame " + versions.get("pygame", "?")
    lieu = "GitHub Actions" if os.environ.get("GITHUB_ACTIONS") == "true" else "un ordinateur personnel"
    commit = os.environ.get("GITHUB_SHA", "")
    lignes = [
        f"{nom_jeu} {version} — fichier {NOM_PROGRAMME}",
        "",
        f"Taille : {taille} octets ({taille / 1_000_000:.1f} Mo)".replace(".", ",", 1),
        f"SHA-256 du programme : {empreinte(donnees)}",
        f"SHA-256 du code source : {empreinte_source(source)}",
        "",
        f"Fabriqué le {datetime.datetime.now(datetime.timezone.utc):%Y-%m-%d à %H:%M} UTC sur {lieu}"
        f" ({platform.system()} {platform.release()}, {platform.machine()})",
        f"à partir de {NOM_SOURCE}" + (f" (commit {commit[:10]})" if commit else "") + ".",
        f"Outils : Python {versions['Python']}, {moteur}, SDL {rapports[0]['sdl']}, PyInstaller {versions.get('pyinstaller', '?')}.",
        "",
        "Vérifications automatiques faites sur ce fichier avant sa publication :",
        "  - lancé dans un profil vide : progression à zéro, équipement de base uniquement ;",
        "  - notice de santé affichée d'office au premier lancement, plus imposée ensuite ;",
        f"  - partie jouée par le programme ({rapports[0]['frames']} images, {rapports[0]['kills']} ennemis éliminés), image non vide ;",
        "  - second lancement : sauvegarde et record retrouvés ;",
        f"  - {rapports[1]['sfx']} sons et la musique fabriqués correctement.",
        "",
        "Vérifier le fichier téléchargé sous Windows (PowerShell) :",
        f"    Get-FileHash {NOM_PROGRAMME} -Algorithm SHA256",
        "Le résultat doit être identique à la ligne « SHA-256 du programme » ci-dessus.",
        "",
        "Bibliothèques contenues dans le programme (auteurs et licences : LICENCES-TIERS.txt) :",
        *textwrap.wrap(", ".join(composants) or "liste non disponible", width=96, initial_indent="    ",
                       subsequent_indent="    ", break_on_hyphens=False),
        "",
    ]
    with open(chemin, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lignes))
    return empreinte(donnees)


def principal() -> int:
    analyse = argparse.ArgumentParser(description="Fabrique et teste FISSION_ARENA.exe")
    analyse.add_argument("--source", help="chemin de FISSION_ARENA.py (par defaut : a cote de ce script)")
    analyse.add_argument("--sortie", help="dossier ou ranger le .exe (par defaut : a cote du fichier .py)")
    analyse.add_argument("--sans-fenetre", action="store_true",
                         help="teste le programme sans ouvrir de fenetre (machines sans ecran)")
    options = analyse.parse_args()

    source = trouver_source(options.source)
    sortie = os.path.abspath(options.sortie or os.path.dirname(source))
    with open(source, encoding="utf-8") as f:
        texte = f.read()
    nom_jeu = lire_constante(texte, "GAME_NAME")
    version = lire_constante(texte, "VERSION")
    versions = verifier_outils()
    dire(f"== {nom_jeu} {version} ==")
    dire(f"Code du jeu : {source}")
    dire("Outils      : " + ", ".join(f"{nom} {numero}" for nom, numero in versions.items()))
    if not SOUS_WINDOWS:
        dire("Remarque    : un .exe Windows ne se fabrique que sous Windows. Ici, le programme obtenu\n"
             "              sera celui de ce systeme (" + platform.system() + ").")

    travail = tempfile.mkdtemp(prefix="fission_arena_exe_")
    try:
        dire("\n[1/4] Verification du code (le jeu joue tout seul 2 x 10 secondes, sans fenetre)...")
        tester([sys.executable, source], travail, "code", sans_fenetre=True, programme_final=False)
        dire("      OK")

        dire("[2/4] Fabrication du programme avec PyInstaller (1 a 3 minutes)...")
        programme = fabriquer(source, travail, nom_jeu, version)
        dire(f"      OK ({os.path.getsize(programme) / 1_000_000:.1f} Mo)")

        dire("[3/4] Test du programme fabrique (une fenetre du jeu s'ouvre et joue toute seule, 2 fois)...")
        rapports = tester([programme], travail, "programme", sans_fenetre=options.sans_fenetre, programme_final=True)
        dire("      OK : nouveau joueur a zero, partie jouee, sauvegarde retrouvee, sons fabriques")

        dire("[4/4] Rangement...")
        composants = composants_du_programme(programme)
        nouveaux = sorted(set(composants) - COMPOSANTS_DECRITS) if SOUS_WINDOWS else []
        os.makedirs(sortie, exist_ok=True)
        destination = os.path.join(sortie, NOM_PROGRAMME)
        shutil.copyfile(programme, destination)
        shutil.copymode(programme, destination)
        somme = ecrire_fiche(os.path.join(sortie, NOM_FICHE), nom_jeu, version, destination, source, versions,
                             rapports, composants)
        for nom in ("image_programme_1.png", "rapport_programme_1.json", "rapport_programme_2.json"):
            if os.environ.get("FISSION_ARENA_GARDER_RAPPORTS"):
                shutil.copyfile(os.path.join(travail, nom), os.path.join(sortie, nom))
    finally:
        shutil.rmtree(travail, ignore_errors=True)

    taille = os.path.getsize(destination)
    dire(f"\nTermine : {destination}")
    dire(f"Taille  : {taille / 1_000_000:.1f} Mo   -   SHA-256 : {somme}")
    dire(f"Fiche   : {os.path.join(sortie, NOM_FICHE)}")
    if nouveaux:
        message = ("Ce .exe contient des bibliotheques qui ne sont pas decrites dans assets/jeux/LICENCES-TIERS.txt : "
                   + ", ".join(nouveaux) + ". Avant de le publier, ajoute leur auteur et leur licence dans ce fichier "
                   "(voir _exe/README.md). Pour un usage personnel, rien a faire.")
        dire("\nATTENTION : " + message)
        annoter("warning", message)
    un, deux = rapports
    annoter("notice", f"{nom_jeu} {version} : {NOM_PROGRAMME} fabrique et teste. Taille {taille} octets. SHA-256 {somme}. "
                      f"Python {un['python']}, pygame {un['pygame']}, SDL {un['sdl']}. "
                      f"Test 1 : depart a zero OK, notice de sante affichee, {un['frames']} images, {un['kills']} elimines, score {un['score']}, "
                      f"ecran {un['video_driver']} {un['window']}, audio {un['audio']}, image {un['window_picture']}. "
                      f"Test 2 : record retrouve {deux['start']['best']}, {deux['sfx']} sons, musique {deux['music']}. "
                      f"{len(composants)} bibliotheques" + (f" dont {len(nouveaux)} NON DECRITES : {', '.join(nouveaux)}." if nouveaux else ", toutes decrites."))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(principal())
    except Echec as erreur:
        dire("\nECHEC : " + str(erreur))
        annoter("error", str(erreur))
        sys.exit(1)
