"""FISSION ARENA - jeu d'arene neon : vagues d'ennemis, boss, boutique.

Copyright (c) 2026 Quanthevaris. Tous droits reserves.
Jeu gratuit : telechargement et usage personnel libres. Toute redistribution ou diffusion
d'une version modifiee demande l'accord de l'auteur (contact.quanthevaris@gmail.com).
Page du jeu et conditions : https://quanthevaris.github.io/fission-arena.html
Le jeu est fourni "en l'etat", sans garantie. Il ne se connecte jamais a Internet.

Lancer le jeu depuis ce fichier :  pip install pygame   puis   python FISSION_ARENA.py
(teste avec Python 3.11 a 3.15 : pygame 2.6 jusqu'a Python 3.13, pygame-ce pour Python 3.14 et 3.15.)
Un seul fichier suffit : images, sons et musique sont fabriques par le programme.

Sante : chez certaines personnes, l'utilisation d'un jeu video necessite des precautions d'emploi
particulieres. La notice s'affiche au premier lancement (puis bouton NOTICE SANTE du menu).

Ce programme utilise pygame (https://www.pygame.org), bibliotheque libre sous licence GNU LGPL.
Le fichier .exe contient aussi Python, SDL et d'autres bibliotheques libres : auteurs et licences
dans https://quanthevaris.github.io/assets/jeux/LICENCES-TIERS.txt
"""
from __future__ import annotations

import json
import math
import os
import random
import sys
import traceback
from array import array
from typing import Any

import pygame

GAME_NAME = "FISSION ARENA"
VERSION = "1.0"          # affichee dans la barre de titre et notee dans la sauvegarde
BASE_W, BASE_H = 960, 540
FPS = 60
HP_CAP = 250
GRID_SPACING = 40

Color = tuple[int, int, int]
GameState = dict[str, Any]

# ------------------------------------------------------------
# Equilibrage / difficulte : tous les reglages au meme endroit
# ------------------------------------------------------------
# Pour rendre le jeu plus facile ou plus dur, il suffit de changer ces nombres.
DIFF_TIME_SCALE = 130.0        # secondes de jeu pour +1.0 de difficulte (plus grand = montee plus lente)
DIFF_WAVE_STEP = 0.04          # difficulte ajoutee a chaque vague
DIFF_MAX = 1.6                 # plafond de difficulte

SPAWN_DELAY_START = 1.05       # delai entre deux apparitions au debut (s)
SPAWN_DELAY_GAIN = 0.5         # reduction du delai quand la difficulte atteint 1.0
SPAWN_DELAY_MIN = 0.32         # delai minimal
MAX_ENEMIES = 65               # ennemis simultanes au maximum

CONTACT_DAMAGE = 14            # degats au contact d'un ennemi classique
CONTACT_DAMAGE_TANK = 17
CONTACT_DAMAGE_BOSS = 24
INVULN_CONTACT = 0.58          # invulnerabilite apres un contact (s)
INVULN_BOSS = 0.62             # ... apres un contact avec un boss
INVULN_BULLET = 0.55           # ... apres un tir ennemi

SHOOTER_FIRST_WAVE = 2         # premiere vague ou les tireurs apparaissent
SHOOTER_FIRST_SHOT = (0.6, 1.6)    # delai avant le premier tir (min, max)
SHOOTER_RELOAD = (1.25, 1.75)      # delai entre deux tirs (min, max)
SHOOTER_BULLET_SPEED = 230
SHOOTER_BULLET_DAMAGE = 9
SHOOTER_SIGHT = 520            # distance maximale de tir
SHOOTER_FAIR = True            # tireurs "loyaux" : ils entrent dans l'arene avant de tirer et y restent
SHOOTER_MARGIN = 30            # marge interieure que les tireurs ne quittent plus une fois entres
SHOOTER_TOP = 50               # idem, en haut de l'ecran (sous le HUD)
SHOOTER_TELEGRAPH = 0.4        # duree du signal lumineux avant un tir (s), seulement si SHOOTER_FAIR
PLAYER_CONTACT_RADIUS = 23     # distance de contact avec un ennemi, hors rayon de l'ennemi (dessin du joueur : 20)

BOSS_HP_BASE = 70
BOSS_HP_PER_WAVE = 7
ARTILLERY_RELOAD = 1.25        # boss ARTILLERIE : delai entre deux salves
ARTILLERY_BULLET_SPEED = 245
ARTILLERY_BULLET_DAMAGE = 10
STORM_RELOAD = 1.8             # boss STORM : delai entre deux couronnes de tirs
STORM_BULLETS = 12
STORM_BULLET_SPEED = 190
STORM_BULLET_DAMAGE = 8
BRUTE_DASH_RELOAD = 2.1        # boss BRUTE : delai entre deux charges

WAVE_CLEAR_HEAL = 8            # soin a la fin de chaque vague
HEAL_DROP_CHANCE = 0.06        # chance qu'un ennemi laisse un soin
COOLDOWN_UPGRADE = 0.90        # amelioration RECHARGE : facteur sur la melee et les tirs (0.90 = -10 %)

LEVELUP_CLICK_DELAY = 0.45     # delai avant de pouvoir cliquer une carte (evite le clic involontaire)
NOTICE_MIN_TIME = 1.5          # au premier lancement, la notice de sante reste affichee au moins ce temps (s)

# pre_init doit etre appele AVANT pygame.init(), sinon ces reglages sont ignores.
pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
pygame.init()
try:
    if pygame.mixer.get_init() is None:
        pygame.mixer.init()
    pygame.mixer.set_num_channels(16)
    pygame.mixer.set_reserved(1)     # canal 0 reserve a la musique
    AUDIO_AVAILABLE = True
except Exception:
    AUDIO_AVAILABLE = False



