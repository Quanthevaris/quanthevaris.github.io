/* Appelé par test-parcours-ia.py, jamais un test de vraie inférence. */
import assert from 'node:assert/strict';
import { mkdirSync } from 'node:fs';
import { resolve } from 'node:path';
import { navigateur, root } from './navigateur.mjs';

const browser = await navigateur();
try {
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.setViewportSize({width: 1100, height: 840});
  const erreurs = [];
  const externes = [];
  page.on('pageerror', e => erreurs.push(e.message));
  page.on('request', r => {if (!r.url().startsWith('http://127.0.0.1:5000')) externes.push(r.url());});
  await page.goto('http://127.0.0.1:5000', {waitUntil: 'networkidle'});
  await page.waitForFunction(() => document.querySelector('#etat').textContent.startsWith('PRÊT'));
  // Capture d'interface au repos : aucune réponse de modèle prétendument réelle.
  mkdirSync(resolve(root, '.cache'), {recursive: true});
  await page.evaluate(() => {document.querySelector('#etat').textContent = 'APERÇU D’INTERFACE · Diagnostic simulé, modèle à vérifier sur ton ordinateur.';});
  await page.screenshot({path: resolve(root, '.cache/pixel-interface.png')});
  for (let i = 0; i < 8; i++) {
    await page.getByLabel('Ton message à Pixel').fill('Bonjour ' + i);
    await page.getByRole('button', {name: 'Envoyer'}).click();
    await page.waitForFunction(() => !document.querySelector('#envoyer').disabled);
  }
  assert.match(await page.locator('#etat').textContent(), /6\/6/);
  assert.equal(await page.locator('#chat img').count(), 0, 'La réponse doit rester du texte');
  assert.match(await page.locator('#chat').textContent(), /<img src=x onerror=alert\(1\)>/);
  await page.getByLabel('Ton message à Pixel').fill('erreur simulée');
  await page.getByRole('button', {name: 'Envoyer'}).click();
  await page.waitForFunction(() => !document.querySelector('#envoyer').disabled);
  assert.match(await page.locator('.erreur').last().textContent(), /Modèle absent/);
  await page.getByRole('button', {name: 'Nouvelle discussion'}).click();
  assert.equal(await page.locator('#chat .message').count(), 1);
  assert.doesNotMatch(await page.locator('#chat').textContent(), /Bonjour 7/);
  await page.reload({waitUntil: 'networkidle'});
  assert.equal(await page.locator('#chat .message').count(), 1);
  assert.deepEqual(await page.evaluate(() => [localStorage.length, sessionStorage.length, document.cookie]), [0, 0, '']);
  for (const width of [390, 768, 1327]) {
    await page.setViewportSize({width, height: 850});
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, 'Débordement à ' + width);
  }
  // La variante ELIZA fonctionne sans aucune requête de génération.
  const eliza = await context.newPage();
  await eliza.goto('file://' + resolve(root, 'assets/code/assistant-ia/eliza-web.html'));
  await eliza.locator('#texte').fill('Hello');
  await eliza.getByRole('button', {name: 'Envoyer'}).click();
  assert.match(await eliza.locator('#chat').textContent(), /How do you do/);
  assert.deepEqual(externes, []);
  assert.deepEqual(erreurs, []);
  console.log('Navigateur OK : dialogue simulé, six échanges, texte non exécutable, erreur, réinitialisation, absence de stockage/appel externe, responsive et ELIZA.');
} finally {
  await browser.close();
}
