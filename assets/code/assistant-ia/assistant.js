/* Pixel local — © 2026 Quanthevaris, MIT. Pas de stockage navigateur. */
'use strict';
const form = document.getElementById('form');
const champ = document.getElementById('texte');
const envoyer = document.getElementById('envoyer');
const effacer = document.getElementById('effacer');
const etat = document.getElementById('etat');
const chat = document.getElementById('chat');
let historique = [];
let occupe = false;

function ajoute(auteur, texte, erreur = false) {
  const boite = document.createElement('div');
  boite.className = 'message ' + (auteur === 'TOI' ? 'toi' : 'bot') + (erreur ? ' erreur' : '');
  const nom = document.createElement('span');
  nom.className = 'auteur'; nom.textContent = auteur;
  const contenu = document.createElement('p');
  contenu.textContent = texte; // jamais innerHTML : une réponse reste du texte
  boite.append(nom, contenu); chat.appendChild(boite);
  chat.scrollTop = chat.scrollHeight;
  return contenu;
}

async function verifier() {
  if (location.protocol === 'file:') {
    etat.textContent = 'Lance python serveur.py puis ouvre http://127.0.0.1:5000.';
    envoyer.disabled = true; return;
  }
  try {
    const r = await fetch('/api/status', {signal: AbortSignal.timeout(7000)});
    const d = await r.json();
    etat.textContent = (d.pret ? 'PRÊT · ' : 'À VÉRIFIER · ') + d.modele + ' — ' + d.information;
  } catch {
    etat.textContent = 'Serveur local injoignable. Ouvre cette page depuis python serveur.py.';
  }
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const message = champ.value.trim();
  if (occupe || !message) return;
  if (message.length > 2000) { etat.textContent = '2 000 caractères maximum.'; return; }
  occupe = true; envoyer.disabled = true; effacer.disabled = true;
  ajoute('TOI', message); champ.value = '';
  const attente = ajoute('PIXEL', 'Génération locale en cours… Le premier chargement peut être lent.');
  try {
    const contexte = historique.slice();
    while (new TextEncoder().encode(JSON.stringify({message, historique: contexte})).length > 60000 && contexte.length) {
      contexte.splice(0, 2); // garde des paires, même avec de longs textes Unicode
    }
    const r = await fetch('/api/chat', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message, historique: contexte}),
      signal: AbortSignal.timeout(200000)
    });
    const d = await r.json();
    if (!r.ok || typeof d.reponse !== 'string') throw new Error(d.erreur || 'Réponse invalide.');
    attente.textContent = d.reponse;
    historique = [...contexte, {role: 'user', content: message}, {role: 'assistant', content: d.reponse}].slice(-12);
    etat.textContent = 'LOCAL · ' + d.modele + ' · ' + (historique.length / 2) + '/6 échanges en contexte';
  } catch (erreur) {
    attente.textContent = erreur.name === 'TimeoutError'
      ? 'Délai dépassé. Attends la fin du calcul dans Ollama, puis réessaie.'
      : (erreur instanceof TypeError ? 'Serveur injoignable. Vérifie python serveur.py.' : erreur.message);
    attente.parentElement.classList.add('erreur');
    // Un échec ne pollue pas l'historique envoyé au modèle.
  } finally {
    occupe = false; envoyer.disabled = false; effacer.disabled = false;
    chat.scrollTop = chat.scrollHeight; champ.focus();
  }
});

effacer.addEventListener('click', () => {
  if (occupe) return;
  historique = []; chat.replaceChildren();
  ajoute('PIXEL', 'Nouvelle discussion. Le contexte de cet onglet a été effacé.');
  champ.value = ''; champ.focus(); verifier();
});
verifier();