def make_icon(size: int = 64) -> pygame.Surface:
    """Icone du jeu, dessinee par le programme (aucun fichier externe)."""
    big = 256
    icon = pygame.Surface((big, big), pygame.SRCALPHA)
    pygame.draw.rect(icon, (7, 10, 27), (0, 0, big, big), border_radius=56)
    pygame.draw.rect(icon, (40, 230, 255), (8, 8, big - 16, big - 16), 10, border_radius=50)
    center = (big // 2, big // 2)
    pygame.draw.circle(icon, (40, 230, 255), center, 74, 10)          # anneau du joueur
    for angle, color in ((-90, (255, 55, 150)), (30, (255, 210, 65)), (150, (145, 80, 255))):
        offset = pygame.Vector2(74, 0).rotate(angle)                    # trois fragments
        spot = (int(center[0] + offset.x), int(center[1] + offset.y))
        pygame.draw.circle(icon, (7, 10, 27), spot, 25)
        pygame.draw.circle(icon, color, spot, 18)
    pygame.draw.circle(icon, (80, 245, 255), center, 36)               # noyau
    pygame.draw.circle(icon, (240, 250, 255), center, 15)
    return icon if size == big else pygame.transform.smoothscale(icon, (size, size))


try:
    pygame.display.set_icon(make_icon(64))
except pygame.error:
    pass
screen = pygame.display.set_mode((BASE_W, BASE_H), pygame.RESIZABLE)
pygame.display.set_caption(f"{GAME_NAME} {VERSION}")
canvas = pygame.Surface((BASE_W, BASE_H))
clock = pygame.time.Clock()
fullscreen = False

BG = (7, 10, 27)
CYAN = (40, 230, 255)
PINK = (255, 55, 150)
PURPLE = (145, 80, 255)
WHITE = (240, 250, 255)
RED = (255, 65, 80)
GOLD = (255, 210, 65)
GREEN = (80, 255, 150)
ORANGE = (255, 150, 50)
GREY = (115, 120, 140)
MINT = (120, 255, 230)
ROSE = (255, 120, 220)

ARENAS: list[dict[str, Any]] = [
    {"name": "NEON", "bg": (7, 10, 27), "grid": (17, 32, 59), "edge": (25, 110, 150), "accent": CYAN,
     "desc": "L'arène classique"},
    {"name": "LAVA", "bg": (28, 8, 17), "grid": (72, 25, 35), "edge": (220, 75, 55), "accent": ORANGE,
     "desc": "Un champ de lave"},
    {"name": "CYBER", "bg": (15, 7, 32), "grid": (45, 22, 80), "edge": (145, 80, 255), "accent": PURPLE,
     "desc": "Une zone cyber"},
]
ARENA_NAMES: list[str] = [a["name"] for a in ARENAS]

WEAPON_NAMES: tuple[str, ...] = ("PULSE", "RAPID", "SPREAD", "HEAVY", "SNIPER", "BURST", "LASER", "FLAK", "MISSILE")
MELEE_STYLES: tuple[str, ...] = ("BLADE", "WHIRLWIND", "LANCE")
NOVA_STYLES: tuple[str, ...] = ("NOVA", "VORTEX", "IMPLOSION")

# cd = multiplicateur de recharge | dmg = (multiplicateur, bonus arme)
# explode = rayon d'explosion a l'impact | homing = vitesse de poursuite (0 = aucun)
WEAPONS: dict[str, dict[str, Any]] = {
    "PULSE":   {"cd": 1.00, "heat": 22, "speed": 405, "radius": 6,  "dmg": (1, 0),  "color": CYAN,   "angles": (0.0,), "pierce": 0},
    "RAPID":   {"cd": 0.72, "heat": 17, "speed": 510, "radius": 5,  "dmg": (1, -1), "color": CYAN,   "angles": (0.0,), "pierce": 0},
    "SPREAD":  {"cd": 1.38, "heat": 27, "speed": 370, "radius": 6,  "dmg": (1, -1), "color": PINK,   "angles": (-0.20, 0.0, 0.20), "pierce": 0},
    "HEAVY":   {"cd": 1.70, "heat": 35, "speed": 300, "radius": 10, "dmg": (2, 0),  "color": ORANGE, "angles": (0.0,), "pierce": 0},
    "SNIPER":  {"cd": 1.85, "heat": 38, "speed": 650, "radius": 8,  "dmg": (3, 0),  "color": GOLD,   "angles": (0.0,), "pierce": 2},
    "BURST":   {"cd": 1.45, "heat": 22, "speed": 455, "radius": 5,  "dmg": (1, -1), "color": PURPLE, "angles": (-0.08, 0.0, 0.08), "pierce": 0},
    "LASER":   {"cd": 1.25, "heat": 30, "speed": 940, "radius": 4,  "dmg": (1, 0),  "color": MINT,   "angles": (0.0,), "pierce": 3},
    "FLAK":    {"cd": 1.55, "heat": 32, "speed": 360, "radius": 7,  "dmg": (2, -1), "color": GOLD,   "angles": (0.0,), "pierce": 0, "explode": 62},
    "MISSILE": {"cd": 1.60, "heat": 30, "speed": 300, "radius": 7,  "dmg": (2, 0),  "color": ROSE,   "angles": (0.0,), "pierce": 0, "homing": 3.2},
}

# ------------------------------------------------------------
# Boutons / zones cliquables
# ------------------------------------------------------------
SHOP_BUTTON_RECT = pygame.Rect(BASE_W - 125, 118, 105, 28)
QUIT_BUTTON_RECT = pygame.Rect(BASE_W - 125, 152, 105, 28)
MUSIC_GAME_RECT = pygame.Rect(BASE_W - 125, 186, 105, 28)
PAUSE_BUTTON_RECT = pygame.Rect(BASE_W - 125, 220, 105, 28)
SHOP_BACK_RECT = pygame.Rect(BASE_W - 150, 20, 130, 42)
SHOP_PREV_RECT = pygame.Rect(30, 420, 200, 32)
SHOP_NEXT_RECT = pygame.Rect(BASE_W - 230, 420, 200, 32)
ARENA_BACK_RECT = pygame.Rect(BASE_W // 2 - 95, 430, 190, 42)
MENU_PLAY_RECT = pygame.Rect(350, 250, 260, 48)
MENU_SHOP_RECT = pygame.Rect(350, 310, 260, 48)
MENU_ARENA_RECT = pygame.Rect(350, 370, 260, 48)
MUSIC_BUTTON_RECT = pygame.Rect(BASE_W - 190, 470, 165, 38)
MENU_RESET_RECT = pygame.Rect(25, 470, 165, 38)
MENU_NOTICE_RECT = pygame.Rect(BASE_W - 190, 24, 165, 32)
PAUSE_RESUME_RECT = pygame.Rect(350, 295, 260, 48)
PAUSE_MENU_RECT = pygame.Rect(350, 355, 260, 48)
GAMEOVER_RETRY_RECT = pygame.Rect(350, 345, 260, 48)
GAMEOVER_MENU_RECT = pygame.Rect(350, 405, 260, 48)
LEVELUP_CARD_RECTS: list[pygame.Rect] = [pygame.Rect(105 + i * 255, 210, 240, 165) for i in range(3)]
SHOP_CARD_RECTS: list[pygame.Rect] = [pygame.Rect(35 + (i % 3) * 300, 125 + (i // 3) * 98, 280, 88) for i in range(9)]
ARENA_CARD_RECTS: list[pygame.Rect] = [pygame.Rect(55 + i * 290, 200, 270, 175) for i in range(3)]

font = pygame.font.Font(None, 27)
small_font = pygame.font.Font(None, 22)
tiny_font = pygame.font.Font(None, 19)
big_font = pygame.font.Font(None, 68)
title_font = pygame.font.Font(None, 86)

# Transformation ecran -> canvas (letterbox : le ratio 16:9 est conserve)
view_scale = 1.0
view_ox = 0.0
view_oy = 0.0
hud_block = 0.0              # empeche d'attaquer en cliquant sur un bouton du HUD

# ------------------------------------------------------------
# Sauvegarde
# ------------------------------------------------------------
def save_directory() -> str:
    """Dossier de sauvegarde propre a chaque utilisateur de l'ordinateur.

    La progression n'est jamais rangee dans le .exe ni a cote de lui : une personne
    qui recoit le jeu n'a pas ce dossier et commence donc forcement a zero.
    """
    home = os.path.expanduser("~")
    if sys.platform.startswith("win"):
        base = os.environ.get("APPDATA") or os.path.join(home, "AppData", "Roaming")
    elif sys.platform == "darwin":
        base = os.path.join(home, "Library", "Application Support")
    else:
        base = os.environ.get("XDG_DATA_HOME") or os.path.join(home, ".local", "share")
    return os.path.join(base, "FissionArena")


SAVE_DIR = save_directory()
SAVE_FILE = os.path.join(SAVE_DIR, "save.json")
MAX_SAVED_VALUE = 999_999_999
save_dirty = False


def _read_save(path: str) -> dict[str, Any] | None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:               # fichier absent, illisible ou abime
        return None
    return data if isinstance(data, dict) else None


def load_save() -> dict[str, Any]:
    """Lit la sauvegarde. Sans fichier (nouveau joueur), renvoie un dictionnaire vide."""
    if not os.path.exists(SAVE_FILE):
        return {}
    data = _read_save(SAVE_FILE)
    if data is None:                # fichier abime : on le met de cote au lieu de l'ecraser
        try:
            os.replace(SAVE_FILE, SAVE_FILE + ".illisible")
        except OSError:
            pass
    return data or {}


def _safe_int(value: Any, default: int = 0, minimum: int = 0, maximum: int = MAX_SAVED_VALUE) -> int:
    if isinstance(value, bool):
        return default
    try:
        number = int(value)
    except (ValueError, TypeError, OverflowError):
        return default
    return max(minimum, min(maximum, number))


def _clean_owned(value: Any, allowed: tuple[str, ...], default: str) -> list[str]:
    if not isinstance(value, list):
        value = []
    return list(dict.fromkeys([default] + [x for x in value if isinstance(x, str) and x in allowed]))


def _clean_choice(value: Any, owned: list[str], default: str) -> str:
    return value if isinstance(value, str) and value in owned else default


PERMANENT_CAPS = {"melee": 3, "shot": 3, "health": 75, "speed": 45}
PERMANENT_STEP = {"melee": 1, "shot": 1, "health": 25, "speed": 15}
STAT_BY_KIND = {"melee": "melee", "shot": "shot", "maxhp": "health", "speed": "speed"}

# Progression du joueur. Les valeurs ci-dessous sont celles d'un NOUVEAU JOUEUR :
# tout est a zero et seul l'equipement de base est possede.
# apply_save_data() les remplace par le contenu de la sauvegarde quand elle existe.
best_score = 0
best_wave = 0
bank_coins = 0
unlocked_arenas: list[str] = ["NEON"]
owned_weapons: list[str] = ["PULSE"]
selected_weapon = "PULSE"
owned_melee_styles: list[str] = ["BLADE"]
selected_melee_style = "BLADE"
owned_nova_styles: list[str] = ["NOVA"]
selected_nova_style = "NOVA"
music_enabled = True
selected_arena = 0
permanent_upgrades: dict[str, int] = {name: 0 for name in PERMANENT_CAPS}
notice_seen = False          # la notice de sante a deja ete lue (elle s'affiche d'office tant que c'est faux)


def apply_save_data(data: dict[str, Any]) -> None:
    """Installe une sauvegarde. Un dictionnaire vide donne un nouveau joueur a zero."""
    global best_score, best_wave, bank_coins, unlocked_arenas, owned_weapons, selected_weapon
    global owned_melee_styles, selected_melee_style, owned_nova_styles, selected_nova_style
    global music_enabled, selected_arena, permanent_upgrades, notice_seen
    notice_seen = data.get("notice_seen") is True
    best_score = _safe_int(data.get("best"))
    best_wave = _safe_int(data.get("best_wave"))
    bank_coins = _safe_int(data.get("coins"))
    unlocked_arenas = _clean_owned(data.get("unlocked_arenas"), tuple(ARENA_NAMES), "NEON")
    owned_weapons = _clean_owned(data.get("owned_weapons"), WEAPON_NAMES, "PULSE")
    selected_weapon = _clean_choice(data.get("selected_weapon"), owned_weapons, "PULSE")
    owned_melee_styles = _clean_owned(data.get("owned_melee_styles"), MELEE_STYLES, "BLADE")
    selected_melee_style = _clean_choice(data.get("selected_melee_style"), owned_melee_styles, "BLADE")
    owned_nova_styles = _clean_owned(data.get("owned_nova_styles"), NOVA_STYLES, "NOVA")
    selected_nova_style = _clean_choice(data.get("selected_nova_style"), owned_nova_styles, "NOVA")
    sound = data.get("music_enabled", True)
    music_enabled = sound if isinstance(sound, bool) else True
    arena = _clean_choice(data.get("selected_arena"), unlocked_arenas, "NEON")
    selected_arena = ARENA_NAMES.index(arena)
    saved_perm = data.get("permanent_upgrades")
    if not isinstance(saved_perm, dict):
        saved_perm = {}
    permanent_upgrades = {
        name: min(cap, _safe_int(saved_perm.get(name)) // PERMANENT_STEP[name] * PERMANENT_STEP[name])
        for name, cap in PERMANENT_CAPS.items()
    }


apply_save_data(load_save())


def save_progress() -> None:
    """Sauvegarde atomique : ecrit un fichier temporaire puis le remplace."""
    global save_dirty
    data = {
        "version": VERSION,
        "best": best_score,
        "best_wave": best_wave,
        "coins": bank_coins,
        "unlocked_arenas": unlocked_arenas,
        "owned_weapons": owned_weapons,
        "selected_arena": ARENA_NAMES[selected_arena],
        "selected_weapon": selected_weapon,
        "owned_melee_styles": owned_melee_styles,
        "owned_nova_styles": owned_nova_styles,
        "selected_melee_style": selected_melee_style,
        "selected_nova_style": selected_nova_style,
        "music_enabled": music_enabled,
        "permanent_upgrades": permanent_upgrades,
        "notice_seen": notice_seen,
    }
    try:
        os.makedirs(SAVE_DIR, exist_ok=True)
        tmp = SAVE_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, SAVE_FILE)
        save_dirty = False
    except OSError:
        pass


# ------------------------------------------------------------
# Donnees de jeu
# ------------------------------------------------------------
def new_game() -> GameState:
    return {
        "player": pygame.Vector2(BASE_W / 2, BASE_H / 2),
        "facing": pygame.Vector2(1, 0),
        "hp": 100 + permanent_upgrades["health"],
        "max_hp": 100 + permanent_upgrades["health"],
        "damage": 1 + permanent_upgrades["melee"],
        "shot_damage": 2 + permanent_upgrades["shot"],
        "speed": 235 + permanent_upgrades["speed"],
        "range": 105,
        "melee_cd": 0.48,
        "shot_cd": 0.62,
        "shot_heat": 0.0,
        "overheat_timer": 0.0,
        "skill_damage": 3,
        "melee_timer": 0.0,
        "shot_timer": 0.0,
        "skill_timer": 0.0,
        "skill_flash": 0.0,
        "score": 0,
        "xp": 0,
        "level": 1,
        "xp_needed": 5,
        "enemies": [],
        "projectiles": [],
        "enemy_projectiles": [],
        "particles": [],
        "slashes": [],
        "texts": [],
        "coin_pickups": [],
        "spawn_timer": 0.8,
        "invulnerable": 0.0,
        "time": 0.0,
        "kills": 0,
        "upgrades": [],
        "difficulty": 0.0,
        "wave": 1,
        "wave_kills": 0,
        "wave_spawned": 0,
        "wave_target": 8,
        "wave_break": 1.0,
        "boss_spawned": False,
        "boss_defeated": False,
        "arena_index": selected_arena,
        "weapon": selected_weapon,
        "melee_style": selected_melee_style,
        "nova_style": selected_nova_style,
        "shake": 0.0,
        "hurt_flash": 0.0,
        "gameover_timer": 0.0,
        "new_record": False,
        "started": False,            # False tant qu'on est seulement dans le menu
        "pending_levelups": 0,       # niveaux gagnes dont l'amelioration reste a choisir
        "levelup_timer": 0.0,        # court delai avant de pouvoir cliquer une carte
    }


game: GameState = new_game()
state = "menu"
running = True
anim_t = 0.0

UPGRADES: list[tuple[str, str, str]] = [
    ("MÊLÉE +1", "Plus de dégâts au corps à corps.", "damage"),
    ("TIRS +1", "Projectiles plus puissants.", "shot"),
    ("VITESSE +15", "Déplacement plus rapide.", "speed"),
    ("VIE MAX +25", "Vie maximale et soin.", "health"),
    ("PORTÉE +20", "Attaques de mêlée plus longues.", "range"),
    (f"RECHARGE -{round((1 - COOLDOWN_UPGRADE) * 100)} %", "Attaques et tirs plus rapides.", "cooldown"),
    ("NOVA +2", "Compétence spéciale plus puissante.", "skill"),
    ("SOIN +35", "Récupère des points de vie.", "heal"),
]

SHOP_ITEMS: list[dict[str, Any]] = [
    {"name": "LAME RENFORCÉE", "desc": "+1 dégât de mêlée (max 3)", "price": 220, "type": "melee"},
    {"name": "TIR AMÉLIORÉ", "desc": "+1 dégât de tir (max 3)", "price": 260, "type": "shot"},
    {"name": "VIE RENFORCÉE", "desc": "+25 vie max (max +75)", "price": 300, "type": "maxhp"},
    {"name": "PROPULSEUR", "desc": "+15 vitesse (max +45)", "price": 250, "type": "speed"},
    {"name": "ARME RAPIDE", "desc": "Cadence rapide, chauffe vite", "price": 400, "type": "weapon", "weapon": "RAPID"},
    {"name": "TIR MULTIPLE", "desc": "3 projectiles en éventail", "price": 650, "type": "weapon", "weapon": "SPREAD"},
    {"name": "CANON LOURD", "desc": "Tirs puissants et lents", "price": 850, "type": "weapon", "weapon": "HEAVY"},
    {"name": "ARÈNE LAVA", "desc": "Débloque l'arène de lave", "price": 900, "type": "arena", "arena": "LAVA"},
    {"name": "ARÈNE CYBER", "desc": "Débloque l'arène futuriste", "price": 1300, "type": "arena", "arena": "CYBER"},
    {"name": "FUSIL SNIPER", "desc": "Perce les ennemis, très lent", "price": 1150, "type": "weapon", "weapon": "SNIPER"},
    {"name": "RAFALE", "desc": "Triple tir concentré", "price": 1450, "type": "weapon", "weapon": "BURST"},
    {"name": "LAME TOURBILLON", "desc": "Frappe tout autour de soi", "price": 700, "type": "melee_style", "style": "WHIRLWIND"},
    {"name": "LANCE PHOTON", "desc": "Mêlée longue et précise", "price": 950, "type": "melee_style", "style": "LANCE"},
    {"name": "NOVA VORTEX", "desc": "Attire les ennemis vers soi", "price": 1200, "type": "nova_style", "style": "VORTEX"},
    {"name": "NOVA IMPLOSION", "desc": "Petit rayon, gros dégâts", "price": 1600, "type": "nova_style", "style": "IMPLOSION"},
    {"name": "LASER PERÇANT", "desc": "Rayon très rapide, traverse 3 ennemis", "price": 1800, "type": "weapon", "weapon": "LASER"},
    {"name": "CANON FLAK", "desc": "Explose à l'impact (dégâts de zone)", "price": 2100, "type": "weapon", "weapon": "FLAK"},
    {"name": "MISSILES AUTOGUIDÉS", "desc": "Poursuivent les ennemis", "price": 2600, "type": "weapon", "weapon": "MISSILE"},
]

shop_return_state = "menu"
shop_page = 0
shop_message = "Choisis un objet à acheter."
shop_message_ok = False
shop_message_timer = 0.0
menu_message = ""
menu_message_timer = 0.0
reset_confirm_timer = 0.0      # > 0 : un second clic sur le bouton confirme la remise a zero
notice_timer = 0.0             # > 0 : la notice de sante ne peut pas encore etre fermee

# ------------------------------------------------------------
# Musique et effets sonores (synthetises, aucun fichier externe)
# ------------------------------------------------------------
_music_sound: pygame.mixer.Sound | None = None
_music_channel: pygame.mixer.Channel | None = None
_sfx: dict[str, pygame.mixer.Sound] = {}
_sfx_last: dict[str, float] = {}


def _mixer_format_ok() -> bool:
    info = pygame.mixer.get_init()
    return bool(info) and info[1] == -16


def _make_background_music() -> pygame.mixer.Sound | None:
    """Boucle electronique legere generee au demarrage."""
    if not AUDIO_AVAILABLE or not _mixer_format_ok():
        return None
    try:
        init = pygame.mixer.get_init()
        if init is None:
            return None
        rate, _, channels = init
        notes = (110.0, 146.83, 164.81, 130.81, 98.0, 146.83, 174.61, 130.81)
        samples = array("h")
        append, extend = samples.append, samples.extend
        for i in range(int(rate * 6.0)):
            t = i / rate
            beat = int(t / 0.375) % len(notes)
            local_t = t % 0.375
            fade = min(1.0, local_t * 30.0, (0.375 - local_t) * 20.0)
            bass = math.sin(math.tau * notes[beat] * t) * 0.20
            pulse = math.sin(math.tau * notes[beat] * 2.0 * t) * 0.10
            melody = math.sin(math.tau * notes[(beat + 3) % len(notes)] * 2.0 * t) * 0.07 * (0.5 + 0.5 * math.sin(math.tau * 1.5 * t))
            value = max(-0.8, min(0.8, (bass + pulse + melody) * fade))
            sample = int(value * 15000)
            if channels == 1:
                append(sample)
            else:
                extend([sample] * channels)
        return pygame.mixer.Sound(buffer=samples.tobytes())
    except Exception:
        return None


def _synth(freq_start: float, freq_end: float, duration: float, volume: float = 0.4,
           kind: str = "square", decay: float = 2.5) -> pygame.mixer.Sound:
    """Petit effet sonore : glissando + enveloppe."""
    init = pygame.mixer.get_init()
    if init is None:
        raise RuntimeError("mixer non initialise")
    rate, _, channels = init
    n = max(1, int(rate * duration))
    buf = array("h")
    append, extend = buf.append, buf.extend
    phase = 0.0
    for i in range(n):
        k = i / n
        phase += (freq_start + (freq_end - freq_start) * k) / rate
        if kind == "square":
            v = 1.0 if (phase % 1.0) < 0.5 else -1.0
        elif kind == "noise":
            v = random.uniform(-1.0, 1.0)
        else:
            v = math.sin(math.tau * phase)
        env = min(1.0, i / 80.0) * (1.0 - k) ** decay
        sample = int(max(-1.0, min(1.0, v * env * volume)) * 32000)
        if channels == 1:
            append(sample)
        else:
            extend([sample] * channels)
    return pygame.mixer.Sound(buffer=buf.tobytes())


def init_sfx() -> None:
    if not AUDIO_AVAILABLE or not _mixer_format_ok():
        return
    specs: dict[str, tuple[Any, ...]] = {
        "melee": (420, 120, 0.11, 0.25, "noise", 2.0),
        "shot": (900, 300, 0.09, 0.14, "square", 2.0),
        "laser": (1500, 700, 0.10, 0.12, "sine", 1.6),
        "explode": (200, 40, 0.28, 0.32, "noise", 1.6),
        "missile": (600, 1000, 0.14, 0.14, "square", 1.8),
        "hit": (300, 150, 0.05, 0.20, "noise", 1.5),
        "kill": (500, 900, 0.12, 0.28, "sine", 1.5),
        "coin": (988, 1318, 0.09, 0.14, "square", 1.5),
        "nova": (220, 55, 0.45, 0.50, "sine", 1.3),
        "hurt": (220, 90, 0.20, 0.30, "square", 1.5),
        "levelup": (440, 880, 0.30, 0.30, "sine", 1.0),
        "boss": (90, 60, 0.50, 0.30, "square", 1.2),
        "click": (700, 700, 0.04, 0.15, "square", 1.0),
        "buy": (700, 1400, 0.20, 0.30, "sine", 1.2),
        "gameover": (330, 70, 0.80, 0.35, "square", 1.3),
    }
    for name, args in specs.items():
        try:
            _sfx[name] = _synth(*args)
        except Exception:
            pass


def play_sfx(name: str, min_gap: float = 0.0) -> None:
    if not (AUDIO_AVAILABLE and music_enabled):
        return
    sound = _sfx.get(name)
    if sound is None:
        return
    if min_gap > 0:
        now = pygame.time.get_ticks() / 1000.0
        if now - _sfx_last.get(name, -9.0) < min_gap:
            return
        _sfx_last[name] = now
    try:
        sound.play()
    except Exception:
        pass


def start_or_update_music() -> None:
    global _music_sound, _music_channel
    if not AUDIO_AVAILABLE:
        return
    try:
        if _music_sound is None:
            _music_sound = _make_background_music()
        if _music_sound is None:
            return
        if _music_channel is None:
            _music_channel = pygame.mixer.Channel(0)
        if music_enabled:
            if not _music_channel.get_busy():
                _music_channel.play(_music_sound, loops=-1)
            _music_channel.set_volume(0.20)
        else:
            _music_channel.stop()
    except Exception:
        pass


def toggle_music() -> None:
    global music_enabled
    music_enabled = not music_enabled
    start_or_update_music()
    save_progress()
    play_sfx("click")


# ------------------------------------------------------------
# Dessin : caches et utilitaires
# ------------------------------------------------------------
_text_cache: dict[tuple[str, int, Color], pygame.Surface] = {}
_glow_cache: dict[tuple[int, Color, int], pygame.Surface] = {}
_shade_cache: dict[int, pygame.Surface] = {}
_grid_cache: dict[int, pygame.Surface] = {}


def clamp(value: float, low: float, high: float) -> float:
    return low if value < low else (high if value > high else value)


def draw_text(surface: pygame.Surface, message: Any, font_obj: pygame.font.Font, color: Color,
              pos: tuple[float, float], center: bool = False) -> None:
    key = (str(message), id(font_obj), color)
    image = _text_cache.get(key)
    if image is None:
        if len(_text_cache) > 600:
            _text_cache.clear()
        image = font_obj.render(str(message), True, color)
        _text_cache[key] = image
    rect = image.get_rect()
    if center:
        rect.center = (int(pos[0]), int(pos[1]))
    else:
        rect.topleft = (int(pos[0]), int(pos[1]))
    surface.blit(image, rect)


def glow(surface: pygame.Surface, pos: tuple[float, float], radius: float, color: Color, alpha: int = 35) -> None:
    radius = max(1, int(radius))
    key = (radius, color, int(alpha))
    layer = _glow_cache.get(key)
    if layer is None:
        if len(_glow_cache) > 320:
            _glow_cache.clear()
        size = max(4, radius * 4)
        layer = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(layer, (*color, int(alpha)), (size // 2, size // 2), radius * 2)
        _glow_cache[key] = layer
    surface.blit(layer, (int(pos[0] - layer.get_width() / 2), int(pos[1] - layer.get_height() / 2)))


def draw_shade(surface: pygame.Surface, alpha: int = 220) -> None:
    shade = _shade_cache.get(alpha)
    if shade is None:
        shade = pygame.Surface((BASE_W, BASE_H), pygame.SRCALPHA)
        shade.fill((4, 5, 20, alpha))
        _shade_cache[alpha] = shade
    surface.blit(shade, (0, 0))


def _build_vignette() -> pygame.Surface:
    surf = pygame.Surface((BASE_W, BASE_H), pygame.SRCALPHA)
    steps = 14
    for i in range(steps):
        alpha = int(150 * (1 - i / steps) ** 2)
        pygame.draw.rect(surf, (255, 40, 60, alpha), (i * 4, i * 4, BASE_W - i * 8, BASE_H - i * 8), 4)
    return surf


VIGNETTE = _build_vignette()


def _grid_surface(arena_index: int) -> pygame.Surface:
    """Grille de l'arene calculee une seule fois puis mise en cache."""
    cached = _grid_cache.get(arena_index)
    if cached is not None:
        return cached
    arena = ARENAS[arena_index]
    height = BASE_H + GRID_SPACING
    surf = pygame.Surface((BASE_W, height), pygame.SRCALPHA)
    for x in range(0, BASE_W + GRID_SPACING, GRID_SPACING):
        pygame.draw.line(surf, arena["grid"], (x, 0), (x, height), 1)
    for y in range(0, height, GRID_SPACING):
        pygame.draw.line(surf, arena["grid"], (0, y), (BASE_W, y), 1)
    _grid_cache[arena_index] = surf
    return surf


def wrap_text(text: str, max_chars: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = (current + " " + word).strip()
        if len(candidate) > max_chars and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def draw_button(surface: pygame.Surface, rect: pygame.Rect, label: str, color: Color = CYAN,
                fill: Color = (20, 32, 65)) -> None:
    pygame.draw.rect(surface, fill, rect, border_radius=12)
    pygame.draw.rect(surface, color, rect, 2, border_radius=12)
    draw_text(surface, label, font, WHITE, rect.center, center=True)


def draw_small_button(surface: pygame.Surface, rect: pygame.Rect, label: str, color: Color,
                      fill: Color = (25, 35, 65)) -> None:
    pygame.draw.rect(surface, fill, rect, border_radius=7)
    pygame.draw.rect(surface, color, rect, 2, border_radius=7)
    draw_text(surface, label, small_font, color, rect.center, center=True)


def update_view(sw: int, sh: int) -> None:
    """Echelle et marges pour conserver le ratio 16:9 dans n'importe quelle fenetre."""
    global view_scale, view_ox, view_oy
    view_scale = max(0.01, min(sw / BASE_W, sh / BASE_H))
    view_ox = (sw - BASE_W * view_scale) / 2
    view_oy = (sh - BASE_H * view_scale) / 2


def screen_to_canvas(x: float, y: float) -> tuple[float, float]:
    return (x - view_ox) / view_scale, (y - view_oy) / view_scale


def mouse_canvas_pos() -> pygame.Vector2:
    """Position de la souris ramenee dans les coordonnees du jeu (960x540)."""
    mx, my = pygame.mouse.get_pos()
    cx, cy = screen_to_canvas(mx, my)
    return pygame.Vector2(clamp(cx, 0, BASE_W), clamp(cy, 0, BASE_H))


# ------------------------------------------------------------
# Effets
# ------------------------------------------------------------
def add_particles(pos: Any, color: Color, count: int = 12, force: float = 180) -> None:
    count = min(count, max(0, 650 - len(game["particles"])))
    for _ in range(count):
        angle = random.random() * math.tau
        speed = random.uniform(force * 0.3, force)
        life = random.uniform(0.2, 0.55)
        game["particles"].append({
            "pos": pygame.Vector2(pos),
            "vel": pygame.Vector2(math.cos(angle) * speed, math.sin(angle) * speed),
            "life": life, "maxlife": life, "color": color, "size": random.randint(2, 5),
        })


def add_float_text(pos: Any, message: Any, color: Color = WHITE) -> None:
    if len(game["texts"]) >= 40:
        return
    game["texts"].append({
        "pos": pygame.Vector2(pos) + pygame.Vector2(random.uniform(-8, 8), -18),
        "text": str(message), "color": color, "life": 0.7,
    })


def add_shake(amount: float) -> None:
    game["shake"] = max(game["shake"], amount)


def add_blast(pos: pygame.Vector2, radius: float, color: Color = GOLD) -> None:
    game["slashes"].append({"pos": pygame.Vector2(pos), "life": 0.26, "maxlife": 0.26,
                            "kind": "blast", "style": "BLAST", "radius": radius,
                            "direction": pygame.Vector2(1, 0), "color": color})


# ------------------------------------------------------------
# Progression
# ------------------------------------------------------------
def raise_max_hp(amount: int) -> None:
    old = game["max_hp"]
    game["max_hp"] = min(HP_CAP, old + amount)
    game["hp"] = min(game["max_hp"], game["hp"] + game["max_hp"] - old)


def upgrade_available(code: str) -> bool:
    if code == "damage":
        return game["damage"] < 7
    if code == "shot":
        return game["shot_damage"] < 5
    if code == "speed":
        return game["speed"] < 330
    if code == "health":
        return game["max_hp"] < HP_CAP
    if code == "range":
        return game["range"] < 175
    if code == "cooldown":
        return game["melee_cd"] > 0.30 or game["shot_cd"] > 0.48
    if code == "skill":
        return game["skill_damage"] < 14
    if code == "heal":
        return game["hp"] < game["max_hp"]
    return True


def gain_xp(amount: int) -> None:
    if state not in ("playing", "levelup"):
        return                      # partie terminee : un dernier tir ne doit pas ranimer le joueur
    game["xp"] += amount
    while game["xp"] >= game["xp_needed"]:
        game["xp"] -= game["xp_needed"]
        game["level"] += 1
        game["xp_needed"] = game["level"] * 5
        game["max_hp"] = min(HP_CAP, game["max_hp"] + 10)
        game["hp"] = min(game["max_hp"], game["hp"] + 25)
        game["pending_levelups"] += 1
        add_particles(game["player"], GOLD, 30, 230)
        play_sfx("levelup")
    if game["pending_levelups"] > 0 and state == "playing":
        open_levelup()


def open_levelup() -> None:
    """Propose trois ameliorations (un choix par niveau gagne)."""
    global state
    pool = [u for u in UPGRADES if upgrade_available(u[2])]
    if len(pool) < 3:
        pool = list(UPGRADES)
    game["upgrades"] = random.sample(pool, 3)
    game["levelup_timer"] = LEVELUP_CLICK_DELAY
    state = "levelup"


def apply_upgrade(index: int) -> None:
    global state
    if index < 0 or index >= len(game["upgrades"]):
        return
    upgrade = game["upgrades"][index][2]
    if upgrade == "damage":
        game["damage"] = min(7, game["damage"] + 1)
    elif upgrade == "shot":
        game["shot_damage"] = min(5, game["shot_damage"] + 1)
    elif upgrade == "speed":
        game["speed"] = min(330, game["speed"] + 15)
    elif upgrade == "health":
        raise_max_hp(25)
    elif upgrade == "range":
        game["range"] = min(175, game["range"] + 20)
    elif upgrade == "cooldown":
        game["melee_cd"] = max(0.30, game["melee_cd"] * COOLDOWN_UPGRADE)
        game["shot_cd"] = max(0.48, game["shot_cd"] * COOLDOWN_UPGRADE)
    elif upgrade == "skill":
        game["skill_damage"] = min(14, game["skill_damage"] + 2)
    elif upgrade == "heal":
        game["hp"] = min(game["max_hp"], game["hp"] + 35)
    add_particles(game["player"], GOLD, 24, 220)
    play_sfx("click")
    game["pending_levelups"] = max(0, game["pending_levelups"] - 1)
    if game["pending_levelups"] > 0:
        open_levelup()              # plusieurs niveaux d'un coup : un choix pour chacun
    else:
        state = "playing"


# ------------------------------------------------------------
# Boutique
# ------------------------------------------------------------
def set_shop_message(message: str, ok: bool = False, duration: float = 2.0) -> None:
    global shop_message, shop_message_ok, shop_message_timer
    shop_message = message
    shop_message_ok = ok
    shop_message_timer = duration


def is_item_owned(item: dict[str, Any]) -> bool:
    kind = item["type"]
    if kind == "weapon":
        return item["weapon"] in owned_weapons
    if kind == "arena":
        return item["arena"] in unlocked_arenas
    if kind == "melee_style":
        return item["style"] in owned_melee_styles
    if kind == "nova_style":
        return item["style"] in owned_nova_styles
    return False


def is_item_capped(item: dict[str, Any]) -> bool:
    stat = STAT_BY_KIND.get(item["type"])
    return bool(stat and permanent_upgrades[stat] >= PERMANENT_CAPS[stat])


def buy_shop_item(index: int) -> None:
    global bank_coins, selected_weapon, selected_melee_style, selected_nova_style
    if index < 0 or index >= len(SHOP_ITEMS):
        return
    item = SHOP_ITEMS[index]
    kind = item["type"]

    if is_item_owned(item):        # deja possede : on l'equipe gratuitement
        if kind == "weapon":
            selected_weapon = item["weapon"]
            game["weapon"] = selected_weapon
            set_shop_message(f"{selected_weapon} équipée !", True)
        elif kind == "melee_style":
            selected_melee_style = item["style"]
            game["melee_style"] = selected_melee_style
            set_shop_message(f"Mêlée {selected_melee_style} équipée !", True)
        elif kind == "nova_style":
            selected_nova_style = item["style"]
            game["nova_style"] = selected_nova_style
            set_shop_message(f"NOVA {selected_nova_style} équipée !", True)
        else:
            set_shop_message(f"Arène {item['arena']} déjà débloquée : menu CHOISIR UNE ARÈNE.", False, 2.8)
            return
        play_sfx("click")
        save_progress()
        return

    if is_item_capped(item):
        set_shop_message("Amélioration déjà au maximum !")
        return
    if bank_coins < item["price"]:
        set_shop_message("Pas assez de pièces !")
        return

    bank_coins -= item["price"]
    if kind == "melee":
        permanent_upgrades["melee"] = min(PERMANENT_CAPS["melee"], permanent_upgrades["melee"] + PERMANENT_STEP["melee"])
        game["damage"] = min(7, game["damage"] + 1)
    elif kind == "shot":
        permanent_upgrades["shot"] = min(PERMANENT_CAPS["shot"], permanent_upgrades["shot"] + PERMANENT_STEP["shot"])
        game["shot_damage"] = min(5, game["shot_damage"] + 1)
    elif kind == "maxhp":
        permanent_upgrades["health"] = min(PERMANENT_CAPS["health"], permanent_upgrades["health"] + PERMANENT_STEP["health"])
        raise_max_hp(PERMANENT_STEP["health"])
    elif kind == "speed":
        permanent_upgrades["speed"] = min(PERMANENT_CAPS["speed"], permanent_upgrades["speed"] + PERMANENT_STEP["speed"])
        game["speed"] = min(330, game["speed"] + PERMANENT_STEP["speed"])
    elif kind == "weapon":
        owned_weapons.append(item["weapon"])
        selected_weapon = item["weapon"]
        game["weapon"] = selected_weapon
    elif kind == "arena":
        unlocked_arenas.append(item["arena"])
    elif kind == "melee_style":
        owned_melee_styles.append(item["style"])
        selected_melee_style = item["style"]
        game["melee_style"] = selected_melee_style
    elif kind == "nova_style":
        owned_nova_styles.append(item["style"])
        selected_nova_style = item["style"]
        game["nova_style"] = selected_nova_style

    play_sfx("buy")
    set_shop_message(f"Achat réussi : {item['name']} !", True)
    save_progress()


def open_shop(return_state: str | None = None) -> None:
    global state, shop_return_state
    shop_return_state = return_state or state
    state = "shop"


def close_shop() -> None:
    global state
    state = shop_return_state


# ------------------------------------------------------------
# Ennemis
# ------------------------------------------------------------
def current_difficulty() -> float:
    """Difficulte courante : monte avec le temps de jeu et le numero de vague."""
    return min(game["time"] / DIFF_TIME_SCALE + (game["wave"] - 1) * DIFF_WAVE_STEP, DIFF_MAX)


def spawn_enemy() -> bool:
    """Fait apparaitre un ennemi ; renvoie False si la limite est atteinte."""
    if len(game["enemies"]) >= MAX_ENEMIES:
        return False
    side = random.randrange(4)
    if side == 0:
        pos: tuple[float, float] = (random.randint(25, BASE_W - 25), -20)
    elif side == 1:
        pos = (BASE_W + 20, random.randint(45, BASE_H - 25))
    elif side == 2:
        pos = (random.randint(25, BASE_W - 25), BASE_H + 20)
    else:
        pos = (-20, random.randint(45, BASE_H - 25))

    difficulty = current_difficulty()
    roll = random.random()
    if roll < 0.24:
        kind, hp, radius, color, points = "fast", 2 + int(difficulty), 10, PURPLE, 18
        speed = random.uniform(110, 145) + difficulty * 18
    elif roll < 0.39:
        kind, hp, radius, color, points = "tank", 5 + int(difficulty * 3), 17, RED, 28
        speed = random.uniform(38, 54) + difficulty * 10
    elif roll < 0.57 and game["wave"] >= SHOOTER_FIRST_WAVE:
        kind, hp, radius, color, points = "shooter", 3 + int(difficulty * 2), 12, GOLD, 22
        speed = random.uniform(42, 58) + difficulty * 5
    else:
        kind, hp, radius, color, points = "normal", 3 + int(difficulty * 2), 13, PINK, 12
        speed = random.uniform(58, 88) + difficulty * 16

    hp += max(0, (game["wave"] - 1) // 3)
    game["enemies"].append({
        "pos": pygame.Vector2(pos), "hp": hp, "max_hp": hp, "speed": speed,
        "phase": random.random() * math.tau, "kind": kind, "radius": radius, "color": color,
        "points": points, "knockback": pygame.Vector2(0, 0),
        "attack_timer": random.uniform(*SHOOTER_FIRST_SHOT) if kind == "shooter" else 0.0,
        "boss_type": "", "dash_timer": 0.0, "dash_dir": pygame.Vector2(0, 0),
        "entered": False,
    })
    return True


def spawn_enemy_bullet(pos: pygame.Vector2, direction: pygame.Vector2, speed: float = 220,
                       damage: int = 8, color: Color = ORANGE, radius: int = 7) -> None:
    if direction.length_squared() == 0:
        direction = pygame.Vector2(1, 0)
    game["enemy_projectiles"].append({
        "pos": pygame.Vector2(pos), "vel": pygame.Vector2(direction).normalize() * speed,
        "life": 3.0, "damage": damage, "radius": radius, "color": color,
    })


def spawn_boss() -> None:
    """Un archetype de boss different alterne toutes les cinq vagues."""
    if any(enemy["kind"] == "boss" for enemy in game["enemies"]):
        return
    boss_type = ("BRUTE", "ARTILLERIE", "STORM")[max(0, game["wave"] // 5 - 1) % 3]
    hp = BOSS_HP_BASE + game["wave"] * BOSS_HP_PER_WAVE
    boss_color = ORANGE if boss_type == "BRUTE" else (RED if boss_type == "ARTILLERIE" else PURPLE)
    game["enemies"].append({
        "pos": pygame.Vector2(BASE_W / 2, 80), "hp": hp, "max_hp": hp,
        "speed": 48 + game["wave"] * 0.9, "phase": 0.0, "kind": "boss", "boss_type": boss_type,
        "radius": 33, "color": boss_color, "points": 200 + game["wave"] * 12,
        "knockback": pygame.Vector2(0, 0), "attack_timer": 1.0,
        "dash_timer": 0.0, "dash_dir": pygame.Vector2(0, 0),
    })
    game["boss_spawned"] = True
    add_particles((BASE_W / 2, 80), boss_color, 55, 300)
    add_shake(8)
    play_sfx("boss")


def advance_wave() -> None:
    game["score"] += game["wave"] * 50
    game["hp"] = min(game["max_hp"], game["hp"] + WAVE_CLEAR_HEAL)
    game["wave"] += 1
    game["wave_kills"] = 0
    game["wave_spawned"] = 0
    game["wave_target"] = 8 + game["wave"] * 2
    game["wave_break"] = 2.0
    game["spawn_timer"] = 0.8
    game["boss_spawned"] = False
    game["boss_defeated"] = False


def hurt_enemy(enemy: dict[str, Any], damage: int, direction: pygame.Vector2 | None = None,
               knockback: float = 120) -> None:
    """Applique des degats a un ennemi precis (verification par identite)."""
    enemies = game["enemies"]
    if not any(e is enemy for e in enemies):
        return

    enemy["hp"] -= damage
    if direction is not None and direction.length_squared() > 0:
        enemy["knockback"] += direction.normalize() * knockback

    add_particles(enemy["pos"], enemy["color"], 9, 150)
    add_float_text(enemy["pos"], damage, WHITE)
    play_sfx("hit", 0.04)

    if enemy["hp"] <= 0:
        is_boss = enemy["kind"] == "boss"
        game["score"] += enemy["points"]
        game["kills"] += 1
        if is_boss:
            game["boss_defeated"] = True
            coin_value = 15 + game["wave"]
            game["wave_kills"] = game["wave_target"]
            add_shake(12)
        else:
            game["wave_kills"] += 1
            coin_value = random.randint(1, 3)
        game["coin_pickups"].append({"pos": pygame.Vector2(enemy["pos"]), "value": coin_value,
                                     "phase": random.random() * math.tau, "kind": "coin"})
        if is_boss or random.random() < HEAL_DROP_CHANCE:
            game["coin_pickups"].append({
                "pos": enemy["pos"] + pygame.Vector2(random.uniform(-18, 18), random.uniform(-18, 18)),
                "value": 40 if is_boss else 20, "phase": random.random() * math.tau,
                "kind": "heal", "life": 14.0,
            })
        add_particles(enemy["pos"], GOLD, 42 if is_boss else 18, 260)
        play_sfx("kill", 0.03)
        enemies.remove(enemy)
        gain_xp(5 if is_boss else 1)


def explode_at(pos: pygame.Vector2, radius: float, damage: int, color: Color = GOLD) -> None:
    """Degats de zone (arme FLAK). Les ennemis au bord prennent moitie moins."""
    add_blast(pos, radius, color)
    add_particles(pos, color, 26, 280)
    add_shake(5)
    play_sfx("explode", 0.05)
    for enemy in game["enemies"][:]:
        delta = enemy["pos"] - pos
        distance = delta.length()
        if distance > radius + enemy["radius"]:
            continue
        falloff = 1.0 - 0.5 * clamp(distance / max(1.0, radius), 0.0, 1.0)
        direction = delta.normalize() if distance > 0 else pygame.Vector2(1, 0)
        hurt_enemy(enemy, max(1, int(damage * falloff)), direction, 260)


def damage_player(amount: int, invuln: float = INVULN_CONTACT) -> bool:
    """Inflige des degats au joueur ; renvoie True si le coup a touche."""
    if game["invulnerable"] > 0 or state != "playing":
        return False
    game["hp"] -= amount
    game["invulnerable"] = invuln
    game["hurt_flash"] = 0.35
    add_shake(7)
    add_particles(game["player"], RED, 14, 210)
    play_sfx("hurt")
    if game["hp"] <= 0:
        game["hp"] = 0
        finish_game()
    return True


# ------------------------------------------------------------
# Actions du joueur
# ------------------------------------------------------------
def melee_attack() -> None:
    if game["melee_timer"] > 0 or state != "playing":
        return

    style = game["melee_style"]
    if style == "WHIRLWIND":
        cooldown = max(0.78, game["melee_cd"] * 2.0)
        reach = 118
    elif style == "LANCE":
        cooldown = max(0.52, game["melee_cd"] * 1.35)
        reach = max(game["range"] + 45, 155)
    else:
        cooldown = game["melee_cd"]
        reach = game["range"]
    game["melee_timer"] = cooldown

    player = game["player"]
    facing = game["facing"]
    game["slashes"].append({"pos": pygame.Vector2(player), "life": 0.30, "maxlife": 0.30,
                            "kind": "melee", "style": style, "direction": pygame.Vector2(facing),
                            "radius": reach, "color": CYAN})
    add_particles(player, CYAN, 22 if style == "WHIRLWIND" else 12, 190)
    play_sfx("melee", 0.05)

    hit_any = False
    for enemy in game["enemies"][:]:
        delta = enemy["pos"] - player
        distance = delta.length()
        if distance > reach + enemy["radius"]:
            continue
        if style != "WHIRLWIND" and distance > 0:
            min_dot = 0.50 if style == "LANCE" else -0.05
            if facing.dot(delta.normalize()) < min_dot:
                continue
        direction = delta.normalize() if distance > 0 else facing
        damage = game["damage"] + (1 if style == "LANCE" else 0)
        hurt_enemy(enemy, damage, direction, 240 if style == "LANCE" else 190)
        hit_any = True
    if hit_any:
        add_shake(3)


def shoot_projectile() -> None:
    if game["shot_timer"] > 0 or state != "playing" or game["overheat_timer"] > 0:
        return

    weapon = WEAPONS.get(game["weapon"], WEAPONS["PULSE"])
    game["shot_timer"] = max(0.34, game["shot_cd"] * weapon["cd"])

    player = game["player"]
    direction = pygame.Vector2(game["facing"])      # visee souris
    if direction.length_squared() == 0:
        direction = pygame.Vector2(1, 0)

    mul, bonus = weapon["dmg"]
    damage = max(1, game["shot_damage"] * mul + bonus)
    explode = weapon.get("explode", 0)
    homing = weapon.get("homing", 0.0)

    for angle in weapon["angles"]:
        shot_direction = direction.rotate_rad(angle)
        game["projectiles"].append({
            "pos": pygame.Vector2(player + shot_direction * 22),
            "vel": shot_direction * weapon["speed"],
            "life": 2.4 if homing else 1.5,      # les missiles ont plus de temps pour poursuivre
            "damage": damage, "radius": weapon["radius"],
            "color": weapon["color"], "pierce": weapon["pierce"],
            "explode": explode, "homing": homing, "hit": set(),
            "speed": weapon["speed"],
        })
        add_particles(player + shot_direction * 18, weapon["color"], 2, 85)

    if explode:
        play_sfx("shot", 0.04)
    elif homing:
        play_sfx("missile", 0.06)
    elif weapon["speed"] >= 900:
        play_sfx("laser", 0.05)
    else:
        play_sfx("shot", 0.04)

    game["shot_heat"] = min(100.0, game["shot_heat"] + weapon["heat"])
    if game["shot_heat"] >= 100.0:
        game["overheat_timer"] = 1.0


def use_skill() -> None:
    if game["skill_timer"] > 0 or state != "playing":
        return

    style = game["nova_style"]
    game["skill_timer"] = 7.0 if style == "IMPLOSION" else (6.5 if style == "VORTEX" else 6.0)
    game["skill_flash"] = 0.45
    player = game["player"]
    if style == "VORTEX":
        radius = 195
        damage = max(1, int(game["skill_damage"] * 0.8))
    elif style == "IMPLOSION":
        radius = 125
        damage = int(game["skill_damage"] * 2.0)
    else:
        radius = 165
        damage = game["skill_damage"]

    game["slashes"].append({"pos": pygame.Vector2(player), "life": 0.48, "maxlife": 0.48,
                            "kind": "nova", "style": style, "radius": radius,
                            "direction": pygame.Vector2(1, 0), "color": PURPLE})
    add_particles(player, PURPLE, 48, 320)
    add_shake(10)
    play_sfx("nova")

    for enemy in game["enemies"][:]:
        delta = enemy["pos"] - player
        distance = delta.length()
        if distance <= radius:
            direction = delta.normalize() if distance > 0 else pygame.Vector2(1, 0)
            if style == "VORTEX":
                enemy["knockback"] -= direction * 260
                hurt_enemy(enemy, damage, -direction, 20)
            else:
                hurt_enemy(enemy, damage, direction, 420 if style == "IMPLOSION" else 330)


# ------------------------------------------------------------
# Mises a jour
# ------------------------------------------------------------
def update_player(dt: float, keys: Any) -> None:
    global hud_block

    move = pygame.Vector2(0, 0)
    # ZQSD (AZERTY), WASD (QWERTY) et fleches directionnelles.
    if keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_q]:
        move.x -= 1
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        move.x += 1
    if keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_z]:
        move.y -= 1
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        move.y += 1
    if move.length() > 1:
        move.scale_to_length(1)

    player = game["player"]
    player += move * game["speed"] * dt
    player.x = clamp(player.x, 28, BASE_W - 28)
    player.y = clamp(player.y, 45, BASE_H - 28)

    # Visee a la souris : le personnage regarde le curseur.
    aim = mouse_canvas_pos() - player
    if aim.length_squared() > 16:
        game["facing"] = aim.normalize()

    for key in ("melee_timer", "shot_timer", "skill_timer", "skill_flash", "invulnerable", "overheat_timer"):
        game[key] = max(0.0, game[key] - dt)
    hud_block = max(0.0, hud_block - dt)

    left, middle, right = (False, False, False)
    try:
        left, middle, right = pygame.mouse.get_pressed(num_buttons=3)
    except TypeError:               # pygame 2.0 : pas de parametre num_buttons
        pressed = pygame.mouse.get_pressed()
        if len(pressed) >= 3:
            left, middle, right = pressed[0], pressed[1], pressed[2]

    attacking = keys[pygame.K_SPACE] or left
    shooting = keys[pygame.K_f] or right
    skilling = keys[pygame.K_e] or middle

    # Refroidissement : plus lent quand la gachette reste enfoncee.
    game["shot_heat"] = max(0.0, game["shot_heat"] - (28.0 if shooting else 44.0) * dt)

    if hud_block > 0:               # clic sur un bouton du HUD : on n'attaque pas
        return
    if attacking:
        melee_attack()
    if shooting:
        shoot_projectile()
    if skilling:
        use_skill()


def update_waves(dt: float) -> None:
    game["difficulty"] = current_difficulty()
    game["spawn_timer"] -= dt
    game["wave_break"] = max(0.0, game["wave_break"] - dt)
    if game["wave_break"] > 0:
        return

    if game["wave"] % 5 == 0:       # vague de boss : le boss arrive seul
        if not game["boss_spawned"]:
            if not game["enemies"]:
                spawn_boss()
        elif game["boss_defeated"] and not game["enemies"]:
            advance_wave()
        return

    if game["wave_spawned"] < game["wave_target"]:
        if game["spawn_timer"] <= 0:
            if spawn_enemy():
                game["wave_spawned"] += 1
                game["spawn_timer"] = max(SPAWN_DELAY_MIN,
                                          SPAWN_DELAY_START - min(game["difficulty"], 1.0) * SPAWN_DELAY_GAIN)
            else:
                game["spawn_timer"] = 0.25
    elif game["wave_kills"] >= game["wave_target"] and not game["enemies"]:
        advance_wave()


def update_enemies(dt: float) -> None:
    player = game["player"]
    for enemy in game["enemies"][:]:
        to_player = player - enemy["pos"]
        distance = to_player.length()
        direction = to_player.normalize() if distance > 0 else pygame.Vector2(1, 0)
        kind = enemy["kind"]
        move_dir = direction

        if kind == "shooter":
            pos = enemy["pos"]
            if SHOOTER_FAIR and not enemy["entered"]:
                # Il entre d'abord dans l'arene : jamais de tir depuis le bord de l'ecran.
                if (SHOOTER_MARGIN <= pos.x <= BASE_W - SHOOTER_MARGIN
                        and SHOOTER_TOP <= pos.y <= BASE_H - SHOOTER_MARGIN):
                    enemy["entered"] = True
                    enemy["attack_timer"] = max(enemy["attack_timer"], SHOOTER_TELEGRAPH)
                else:
                    to_center = pygame.Vector2(BASE_W / 2, BASE_H / 2) - pos
                    if to_center.length_squared() > 0:
                        move_dir = to_center.normalize()
            if enemy["entered"] or not SHOOTER_FAIR:
                if distance < 155:
                    move_dir = -direction
                elif distance < 250:
                    move_dir = pygame.Vector2(-direction.y, direction.x)
            enemy["pos"] += move_dir * enemy["speed"] * dt
            enemy["attack_timer"] -= dt
            if (enemy["attack_timer"] <= 0 and distance < SHOOTER_SIGHT
                    and (enemy["entered"] or not SHOOTER_FAIR)):
                spawn_enemy_bullet(enemy["pos"] + direction * (enemy["radius"] + 10), direction,
                                   speed=SHOOTER_BULLET_SPEED, damage=SHOOTER_BULLET_DAMAGE,
                                   color=GOLD, radius=7)
                enemy["attack_timer"] = random.uniform(*SHOOTER_RELOAD)

        elif kind == "boss":
            boss_type = enemy["boss_type"]
            enemy["attack_timer"] -= dt
            if boss_type == "BRUTE":
                if enemy["dash_timer"] <= 0 and enemy["attack_timer"] <= 0:
                    enemy["dash_dir"] = pygame.Vector2(direction)
                    enemy["dash_timer"] = 0.46
                    enemy["attack_timer"] = BRUTE_DASH_RELOAD
                if enemy["dash_timer"] > 0:
                    enemy["dash_timer"] = max(0.0, enemy["dash_timer"] - dt)
                    enemy["pos"] += enemy["dash_dir"] * enemy["speed"] * 2.8 * dt
                elif distance > 1:
                    enemy["pos"] += direction * enemy["speed"] * 0.60 * dt
            else:
                if boss_type == "ARTILLERIE":
                    if distance < 210:
                        move_dir = -direction
                    if enemy["attack_timer"] <= 0:
                        for angle in (-0.22, 0.0, 0.22):
                            shot_dir = direction.rotate_rad(angle)
                            spawn_enemy_bullet(enemy["pos"] + shot_dir * (enemy["radius"] + 10), shot_dir,
                                               speed=ARTILLERY_BULLET_SPEED, damage=ARTILLERY_BULLET_DAMAGE,
                                               color=RED, radius=8)
                        enemy["attack_timer"] = ARTILLERY_RELOAD
                else:                                   # STORM
                    move_dir = pygame.Vector2(-direction.y, direction.x)
                    if enemy["attack_timer"] <= 0:
                        phase = random.random() * math.tau
                        for n in range(STORM_BULLETS):
                            angle = phase + math.tau * n / STORM_BULLETS
                            shot_dir = pygame.Vector2(math.cos(angle), math.sin(angle))
                            spawn_enemy_bullet(enemy["pos"] + shot_dir * (enemy["radius"] + 10), shot_dir,
                                               speed=STORM_BULLET_SPEED, damage=STORM_BULLET_DAMAGE,
                                               color=PURPLE, radius=7)
                        enemy["attack_timer"] = STORM_RELOAD
                if distance > 1:
                    enemy["pos"] += move_dir * enemy["speed"] * 0.72 * dt
            enemy["pos"].x = clamp(enemy["pos"].x, 35, BASE_W - 35)
            enemy["pos"].y = clamp(enemy["pos"].y, 60, BASE_H - 35)

        elif distance > 1:
            enemy["pos"] += move_dir * enemy["speed"] * dt

        enemy["pos"] += enemy["knockback"] * dt
        enemy["knockback"] *= max(0.0, 1 - 8 * dt)
        if kind == "shooter" and SHOOTER_FAIR and enemy["entered"]:    # un tireur entre ne ressort plus
            enemy["pos"].x = clamp(enemy["pos"].x, SHOOTER_MARGIN, BASE_W - SHOOTER_MARGIN)
            enemy["pos"].y = clamp(enemy["pos"].y, SHOOTER_TOP, BASE_H - SHOOTER_MARGIN)

        if player.distance_to(enemy["pos"]) < (PLAYER_CONTACT_RADIUS + enemy["radius"]):
            contact_damage = (CONTACT_DAMAGE_BOSS if kind == "boss"
                              else (CONTACT_DAMAGE_TANK if kind == "tank" else CONTACT_DAMAGE))
            damage_player(contact_damage, INVULN_BOSS if kind == "boss" else INVULN_CONTACT)
            if state != "playing":
                break


def update_projectiles(dt: float) -> None:
    survivors: list[dict[str, Any]] = []
    enemies = game["enemies"]
    for projectile in game["projectiles"]:
        # Missiles : la trajectoire s'incurve vers l'ennemi le plus proche.
        if projectile["homing"] > 0 and enemies:
            target = min(enemies, key=lambda e: projectile["pos"].distance_squared_to(e["pos"]))
            to_target = target["pos"] - projectile["pos"]
            if to_target.length_squared() > 1:
                speed = projectile["speed"]
                desired = to_target.normalize() * speed
                velocity = projectile["vel"]
                if velocity.dot(desired) < -0.98 * speed * speed:
                    steered = velocity.rotate(8)        # cible dans le dos : on amorce le demi-tour
                else:
                    steered = velocity.lerp(desired, min(1.0, projectile["homing"] * dt))
                if steered.length_squared() > 1:
                    steered.scale_to_length(speed)      # un missile qui tourne ne ralentit plus
                    projectile["vel"] = steered

        projectile["pos"] += projectile["vel"] * dt
        projectile["life"] -= dt
        pos = projectile["pos"]
        if (projectile["life"] <= 0 or pos.x < -20 or pos.x > BASE_W + 20
                or pos.y < -20 or pos.y > BASE_H + 20):
            continue

        alive = True
        for enemy in list(enemies):
            if id(enemy) in projectile["hit"]:
                continue
            reach = projectile["radius"] + enemy["radius"]
            if pos.distance_squared_to(enemy["pos"]) < reach * reach:
                if projectile["explode"] > 0:
                    explode_at(pygame.Vector2(pos), projectile["explode"], max(1, projectile["damage"] // 2),
                               projectile["color"])
                hurt_enemy(enemy, projectile["damage"], projectile["vel"], 100)
                if projectile["pierce"] > 0:
                    projectile["pierce"] -= 1
                    projectile["hit"].add(id(enemy))
                else:
                    alive = False
                    break
        if alive:
            survivors.append(projectile)
    game["projectiles"] = survivors


def update_enemy_projectiles(dt: float) -> None:
    player = game["player"]
    survivors: list[dict[str, Any]] = []
    for projectile in game["enemy_projectiles"]:
        projectile["pos"] += projectile["vel"] * dt
        projectile["life"] -= dt
        p = projectile["pos"]
        if projectile["life"] <= 0 or p.x < -30 or p.x > BASE_W + 30 or p.y < -30 or p.y > BASE_H + 30:
            continue
        if p.distance_to(player) < projectile["radius"] + 15:
            if damage_player(projectile["damage"], INVULN_BULLET):
                continue        # le tir est consomme par l'impact
        survivors.append(projectile)
    game["enemy_projectiles"] = survivors


def update_coin_pickups(dt: float) -> None:
    global bank_coins, save_dirty
    player = game["player"]
    remaining: list[dict[str, Any]] = []
    for pickup in game["coin_pickups"]:
        is_heal = pickup.get("kind") == "heal"
        if "life" in pickup:
            pickup["life"] -= dt
            if pickup["life"] <= 0:
                continue
        if is_heal and game["hp"] >= game["max_hp"]:
            remaining.append(pickup)
            continue
        delta = player - pickup["pos"]
        distance = delta.length()
        if 0 < distance < 90:
            pickup["pos"] += delta.normalize() * (130 * dt)
        if distance < 25:
            if is_heal:
                game["hp"] = min(game["max_hp"], game["hp"] + pickup["value"])
                add_float_text(pickup["pos"], f"+{pickup['value']} PV", GREEN)
                add_particles(pickup["pos"], GREEN, 10, 140)
            else:
                bank_coins += pickup["value"]
                save_dirty = True
                add_float_text(pickup["pos"], f"+{pickup['value']}", GOLD)
                add_particles(pickup["pos"], GOLD, 8, 140)
            play_sfx("coin", 0.04)
            continue
        remaining.append(pickup)
    game["coin_pickups"] = remaining


def update_effects(dt: float) -> None:
    alive: list[dict[str, Any]] = []
    for particle in game["particles"]:
        particle["life"] -= dt
        if particle["life"] <= 0:
            continue
        particle["pos"] += particle["vel"] * dt
        particle["vel"] *= max(0.0, 1 - 2.8 * dt)
        alive.append(particle)
    game["particles"] = alive

    for slash in game["slashes"]:
        slash["life"] -= dt
    game["slashes"] = [s for s in game["slashes"] if s["life"] > 0]

    for text in game["texts"]:
        text["life"] -= dt
        text["pos"].y -= 42 * dt
    game["texts"] = [t for t in game["texts"] if t["life"] > 0]

    game["shake"] = max(0.0, game["shake"] - 30 * dt)
    game["hurt_flash"] = max(0.0, game["hurt_flash"] - dt)


def update_game(dt: float, keys: Any) -> None:
    game["time"] += dt
    update_player(dt, keys)
    update_waves(dt)
    update_enemies(dt)
    update_projectiles(dt)
    if state == "playing":
        update_enemy_projectiles(dt)
    update_coin_pickups(dt)
    update_effects(dt)


# ------------------------------------------------------------
# Dessin
# ------------------------------------------------------------
def draw_background(surface: pygame.Surface, t: float) -> None:
    arena_index = game["arena_index"] % len(ARENAS)
    arena = ARENAS[arena_index]
    surface.fill(arena["bg"])

    grid = _grid_surface(arena_index)
    offset = int(t * (24 if arena_index == 1 else 18)) % GRID_SPACING
    surface.blit(grid, (0, offset - GRID_SPACING))

    pygame.draw.rect(surface, arena["edge"], (10, 10, BASE_W - 20, BASE_H - 20), 2, border_radius=18)

    if arena_index == 1:
        for i in range(7):
            x = (i * 137 + int(t * 22)) % BASE_W
            pygame.draw.line(surface, (90, 32, 28), (x, 25), (x - 35, BASE_H - 25), 2)
    elif arena_index == 2:
        for i in range(8):
            x = (i * 121 + int(t * 12)) % BASE_W
            y = 45 + (i * 53) % (BASE_H - 90)
            pygame.draw.rect(surface, (48, 27, 82), (x, y, 18, 18), 1)

    for i in range(12):
        x = (i * 91 + int(t * 30)) % BASE_W
        y = 35 + (i * 47) % (BASE_H - 70)
        pygame.draw.circle(surface, (25, 65, 95), (x, y), 2)


def draw_player(surface: pygame.Surface, player: pygame.Vector2, t: float) -> None:
    x, y = int(player.x), int(player.y)
    glow(surface, (x, y), 20, CYAN, 45)
    if game["invulnerable"] > 0 and int(t * 18) % 2 == 0:
        return
    pygame.draw.circle(surface, CYAN, (x, y), 19, 2)
    pygame.draw.circle(surface, (35, 105, 160), (x, y), 13, 2)
    pygame.draw.circle(surface, (80, 245, 255), (x, y), 9)
    pygame.draw.circle(surface, WHITE, (x, y), 4)
    tip = player + game["facing"] * 23
    pygame.draw.line(surface, WHITE, (x, y), (int(tip.x), int(tip.y)), 3)


def draw_crosshair(surface: pygame.Surface) -> None:
    """Reticule a la souris (visee PC)."""
    pos = mouse_canvas_pos()
    x, y = int(pos.x), int(pos.y)
    pygame.draw.circle(surface, CYAN, (x, y), 11, 1)
    pygame.draw.line(surface, CYAN, (x - 15, y), (x - 5, y), 2)
    pygame.draw.line(surface, CYAN, (x + 5, y), (x + 15, y), 2)
    pygame.draw.line(surface, CYAN, (x, y - 15), (x, y - 5), 2)
    pygame.draw.line(surface, CYAN, (x, y + 5), (x, y + 15), 2)
    pygame.draw.circle(surface, WHITE, (x, y), 2)


def draw_enemy(surface: pygame.Surface, enemy: dict[str, Any], t: float) -> None:
    p = enemy["pos"]
    x, y = int(p.x), int(p.y)
    radius = enemy["radius"]
    color = enemy["color"]
    kind = enemy["kind"]
    pulse = int((5 if kind == "boss" else 2) * math.sin(t * 6 + enemy["phase"]))

    if kind == "shooter":
        glow(surface, (x, y), radius + 15, CYAN, 100)
        to_player = game["player"] - p
        aim = to_player.normalize() if to_player.length_squared() > 0 else pygame.Vector2(1, 0)
        side = pygame.Vector2(-aim.y, aim.x)
        tip = p + aim * (radius + 10)
        back = p - aim * (radius * 0.75)
        p1 = back + side * (radius * 0.95)
        p2 = back - side * (radius * 0.95)
        points = [(int(tip.x), int(tip.y)), (int(p1.x), int(p1.y)), (int(p2.x), int(p2.y))]
        pygame.draw.polygon(surface, (10, 12, 28), points)
        pygame.draw.polygon(surface, WHITE, points, 3)
        pygame.draw.polygon(surface, CYAN, points, 1)
        b0 = p + aim * (radius * 0.25)
        b1 = p + aim * (radius + 20)
        b0i, b1i = (int(b0.x), int(b0.y)), (int(b1.x), int(b1.y))
        pygame.draw.line(surface, (15, 15, 28), b0i, b1i, 10)
        pygame.draw.line(surface, GOLD, b0i, b1i, 5)
        pygame.draw.line(surface, WHITE, b0i, b1i, 2)
        pygame.draw.circle(surface, GOLD, (x, y), 7)
        pygame.draw.circle(surface, WHITE, (x, y), 3)
        if enemy["entered"] and 0 < enemy["attack_timer"] <= SHOOTER_TELEGRAPH:
            # Signal lumineux juste avant le tir : le joueur a le temps de reagir.
            charge = 1.0 - enemy["attack_timer"] / SHOOTER_TELEGRAPH
            end = b1 + aim * (25 + 45 * charge)
            pygame.draw.line(surface, RED, b1i, (int(end.x), int(end.y)), 2)
            glow(surface, b1i, 5 + int(7 * charge), RED, 120)
            pygame.draw.circle(surface, WHITE, b1i, 2 + int(3 * charge))
        draw_text(surface, "SNIPER", small_font, (20, 10, 20), (x + 1, y - radius - 24), center=True)
        draw_text(surface, "SNIPER", small_font, WHITE, (x, y - radius - 25), center=True)
    else:
        glow(surface, (x, y), radius + (12 if kind == "boss" else 4), color, 55 if kind == "boss" else 35)
        if kind == "boss":
            pygame.draw.circle(surface, ORANGE, (x, y), radius + 7 + pulse, 2)
        pygame.draw.circle(surface, color, (x, y), max(3, radius + pulse), 2)
        pygame.draw.circle(surface, (70, 25, 65), (x, y), max(4, radius - 5))
        pygame.draw.circle(surface, WHITE, (x - 3, y - 2), 2)
        pygame.draw.circle(surface, WHITE, (x + 3, y - 2), 2)

    if kind != "boss":       # le boss possede sa grande barre en haut de l'ecran
        bar_w = radius * 2 + 4
        bar_x = x - bar_w // 2
        bar_y = y - radius - 9
        pygame.draw.rect(surface, (15, 10, 25), (bar_x - 1, bar_y - 1, bar_w + 2, 6))
        pygame.draw.rect(surface, (50, 25, 45), (bar_x, bar_y, bar_w, 4))
        ratio = clamp(enemy["hp"] / max(1, enemy["max_hp"]), 0.0, 1.0)
        pygame.draw.rect(surface, color, (bar_x, bar_y, int(bar_w * ratio), 4))


def draw_projectile(surface: pygame.Surface, projectile: dict[str, Any]) -> None:
    p = projectile["pos"]
    x, y = int(p.x), int(p.y)
    color = projectile["color"]
    radius = projectile["radius"]
    glow(surface, (x, y), radius + (3 if projectile["explode"] else 0), color, 65)

    if projectile["homing"] > 0:            # missile : trainee
        vel = projectile["vel"]
        norm = vel.normalize() if vel.length_squared() > 0 else pygame.Vector2(1, 0)
        tail = p - norm * 16
        pygame.draw.line(surface, color, (int(tail.x), int(tail.y)), (x, y), radius + 2)
    elif projectile["radius"] <= 4:         # laser : trait fin et long
        vel = projectile["vel"]
        norm = vel.normalize() if vel.length_squared() > 0 else pygame.Vector2(1, 0)
        tail = p - norm * 26
        pygame.draw.line(surface, color, (int(tail.x), int(tail.y)), (x, y), 3)

    pygame.draw.circle(surface, color, (x, y), radius)
    pygame.draw.circle(surface, WHITE, (x, y), max(2, radius // 2))


def draw_enemy_projectile(surface: pygame.Surface, projectile: dict[str, Any]) -> None:
    p = projectile["pos"]
    direction = pygame.Vector2(projectile["vel"])
    direction = direction.normalize() if direction.length_squared() > 0 else pygame.Vector2(1, 0)
    color = projectile["color"]
    radius = max(6, int(projectile["radius"]))
    head = (int(p.x), int(p.y))
    tail_pos = p - direction * 25
    tail = (int(tail_pos.x), int(tail_pos.y))
    glow(surface, head, radius + 3, color, 120)
    pygame.draw.line(surface, (25, 15, 35), tail, head, radius + 7)
    pygame.draw.line(surface, color, tail, head, radius + 3)
    pygame.draw.line(surface, WHITE, tail, head, max(2, radius // 2))
    pygame.draw.circle(surface, WHITE, head, max(3, radius // 2))


def draw_effects(surface: pygame.Surface) -> None:
    for slash in game["slashes"]:
        p = slash["pos"]
        px, py = int(p.x), int(p.y)
        ratio = max(0.0, slash["life"] / slash["maxlife"])
        kind = slash["kind"]

        if kind == "nova":
            radius = int(slash["radius"] * (1 - ratio)) + 15
            pygame.draw.circle(surface, PURPLE, (px, py), radius, 4)
            pygame.draw.circle(surface, CYAN, (px, py), max(2, radius - 10), 2)
        elif kind == "blast":
            radius = int(slash["radius"] * (1 - ratio * 0.85))
            glow(surface, (px, py), radius, slash["color"], 60)
            pygame.draw.circle(surface, slash["color"], (px, py), max(3, radius), 3)
            pygame.draw.circle(surface, WHITE, (px, py), max(2, int(radius * 0.45)), 2)
        elif slash.get("style") == "LANCE":
            end_pos = p + slash["direction"] * slash["radius"] * (1 - ratio * 0.25)
            pygame.draw.line(surface, CYAN, (px, py), (int(end_pos.x), int(end_pos.y)), 7)
        else:
            radius = int(slash["radius"] * (1 - ratio * 0.25))
            pygame.draw.circle(surface, CYAN, (px, py), radius, 3)


def draw_coin_pickups(surface: pygame.Surface, t: float) -> None:
    for pickup in game["coin_pickups"]:
        p = pickup["pos"]
        bob = math.sin(t * 5 + pickup["phase"]) * 3
        pos = (int(p.x), int(p.y + bob))
        if pickup.get("kind") == "heal":
            if "life" in pickup and pickup["life"] < 3 and int(t * 10) % 2 == 0:
                continue        # clignote avant de disparaitre
            glow(surface, pos, 9, GREEN, 60)
            pygame.draw.circle(surface, (20, 90, 55), pos, 9)
            pygame.draw.circle(surface, GREEN, pos, 9, 2)
            pygame.draw.line(surface, WHITE, (pos[0] - 4, pos[1]), (pos[0] + 4, pos[1]), 2)
            pygame.draw.line(surface, WHITE, (pos[0], pos[1] - 4), (pos[0], pos[1] + 4), 2)
        else:
            glow(surface, pos, 7, GOLD, 55)
            pygame.draw.circle(surface, GOLD, pos, 7)
            pygame.draw.circle(surface, WHITE, pos, 3)


def draw_float_texts(surface: pygame.Surface) -> None:
    for text in game["texts"]:
        draw_text(surface, text["text"], small_font, text["color"], text["pos"], center=True)


def draw_hud(surface: pygame.Surface) -> None:
    # Vie
    pygame.draw.rect(surface, (45, 30, 50), (25, 24, 220, 17), border_radius=8)
    health_width = int(220 * game["hp"] / max(1, game["max_hp"]))
    if health_width > 0:
        color = GREEN if game["hp"] > game["max_hp"] * 0.5 else RED
        pygame.draw.rect(surface, color, (25, 24, health_width, 17), border_radius=8)
    draw_text(surface, f"VIE {game['hp']}/{game['max_hp']}", small_font, WHITE, (27, 45))

    # XP
    pygame.draw.rect(surface, (35, 35, 60), (25, 76, 220, 10), border_radius=5)
    xp_width = int(220 * game["xp"] / max(1, game["xp_needed"]))
    if xp_width > 0:
        pygame.draw.rect(surface, GOLD, (25, 76, xp_width, 10), border_radius=5)
    draw_text(surface, f"XP {game['xp']}/{game['xp_needed']}", small_font, GOLD, (25, 90))

    # Chaleur
    pygame.draw.rect(surface, (25, 35, 65), (25, 115, 150, 8), border_radius=4)
    heat = clamp(game["shot_heat"], 0.0, 100.0)
    overheated = game["overheat_timer"] > 0
    heat_color = RED if overheated else ORANGE
    if heat > 0:
        pygame.draw.rect(surface, heat_color, (25, 115, int(150 * heat / 100), 8), border_radius=4)
    draw_text(surface, "SURCHAUFFE" if overheated else "CHALEUR", small_font, heat_color, (25, 125))

    # Centre
    draw_text(surface, f"NIVEAU {game['level']}", font, CYAN, (BASE_W // 2, 22), center=True)
    wave_text = f"VAGUE {game['wave']} - BOSS" if game["wave"] % 5 == 0 else f"VAGUE {game['wave']}"
    draw_text(surface, wave_text, small_font, ORANGE, (BASE_W // 2, 50), center=True)
    draw_text(surface, f"TIR {game['weapon']} | MÊLÉE {game['melee_style']}", small_font, CYAN,
              (BASE_W // 2, 73), center=True)

    # Colonne de droite
    right_x = BASE_W - 175
    draw_text(surface, f"SCORE {game['score']}", font, GOLD, (right_x, 22))
    draw_text(surface, f"ÉLIMINATIONS {game['kills']}", small_font, WHITE, (right_x, 52))
    ready = game["skill_timer"] <= 0
    skill_name = "NOVA" if game["nova_style"] == "NOVA" else game["nova_style"]
    skill_text = f"{skill_name} PRÊTE" if ready else f"NOVA {game['skill_timer']:.1f}s"
    draw_text(surface, skill_text, small_font, PURPLE if ready else WHITE, (right_x, 72))
    draw_text(surface, f"PIÈCES {bank_coins}", small_font, GOLD, (right_x, 92))

    if state == "playing":
        draw_small_button(surface, SHOP_BUTTON_RECT, "BOUTIQUE", GOLD)
        draw_small_button(surface, QUIT_BUTTON_RECT, "QUITTER", PINK, (45, 25, 50))
        music_color = CYAN if music_enabled else (145, 150, 170)
        draw_small_button(surface, MUSIC_GAME_RECT, "SON ON" if music_enabled else "SON OFF", music_color, (20, 28, 55))
        draw_small_button(surface, PAUSE_BUTTON_RECT, "PAUSE", WHITE, (30, 35, 65))

    draw_text(surface, "ZQSD / FLÈCHES : bouger | SOURIS : viser | CLIC G : mêlée | CLIC D : tir | "
              "MOLETTE / E : NOVA | P : pause",
              tiny_font, (130, 160, 195), (BASE_W // 2, BASE_H - 26), center=True)


def draw_boss_bar(surface: pygame.Surface) -> None:
    boss = next((e for e in game["enemies"] if e["kind"] == "boss"), None)
    if boss is None:
        return
    rect = pygame.Rect(BASE_W // 2 - 170, 96, 340, 12)
    pygame.draw.rect(surface, (15, 10, 25), rect.inflate(4, 4), border_radius=7)
    pygame.draw.rect(surface, (60, 25, 45), rect, border_radius=6)
    width = int(rect.width * clamp(boss["hp"] / max(1, boss["max_hp"]), 0.0, 1.0))
    if width > 0:
        pygame.draw.rect(surface, boss["color"], (rect.x, rect.y, width, rect.height), border_radius=6)
    draw_text(surface, f"BOSS {boss['boss_type']}", small_font, GOLD, (BASE_W // 2, rect.bottom + 12), center=True)


def draw_wave_banner(surface: pygame.Surface) -> None:
    if state != "playing" or game["wave_break"] <= 0:
        return
    is_boss = game["wave"] % 5 == 0
    label = f"VAGUE {game['wave']}" + (" - BOSS !" if is_boss else "")
    color = RED if is_boss else CYAN
    draw_text(surface, label, big_font, (10, 10, 25), (BASE_W // 2 + 2, 202), center=True)
    draw_text(surface, label, big_font, color, (BASE_W // 2, 200), center=True)


def draw_first_steps(surface: pygame.Surface) -> None:
    """Rappel des commandes au tout debut, tant que le joueur n'a encore aucun record."""
    if state != "playing" or best_score > 0 or game["wave"] != 1 or game["time"] > 10.0:
        return
    lines = ("Déplace-toi avec ZQSD ou les flèches, vise avec la souris.",
             "Clic gauche : mêlée   -   Clic droit : tir   -   Clic molette ou E : NOVA")
    for i, line in enumerate(lines):
        y = 392 + i * 26
        draw_text(surface, line, font, (10, 10, 25), (BASE_W // 2 + 1, y + 1), center=True)
        draw_text(surface, line, font, WHITE, (BASE_W // 2, y), center=True)


def draw_overlay(surface: pygame.Surface, title: str, subtitle: str, color: Color = CYAN) -> None:
    draw_shade(surface, 220)
    draw_text(surface, title, title_font, color, (BASE_W // 2, BASE_H // 2 - 75), center=True)
    draw_text(surface, subtitle, font, WHITE, (BASE_W // 2, BASE_H // 2 - 15), center=True)


def draw_levelup(surface: pygame.Surface) -> None:
    draw_shade(surface, 225)
    draw_text(surface, "NOUVEAU NIVEAU !", big_font, GOLD, (BASE_W // 2, 100), center=True)
    draw_text(surface, "Choisis une amélioration", font, WHITE, (BASE_W // 2, 155), center=True)
    ready = game["levelup_timer"] <= 0
    for i, upgrade in enumerate(game["upgrades"]):
        rect = LEVELUP_CARD_RECTS[i]
        pygame.draw.rect(surface, (20, 32, 65), rect, border_radius=14)
        pygame.draw.rect(surface, CYAN if ready else GREY, rect, 2, border_radius=14)
        draw_text(surface, f"{i + 1}. {upgrade[0]}", font, GOLD, (rect.centerx, rect.y + 35), center=True)
        for j, line in enumerate(wrap_text(upgrade[1], 23)):
            draw_text(surface, line, small_font, WHITE, (rect.centerx, rect.y + 75 + j * 24), center=True)
    draw_text(surface, "1, 2, 3 ou clic sur une carte", small_font, CYAN, (BASE_W // 2, 420), center=True)


# ------------------------------------------------------------
# Notice de sante
# ------------------------------------------------------------
# Texte de mise en garde de l'annexe I du decret n° 96-360 du 23 avril 1996 relatif aux mises en
# garde concernant les jeux video. C'est un texte officiel : il est reproduit mot pour mot
# (ne pas le reformuler). Il s'affiche au premier lancement, puis a la demande depuis le menu.
NOTICE_TITLE = "À lire avant toute utilisation d'un jeu vidéo par vous-même ou par votre enfant."
NOTICE_TEXT: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("I. - Précautions à prendre dans tous les cas pour l'utilisation d'un jeu vidéo.", (
        "Évitez de jouer si vous êtes fatigué ou si vous manquez de sommeil.",
        "Assurez-vous que vous jouez dans une pièce bien éclairée en modérant la luminosité de votre écran.",
        "Lorsque vous utilisez un jeu vidéo susceptible d'être connecté à un écran, jouez à bonne distance de "
        "cet écran de télévision et aussi loin que le permet le cordon de raccordement.",
        "En cours d'utilisation, faites des pauses de dix à quinze minutes toutes les heures.",
    )),
    ("II. - Avertissement sur l'épilepsie.", (
        "Certaines personnes sont susceptibles de faire des crises d'épilepsie comportant, le cas échéant, "
        "des pertes de conscience à la vue, notamment, de certains types de stimulations lumineuses fortes : "
        "succession rapide d'images ou répétition de figures géométriques simples, d'éclairs ou d'explosions. "
        "Ces personnes s'exposent à des crises lorsqu'elles jouent à certains jeux vidéo comportant de telles "
        "stimulations, alors même qu'elles n'ont pas d'antécédent médical ou n'ont jamais été sujettes "
        "elles-mêmes à des crises d'épilepsie.",
        "Si vous-même ou un membre de votre famille avez déjà présenté des symptômes liés à l'épilepsie "
        "(crise ou perte de conscience) en présence de stimulations lumineuses, consultez votre médecin "
        "avant toute utilisation.",
        "Les parents se doivent également d'être particulièrement attentifs à leurs enfants lorsqu'ils jouent "
        "avec des jeux vidéo. Si vous-même ou votre enfant présentez un des symptômes suivants : vertige, "
        "trouble de la vision, contraction des yeux ou des muscles, trouble de l'orientation, mouvement "
        "involontaire ou convulsion, perte momentanée de conscience, il faut cesser immédiatement de jouer "
        "et consulter un médecin.",
    )),
)
# Mentions affichees sous la notice : origine du texte, droits sur le jeu, bibliotheque libre utilisee.
NOTICE_CREDITS = (
    "Texte officiel de mise en garde (décret n° 96-360 du 23 avril 1996, annexe I). "
    "Pour le relire : bouton NOTICE SANTÉ du menu.",
    f"{GAME_NAME} {VERSION} © 2026 Quanthevaris - jeu gratuit, tous droits réservés - "
    "quanthevaris.github.io/fission-arena.html",
    "Ce jeu utilise pygame (© Pete Shinners et contributeurs), bibliothèque libre sous licence GNU LGPL : "
    "détails sur la page du jeu.",
)
NOTICE_TOP = 56                 # hauteur de la premiere ligne du texte
NOTICE_BOTTOM = 452             # le texte s'arrete au-dessus de la ligne "ENTREE ou clic : continuer"
_notice_lines: list[tuple[str, pygame.font.Font, Color, int, int]] = []


def wrap_pixels(text: str, font_obj: pygame.font.Font, max_width: int) -> list[str]:
    """Decoupe un texte en lignes qui tiennent dans max_width pixels."""
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = (current + " " + word).strip()
        if current and font_obj.size(candidate)[0] > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def notice_layout() -> list[tuple[str, pygame.font.Font, Color, int, int]]:
    """Lignes de la notice, calculees une seule fois : (texte, police, couleur, x, y).

    La largeur des lettres change un peu d'une version de pygame a l'autre : on garde la premiere
    mise en page (taille de police, marge) avec laquelle tout le texte tient a l'ecran.
    """
    if _notice_lines:
        return _notice_lines
    lines: list[tuple[str, pygame.font.Font, Color, int, int]] = []
    for size, left in ((22, 70), (22, 40), (21, 40), (20, 40), (19, 40), (18, 40), (17, 30), (16, 30)):
        font_obj = small_font if size == 22 else pygame.font.Font(None, size)
        step = font_obj.get_linesize() + 2
        lines = []
        y = NOTICE_TOP
        for heading, paragraphs in NOTICE_TEXT:
            lines.append((heading, font_obj, CYAN, left, y))
            y += step + 6
            for paragraph in paragraphs:
                for line in wrap_pixels(paragraph, font_obj, BASE_W - 2 * left):
                    lines.append((line, font_obj, WHITE, left, y))
                    y += step
                y += 5
            y += 10
        if y - 15 <= NOTICE_BOTTOM:     # 15 = les deux derniers espacements, inutiles apres la derniere ligne
            break
    _notice_lines.extend(lines)
    return _notice_lines


def open_notice(first_launch: bool = False) -> None:
    global state, notice_timer
    state = "notice"
    notice_timer = NOTICE_MIN_TIME if first_launch else 0.0


def close_notice() -> None:
    """Notice lue : retour au menu. Elle ne s'affichera plus d'office aux lancements suivants."""
    global state, notice_seen
    if notice_timer > 0:            # premier lancement : laisse le temps de voir l'avertissement
        return
    state = "menu"
    play_sfx("click")
    if not notice_seen:
        notice_seen = True
        save_progress()


def draw_notice(surface: pygame.Surface) -> None:
    draw_shade(surface, 240)
    draw_text(surface, NOTICE_TITLE, font, GOLD, (BASE_W // 2, 30), center=True)
    for text, font_obj, color, x, y in notice_layout():
        draw_text(surface, text, font_obj, color, (x, y))
    if notice_timer <= 0:
        draw_text(surface, "ENTRÉE ou clic : continuer", font, GREEN, (BASE_W // 2, 472), center=True)
    for i, text in enumerate(NOTICE_CREDITS):
        draw_text(surface, text, tiny_font, (130, 160, 195), (BASE_W // 2, 495 + 16 * i), center=True)


def set_menu_message(message: str, duration: float = 3.0) -> None:
    global menu_message, menu_message_timer
    menu_message = message
    menu_message_timer = duration


def draw_menu(surface: pygame.Surface) -> None:
    draw_shade(surface, 220)
    draw_text(surface, GAME_NAME, title_font, CYAN, (BASE_W // 2, 85), center=True)
    draw_text(surface, "Combats néon - vagues - boss", font, WHITE, (BASE_W // 2, 138), center=True)
    draw_text(surface, f"MEILLEUR SCORE : {best_score}   VAGUE MAX : {best_wave}   PIÈCES : {bank_coins}",
              font, GOLD, (BASE_W // 2, 188), center=True)
    draw_text(surface, f"ARÈNE : {ARENA_NAMES[selected_arena]}  |  ARME : {selected_weapon}",
              small_font, WHITE, (BASE_W // 2, 218), center=True)
    draw_button(surface, MENU_PLAY_RECT, "JOUER", CYAN)
    draw_button(surface, MENU_SHOP_RECT, "BOUTIQUE", GOLD)
    draw_button(surface, MENU_ARENA_RECT, "CHOISIR UNE ARÈNE", PURPLE)

    # Commandes : visibles avant meme la premiere partie.
    draw_text(surface, "ZQSD ou flèches : bouger   |   Souris : viser   |   Clic gauche : mêlée   |   Clic droit : tir",
              small_font, (200, 215, 240), (BASE_W // 2, 440), center=True)
    draw_text(surface, "Clic molette ou E : NOVA   |   P : pause   |   F11 : plein écran",
              small_font, (200, 215, 240), (BASE_W // 2, 462), center=True)

    draw_button(surface, MUSIC_BUTTON_RECT, "SON : ON" if music_enabled else "SON : OFF",
                CYAN if music_enabled else GREY)
    draw_small_button(surface, MENU_NOTICE_RECT, "NOTICE SANTÉ", (200, 215, 240), (20, 25, 45))
    if reset_confirm_timer > 0:
        draw_small_button(surface, MENU_RESET_RECT, "CONFIRMER ?", RED, (60, 20, 35))
        draw_text(surface, "Clique encore pour tout effacer : records, pièces et achats.", small_font, RED,
                  (BASE_W // 2, 489), center=True)
    else:
        draw_small_button(surface, MENU_RESET_RECT, "REMETTRE À ZÉRO", GREY, (20, 25, 45))
        if menu_message_timer > 0:
            draw_text(surface, menu_message, small_font, GREEN, (BASE_W // 2, 489), center=True)
    draw_text(surface, "ENTRÉE : jouer | B : boutique | A : arènes | N : notice | M : son | F11 : plein écran | ÉCHAP : quitter",
              tiny_font, (130, 160, 195), (BASE_W // 2, 520), center=True)


def draw_shop(surface: pygame.Surface) -> None:
    draw_shade(surface, 230)
    draw_text(surface, "BOUTIQUE", title_font, GOLD, (BASE_W // 2, 48), center=True)
    draw_button(surface, SHOP_BACK_RECT, "RETOUR", PINK)
    draw_text(surface, f"Solde : {bank_coins} pièces", font, WHITE, (BASE_W // 2, 91), center=True)

    per_page = len(SHOP_CARD_RECTS)
    page_count = max(1, (len(SHOP_ITEMS) + per_page - 1) // per_page)
    visible_items = SHOP_ITEMS[shop_page * per_page:(shop_page + 1) * per_page]

    for local_index, item in enumerate(visible_items):
        rect = SHOP_CARD_RECTS[local_index]
        kind = item["type"]
        owned = is_item_owned(item)
        capped = is_item_capped(item)
        color = GREEN if owned else (RED if capped else (GOLD if bank_coins >= item["price"] else (105, 115, 140)))
        pygame.draw.rect(surface, (19, 29, 58), rect, border_radius=12)
        pygame.draw.rect(surface, color, rect, 2, border_radius=12)
        draw_text(surface, f"{local_index + 1}. {item['name']}", small_font, WHITE, (rect.centerx, rect.y + 18), center=True)
        draw_text(surface, item["desc"], tiny_font, (200, 215, 240), (rect.centerx, rect.y + 42), center=True)

        if owned and kind == "weapon":
            action = "ÉQUIPÉE" if selected_weapon == item["weapon"] else "ÉQUIPER"
        elif owned and kind == "arena":
            action = "DÉBLOQUÉE - MENU ARÈNES"
        elif owned and kind == "melee_style":
            action = "ÉQUIPÉE" if selected_melee_style == item["style"] else "ÉQUIPER"
        elif owned and kind == "nova_style":
            action = "ÉQUIPÉE" if selected_nova_style == item["style"] else "ÉQUIPER"
        elif capped:
            action = "MAXIMUM"
        else:
            action = f"{item['price']} PIÈCES"
        draw_text(surface, action, small_font, color, (rect.centerx, rect.y + 67), center=True)

    if shop_page > 0:
        draw_button(surface, SHOP_PREV_RECT, "PAGE PRÉCÉDENTE", PURPLE)
    else:
        draw_button(surface, SHOP_PREV_RECT, "DÉBUT", (80, 90, 115), (25, 28, 45))
    if shop_page < page_count - 1:
        draw_button(surface, SHOP_NEXT_RECT, "PAGE SUIVANTE", CYAN)
    else:
        draw_button(surface, SHOP_NEXT_RECT, "FIN", (80, 90, 115), (25, 28, 45))
    draw_text(surface, f"Page {shop_page + 1}/{page_count}", small_font, WHITE, (BASE_W // 2, 436), center=True)

    if shop_message_timer > 0:
        draw_text(surface, shop_message, small_font, GREEN if shop_message_ok else GOLD,
                  (BASE_W // 2, 465), center=True)
    draw_text(surface, "Les arènes se choisissent dans CHOISIR UNE ARÈNE. Un objet déjà acheté se rééquipe gratuitement.",
              tiny_font, WHITE, (BASE_W // 2, 500), center=True)


def draw_arena_select(surface: pygame.Surface) -> None:
    draw_shade(surface, 230)
    draw_text(surface, "CHOIX DE L'ARÈNE", title_font, PURPLE, (BASE_W // 2, 62), center=True)
    draw_text(surface, "Les nouvelles arènes se débloquent dans la boutique", font, WHITE,
              (BASE_W // 2, 112), center=True)
    for i, arena in enumerate(ARENAS):
        rect = ARENA_CARD_RECTS[i]
        unlocked = arena["name"] in unlocked_arenas
        color = arena["accent"] if unlocked else (100, 105, 130)
        pygame.draw.rect(surface, arena["bg"], rect, border_radius=14)
        pygame.draw.rect(surface, color, rect, 3, border_radius=14)
        draw_text(surface, arena["name"], big_font, color, (rect.centerx, rect.y + 48), center=True)
        draw_text(surface, arena["desc"], small_font, WHITE, (rect.centerx, rect.y + 91), center=True)
        status = ("SÉLECTIONNÉE" if selected_arena == i else "CHOISIR") if unlocked else "VERROUILLÉE - BOUTIQUE"
        draw_text(surface, status, small_font, GREEN if unlocked else GOLD, (rect.centerx, rect.y + 133), center=True)
    draw_button(surface, ARENA_BACK_RECT, "RETOUR AU MENU", PINK)


def draw_pause(surface: pygame.Surface) -> None:
    draw_overlay(surface, "PAUSE", "Le jeu est en pause", GOLD)
    draw_button(surface, PAUSE_RESUME_RECT, "REPRENDRE", CYAN)
    draw_button(surface, PAUSE_MENU_RECT, "QUITTER LA PARTIE", PINK)
    draw_text(surface, "P ou ÉCHAP pour reprendre   -   le score est enregistré si tu quittes",
              small_font, (130, 160, 195), (BASE_W // 2, 430), center=True)


def draw_gameover(surface: pygame.Surface) -> None:
    draw_overlay(surface, "GAME OVER",
                 f"Score : {game['score']}   Niveau : {game['level']}   Vague : {game['wave']}", PINK)
    if game["new_record"]:
        draw_text(surface, "NOUVEAU RECORD !", font, GREEN, (BASE_W // 2, 305), center=True)
    else:
        draw_text(surface, f"Meilleur score : {best_score}", font, GOLD, (BASE_W // 2, 305), center=True)
    ready = game["gameover_timer"] <= 0
    draw_button(surface, GAMEOVER_RETRY_RECT, "REJOUER", CYAN if ready else GREY)
    draw_button(surface, GAMEOVER_MENU_RECT, "MENU", PINK if ready else GREY)
    draw_text(surface, "R / ENTRÉE : rejouer   |   ÉCHAP : menu", small_font, (130, 160, 195),
              (BASE_W // 2, 475), center=True)


def render() -> None:
    draw_background(canvas, anim_t)

    for particle in game["particles"]:
        ratio = max(0.0, particle["life"] / particle["maxlife"])
        pos = (int(particle["pos"].x), int(particle["pos"].y))
        pygame.draw.circle(canvas, particle["color"], pos, max(1, int(particle["size"] * ratio)))

    draw_effects(canvas)
    draw_coin_pickups(canvas, anim_t)
    for projectile in game["projectiles"]:
        draw_projectile(canvas, projectile)
    for enemy in game["enemies"]:
        draw_enemy(canvas, enemy, anim_t)
    for projectile in game["enemy_projectiles"]:
        draw_enemy_projectile(canvas, projectile)
    draw_player(canvas, game["player"], anim_t)
    draw_float_texts(canvas)

    if state in ("playing", "paused", "levelup", "gameover"):
        draw_hud(canvas)
        draw_boss_bar(canvas)
        draw_wave_banner(canvas)
        draw_first_steps(canvas)
        if game["hurt_flash"] > 0:
            VIGNETTE.set_alpha(int(255 * min(1.0, game["hurt_flash"] / 0.35)))
            canvas.blit(VIGNETTE, (0, 0))
    if state == "playing":
        draw_crosshair(canvas)

    if state == "menu":
        draw_menu(canvas)
    elif state == "notice":
        draw_notice(canvas)
    elif state == "shop":
        draw_shop(canvas)
    elif state == "arena":
        draw_arena_select(canvas)
    elif state == "paused":
        draw_pause(canvas)
    elif state == "levelup":
        draw_levelup(canvas)
    elif state == "gameover":
        draw_gameover(canvas)


def present() -> None:
    """Affiche le canvas en conservant le ratio 16:9 (bandes noires) + tremblement."""
    shake = game["shake"] if state in ("playing", "gameover") else 0.0
    sx = random.uniform(-shake, shake) * view_scale if shake > 0 else 0
    sy = random.uniform(-shake, shake) * view_scale if shake > 0 else 0
    size = (max(1, int(BASE_W * view_scale)), max(1, int(BASE_H * view_scale)))
    screen.fill((0, 0, 0))
    if size == (BASE_W, BASE_H):
        screen.blit(canvas, (int(view_ox + sx), int(view_oy + sy)))
    else:
        screen.blit(pygame.transform.smoothscale(canvas, size), (int(view_ox + sx), int(view_oy + sy)))
    pygame.display.flip()


def toggle_fullscreen() -> None:
    """F11 : bascule fenetre / plein ecran (le ratio reste 16:9)."""
    global screen, fullscreen
    fullscreen = not fullscreen
    try:
        if fullscreen:
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            screen = pygame.display.set_mode((BASE_W, BASE_H), pygame.RESIZABLE)
    except pygame.error:
        screen = pygame.display.set_mode((BASE_W, BASE_H), pygame.RESIZABLE)
        fullscreen = False


# ------------------------------------------------------------
# Etats de jeu
# ------------------------------------------------------------
def record_run() -> bool:
    """Met a jour les records puis sauvegarde. Renvoie True si nouveau record."""
    global best_score, best_wave
    new_record = False
    if game["started"]:             # ouvrir puis fermer le jeu ne compte pas comme une partie
        new_record = game["score"] > best_score
        best_score = max(best_score, game["score"])
        best_wave = max(best_wave, game["wave"])
    save_progress()
    return new_record


def start_game() -> None:
    global game, state
    game = new_game()
    game["started"] = True
    state = "playing"
    play_sfx("click")


def reset_progress() -> None:
    """Remet toute la progression a zero (records, pieces, achats). Le reglage du son est garde.

    Comme pour un nouveau joueur, la notice de sante s'affichera de nouveau au prochain lancement.
    """
    global game
    apply_save_data({"music_enabled": music_enabled})
    game = new_game()
    save_progress()


def return_to_menu() -> None:
    global game, state
    record_run()
    game = new_game()
    state = "menu"


def finish_game() -> None:
    global state
    state = "gameover"
    game["new_record"] = record_run()
    game["gameover_timer"] = 0.9
    add_shake(14)
    play_sfx("gameover")


def pause_game() -> None:
    global state
    if state == "playing":
        state = "paused"


def handle_hud_buttons(x: float, y: float) -> bool:
    """Boutons du HUD pendant la partie. Renvoie True si le clic est consomme."""
    global hud_block
    point = (int(x), int(y))
    if QUIT_BUTTON_RECT.collidepoint(point):
        pause_game()                # confirmation sur l'ecran de pause (un clic de combat ne quitte plus)
        return True
    if MUSIC_GAME_RECT.collidepoint(point):
        toggle_music()
        return True
    if SHOP_BUTTON_RECT.collidepoint(point):
        open_shop("playing")
        return True
    if PAUSE_BUTTON_RECT.collidepoint(point):
        pause_game()
        return True
    if state == "playing" and (point[1] < 110 or point[0] > BASE_W - 140):
        hud_block = 0.15        # clic sur le HUD : pas d'attaque involontaire
    return False


def handle_click(mx: float, my: float) -> None:
    """Clic gauche dans les menus (tout sauf le gameplay)."""
    global state, selected_arena, shop_page, reset_confirm_timer
    point = (int(mx), int(my))

    if state == "notice":
        close_notice()
        return

    if state == "menu":
        if MENU_RESET_RECT.collidepoint(point):
            play_sfx("click")
            if reset_confirm_timer > 0:         # second clic : on efface vraiment
                reset_confirm_timer = 0.0
                reset_progress()
                set_menu_message("Progression remise à zéro.")
            else:
                reset_confirm_timer = 3.0
            return
        reset_confirm_timer = 0.0
        if MENU_PLAY_RECT.collidepoint(point):
            start_game()
        elif MENU_SHOP_RECT.collidepoint(point):
            play_sfx("click")
            open_shop("menu")
        elif MENU_ARENA_RECT.collidepoint(point):
            play_sfx("click")
            state = "arena"
        elif MENU_NOTICE_RECT.collidepoint(point):
            play_sfx("click")
            open_notice()
        elif MUSIC_BUTTON_RECT.collidepoint(point):
            toggle_music()

    elif state == "shop":
        if SHOP_BACK_RECT.collidepoint(point):
            play_sfx("click")
            close_shop()
            return
        per_page = len(SHOP_CARD_RECTS)
        page_count = (len(SHOP_ITEMS) + per_page - 1) // per_page
        if SHOP_PREV_RECT.collidepoint(point):
            shop_page = max(0, shop_page - 1)
            return
        if SHOP_NEXT_RECT.collidepoint(point):
            shop_page = min(page_count - 1, shop_page + 1)
            return
        for i, rect in enumerate(SHOP_CARD_RECTS):
            index = shop_page * per_page + i
            if index < len(SHOP_ITEMS) and rect.collidepoint(point):
                buy_shop_item(index)
                return

    elif state == "arena":
        if ARENA_BACK_RECT.collidepoint(point):
            state = "menu"
            return
        for i, rect in enumerate(ARENA_CARD_RECTS):
            if rect.collidepoint(point):
                if ARENA_NAMES[i] in unlocked_arenas:
                    selected_arena = i
                    game["arena_index"] = i
                    save_progress()
                    play_sfx("click")
                    state = "menu"
                else:
                    open_shop("arena")
                return

    elif state == "paused":
        if PAUSE_RESUME_RECT.collidepoint(point):
            state = "playing"
        elif PAUSE_MENU_RECT.collidepoint(point):
            return_to_menu()

    elif state == "gameover":
        if game["gameover_timer"] > 0:
            return
        if GAMEOVER_RETRY_RECT.collidepoint(point):
            start_game()
        elif GAMEOVER_MENU_RECT.collidepoint(point):
            return_to_menu()

    elif state == "levelup":
        if game["levelup_timer"] > 0:
            return
        for i in range(len(game["upgrades"])):
            if LEVELUP_CARD_RECTS[i].collidepoint(point):
                apply_upgrade(i)
                return


_KSCAN_1 = getattr(pygame, "KSCAN_1", 30)


def digit_from_key(key: int, scancode: int = 0) -> int:
    """Chiffre 1 a 9 tape au clavier (0 sinon).

    Fonctionne aussi sur un clavier AZERTY sans MAJ (rangee & e " ' ...) et au pave numerique.
    """
    if pygame.K_1 <= key <= pygame.K_9:
        return key - pygame.K_1 + 1
    if pygame.K_KP1 <= key <= pygame.K_KP9:
        return key - pygame.K_KP1 + 1
    if _KSCAN_1 <= scancode <= _KSCAN_1 + 8:      # position physique de la touche
        return scancode - _KSCAN_1 + 1
    return 0


def handle_keydown(key: int, scancode: int = 0) -> None:
    global state, shop_page, running
    digit = digit_from_key(key, scancode)

    if key == pygame.K_F11:
        toggle_fullscreen()
        return

    if state == "notice":
        if key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_ESCAPE, pygame.K_n):
            close_notice()
        return

    if key == pygame.K_ESCAPE:
        if state == "playing":
            pause_game()
        elif state == "paused":
            state = "playing"
        elif state == "shop":
            close_shop()
        elif state == "arena":
            state = "menu"
        elif state == "gameover":
            return_to_menu()
        elif state == "menu":
            running = False
        return

    if key == pygame.K_m:
        toggle_music()
        return

    if key == pygame.K_p:
        if state == "playing":
            pause_game()
        elif state == "paused":
            state = "playing"
        return

    if state == "playing" and key == pygame.K_b:
        open_shop("playing")
    elif state == "menu":
        if key == pygame.K_b:
            open_shop("menu")
        elif key == pygame.K_a:
            state = "arena"
        elif key == pygame.K_n:
            open_notice()
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            start_game()
    elif state == "gameover" and key in (pygame.K_r, pygame.K_RETURN):
        if game["gameover_timer"] <= 0:
            start_game()
    elif state == "paused" and key in (pygame.K_RETURN, pygame.K_SPACE):
        state = "playing"
    elif state == "shop":
        per_page = len(SHOP_CARD_RECTS)
        if digit:
            buy_shop_item(shop_page * per_page + digit - 1)
        elif key == pygame.K_LEFT:
            shop_page = max(0, shop_page - 1)
        elif key == pygame.K_RIGHT:
            shop_page = min((len(SHOP_ITEMS) - 1) // per_page, shop_page + 1)
        elif key == pygame.K_b:
            close_shop()
    elif state == "levelup" and 1 <= digit <= 3:
        apply_upgrade(digit - 1)


# Evenements qui mettent le jeu en pause automatiquement (fenetre en arriere-plan ou reduite).
_PAUSE_EVENTS = tuple(getattr(pygame, name) for name in ("WINDOWFOCUSLOST", "WINDOWMINIMIZED")
                      if hasattr(pygame, name))
_cursor_hidden = False


def update_cursor() -> None:
    """Pendant le combat, seul le reticule du jeu est affiche (pas la fleche du systeme)."""
    global _cursor_hidden
    hide = state == "playing"
    if hide != _cursor_hidden:
        _cursor_hidden = hide
        try:
            pygame.mouse.set_visible(not hide)
        except pygame.error:
            pass


def draw_loading_screen() -> None:
    """Premiere image, affichee pendant que la musique et les sons sont fabriques."""
    canvas.fill(BG)
    draw_text(canvas, GAME_NAME, title_font, CYAN, (BASE_W // 2, BASE_H // 2 - 40), center=True)
    draw_text(canvas, "Chargement...", font, WHITE, (BASE_W // 2, BASE_H // 2 + 35), center=True)
    present()
    pygame.event.pump()


# ------------------------------------------------------------
# Boucle principale
# ------------------------------------------------------------
def main() -> None:
    global running, anim_t, shop_message_timer, menu_message_timer, reset_confirm_timer, notice_timer

    update_view(*screen.get_size())
    draw_loading_screen()
    start_or_update_music()
    init_sfx()
    autosave_timer = 0.0
    running = True
    if not notice_seen:             # premier lancement sur cet ordinateur : notice de sante d'abord
        open_notice(first_launch=True)

    while running:
        dt = min(clock.tick(FPS) / 1000.0, 0.04)
        if _autotest is not None:
            dt = 1.0 / FPS      # verification automatique : meme deroulement sur toutes les machines
        anim_t += dt
        sw, sh = screen.get_size()
        visible = sw > 0 and sh > 0
        if visible:
            update_view(sw, sh)

        shop_message_timer = max(0.0, shop_message_timer - dt)
        menu_message_timer = max(0.0, menu_message_timer - dt)
        reset_confirm_timer = max(0.0, reset_confirm_timer - dt)
        notice_timer = max(0.0, notice_timer - dt)

        # Les evenements sont toujours traites, meme fenetre reduite (sinon elle ne repondrait plus).
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                handle_keydown(event.key, getattr(event, "scancode", 0))
            elif event.type in _PAUSE_EVENTS:
                pause_game()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = screen_to_canvas(*event.pos)
                if state == "playing":
                    handle_hud_buttons(x, y)
                else:
                    handle_click(x, y)

        keys = pygame.key.get_pressed()
        if state == "playing":
            update_game(dt, keys)
        elif state == "levelup":
            game["levelup_timer"] = max(0.0, game["levelup_timer"] - dt)
        elif state == "gameover":
            game["gameover_timer"] = max(0.0, game["gameover_timer"] - dt)
            update_effects(dt)

        autosave_timer += dt
        if autosave_timer >= 5.0:
            autosave_timer = 0.0
            if save_dirty:
                save_progress()

        update_cursor()
        if visible:
            render()
            present()
        if _autotest is not None:
            _autotest_step()

    record_run()
    pygame.quit()


# ------------------------------------------------------------
# Verification automatique (sert uniquement apres la fabrication du .exe)
# ------------------------------------------------------------
# Si la variable d'environnement FISSION_ARENA_AUTOTEST contient un chemin de fichier,
# le jeu joue tout seul une dizaine de secondes, ecrit un rapport a cet endroit puis se ferme.
# Sans cette variable (utilisation normale), rien de ce qui suit ne s'execute.
_autotest: dict[str, Any] | None = None


def _autotest_step() -> None:
    """Scenario : boutique, choix d'arene, partie de quelques secondes, capture d'ecran, fermeture."""
    info = _autotest
    if info is None:
        return
    info["frames"] += 1
    frame = info["frames"]

    def press(key: int) -> None:
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key, scancode=0, unicode="", mod=0))

    if state == "notice":                   # premier lancement : notice de sante, fermee des que possible
        if notice_timer <= 0:
            press(pygame.K_RETURN)
        info["first_frame"] = frame         # le scenario commence quand la notice est fermee
        frame = 0
    else:
        frame -= info["first_frame"]
    script = {10: pygame.K_b, 20: pygame.K_ESCAPE, 28: pygame.K_a, 36: pygame.K_ESCAPE, 44: pygame.K_RETURN}
    if frame in script:
        press(script[frame])
    elif frame > 44:
        if state == "playing":
            # vise l'ennemi le plus proche (sans dependre de la position reelle de la souris) et attaque
            player = game["player"]
            target = min(game["enemies"], key=lambda e: e["pos"].distance_squared_to(player), default=None)
            if target is not None and target["pos"] != player:
                game["facing"] = (target["pos"] - player).normalize()
            melee_attack()
            shoot_projectile()
            use_skill()
        elif state == "levelup" and game["levelup_timer"] <= 0:
            press(pygame.K_1)
    if state not in info["states"]:
        info["states"].append(state)
    if frame == info["last_frame"] - 2 and info["screenshot"]:
        pygame.image.save(canvas, info["screenshot"])
    if frame >= info["last_frame"]:
        info.update(state=state, wave=game["wave"], level=game["level"], kills=game["kills"],
                    score=game["score"], video_driver=pygame.display.get_driver(),
                    window=list(screen.get_size()), sfx=len(_sfx), music=_music_sound is not None,
                    # couleur moyenne de l'image du jeu et de la fenetre : prouve que l'affichage n'est pas noir
                    picture=list(pygame.transform.average_color(canvas))[:3],
                    window_picture=list(pygame.transform.average_color(screen))[:3])
        pygame.event.post(pygame.event.Event(pygame.QUIT))


def run_autotest(report_path: str) -> int:
    """Lance le vrai jeu avec le scenario ci-dessus et ecrit un rapport JSON. Renvoie 0 si tout va bien."""
    global _autotest
    _autotest = {"frames": 0, "first_frame": 0, "last_frame": 600, "states": [],
                 "screenshot": os.environ.get("FISSION_ARENA_AUTOTEST_SHOT", "")}
    report: dict[str, Any] = {
        "ok": False, "game": GAME_NAME, "version": VERSION, "frozen": bool(getattr(sys, "frozen", False)),
        "python": sys.version.split()[0], "pygame": pygame.version.ver,
        "sdl": ".".join(str(n) for n in pygame.get_sdl_version()),
        "audio": AUDIO_AVAILABLE, "mixer": pygame.mixer.get_init() if AUDIO_AVAILABLE else None,
        "save_file": SAVE_FILE, "save_existed": os.path.isfile(SAVE_FILE), "notice_seen": notice_seen,
        # progression au lancement : tout doit etre a zero sur un ordinateur qui n'a jamais lance le jeu
        "start": {"best": best_score, "best_wave": best_wave, "coins": bank_coins,
                  "weapons": list(owned_weapons), "arenas": list(unlocked_arenas),
                  "melee_styles": list(owned_melee_styles), "nova_styles": list(owned_nova_styles),
                  "upgrades": dict(permanent_upgrades)},
    }
    try:
        random.seed(2026)           # memes apparitions d'ennemis a chaque verification
        main()
        report.update({k: v for k, v in _autotest.items() if k not in ("last_frame", "screenshot")})
        report["save_written"] = os.path.isfile(SAVE_FILE)
        report["ok"] = _autotest["frames"] >= _autotest["last_frame"] and "playing" in _autotest["states"]
    except Exception:
        report["error"] = traceback.format_exc()
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
    except OSError:
        return 2
    return 0 if report["ok"] else 1


def save_crash_report() -> str:
    """Erreur imprevue : garde la progression et note l'erreur dans erreur.txt, a cote de la sauvegarde.

    Le fichier reste sur l'ordinateur ; il sert seulement a decrire le probleme si on veut le signaler.
    """
    details = traceback.format_exc()
    path = os.path.join(SAVE_DIR, "erreur.txt")
    try:
        save_progress()
        os.makedirs(SAVE_DIR, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"{GAME_NAME} {VERSION} - Python {sys.version.split()[0]} - pygame {pygame.version.ver}\n\n{details}")
    except Exception:
        return ""
    return path


if __name__ == "__main__":
    _report_path = os.environ.get("FISSION_ARENA_AUTOTEST", "")
    if _report_path:
        sys.exit(run_autotest(_report_path))
    try:
        main()
    except Exception:
        save_crash_report()
        raise
