/* Interface du planner Semaine Claire. Aucun appel réseau, aucune dépendance. */
import {
  DAYS,
  DAY_LABELS,
  PRIORITY_LABELS,
  MAX_TASKS,
  addTask,
  archiveWeek,
  createEmptyState,
  createTask,
  formatShortDate,
  formatWeekRange,
  parseImport,
  progress,
  removeTask,
  selectTopThree,
  serializeState,
  setTaskDay,
  setTaskFocus,
  sortedTasks,
  toISODate,
  toggleDone,
  validateDraft,
  weekDates,
  weekKey
} from "./planner-core.mjs";

const CLE_STOCKAGE = "semaine-claire:v1";
const $ = (identifiant) => document.getElementById(identifiant);

const ui = {
  weekRange: $("week-range"),
  weekBanner: $("week-banner"),
  storageWarning: $("storage-warning"),
  progressBar: $("progress-bar"),
  progressLabel: $("progress-label"),
  statTotal: $("stat-total"),
  statFocus: $("stat-focus"),
  statDone: $("stat-done"),
  taskForm: $("task-form"),
  taskTitle: $("task-title"),
  taskSubject: $("task-subject"),
  taskDue: $("task-due"),
  taskDuration: $("task-duration"),
  taskPriority: $("task-priority"),
  taskDay: $("task-day"),
  formErrors: $("form-errors"),
  sampleBtn: $("sample-btn"),
  autoFocusBtn: $("auto-focus-btn"),
  focusList: $("focus-list"),
  weekBoard: $("week-board"),
  reviewForm: $("review-form"),
  reviewGood: $("review-good"),
  reviewHard: $("review-hard"),
  reviewNext: $("review-next"),
  bannerNewWeekBtn: $("banner-new-week-btn"),
  newWeekBtn: $("new-week-btn"),
  clearBtn: $("clear-btn"),
  printBtn: $("print-btn"),
  exportBtn: $("export-btn"),
  importFile: $("import-file"),
  toast: $("toast"),
  printSheet: $("print-sheet")
};

let etat = chargerEtat();
let minuteurToast;

function nouvelIdentifiant() {
  if (globalThis.crypto && typeof globalThis.crypto.randomUUID === "function") {
    return `t-${globalThis.crypto.randomUUID()}`;
  }
  return `t-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 9)}`;
}

function chargerEtat() {
  try {
    const brut = localStorage.getItem(CLE_STOCKAGE);
    return brut ? parseImport(brut, new Date()) : createEmptyState(new Date());
  } catch {
    return createEmptyState(new Date());
  }
}

function sauvegarderEtat() {
  etat.updatedAt = new Date().toISOString();
  try {
    localStorage.setItem(CLE_STOCKAGE, serializeState(etat));
  } catch {
    ui.storageWarning.hidden = false;
  }
}

function element(balise, classe = "", texte = "") {
  const noeud = document.createElement(balise);
  if (classe) noeud.className = classe;
  if (texte !== "") noeud.textContent = texte;
  return noeud;
}

function messageToast(texte) {
  window.clearTimeout(minuteurToast);
  ui.toast.textContent = texte;
  ui.toast.classList.add("is-visible");
  minuteurToast = window.setTimeout(() => ui.toast.classList.remove("is-visible"), 3400);
}

function definirJourParDefaut() {
  const aujourdhui = new Date();
  const index = (aujourdhui.getDay() + 6) % 7;
  ui.taskDay.value = DAYS[index];
}

function renderProgression() {
  const bilan = progress(etat);
  const focus = etat.tasks.filter((tache) => tache.focus).length;
  ui.progressBar.value = String(bilan.percent);
  ui.progressBar.textContent = `${bilan.percent} %`;
  ui.progressLabel.textContent = bilan.total === 0
    ? "Aucune tâche pour le moment."
    : `${bilan.done} sur ${bilan.total} terminée${bilan.total > 1 ? "s" : ""} · ${bilan.percent} %`;
  ui.statTotal.textContent = String(bilan.total);
  ui.statFocus.textContent = String(focus);
  ui.statDone.textContent = String(bilan.done);
}

