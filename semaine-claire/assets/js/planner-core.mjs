/* Logique métier du planner, sans DOM : testable avec Node, réutilisable par le navigateur. */

export const DAYS = Object.freeze([
  "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"
]);

export const DAY_LABELS = Object.freeze({
  lundi: "Lundi",
  mardi: "Mardi",
  mercredi: "Mercredi",
  jeudi: "Jeudi",
  vendredi: "Vendredi",
  samedi: "Samedi",
  dimanche: "Dimanche"
});

export const PRIORITY_LABELS = Object.freeze({
  1: "Urgent",
  2: "Important",
  3: "Plus tard"
});

export const MAX_TASKS = 200;
export const MAX_HISTORY = 12;
const MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"];
const MOIS_COURTS = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."];

function nettoyer(valeur, longueur) {
  if (typeof valeur !== "string") return "";
  return valeur.trim().replace(/\s+/g, " ").slice(0, longueur);
}

function dateLocale(valeur) {
  if (valeur instanceof Date) {
    const copie = new Date(valeur.getTime());
    copie.setHours(12, 0, 0, 0);
    return copie;
  }
  if (typeof valeur === "string" && /^\d{4}-\d{2}-\d{2}$/.test(valeur)) {
    const [annee, mois, jour] = valeur.split("-").map(Number);
    return new Date(annee, mois - 1, jour, 12);
  }
  if (typeof valeur === "number" || typeof valeur === "string") {
    const date = new Date(valeur);
    if (!Number.isNaN(date.getTime())) {
      date.setHours(12, 0, 0, 0);
      return date;
    }
  }
  const maintenant = new Date();
  maintenant.setHours(12, 0, 0, 0);
  return maintenant;
}

export function toISODate(date = new Date()) {
  const d = dateLocale(date);
  const annee = d.getFullYear();
  const mois = String(d.getMonth() + 1).padStart(2, "0");
  const jour = String(d.getDate()).padStart(2, "0");
  return `${annee}-${mois}-${jour}`;
}

export function isValidISODate(valeur) {
  if (typeof valeur !== "string") return false;
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(valeur);
  if (!match) return false;
  const annee = Number(match[1]);
  const mois = Number(match[2]);
  const jour = Number(match[3]);
  const date = new Date(annee, mois - 1, jour, 12);
  return date.getFullYear() === annee && date.getMonth() === mois - 1 && date.getDate() === jour;
}

export function startOfWeek(date = new Date()) {
  const d = dateLocale(date);
  const decalage = (d.getDay() + 6) % 7; // lundi = 0
  d.setDate(d.getDate() - decalage);
  return d;
}

export function weekDates(date = new Date()) {
  const debut = startOfWeek(date);
  return DAYS.map((_, index) => {
    const d = new Date(debut.getTime());
    d.setDate(debut.getDate() + index);
    return d;
  });
}

export function weekKey(date = new Date()) {
  return toISODate(startOfWeek(date));
}

export function formatWeekRange(date = new Date()) {
  const dates = weekDates(date);
  const debut = dates[0];
  const fin = dates[6];
  const p1 = { j: debut.getDate(), m: MOIS[debut.getMonth()], a: debut.getFullYear() };
  const p2 = { j: fin.getDate(), m: MOIS[fin.getMonth()], a: fin.getFullYear() };
  if (p1.m === p2.m && p1.a === p2.a) return `du ${p1.j} au ${p2.j} ${p2.m} ${p2.a}`;
  if (p1.a === p2.a) return `du ${p1.j} ${p1.m} au ${p2.j} ${p2.m} ${p2.a}`;
  return `du ${p1.j} ${p1.m} ${p1.a} au ${p2.j} ${p2.m} ${p2.a}`;
}

export function formatShortDate(iso) {
  if (!isValidISODate(iso)) return "";
  const [annee, mois, jour] = iso.split("-").map(Number);
  const date = new Date(annee, mois - 1, jour, 12);
  return `${date.getDate()} ${MOIS_COURTS[date.getMonth()]}`;
}

