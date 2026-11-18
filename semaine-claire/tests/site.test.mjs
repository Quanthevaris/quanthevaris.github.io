import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const RACINE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const PAGES = ["index.html", "planner.html", "contact.html", "confidentialite.html"];

function lire(relatif) {
  return fs.readFileSync(path.join(RACINE, relatif), "utf8");
}

function extraireReferences(texte) {
  const references = [];
  for (const match of texte.matchAll(/(?:href|src|srcset)\s*=\s*"([^"]+)"/gi)) {
    match[1].split(",").forEach((candidat) => {
      const url = candidat.trim().split(/\s+/)[0];
      if (url) references.push(url);
    });
  }
  for (const match of texte.matchAll(/<meta\b[^>]+(?:property|name)="(?:og:image|twitter:image)"[^>]+content="([^"]+)"/gi)) {
    references.push(match[1]);
  }
  return references;
}

function idsDuHtml(texte) {
  return new Set([...texte.matchAll(/\sid="([^"]+)"/g)].map((match) => match[1]));
}

function verifierReference(fichierSource, reference) {
  if (/^(?:mailto:|data:|https?:|#|javascript:)/i.test(reference)) return;
  const [cheminBrut, fragment] = reference.split("#");
  const cible = cheminBrut
    ? path.resolve(path.dirname(path.join(RACINE, fichierSource)), decodeURIComponent(cheminBrut))
    : path.join(RACINE, fichierSource);
  assert.ok(fs.existsSync(cible), `${fichierSource} → ${reference} introuvable`);
  if (fragment && /\.(?:html|md)$/i.test(cible)) {
    const ids = idsDuHtml(fs.readFileSync(cible, "utf8"));
    assert.ok(ids.has(decodeURIComponent(fragment)), `${fichierSource} → ancre #${fragment} absente de ${path.relative(RACINE, cible)}`);
  }
}

test("les pages sont autonomes, accessibles et sans appel externe", () => {
  PAGES.forEach((page) => {
    const texte = lire(page);
    assert.ok(texte.startsWith("<!DOCTYPE html>"), page);
    assert.match(texte, /<html lang="fr">/);
    assert.match(texte, /<meta charset="utf-8">/i);
    assert.match(texte, /<meta name="robots" content="noindex, nofollow">/);
    assert.match(texte, /class="skip-link"/);
    assert.match(texte, /<main\b/);
    assert.match(texte, /<footer\b/);
    assert.doesNotMatch(texte, /https?:\/\//i, `${page} contient une URL externe`);
    assert.doesNotMatch(texte, /\sstyle\s*=/i, `${page} contient un style inline`);
    assert.doesNotMatch(texte, /\son[a-z]+\s*=/i, `${page} contient un gestionnaire d’événement inline`);
    for (const script of texte.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)) {
      assert.equal(script[1].trim(), "", `${page} contient un script inline`);
    }
    const visible = texte.replace(/<[^>]*>/g, " ");
    assert.doesNotMatch(visible, /Quanthevaris/i, `${page} affiche la marque du dépôt hôte`);
    const csp = texte.match(/<meta http-equiv="Content-Security-Policy" content="([^"]+)">/i);
    assert.ok(csp, `${page} sans CSP`);
    assert.match(csp[1], /default-src 'none'/);
    assert.match(csp[1], /script-src 'self'/);
    assert.match(csp[1], /style-src 'self'/);
    assert.match(csp[1], /connect-src 'none'/);
    assert.doesNotMatch(csp[1], /unsafe-inline|unsafe-eval/);
  });
});

test("toutes les ressources et ancres locales existent", () => {
  const sources = [
    ...PAGES,
    "assets/css/site.css",
    "assets/css/planner.css",
    "assets/js/planner.mjs"
  ];
  sources.forEach((source) => {
    const texte = lire(source);
    const references = extraireReferences(texte);
    if (source.endsWith(".css")) {
      for (const match of texte.matchAll(/url\("?([^"')]+)"?\)/g)) references.push(match[1]);
    }
    if (source.endsWith(".mjs")) {
      for (const match of texte.matchAll(/from\s+"([^"]+)"/g)) references.push(match[1]);
    }
    references.forEach((reference) => verifierReference(source, reference));
  });
});

test("le planner expose tous les identifiants attendus par son script", () => {
  const html = lire("planner.html");
  const script = lire("assets/js/planner.mjs");
  const ids = idsDuHtml(html);
  const attendus = [...script.matchAll(/\$\("([^"]+)"\)/g)].map((match) => match[1]);
  assert.ok(attendus.length > 20);
  attendus.forEach((identifiant) => {
    assert.ok(ids.has(identifiant), `id="${identifiant}" absent de planner.html`);
  });
});

test("les livrables produit et la documentation de reprise sont présents", () => {
  const fichiers = [
    "README.md",
    "A-FINALISER.md",
    "package.json",
    "docs/DOSSIER-RELANCE.md",
    "docs/AUDIT-DEPART.md",
    "outils/generer-kit.py",
    "outils/requirements.txt",
    "assets/pdf/kit-semaine-claire.pdf",
    "assets/img/hero-planner.webp",
    "assets/img/apercu-kit.webp",
    "assets/img/og-image.png",
    "assets/img/favicon.svg",
    "assets/fonts/Inter-LICENSE.txt"
  ];
  fichiers.forEach((fichier) => {
    const absolu = path.join(RACINE, fichier);
    assert.ok(fs.existsSync(absolu), `${fichier} manquant`);
    assert.ok(fs.statSync(absolu).size > 0, `${fichier} vide`);
  });
  const pdf = fs.readFileSync(path.join(RACINE, "assets/pdf/kit-semaine-claire.pdf"));
  assert.equal(pdf.subarray(0, 5).toString(), "%PDF-");
  assert.ok(pdf.length > 50000);
  const dossier = lire("docs/DOSSIER-RELANCE.md");
  assert.match(dossier, /Positionnement/);
  assert.match(dossier, /Plan de lancement/);
  assert.match(dossier, /Indicateurs/);
  const finale = lire("A-FINALISER.md");
  assert.match(finale, /pseudonyme/i);
  assert.match(finale, /adresse de contact/i);
});