function renderPriorites() {
  ui.focusList.replaceChildren();
  const choix = sortedTasks(etat.tasks.filter((tache) => tache.focus));
  if (choix.length === 0) {
    const vide = element("p", "focus-empty", "Aucune priorité choisie. Ajoute des devoirs ou utilise le bouton de sélection automatique.");
    ui.focusList.append(vide);
    return;
  }
  choix.forEach((tache, index) => {
    const carte = element("article", "focus-item");
    carte.append(element("span", "rang", `Priorité ${index + 1}`));
    carte.append(element("h3", "", tache.title));
    const details = [
      tache.subject,
      `${tache.duration} min`,
      DAY_LABELS[tache.day],
      tache.dueDate ? `pour le ${formatShortDate(tache.dueDate)}` : ""
    ].filter(Boolean).join(" · ");
    carte.append(element("p", "", details));
    const bouton = element("button", "btn btn-texte", "Retirer cette priorité");
    bouton.type = "button";
    bouton.dataset.action = "unfocus";
    bouton.dataset.id = tache.id;
    bouton.setAttribute("aria-label", `Retirer la priorité : ${tache.title}`);
    carte.append(bouton);
    ui.focusList.append(carte);
  });
}

function champSelectJour(tache) {
  const champ = element("div", "field deplacer");
  const identifiant = `jour-${tache.id}`;
  const label = element("label", "visually-hidden", "Déplacer cette tâche vers un autre jour");
  label.setAttribute("for", identifiant);
  const select = document.createElement("select");
  select.id = identifiant;
  select.dataset.action = "day";
  select.dataset.id = tache.id;
  select.setAttribute("aria-label", `Jour prévu pour ${tache.title}`);
  DAYS.forEach((jour) => {
    const option = document.createElement("option");
    option.value = jour;
    option.textContent = DAY_LABELS[jour];
    if (jour === tache.day) option.selected = true;
    select.append(option);
  });
  champ.append(label, select);
  return champ;
}

function carteTache(tache) {
  const carte = element("article", `task-card priorite-${tache.priority}`);
  if (tache.done) carte.classList.add("is-done");
  if (tache.focus) carte.classList.add("is-focus");

  const haut = element("div", "task-top");
  const caseFaite = document.createElement("input");
  caseFaite.type = "checkbox";
  caseFaite.className = "task-check";
  caseFaite.checked = tache.done;
  caseFaite.id = `fait-${tache.id}`;
  caseFaite.dataset.action = "done";
  caseFaite.dataset.id = tache.id;
  caseFaite.setAttribute("aria-label", `Marquer comme terminée : ${tache.title}`);
  const titre = element("h4", "task-title", tache.title);
  haut.append(caseFaite, titre);

  const meta = element("p", "task-meta", `${tache.subject} · ${tache.duration} min`);
  const badge = element("span", `priority-badge p${tache.priority}`, PRIORITY_LABELS[tache.priority]);
  const echeance = element("p", "task-due", tache.dueDate ? `Pour le ${formatShortDate(tache.dueDate)}` : "Sans date limite");

  const controles = element("div", "task-controls");
  const boutonFocus = element("button", "", tache.focus ? "★ Priorité" : "☆ Priorité");
  boutonFocus.type = "button";
  boutonFocus.dataset.action = "focus";
  boutonFocus.dataset.id = tache.id;
  boutonFocus.setAttribute("aria-pressed", String(tache.focus));
  boutonFocus.setAttribute("aria-label", tache.focus ? `Retirer la priorité : ${tache.title}` : `Mettre en priorité : ${tache.title}`);

  const boutonSupprimer = element("button", "danger", "Supprimer");
  boutonSupprimer.type = "button";
  boutonSupprimer.dataset.action = "delete";
  boutonSupprimer.dataset.id = tache.id;
  boutonSupprimer.setAttribute("aria-label", `Supprimer : ${tache.title}`);

  controles.append(boutonFocus, boutonSupprimer, champSelectJour(tache));
  carte.append(haut, meta, badge, echeance, controles);
  return carte;
}

