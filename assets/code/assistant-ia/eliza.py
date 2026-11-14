# © 2026 Quanthevaris — licence MIT (voir LICENCE-MIT.txt).
# -*- coding: utf-8 -*-
"""
ELIZA — adaptation pédagogique simplifiée du chatbot de Joseph Weizenbaum (1966).
Script DOCTOR : mots-clés, réflexion des pronoms, réponses par défaut, mémoire.
"""
import random
import re

# Étape 1 — La réflexion : retourner les pronoms, comme un miroir.
REFLEXION = {
    "i": "you", "me": "you", "my": "your", "myself": "yourself",
    "am": "are", "you": "me", "your": "my", "yours": "mine",
    "yourself": "myself", "are": "am", "mine": "yours",
}

# Les contractions sont dépliées avant tout traitement.
CONTRACTIONS = {
    "i'm": "i am", "i've": "i have", "i'd": "i would", "i'll": "i will",
    "don't": "do not", "can't": "cannot", "won't": "will not",
}

# Étape 2 — Les règles : (motif regex, réponses possibles).
# {0}, {1}… sont remplacés par les morceaux capturés, après réflexion.
REGLES = [
    (r".*\bi am (depressed|sad|unhappy|lonely|afraid|scared|angry|worried)\b.*", [
        "I am sorry to hear you are {0}.",
        "Why do you say you are {0}?",
        "How long have you felt {0}?",
    ]),
    (r".*\bi need\b(.*)", [
        "Why do you need {0}?",
        "Would it really help you to get {0}?",
        "What would it mean to you if you got {0}?",
    ]),
    (r".*\bi (?:feel|think)\b(.*)", [
        "Why do you feel {0}?",
        "Do you often feel {0}?",
        "What makes you feel {0}?",
    ]),
    (r".*(\bmy (?:mother|father|mum|dad|brother|sister|family|boyfriend|girlfriend|friend|wife|husband|son|daughter)\b.*)", [
        "{0}?",
        "Tell me more about your family.",
    ]),
    (r".*\bi remember\b(.*)", [
        "Do you often think of {0}?",
        "What else do you remember?",
        "Why do you remember {0} just now?",
    ]),
    (r".*\bdream\b(.*)", [
        "What does that dream suggest to you?",
        "Do you dream often?",
        "What persons appear in your dreams?",
    ]),
    (r".*\bsorry\b(.*)", [
        "Please do not apologize.",
        "Apologies are not necessary.",
        "What feelings do you have when you apologize?",
    ]),
    (r".*\bno\b(.*)", [
        "Why not?",
        "Are you saying no just to be negative?",
    ]),
    (r".*\byes\b(.*)", [
        "Why do you think so?",
        "I see. And what does that suggest to you?",
    ]),
    (r".*\bperhaps\b(.*)", [
        "You do not seem very certain.",
        "Would you say it is likely, or not?",
    ]),
    (r".*\bhello\b.*", [
        "How do you do. Please state your problem.",
    ]),
    (r".*\byou\b(.*)", [
        "Why do you say I {0}?",
        "What makes you think I {0}?",
        "We were discussing you, not me.",
    ]),
]

# Étape 3 — Les réponses par défaut : le filet de sécurité.
REPONSES_DEFAUT = [
    "Tell me more.",
    "In what way?",
    "Can you be more specific?",
    "I see. And what does that suggest to you?",
    "Why do you say that?",
    "That is interesting. Please go on.",
]

MEMOIRE = []  # La petite réserve d'ELIZA.

def reflechir(texte):
    """Retourne le texte avec les pronoms retournés (my -> your, etc.)."""
    if not texte:
        return ""
    mots = texte.strip(" .!?,;: ").lower().split()
    return " ".join(REFLEXION.get(mot, mot) for mot in mots)

def repondre(phrase):
    """Le cœur d'ELIZA : une phrase entre, une réponse sort."""
    phrase = phrase.lower()
    for contraction, depliee in CONTRACTIONS.items():
        phrase = phrase.replace(contraction, depliee)

    # Parfois, ELIZA ressort un souvenir rangé quelques échanges plus tôt.
    if MEMOIRE and random.random() < 0.25:
        souvenir = MEMOIRE.pop(0)
        return ("Earlier you said you remembered " + souvenir
                + ". Does that have anything to do with now?")

    for motif, reponses in REGLES:
        m = re.match(motif, phrase)
        if m:
            morceaux = [reflechir(g) for g in m.groups()]
            if "remember" in motif:
                MEMOIRE.append(reflechir(m.group(1)))
                del MEMOIRE[:-20]
            reponse = random.choice(reponses).format(*morceaux)
            return reponse[0].upper() + reponse[1:]
    return random.choice(REPONSES_DEFAUT)

def main():
    print("ELIZA — script DOCTOR. Tape 'au revoir' pour quitter.")
    print("ELIZA > How do you do. Please state your problem.")
    while True:
        phrase = input("Toi > ").strip()
        if phrase.lower() in {"au revoir", "quit", "bye", "q"}:
            print("ELIZA > Au revoir. Cela m'a fait plaisir de te parler.")
            break
        if phrase:
            print("ELIZA >", repondre(phrase))

if __name__ == "__main__":
    main()
