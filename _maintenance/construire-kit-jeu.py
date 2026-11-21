"""Reconstruit assets/jeux/FISSION_ARENA-kit.zip depuis _exe/ (sans dépendance).

Usage : python3 _maintenance/construire-kit-jeu.py [--check]

Le kit publié doit rester identique aux sources de _exe/. Les dates des entrées
sont figées pour que deux constructions produisent le même fichier.
"""
import argparse
import hashlib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / '_exe'
ARCHIVE = ROOT / 'assets/jeux/FISSION_ARENA-kit.zip'
DATE = (2026, 11, 21, 0, 0, 0)
FICHIERS = (
    ('fabriquer_exe.py', 'fabriquer_exe.py'),
    ('construire_exe.bat', 'construire_exe.bat'),
    ('fission-arena.ico', 'fission-arena.ico'),
    ('LIRE-MOI.txt', 'LIRE-MOI.txt'),
    ('LICENCE-JEU.txt', 'LICENCE-FISSION-ARENA.txt'),
)


def construire():
    with ZipFile(ARCHIVE, 'w', compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for source, destination in FICHIERS:
            info = ZipInfo('FISSION_ARENA-kit/' + destination, date_time=DATE)
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, (SOURCE / source).read_bytes())
    return hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()


def verifier():
    """Le ZIP publié doit contenir exactement les fichiers de _exe/, à l'octet près."""
    with ZipFile(ARCHIVE) as archive:
        noms = archive.namelist()
        attendus = ['FISSION_ARENA-kit/' + destination for _, destination in FICHIERS]
        if sorted(noms) != sorted(attendus):
            return 'entrées différentes : ' + ', '.join(sorted(set(noms) ^ set(attendus)))
        for source, destination in FICHIERS:
            contenu = archive.read('FISSION_ARENA-kit/' + destination)
            if contenu != (SOURCE / source).read_bytes():
                return 'contenu différent de _exe/' + source
    return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    options = parser.parse_args()
    if options.check:
        ecart = verifier()
        if ecart:
            raise SystemExit('Kit du jeu à reconstruire : ' + ecart)
        print('Kit du jeu à jour.')
    else:
        print('Kit du jeu reconstruit : sha256 =', construire())
