#!/usr/bin/env python3
"""Génère le kit A4 remplissable « Semaine Claire » à partir de zéro.

Dépendance : reportlab (voir requirements.txt). Aucun fichier source Canva ou
LibreOffice n'est réutilisé : le contenu, la méthode et la maquette sont nouveaux.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

W, H = A4
M = 42
CW = W - 2 * M
TOTAL = 8

BLEU = colors.HexColor("#135BEA")
BLEU_CLAIR = colors.HexColor("#EEF4FF")
BLEU_TRES_CLAIR = colors.HexColor("#F7F9FD")
MARINE = colors.HexColor("#10233F")
ENCRE = colors.HexColor("#1B2C47")
GRIS = colors.HexColor("#52627B")
GRIS_CLAIR = colors.HexColor("#6C7D96")
LIGNE = colors.HexColor("#B9C9E2")
BLANC = colors.white

_compteur_champs = 0


def nom_champ(prefixe: str) -> str:
    global _compteur_champs
    _compteur_champs += 1
    return f"sc_{prefixe}_{_compteur_champs:03d}"


def texte_enroule(c: canvas.Canvas, texte: str, x: float, y: float, largeur: float,
                  police: str = "Helvetica", taille: float = 10, interligne: float = 14,
                  couleur=GRIS) -> float:
    """Dessine un paragraphe justifié à gauche et renvoie le y final."""
    c.setFont(police, taille)
    c.setFillColor(couleur)
    lignes: list[str] = []
    for paragraphe in texte.split("\n"):
        courante = ""
        for mot in paragraphe.split():
            essai = f"{courante} {mot}".strip()
            if c.stringWidth(essai, police, taille) <= largeur:
                courante = essai
            else:
                if courante:
                    lignes.append(courante)
                courante = mot
        if courante:
            lignes.append(courante)
    for ligne in lignes:
        c.drawString(x, y, ligne)
        y -= interligne
    return y


def carte(c: canvas.Canvas, x: float, y: float, largeur: float, hauteur: float,
          fond=BLEU_TRES_CLAIR, bord=LIGNE, rayon: float = 9):
    c.setFillColor(fond)
    c.setStrokeColor(bord)
    c.setLineWidth(0.8)
    c.roundRect(x, y, largeur, hauteur, rayon, stroke=1, fill=1)


def champ(c: canvas.Canvas, x: float, y: float, largeur: float, hauteur: float,
          prefixe: str, info: str, multiligne: bool = False, maxlen: int = 120):
    c.acroForm.textfield(
        name=nom_champ(prefixe),
        tooltip=info,
        x=x, y=y, width=largeur, height=hauteur,
        borderStyle="underlined",
        borderColor=LIGNE,
        borderWidth=0.7,
        fillColor=BLANC,
        textColor=ENCRE,
        forceBorder=True,
        fieldFlags="multiline" if multiligne else "",
        fontName="Helvetica",
        fontSize=9,
        maxlen=maxlen,
    )


def case(c: canvas.Canvas, x: float, y: float, prefixe: str, info: str = "Fait", taille: float = 13):
    c.acroForm.checkbox(
        name=nom_champ(prefixe),
        tooltip=info,
        x=x, y=y, size=taille,
        checked=False,
        buttonStyle="check",
        shape="square",
        borderStyle="solid",
        borderColor=LIGNE,
        borderWidth=0.7,
        fillColor=BLANC,
        textColor=BLEU,
        forceBorder=True,
        fieldFlags="",
    )


def entete(c: canvas.Canvas, numero: int, surtitre: str, titre: str, signet: str):
    c.bookmarkPage(f"page-{numero}")
    c.addOutlineEntry(signet, f"page-{numero}")
    c.setFillColor(BLEU)
    c.rect(0, H - 8, W, 8, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(BLEU)
    c.drawString(M, H - 38, surtitre.upper())
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(MARINE)
    c.drawString(M, H - 66, titre)
    c.setStrokeColor(LIGNE)
    c.setLineWidth(1)
    c.line(M, H - 77, W - M, H - 77)
    pied(c, numero)


def pied(c: canvas.Canvas, numero: int):
    c.setStrokeColor(LIGNE)
    c.setLineWidth(0.6)
    c.line(M, 39, W - M, 39)
    c.setFont("Helvetica", 7.5)
    c.setFillColor(GRIS_CLAIR)
    c.drawString(M, 25, "Semaine Claire · nom de travail · kit gratuit")
    c.drawRightString(W - M, 25, f"{numero} / {TOTAL}")


def titre_bloc(c: canvas.Canvas, texte: str, y: float):
    c.setFillColor(BLEU)
    c.rect(M, y - 3, 4, 17, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(MARINE)
    c.drawString(M + 12, y, texte)
    return y - 24


def ligne_table(c: canvas.Canvas, x: float, y: float, largeurs: list[float], hauteur: float):
    c.setStrokeColor(LIGNE)
    c.setLineWidth(0.6)
    total = sum(largeurs)
    c.rect(x, y, total, hauteur, stroke=1, fill=0)
    curseur = x
    for largeur in largeurs[:-1]:
        curseur += largeur
        c.line(curseur, y, curseur, y + hauteur)


def page_couverture(c: canvas.Canvas):
    c.bookmarkPage("page-1")
    c.addOutlineEntry("Couverture et rituel", "page-1")
    c.setFillColor(BLEU)
    c.rect(0, H - 10, W, 10, fill=1, stroke=0)
    c.setFillColor(BLEU_CLAIR)
    c.rect(0, 0, W, 110, fill=1, stroke=0)
    c.setFillColor(BLEU)
    p = c.beginPath()
    p.moveTo(W - 170, 110)
    p.lineTo(W, 110)
    p.lineTo(W, 280)
    p.close()
    c.drawPath(p, stroke=0, fill=1)

    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(BLEU)
    c.drawString(M, H - 82, "KIT DE TRAVAIL · A4 · GRATUIT")
    c.setFont("Helvetica-Bold", 44)
    c.setFillColor(MARINE)
    c.drawString(M, H - 160, "SEMAINE")
    c.setFillColor(BLEU)
    c.drawString(M, H - 210, "CLAIRE")
    c.setStrokeColor(BLEU)
    c.setLineWidth(2)
    c.line(M, H - 232, M + 190, H - 232)
    fin = texte_enroule(
        c,
        "Le rituel de 10 minutes pour transformer une pile de devoirs en plan clair. "
        "Pas un énième agenda à remplir : une décision à prendre, puis une semaine à suivre.",
        M, H - 268, CW - 70, "Helvetica", 12, 18, GRIS
    )
    c.setFont("Helvetica", 9.5)
    c.setFillColor(GRIS_CLAIR)
    c.drawString(M, fin - 6, "Collège · lycée · une semaine à la fois")

    y_carte = 278
    carte(c, M, y_carte, CW, 286, BLANC, LIGNE, 14)
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(MARINE)
    c.drawString(M + 24, y_carte + 250, "Le dimanche, 10 minutes")
    c.setFont("Helvetica", 9.5)
    c.setFillColor(GRIS)
    c.drawString(M + 24, y_carte + 230, "Une fois par semaine, dans cet ordre :")
    gestes = [
        ("1", "Vider", "Tout noter, sans trier."),
        ("2", "Choisir", "Garder trois priorités maximum."),
        ("3", "Placer", "Donner un jour à chaque tâche."),
        ("4", "Vérifier", "Cocher, puis préparer la suite."),
    ]
    y = y_carte + 194
    for numero, nom, description in gestes:
        c.setFillColor(BLEU_CLAIR)
        c.roundRect(M + 24, y - 5, 28, 28, 7, stroke=0, fill=1)
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(BLEU)
        c.drawCentredString(M + 38, y + 3, numero)
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(MARINE)
        c.drawString(M + 64, y + 8, nom)
        c.setFont("Helvetica", 9.5)
        c.setFillColor(GRIS)
        c.drawString(M + 150, y + 8, description)
        y -= 43

    c.setFont("Helvetica", 8.5)
    c.setFillColor(MARINE)
    c.drawString(M, 72, "8 pages · remplissable à l’écran ou imprimable · aucune donnée obligatoire")
    c.setFillColor(GRIS_CLAIR)
    c.drawString(M, 52, "Nom de travail : l’identité et les mentions légales définitives seront fixées avant publication officielle.")
    c.setFont("Helvetica", 7.5)
    c.drawRightString(W - M, 25, f"1 / {TOTAL}")
    c.showPage()


def page_vider_choisir(c: canvas.Canvas):
    entete(c, 2, "Étapes 1 et 2", "Vider, puis choisir", "Vider et choisir")
    y = texte_enroule(
        c,
        "Écris d’abord tout ce qui occupe ta tête. Le tri arrive ensuite : trois priorités, pas une de plus.",
        M, H - 105, CW, "Helvetica", 10, 14
    )
    y = titre_bloc(c, "1. Tout sortir de ma tête", y - 12)
    largeurs = [78, 252, 96, 85]
    ligne_table(c, M, y - 27, largeurs, 27)
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(MARINE)
    libelles = ["Matière", "Devoir / contrôle", "Date", "Durée"]
    curseur = M
    for libelle, largeur in zip(libelles, largeurs):
        c.drawString(curseur + 6, y - 18, libelle)
        curseur += largeur
    y -= 27
    for ligne in range(8):
        hauteur = 31
        ligne_table(c, M, y - hauteur, largeurs, hauteur)
        curseur = M
        for index, largeur in enumerate(largeurs):
            champ(c, curseur + 3, y - hauteur + 4, largeur - 6, hauteur - 8,
                  f"inventaire_{ligne}_{index}", libelles[index], maxlen=80)
            curseur += largeur
        y -= hauteur

    y = titre_bloc(c, "2. Mes trois priorités", y - 18)
    carte(c, M, y - 112, CW, 112, BLEU_TRES_CLAIR, LIGNE, 10)
    ecart = 12
    largeur_carte = (CW - 2 * ecart) / 3
    for index in range(3):
        x = M + index * (largeur_carte + ecart)
        c.setFont("Helvetica-Bold", 8.5)
        c.setFillColor(BLEU)
        c.drawString(x + 12, y - 18, f"PRIORITÉ {index + 1}")
        champ(c, x + 12, y - 76, largeur_carte - 24, 52, f"priorite_{index}",
              "Une seule tâche importante", multiligne=True, maxlen=140)
        case(c, x + 12, y - 100, f"priorite_faite_{index}", "Priorité terminée", 12)
        c.setFont("Helvetica", 8)
        c.setFillColor(GRIS_CLAIR)
        c.drawString(x + 31, y - 97, "Fait")
    c.setFont("Helvetica", 8.5)
    c.setFillColor(GRIS_CLAIR)
    c.drawString(M, 55, "Conseil : une priorité doit être assez précise pour être cochée, pas assez vague pour revenir chaque semaine.")
    c.showPage()


def page_placer(c: canvas.Canvas):
    entete(c, 3, "Étape 3", "Placer dans la semaine", "Placer dans la semaine")
    y = texte_enroule(
        c,
        "Donne un jour à chaque tâche. Laisse volontairement des cases vides : une semaine sans imprévu n’existe pas.",
        M, H - 105, CW, "Helvetica", 10, 14
    )
    y = titre_bloc(c, "Ma semaine", y - 12)
    largeurs = [88, 362, 61]
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    hauteur = 72
    for index, jour in enumerate(jours):
        haut = y - hauteur
        ligne_table(c, M, haut, largeurs, hauteur)
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(MARINE)
        c.drawString(M + 9, haut + hauteur / 2 + 2, jour)
        champ(c, M + largeurs[0] + 5, haut + 39, largeurs[1] - 10, 23,
              f"placer_{index}_a", "Tâche principale", maxlen=110)
        champ(c, M + largeurs[0] + 5, haut + 9, largeurs[1] - 10, 23,
              f"placer_{index}_b", "Révision ou seconde tâche", maxlen=110)
        case(c, M + largeurs[0] + largeurs[1] + 23, haut + hauteur / 2 - 7,
             f"placer_fait_{index}", "Jour terminé", 14)
        y -= hauteur
    c.setFont("Helvetica", 8.5)
    c.setFillColor(GRIS_CLAIR)
    c.drawString(M, 55, "Si une tâche reste deux jours de suite, ce n’est pas un échec : c’est une information pour le bilan.")
    c.showPage()


def page_verifier(c: canvas.Canvas):
    entete(c, 4, "Étape 4", "Vérifier sans se juger", "Vérifier")
    y = texte_enroule(
        c,
        "Le but n’est pas d’avoir tout coché. Le but est de voir ce qui est fait, ce qui reste, et ce qui doit changer de place.",
        M, H - 105, CW, "Helvetica", 10, 14
    )
    y = titre_bloc(c, "Ma progression", y - 12)
    jours = ["L", "M", "M", "J", "V", "S", "D"]
    largeur_case = 62
    for index, jour in enumerate(jours):
        x = M + index * (largeur_case + 8)
        carte(c, x, y - 62, largeur_case, 56, BLEU_TRES_CLAIR, LIGNE, 8)
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(BLEU)
        c.drawCentredString(x + largeur_case / 2, y - 22, jour)
        case(c, x + largeur_case / 2 - 7, y - 48, f"progression_{index}", "Journée validée", 14)
    y -= 88

    sections = [
        ("Ce que j’ai terminé", 5, "termine"),
        ("Ce qu’il me reste", 4, "reste"),
        ("Ce que je déplace", 3, "deplace"),
    ]
    for titre, lignes, prefixe in sections:
        y = titre_bloc(c, titre, y)
        for ligne in range(lignes):
            c.setStrokeColor(LIGNE)
            c.setLineWidth(0.7)
            c.line(M + 26, y - 2, W - M, y - 2)
            case(c, M, y - 9, f"{prefixe}_check_{ligne}", "Élément coché", 11)
            champ(c, M + 26, y - 5, CW - 26, 21, f"{prefixe}_{ligne}", titre, maxlen=110)
            y -= 27
        y -= 10
    c.setFont("Helvetica", 8.5)
    c.setFillColor(GRIS_CLAIR)
    c.drawString(M, 55, "Une petite amélioration répétée vaut mieux qu’une grande résolution abandonnée.")
    c.showPage()


def page_revisions(c: canvas.Canvas):
    entete(c, 5, "Bonus", "Contrôles et révisions", "Révisions")
    y = texte_enroule(
        c,
        "Répartir les révisions sur plusieurs jours évite de tout découvrir la veille. Note la date, la durée, puis coche.",
        M, H - 105, CW, "Helvetica", 10, 14
    )
    y = titre_bloc(c, "Mon tableau de révisions", y - 12)
    largeurs = [84, 190, 86, 80, 71]
    libelles = ["Matière", "Chapitre", "Date", "Durée", "Fait"]
    ligne_table(c, M, y - 27, largeurs, 27)
    curseur = M
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(MARINE)
    for libelle, largeur in zip(libelles, largeurs):
        c.drawString(curseur + 6, y - 18, libelle)
        curseur += largeur
    y -= 27
    for ligne in range(7):
        hauteur = 34
        ligne_table(c, M, y - hauteur, largeurs, hauteur)
        curseur = M
        for index, largeur in enumerate(largeurs[:-1]):
            champ(c, curseur + 3, y - hauteur + 5, largeur - 6, hauteur - 10,
                  f"revision_{ligne}_{index}", libelles[index], maxlen=80)
            curseur += largeur
        case(c, M + sum(largeurs[:-1]) + 28, y - hauteur + 10,
             f"revision_fait_{ligne}", "Révision terminée", 13)
        y -= hauteur

    y = titre_bloc(c, "Le plan en trois passages", y - 18)
    largeur_carte = (CW - 24) / 3
    passages = [("J − 5", "Comprendre", "Lire le cours et repérer les points flous."),
                ("J − 2", "Refaire", "Refaire les exercices sans regarder la correction."),
                ("J − 1", "Vérifier", "Revoir uniquement les erreurs et les formules.")]
    for index, (quand, titre, texte) in enumerate(passages):
        x = M + index * (largeur_carte + 12)
        carte(c, x, y - 132, largeur_carte, 132, BLEU_TRES_CLAIR, LIGNE, 10)
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(BLEU)
        c.drawString(x + 12, y - 20, quand)
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(MARINE)
        c.drawString(x + 12, y - 40, titre)
        texte_enroule(c, texte, x + 12, y - 60, largeur_carte - 24,
                      "Helvetica", 8.5, 12, GRIS)
        champ(c, x + 12, y - 110, largeur_carte - 24, 38,
              f"passage_{index}", "Ce que je dois revoir", multiligne=True, maxlen=140)
    c.showPage()


def page_routine(c: canvas.Canvas):
    entete(c, 6, "Bonus", "Ma routine de séance", "Routine de séance")
    y = texte_enroule(
        c,
        "Une routine courte réduit le temps perdu avant de commencer. Coche seulement ce qui t’aide vraiment.",
        M, H - 105, CW, "Helvetica", 10, 14
    )
    y = titre_bloc(c, "Avant / pendant / après", y - 12)
    colonnes = [
        ("Avant", ["Je prépare mon matériel", "Je choisis une seule tâche", "J’éloigne les distractions", "Je fixe une durée"]),
        ("Pendant", ["Je fais une tâche à la fois", "Je pause si je bloque", "Je note la question qui revient", "Je vérifie mon travail"]),
        ("Après", ["Je coche ce qui est fait", "Je note ce qu’il reste", "Je range mes affaires", "Je prépare la prochaine séance"]),
    ]
    largeur_carte = (CW - 24) / 3
    for index, (titre, gestes) in enumerate(colonnes):
        x = M + index * (largeur_carte + 12)
        carte(c, x, y - 205, largeur_carte, 205, BLANC, LIGNE, 10)
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(BLEU)
        c.drawString(x + 14, y - 25, titre)
        y_case = y - 55
        for geste_index, geste in enumerate(gestes):
            case(c, x + 14, y_case - 4, f"routine_{index}_{geste_index}", geste, 12)
            texte_enroule(c, geste, x + 34, y_case, largeur_carte - 48,
                          "Helvetica", 8.6, 11, ENCRE)
            y_case -= 38
    y -= 230
    y = titre_bloc(c, "Ma règle de concentration", y)
    champ(c, M, y - 76, CW, 70, "regle_concentration",
          "Une règle simple pour mes séances", multiligne=True, maxlen=260)
    y -= 100
    y = titre_bloc(c, "Ce que j’éloigne pendant une séance", y)
    champ(c, M, y - 30, CW, 28, "distraction", "Une distraction à éloigner", maxlen=120)
    c.setFont("Helvetica", 8.5)
    c.setFillColor(GRIS_CLAIR)
    c.drawString(M, 55, "Une routine simple, répétée, vaut mieux qu’une routine parfaite, abandonnée.")
    c.showPage()


def page_bilan(c: canvas.Canvas):
    entete(c, 7, "Étape 4 · suite", "Mon bilan de la semaine", "Bilan de semaine")
    y = texte_enroule(
        c,
        "Deux minutes suffisent. Réponds sans chercher la phrase parfaite : une seule amélioration pour la semaine suivante.",
        M, H - 105, CW, "Helvetica", 10, 14
    )
    questions = [
        ("Ce qui a marché", "Un geste, un jour ou une décision qui m’a aidé."),
        ("Ce qui a été difficile", "Le moment où j’ai perdu le fil, sans jugement."),
        ("Ce que je change", "Une seule chose, assez petite pour être tenue."),
    ]
    for index, (titre, aide) in enumerate(questions):
        y = titre_bloc(c, titre, y - 4)
        c.setFont("Helvetica", 9)
        c.setFillColor(GRIS_CLAIR)
        c.drawString(M, y - 2, aide)
        champ(c, M, y - 82, CW, 72, f"bilan_{index}",
              titre, multiligne=True, maxlen=360)
        y -= 100
    y = titre_bloc(c, "Une seule amélioration pour la semaine prochaine", y - 2)
    champ(c, M, y - 56, CW, 50, "amelioration",
          "Une seule amélioration", multiligne=True, maxlen=220)
    y -= 72
    y = titre_bloc(c, "Ma première priorité de la semaine prochaine", y)
    champ(c, M, y - 30, CW, 28, "priorite_suivante", "Une tâche précise", maxlen=140)
    c.setFont("Helvetica", 8.5)
    c.setFillColor(GRIS_CLAIR)
    c.drawString(M, 55, "Chaque semaine est une nouvelle occasion de repartir, pas une note à rattraper.")
    c.showPage()


def page_relancer(c: canvas.Canvas):
    entete(c, 8, "Et ensuite", "Relancer la semaine", "Relancer la semaine")
    y = texte_enroule(
        c,
        "Le kit est fait pour être recommencé, pas collectionné. Le dimanche suivant, reprends les quatre gestes.",
        M, H - 105, CW, "Helvetica", 10, 14
    )
    y = titre_bloc(c, "Check-list du dimanche", y - 12)
    gestes = [
        "Je regarde mon bilan de la semaine précédente",
        "Je vide les nouveaux devoirs",
        "Je choisis trois priorités maximum",
        "Je place les tâches et je laisse des cases libres",
    ]
    for index, geste in enumerate(gestes):
        case(c, M, y - 6, f"relance_check_{index}", geste, 13)
        c.setFont("Helvetica", 10)
        c.setFillColor(ENCRE)
        c.drawString(M + 25, y - 2, geste)
        y -= 38

    y -= 12
    y = titre_bloc(c, "Ma première tâche de la semaine", y)
    champ(c, M, y - 34, CW, 30, "premiere_tache", "Une tâche précise", maxlen=140)
    y -= 56
    c.setFont("Helvetica", 9)
    c.setFillColor(GRIS_CLAIR)
    c.drawString(M, y, "Matière")
    c.drawString(M + 180, y, "Jour prévu")
    c.drawString(M + 360, y, "Durée")
    champ(c, M, y - 32, 160, 28, "premiere_matiere", "Matière", maxlen=60)
    champ(c, M + 180, y - 32, 160, 28, "premiere_jour", "Jour prévu", maxlen=60)
    champ(c, M + 360, y - 32, CW - 360, 28, "premiere_duree", "Durée", maxlen=60)
    y -= 70

    y = titre_bloc(c, "Version numérique, même méthode", y)
    carte(c, M, y - 132, CW, 132, BLEU_CLAIR, LIGNE, 12)
    texte_enroule(
        c,
        "Le planner web reprend les quatre mêmes gestes. Il fonctionne sans compte, enregistre la semaine dans le navigateur, "
        "permet d’exporter une sauvegarde et imprime une feuille A4. Le kit PDF reste utilisable seul, sans connexion.",
        M + 18, y - 28, CW - 36, "Helvetica", 9.5, 14, ENCRE
    )
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(MARINE)
    c.drawString(M + 18, y - 105, "8 pages · une méthode · aucune donnée obligatoire")
    c.showPage()


def generer(sortie: Path):
    sortie.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(sortie), pagesize=A4, pageCompression=1)
    c.setTitle("Semaine Claire — kit d’organisation scolaire")
    c.setAuthor("Semaine Claire (nom de travail)")
    c.setSubject("Kit A4 remplissable : vider, choisir, placer, vérifier")
    c.setKeywords("organisation scolaire, devoirs, planner, collège, lycée, gratuit")
    c.setCreator("generer-kit.py — Semaine Claire")
    page_couverture(c)
    page_vider_choisir(c)
    page_placer(c)
    page_verifier(c)
    page_revisions(c)
    page_routine(c)
    page_bilan(c)
    page_relancer(c)
    c.save()
    print(f"PDF généré : {sortie} ({sortie.stat().st_size} octets)")


if __name__ == "__main__":
    racine = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sortie", type=Path, default=racine / "assets/pdf/kit-semaine-claire.pdf")
    args = parser.parse_args()
    generer(args.sortie)
