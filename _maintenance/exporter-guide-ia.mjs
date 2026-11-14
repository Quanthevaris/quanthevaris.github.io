/* npm ci --prefix _maintenance ; node _maintenance/exporter-guide-ia.mjs */
import { writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { navigateur, servir, root } from './navigateur.mjs';

const {server, url} = await servir();
let browser;
try {
  browser = await navigateur();
  const page = await browser.newPage();
  await page.goto(url + '/guide-assistant-ia.html', {waitUntil: 'networkidle'});
  await page.evaluate(() => document.fonts.ready);
  const pdf = await page.pdf({format: 'A4', printBackground: true, preferCSSPageSize: true,
    displayHeaderFooter: true, outline: true, tagged: true,
    headerTemplate: '<div style="font:7px Arial;color:#8797ad;width:100%;padding:0 14mm;display:flex;justify-content:space-between"><span>QUANTHEVARIS / ASSISTANT IA</span><span>ÉDITION LOCALE 2.0 · 14 NOVEMBRE 2026</span></div>',
    footerTemplate: '<div style="font:7px Arial;color:#8797ad;width:100%;padding:0 14mm;display:flex;justify-content:space-between"><span>Python · Flask · Ollama</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>'});
  for (const name of ['guide-assistant-ia.pdf', 'assets/pdf/assistant-ia-guide.pdf']) writeFileSync(resolve(root, name), pdf);
  console.log('Deux copies PDF identiques générées :', pdf.length, 'octets.');
} finally {
  if (browser) await browser.close();
  await new Promise(resolve => server.close(resolve));
}