function renderSemaine() {
  ui.weekBoard.replaceChildren();
  const parJour = new Map(DAYS.map((jour) => [jour, []]));
  sortedTasks(etat.tasks).forEach((tache) => parJour.get(tache.day).push(tache));

  DAYS.forEach((jour) => {
    const colonne = element("article", "day-column");
    const titre = element("h3", "", DAY_LABELS[jour]);
    const nombre = element("span", "", String(parJour.get(jour).length));
    titre.append(nombre);
    colonne.append(titre);
    const taches = parJour.get(jour);
    if (taches.length === 0) {
      colonne.append(element("p", "day-empty", "Rien de prévu"));
    } else {
      taches.forEach((tache) => colonne.append(carteTache(tache)));
    }
    ui.weekBoard.append(colonne);
  });
}

function renderBilan() {
  ui.reviewGood.value = etat.review.good || "";
  ui.reviewHard.value = etat.review.hard || "";
  ui.reviewNext.value = etat.review.next || "";
}

function renderImpression() {
  ui.printSheet.replaceChildren();

  const entete = element("header", "print-header");
  const gauche = element("div", "");
  gauche.append(element("h1", "", "Semaine Claire"));
  gauche.append(element("p", "", "Ma feuille de semaine · nom de travail"));
  entete.append(gauche, element("p", "", formatWeekRange(etat.weekKey)));
  ui.printSheet.append(entete);

  const blocPriorites = element("section", "print-block");
  blocPriorites.append(element("h2", "", "Mes 3 priorités"));
  const grillePriorites = element("div", "print-priorities");
  const prioritaires = sortedTasks(etat.tasks.filter((tache) => tache.focus));
  for (let i = 0; i < 3; i += 1) {
    const carte = element("div", "");
    carte.append(element("small", "", `Priorité ${i + 1}`));
    const tache = prioritaires[i];
    carte.append(element("div", "", tache ? tache.title : "—"));
    grillePriorites.append(carte);
  }
  blocPriorites.append(grillePriorites);
  ui.printSheet.append(blocPriorites);

  const blocSemaine = element("section", "print-block");
  blocSemaine.append(element("h2", "", "Mon planning"));
  const tableau = document.createElement("table");
  tableau.className = "print-week-table";
  const thead = document.createElement("thead");
  const ligneEntete = document.createElement("tr");
  ["Jour", "Devoirs et révisions", "Fait"].forEach((texte) => {
    const th = document.createElement("th");
    th.scope = "col";
    th.textContent = texte;
    ligneEntete.append(th);
  });
  thead.append(ligneEntete);
  const tbody = document.createElement("tbody");
  const parJour = new Map(DAYS.map((jour) => [jour, []]));
  sortedTasks(etat.tasks).forEach((tache) => parJour.get(tache.day).push(tache));
  DAYS.forEach((jour) => {
    const ligne = document.createElement("tr");
    const celluleJour = document.createElement("th");
    celluleJour.scope = "row";
    celluleJour.textContent = DAY_LABELS[jour];
    const celluleTaches = document.createElement("td");
    const taches = parJour.get(jour);
    if (taches.length === 0) {
      celluleTaches.append(element("div", "print-task-line", ""));
    } else {
      taches.forEach((tache) => {
        const ligneTache = element("div", "print-task-line", tache.title);
        ligneTache.append(element("small", "", ` · ${tache.subject}, ${tache.duration} min`));
        celluleTaches.append(ligneTache);
      });
    }
    const celluleFait = document.createElement("td");
    const toutesFaites = taches.length > 0 && taches.every((tache) => tache.done);
    celluleFait.textContent = toutesFaites ? "☑" : "☐";
    ligne.append(celluleJour, celluleTaches, celluleFait);
    tbody.append(ligne);
  });
  tableau.append(thead, tbody);
  blocSemaine.append(tableau);
  ui.printSheet.append(blocSemaine);

  const blocBilan = element("section", "print-block");
  blocBilan.append(element("h2", "", "Mon bilan de semaine"));
  const grilleBilan = element("div", "print-review");
  [
    ["Ce qui a marché", etat.review.good],
    ["Ce qui a bloqué", etat.review.hard],
    ["Une amélioration", etat.review.next]
  ].forEach(([label, valeur]) => {
    const carte = element("div", "");
    carte.append(element("strong", "", label));
    carte.append(element("span", "", valeur || " "));
    grilleBilan.append(carte);
  });
  blocBilan.append(grilleBilan);
  ui.printSheet.append(blocBilan);
  ui.printSheet.append(element("p", "print-footer", "Semaine Claire · planner local, sans compte · aucune donnée de semaine envoyée à un serveur."));
}