export function createEmptyState(date = new Date()) {
  return {
    version: 1,
    weekKey: weekKey(date),
    tasks: [],
    review: { good: "", hard: "", next: "" },
    history: [],
    updatedAt: null
  };
}

export function normalizeTask(raw, index = 0) {
  if (!raw || typeof raw !== "object") return null;
  const title = nettoyer(raw.title, 120);
  if (!title) return null;
  const subject = nettoyer(raw.subject, 40) || "Autre";
  const dueDate = isValidISODate(raw.dueDate) ? raw.dueDate : "";
  const dureeBrute = Number(raw.duration);
  const duration = Number.isFinite(dureeBrute)
    ? Math.min(240, Math.max(5, Math.round(dureeBrute / 5) * 5))
    : 30;
  const prioriteBrute = Number(raw.priority);
  const priority = Number.isFinite(prioriteBrute)
    ? Math.min(3, Math.max(1, Math.round(prioriteBrute)))
    : 2;
  const day = DAYS.includes(raw.day) ? raw.day : "lundi";
  return {
    id: nettoyer(raw.id, 80) || `t-${index}`,
    title,
    subject,
    dueDate,
    duration,
    priority,
    day,
    done: raw.done === true,
    focus: raw.focus === true,
    createdAt: nettoyer(raw.createdAt, 40)
  };
}

export function normalizeState(raw, date = new Date()) {
  const source = raw && typeof raw === "object" ? raw : {};
  const tasks = [];
  const vus = new Set();
  if (Array.isArray(source.tasks)) {
    source.tasks.slice(0, MAX_TASKS).forEach((brut, index) => {
      const tache = normalizeTask(brut, index);
      if (!tache) return;
      let identifiant = tache.id;
      if (vus.has(identifiant)) identifiant = `${identifiant}-${index}`;
      vus.add(identifiant);
      tasks.push({ ...tache, id: identifiant });
    });
  }
  let focusCount = 0;
  const tasksLimitees = tasks.map((tache) => {
    if (!tache.focus) return tache;
    if (focusCount >= 3) return { ...tache, focus: false };
    focusCount += 1;
    return tache;
  });

  const brutBilan = source.review && typeof source.review === "object" ? source.review : {};
  const review = {
    good: nettoyer(brutBilan.good, 600),
    hard: nettoyer(brutBilan.hard, 600),
    next: nettoyer(brutBilan.next, 600)
  };

  const history = Array.isArray(source.history)
    ? source.history.slice(-MAX_HISTORY).map((entree) => ({
        weekKey: nettoyer(entree?.weekKey, 10),
        closedAt: nettoyer(entree?.closedAt, 40),
        done: Math.max(0, Number(entree?.done) || 0),
        total: Math.max(0, Number(entree?.total) || 0),
        percent: Math.min(100, Math.max(0, Number(entree?.percent) || 0)),
        next: nettoyer(entree?.next, 200)
      })).filter((entree) => isValidISODate(entree.weekKey))
    : [];

  return {
    version: 1,
    weekKey: isValidISODate(source.weekKey) ? source.weekKey : weekKey(date),
    tasks: tasksLimitees,
    review,
    history,
    updatedAt: nettoyer(source.updatedAt, 40) || null
  };
}

export function validateDraft(draft) {
  const donnees = draft && typeof draft === "object" ? draft : {};
  const errors = [];
  const title = nettoyer(donnees.title, 120);
  const subject = nettoyer(donnees.subject, 40) || "Autre";
  const dueDate = nettoyer(donnees.dueDate, 10);
  const duration = Number(donnees.duration);
  const priority = Number(donnees.priority);
  const day = donnees.day;

  if (!title) errors.push("Ajoute un intitulé de devoir.");
  if (title.length > 120) errors.push("L’intitulé dépasse 120 caractères.");
  if (dueDate && !isValidISODate(dueDate)) errors.push("La date limite n’est pas valide.");
  if (!Number.isFinite(duration) || duration < 5 || duration > 240) errors.push("Choisis une durée valide.");
  if (!Number.isFinite(priority) || ![1, 2, 3].includes(priority)) errors.push("Choisis une priorité valide.");
  if (!DAYS.includes(day)) errors.push("Choisis un jour de la semaine.");

  return {
    ok: errors.length === 0,
    errors,
    values: { title, subject, dueDate, duration, priority, day }
  };
}

