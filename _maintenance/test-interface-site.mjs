/* Contrôle du site statique en navigateur, sans envoyer de mesure d’audience. */
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdirSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { navigateur, servir, root } from './navigateur.mjs';

const {server, url} = await servir();
let browser;
try {
  browser = await navigateur();
  const page = await browser.newPage();
  const erreurs = [];
  page.on('pageerror', e => erreurs.push(e.message));
  mkdirSync(resolve(root, '.cache'), {recursive: true});
  const pages = ['index.html', 'guides.html', 'assistant-ia.html', 'esquive-en-pixels.html',
    'jeux.html', 'fission-arena.html', 'contact.html', 'mentions-legales.html',
    'confidentialite.html', 'guide-assistant-ia.html'];
  for (const largeur of [390, 768, 1327]) {
    await page.setViewportSize({width: largeur, height: 900});
    for (const fichier of pages) {
      const reponse = await page.goto(url + '/' + fichier, {waitUntil: 'networkidle'});
      assert.equal(reponse.status(), 200, fichier);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth),
        false, fichier + ' déborde à ' + largeur);
      await page.locator('img').evaluateAll(images => Promise.all(images.map(async image => {
        image.loading = 'eager';
        await image.decode();
      })));
      if (largeur === 390 && fichier === 'assistant-ia.html') {
        await page.screenshot({path: resolve(root, '.cache/relecture-ia-mobile.png'), fullPage: true});
      }
      if (largeur === 1327 && fichier === 'index.html') {
        await page.screenshot({path: resolve(root, '.cache/relecture-accueil.png')});
      }
    }
  }
  for (const [fiche, nom] of [['assistant-ia.html', 'assistant-ia-guide.pdf'],
                            ['esquive-en-pixels.html', 'esquive-en-pixels-guide.pdf']]) {
    await page.goto(url + '/' + fiche);
    const href = await page.locator('a[href*="' + nom + '"]').first().getAttribute('href');
    assert.match(href, /\?v=[a-f0-9]{12}$/);
    const reponse = await page.request.get(url + href);
    assert.equal(reponse.status(), 200);
    const empreinte = contenu => createHash('sha256').update(contenu).digest('hex');
    assert.equal(empreinte(await reponse.body()), empreinte(readFileSync(resolve(root, 'assets/pdf', nom))));
  }
  assert.deepEqual(erreurs, []);
  console.log('Site OK : 10 pages × 3 largeurs, images chargées, sans débordement ni erreur JS ; les deux téléchargements PDF correspondent aux fichiers livrés.');
} finally {
  if (browser) await browser.close();
  await new Promise(resolve => server.close(resolve));
}
