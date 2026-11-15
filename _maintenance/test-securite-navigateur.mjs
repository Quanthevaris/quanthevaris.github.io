/* Tests CSP réels sur le serveur local, jamais sur un service tiers. */
import assert from 'node:assert/strict';
import { navigateur, servir } from './navigateur.mjs';

const {server, url} = await servir();
let browser;
try {
  browser = await navigateur();
  const page = await browser.newPage();
  await page.addInitScript(() => {
    window.violationsCSP = [];
    document.addEventListener('securitypolicyviolation', e => {
      window.violationsCSP.push({directive: e.effectiveDirective, uri: e.blockedURI});
    });
  });
  for (const nom of ['index.html', 'guides.html', 'assistant-ia.html', 'esquive-en-pixels.html',
    'fission-arena.html', 'jeux.html', 'contact.html', 'mentions-legales.html',
    'confidentialite.html', '404.html', 'guide-assistant-ia.html']) {
    await page.goto(url + '/' + nom, {waitUntil: 'networkidle'});
    await page.evaluate(() => document.fonts.ready);
    assert.deepEqual(await page.evaluate(() => window.violationsCSP), [], nom);
    assert.equal(await page.locator('meta[name="referrer"]').getAttribute('content'), 'no-referrer', nom);
  }
  await page.evaluate(() => { window.print = () => { window.impressionDemandee = true; }; });
  await page.locator('#imprimer-guide').click();
  assert.equal(await page.evaluate(() => window.impressionDemandee), true);

  await page.goto(url + '/index.html', {waitUntil: 'networkidle'});
  await page.setViewportSize({width: 390, height: 900});
  await page.locator('.burger').click();
  assert.equal(await page.locator('.burger').getAttribute('aria-expanded'), 'true');
  await page.keyboard.press('Escape');
  assert.equal(await page.locator('.burger').getAttribute('aria-expanded'), 'false');
  assert.deepEqual(await page.evaluate(() => window.violationsCSP), []);

  // Une balise injectée ne doit pas exécuter son JavaScript inline.
  await page.evaluate(() => {
    const script = document.createElement('script');
    script.textContent = 'window.injectionExecutee = true';
    document.body.appendChild(script);
    const button = document.createElement('button');
    button.setAttribute('onclick', 'window.gestionnaireExecute = true');
    document.body.appendChild(button);
    button.click();
  });
  await page.waitForFunction(() => window.violationsCSP.length >= 2);
  assert.equal(await page.evaluate(() => window.injectionExecutee === true), false);
  assert.equal(await page.evaluate(() => window.gestionnaireExecute === true), false);
  const directives = await page.evaluate(() => window.violationsCSP.map(v => v.directive));
  assert.ok(directives.includes('script-src-elem'));
  assert.ok(directives.includes('script-src-attr'));
  console.log('Sécurité navigateur OK : 11 pages sans violation CSP normale ; menu et impression fonctionnels ; script et gestionnaire inline injectés bloqués.');
} finally {
  if (browser) await browser.close();
  await new Promise(resolve => server.close(resolve));
}
