import test from "node:test";
import assert from "node:assert/strict";
import {
  addTask,
  archiveWeek,
  createEmptyState,
  createTask,
  formatShortDate,
  formatWeekRange,
  normalizeState,
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
} from "../assets/js/planner-core.mjs";

const mercredi = new Date(2026, 10, 18, 15, 30);

function brouillon(supplement = {}) {
  return {
    title: "Exercice de maths",
    subject: "Maths",
    dueDate: "2026-11-18",
    duration: 30,
    priority: 1,
    day: "mercredi",
    ...supplement
  };
}

test("la semaine commence toujours le lundi", () => {
  assert.equal(weekKey(mercredi), "2026-11-16");
  assert.equal(toISODate(weekDates(mercredi)[0]), "2026-11-16");
  assert.equal(toISODate(weekDates(mercredi)[6]), "2026-11-22");
  assert.equal(formatWeekRange(mercredi), "du 16 au 22 novembre 2026");
  assert.equal(formatWeekRange(new Date(2026, 10, 30, 12)), "du 30 novembre au 6 décembre 2026");
  assert.equal(formatShortDate("2026-11-18"), "18 nov.");
  assert.equal(formatShortDate("date-invalide"), "");
});

test("un projet valide devient une tâche normée", () => {
  const verification = validateDraft(brouillon());
  assert.equal(verification.ok, true);
  const tache = createTask(brouillon(), "t-maths", mercredi);
  assert.equal(tache.id, "t-maths");
  assert.equal(tache.subject, "Maths");
  assert.equal(tache.done, false);
  assert.equal(tache.focus, false);
  assert.equal(validateDraft(brouillon({ title: "  " })).ok, false);
  assert.equal(validateDraft(brouillon({ dueDate: "2026-13-40" })).ok, false);
  assert.equal(validateDraft(brouillon({ day: "jour-inventé" })).ok, false);
});

test("ajout, tri, déplacement et progression", () => {
  let etat = createEmptyState(mercredi);
  etat = addTask(etat, createTask(brouillon({ title: "Devoir important", priority: 2, duration: 45 }), "t-2", mercredi));
  etat = addTask(etat, createTask(brouillon({ title: "Devoir urgent", priority: 1, duration: 20 }), "t-1", mercredi));
  etat = addTask(etat, createTask(brouillon({ title: "Plus tard", priority: 3, duration: 60 }), "t-3", mercredi));
  assert.deepEqual(sortedTasks(etat.tasks).map((tache) => tache.id), ["t-1", "t-2", "t-3"]);
  etat = setTaskDay(etat, "t-1", "vendredi");
  assert.equal(etat.tasks.find((tache) => tache.id === "t-1").day, "vendredi");
  etat = toggleDone(etat, "t-1");
  assert.deepEqual(progress(etat), { total: 3, done: 1, percent: 33 });
  etat = removeTask(etat, "t-3");
  assert.deepEqual(progress(etat), { total: 2, done: 1, percent: 50 });
});

test("trois priorités maximum, avec sélection automatique", () => {
  let etat = createEmptyState(mercredi);
  ["A", "B", "C", "D"].forEach((nom, index) => {
    etat = addTask(etat, createTask(brouillon({
      title: `Tâche ${nom}`,
      priority: index + 1 <= 3 ? 2 : 3,
      dueDate: `2026-11-${String(16 + index).padStart(2, "0")}`
    }), `t-${nom}`, mercredi));
  });
  etat = setTaskFocus(etat, "t-A", true);
  etat = setTaskFocus(etat, "t-B", true);
  etat = setTaskFocus(etat, "t-C", true);
  assert.equal(etat.tasks.filter((tache) => tache.focus).length, 3);
  etat = setTaskFocus(etat, "t-D", true);
  assert.equal(etat.tasks.find((tache) => tache.id === "t-D").focus, false);
  etat = selectTopThree(etat);
  assert.equal(etat.tasks.filter((tache) => tache.focus).length, 3);
  assert.equal(etat.tasks.find((tache) => tache.id === "t-A").focus, true);
  assert.equal(etat.tasks.find((tache) => tache.id === "t-D").focus, false);
});

test("la nouvelle semaine archive un résumé puis vide les tâches", () => {
  let etat = createEmptyState(mercredi);
  etat = addTask(etat, createTask(brouillon(), "t-1", mercredi));
  etat = toggleDone(etat, "t-1");
  etat.review.next = "Commencer par la tâche urgente";
  const suivante = new Date(2026, 10, 23, 12);
  const archive = archiveWeek(etat, suivante);
  assert.equal(archive.weekKey, "2026-11-23");
  assert.equal(archive.tasks.length, 0);
  assert.equal(archive.review.next, "");
  assert.equal(archive.history.length, 1);
  assert.equal(archive.history[0].done, 1);
  assert.equal(archive.history[0].total, 1);
  assert.equal(archive.history[0].percent, 100);
  assert.match(archive.history[0].next, /Commencer/);
});

test("import, export et normalisation restent défensifs", () => {
  const etat = addTask(createEmptyState(mercredi), createTask(brouillon(), "t-1", mercredi));
  const texte = serializeState(etat);
  const relu = parseImport(texte, mercredi);
  assert.equal(relu.tasks.length, 1);
  assert.equal(relu.tasks[0].title, "Exercice de maths");
  const hostile = normalizeState({
    weekKey: "pas-une-date",
    tasks: [
      { id: "x", title: "  Tâche   utile  ", day: "inconnu", priority: 99, duration: -5, focus: true },
      { id: "x", title: "Autre", focus: true },
      { id: "y", title: "Troisième", focus: true },
      { id: "z", title: "Quatrième", focus: true },
      { title: "" }
    ],
    review: { good: "ok", next: 42 },
    history: "pas-un-tableau"
  }, mercredi);
  assert.equal(hostile.weekKey, "2026-11-16");
  assert.equal(hostile.tasks.length, 4);
  assert.equal(hostile.tasks[0].day, "lundi");
  assert.equal(hostile.tasks[0].priority, 3);
  assert.equal(hostile.tasks[0].duration, 5);
  assert.equal(hostile.tasks.filter((tache) => tache.focus).length, 3);
  assert.equal(hostile.review.good, "ok");
  assert.equal(hostile.review.next, "");
  assert.deepEqual(hostile.history, []);
  assert.throws(() => parseImport("{json invalide", mercredi));
  assert.throws(() => parseImport("[]", mercredi));
  assert.throws(() => parseImport("x".repeat(300001), mercredi));
});