export function createTask(draft, id, date = new Date()) {
  const { ok, values } = validateDraft(draft);
  if (!ok) return null;
  return {
    id: nettoyer(id, 80) || `t-${Date.now()}`,
    ...values,
    done: false,
    focus: false,
    createdAt: new Date(date).toISOString()
  };
}

export function addTask(state, task) {
  if (!task || state.tasks.length >= MAX_TASKS) return normalizeState(state);
  return normalizeState({ ...state, tasks: [...state.tasks, task] });
}

export function updateTask(state, id, patch) {
  return normalizeState({
    ...state,
    tasks: state.tasks.map((tache) => tache.id === id ? { ...tache, ...patch } : tache)
  });
}

export function removeTask(state, id) {
  return normalizeState({ ...state, tasks: state.tasks.filter((tache) => tache.id !== id) });
}

export function toggleDone(state, id) {
  const tache = state.tasks.find((item) => item.id === id);
  if (!tache) return normalizeState(state);
  return updateTask(state, id, { done: !tache.done });
}

export function setTaskDay(state, id, day) {
  if (!DAYS.includes(day)) return normalizeState(state);
  return updateTask(state, id, { day });
}

export function setTaskFocus(state, id, focus) {
  const tache = state.tasks.find((item) => item.id === id);
  if (!tache) return normalizeState(state);
  if (focus && !tache.focus && state.tasks.filter((item) => item.focus).length >= 3) {
    return normalizeState(state);
  }
  return updateTask(state, id, { focus: Boolean(focus) });
}

function comparerTaches(a, b, ordreA, ordreB) {
  if (a.priority !== b.priority) return a.priority - b.priority;
  if (a.dueDate && b.dueDate && a.dueDate !== b.dueDate) return a.dueDate.localeCompare(b.dueDate);
  if (a.dueDate && !b.dueDate) return -1;
  if (!a.dueDate && b.dueDate) return 1;
  if (a.duration !== b.duration) return a.duration - b.duration;
  const titre = a.title.localeCompare(b.title, "fr");
  return titre !== 0 ? titre : ordreA - ordreB;
}

export function sortedTasks(tasks) {
  return (Array.isArray(tasks) ? tasks : [])
    .map((tache, index) => ({ tache, index }))
    .sort((a, b) => comparerTaches(a.tache, b.tache, a.index, b.index))
    .map((entree) => entree.tache);
}

export function selectTopThree(state) {
  const choix = new Set(sortedTasks(state.tasks).filter((tache) => !tache.done).slice(0, 3).map((tache) => tache.id));
  return normalizeState({
    ...state,
    tasks: state.tasks.map((tache) => ({ ...tache, focus: choix.has(tache.id) }))
  });
}

export function progress(state) {
  const total = state.tasks.length;
  const done = state.tasks.filter((tache) => tache.done).length;
  const percent = total === 0 ? 0 : Math.round((done / total) * 100);
  return { total, done, percent };
}

export function archiveWeek(state, date = new Date()) {
  const bilan = progress(state);
  const entree = {
    weekKey: state.weekKey || weekKey(date),
    closedAt: new Date().toISOString(),
    done: bilan.done,
    total: bilan.total,
    percent: bilan.percent,
    next: nettoyer(state.review?.next, 200)
  };
  const history = [...(state.history || []), entree].slice(-MAX_HISTORY);
  return {
    ...createEmptyState(date),
    history,
    updatedAt: new Date().toISOString()
  };
}

export function serializeState(state) {
  return JSON.stringify(normalizeState(state), null, 2);
}

export function parseImport(text, date = new Date()) {
  if (typeof text !== "string" || text.length > 300000) {
    throw new Error("Fichier trop volumineux ou illisible.");
  }
  const parsed = JSON.parse(text);
  if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
    throw new Error("Le fichier ne contient pas une sauvegarde valide.");
  }
  return normalizeState(parsed, date);
}