function render() {
  ui.weekRange.textContent = `Semaine ${formatWeekRange(etat.weekKey)}`;
  ui.weekBanner.hidden = etat.weekKey === weekKey(new Date());
  renderProgression();
  renderPriorites();
  renderSemaine();
  renderBilan();
  renderImpression();
}

function ajouterTache(event) {
  event.preventDefault();
  const projet = {
    title: ui.taskTitle.value,
    subject: ui.taskSubject.value,
    dueDate: ui.taskDue.value,
    duration: ui.taskDuration.value,
    priority: ui.taskPriority.value,
    day: ui.taskDay.value
  };
  const verification = validateDraft(projet);
  if (!verification.ok) {
    ui.formErrors.textContent = verification.errors.join(" ");
    ui.formErrors.hidden = false;
    return;
  }
  if (etat.tasks.length >= MAX_TASKS) {
    ui.formErrors.textContent = "Cette semaine contient déjà 200 tâches. Archive-la avant d’en ajouter.";
    ui.formErrors.hidden = false;
    return;
  }
  const tache = createTask(projet, nouvelIdentifiant(), new Date());
  etat = addTask(etat, tache);
  sauvegarderEtat();
  ui.formErrors.hidden = true;
  ui.formErrors.textContent = "";
  ui.taskForm.reset();
  definirJourParDefaut();
  render();
  ui.taskTitle.focus();
  messageToast("Devoir ajouté à ta semaine.");
}

function chargerExemple() {
  if (etat.tasks.length > 0) {
    messageToast("L’exemple s’affiche dans une semaine vide. Efface d’abord tes tâches si tu veux le tester.");
    return;
  }
  const dates = weekDates(new Date());
  const modeles = [
    ["Terminer les exercices 4 et 5 de maths", "Maths", 0, 30, 1, "lundi"],
    ["Apprendre la liste de vocabulaire", "Anglais", 1, 20, 2, "mardi"],
    ["Relire le chapitre sur la Révolution", "Histoire", 2, 45, 2, "mercredi"],
    ["Rendre la rédaction de français", "Français", 3, 60, 1, "jeudi"],
    ["Préparer le contrôle de SVT", "SVT", 5, 90, 3, "samedi"]
  ];
  let brouillon = createEmptyState(new Date());
  modeles.forEach(([title, subject, indexDate, duration, priority, day]) => {
    const tache = createTask({
      title,
      subject,
      dueDate: toISODate(dates[indexDate]),
      duration,
      priority,
      day
    }, nouvelIdentifiant(), new Date());
    brouillon = addTask(brouillon, tache);
  });
  etat = selectTopThree(brouillon);
  sauvegarderEtat();
  render();
  messageToast("Exemple chargé : cinq devoirs et trois priorités.");
}

function actionTache(cible, evenement) {
  const action = cible.dataset.action;
  const identifiant = cible.dataset.id;
  if (!action || !identifiant) return;

  if (action === "done") {
    etat = toggleDone(etat, identifiant);
  } else if (action === "day") {
    etat = setTaskDay(etat, identifiant, cible.value);
  } else if (action === "focus") {
    const tache = etat.tasks.find((item) => item.id === identifiant);
    if (!tache) return;
    if (!tache.focus && etat.tasks.filter((item) => item.focus).length >= 3) {
      messageToast("Trois priorités maximum : retire-en une avant d’en ajouter une autre.");
      return;
    }
    etat = setTaskFocus(etat, identifiant, !tache.focus);
  } else if (action === "unfocus") {
    etat = setTaskFocus(etat, identifiant, false);
  } else if (action === "delete") {
    if (!window.confirm("Supprimer cette tâche de la semaine ?")) return;
    etat = removeTask(etat, identifiant);
    messageToast("Tâche supprimée.");
  } else {
    return;
  }
  sauvegarderEtat();
  render();
}

function demarrerNouvelleSemaine() {
  if (!window.confirm("Archiver le résumé de cette semaine et repartir avec une page vide ?")) return;
  etat = archiveWeek(etat, new Date());
  sauvegarderEtat();
  ui.taskForm.reset();
  definirJourParDefaut();
  render();
  messageToast("Nouvelle semaine prête.");
}

function toutEffacer() {
  if (!window.confirm("Effacer les tâches, le bilan et l’historique local ? Cette action est définitive.")) return;
  etat = createEmptyState(new Date());
  sauvegarderEtat();
  ui.taskForm.reset();
  definirJourParDefaut();
  render();
  messageToast("Données locales effacées.");
}

function exporter() {
  const blob = new Blob([serializeState(etat)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const lien = document.createElement("a");
  lien.href = url;
  lien.download = `semaine-claire-${etat.weekKey}.json`;
  document.body.append(lien);
  lien.click();
  lien.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  messageToast("Sauvegarde JSON téléchargée.");
}

async function importer(evenement) {
  const fichier = evenement.target.files && evenement.target.files[0];
  if (!fichier) return;
  try {
    if (fichier.size > 300000) throw new Error("Fichier trop volumineux.");
    const texte = await fichier.text();
    const imported = parseImport(texte, new Date());
    if (!window.confirm("Remplacer la semaine affichée par cette sauvegarde ?")) return;
    etat = imported;
    sauvegarderEtat();
    render();
    messageToast("Sauvegarde importée.");
  } catch {
    messageToast("Import impossible : le fichier n’est pas une sauvegarde valide.");
  } finally {
    evenement.target.value = "";
  }
}

ui.taskForm.addEventListener("submit", ajouterTache);
ui.sampleBtn.addEventListener("click", chargerExemple);
ui.autoFocusBtn.addEventListener("click", () => {
  if (etat.tasks.length === 0) {
    messageToast("Ajoute d’abord au moins un devoir.");
    return;
  }
  etat = selectTopThree(etat);
  sauvegarderEtat();
  render();
  messageToast("Les trois tâches les plus urgentes sont sélectionnées.");
});
ui.bannerNewWeekBtn.addEventListener("click", demarrerNouvelleSemaine);
ui.newWeekBtn.addEventListener("click", demarrerNouvelleSemaine);
ui.clearBtn.addEventListener("click", toutEffacer);
ui.printBtn.addEventListener("click", () => {
  renderImpression();
  window.print();
});
ui.exportBtn.addEventListener("click", exporter);
ui.importFile.addEventListener("change", importer);

ui.reviewForm.addEventListener("input", (evenement) => {
  const champs = { "review-good": "good", "review-hard": "hard", "review-next": "next" };
  const cle = champs[evenement.target.id];
  if (!cle) return;
  etat.review[cle] = evenement.target.value.slice(0, 600);
  sauvegarderEtat();
  renderImpression();
});

document.addEventListener("click", (evenement) => {
  if (!(evenement.target instanceof Element)) return;
  const cible = evenement.target.closest("[data-action]");
  if (!cible || cible.matches("input, select, textarea")) return;
  actionTache(cible, evenement);
});

document.addEventListener("change", (evenement) => {
  if (!(evenement.target instanceof Element)) return;
  const cible = evenement.target.closest("[data-action]");
  if (!cible) return;
  actionTache(cible, evenement);
});

window.addEventListener("beforeprint", renderImpression);

definirJourParDefaut();
render();
