/* Tests sans dépendance : node --test _audience/test-audience.mjs */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../', import.meta.url));
const source = fs.readFileSync(path.join(root, 'js/audience.js'), 'utf8');
const ENDPOINT = 'https://quanthevaris.goatcounter.com/count';

function charger(options = {}) {
  const calls = [];
  const listeners = Object.create(null);
  const canonical = options.canonical === undefined
    ? 'https://quanthevaris.github.io/guides.html'
    : options.canonical;
  const document = {
    readyState: options.readyState || 'complete',
    visibilityState: options.visibility || 'visible',
    querySelector(selector) {
      if (selector === 'link[rel~="canonical"][href]' && canonical !== null) {
        return { getAttribute: () => canonical };
      }
      return null;
    },
    addEventListener(type, fn) {
      (listeners[type] ||= []).push(fn);
    },
    removeEventListener(type, fn) {
      listeners[type] = (listeners[type] || []).filter((item) => item !== fn);
    }
  };
  const window = {
    document,
    location: {
      protocol: options.protocol || 'https:',
      origin: options.origin || 'https://quanthevaris.github.io',
      pathname: options.pathname || '/guides.html',
      search: options.search || '',
      hash: options.hash || ''
    },
    navigator: options.navigator || {},
    fetch: options.fetch === undefined
      ? (...args) => { calls.push(args); return Promise.resolve({ ok: true }); }
      : options.fetch
  };
  window.top = options.iframe ? {} : window;
  window.self = window;
  const sandbox = { window, document, URL, encodeURIComponent, console };
  const interdit = () => { throw new Error('Accès au stockage navigateur interdit'); };
  Object.defineProperty(window, 'localStorage', { get: interdit });
  Object.defineProperty(window, 'sessionStorage', { get: interdit });
  Object.defineProperty(document, 'cookie', { get: interdit, set: interdit });
  if (options.doNotTrackWindow !== undefined) window.doNotTrack = options.doNotTrackWindow;
  let code = source;
  if (options.endpoint !== undefined) {
    code = code.replace(/endpoint:\s*"[^"]*"/, `endpoint: ${JSON.stringify(options.endpoint)}`);
  }
  vm.createContext(sandbox);
  vm.runInContext(code, sandbox, { filename: 'audience.js' });
  return {
    calls,
    emit(type) {
      for (const fn of [...(listeners[type] || [])]) fn();
    },
    setVisibility(value) { document.visibilityState = value; },
    listenerCount(type) { return (listeners[type] || []).length; }
  };
}

test('configuration livrée : endpoint vide sans appel, endpoint renseigné avec un seul appel', () => {
  const match = source.match(/endpoint:\s*"([^"]*)"/);
  assert.ok(match, 'CONFIG.endpoint introuvable');
  const env = charger();
  if (match[1] === '') {
    assert.equal(env.calls.length, 0);
  } else {
    assert.equal(env.calls.length, 1);
    assert.ok(env.calls[0][0].startsWith(match[1] + '?p='));
  }
});

test('activation : un seul POST minimal, sans cookies ni referrer', () => {
  const env = charger({ endpoint: ENDPOINT, search: '?utm_source=secret', hash: '#ancre' });
  assert.equal(env.calls.length, 1);
  const [url, init] = env.calls[0];
  assert.equal(url, ENDPOINT + '?p=%2Fguides.html');
  assert.equal(init.method, 'POST');
  assert.equal(init.credentials, 'omit');
  assert.equal(init.referrerPolicy, 'no-referrer');
  assert.equal(init.mode, 'no-cors');
  assert.equal(init.cache, 'no-store');
  assert.equal(init.keepalive, true);
  assert.equal(init.body, undefined);
});

test('chemin canonique racine', () => {
  const env = charger({ endpoint: ENDPOINT, canonical: 'https://quanthevaris.github.io/' });
  assert.equal(env.calls[0][0], ENDPOINT + '?p=%2F');
});

test('localhost, aperçu et fichier local ne comptent pas', () => {
  for (const origin of ['http://localhost:8000', 'http://127.0.0.1:8000', 'https://8000-sandbox.e2b.app']) {
    const env = charger({ endpoint: ENDPOINT, origin, protocol: origin.startsWith('http:') ? 'http:' : 'https:' });
    assert.equal(env.calls.length, 0, origin);
  }
  const file = charger({ endpoint: ENDPOINT, origin: 'null', protocol: 'file:' });
  assert.equal(file.calls.length, 0);
});

test('iframe, 404 sans canonique, chemin inconnu et canonique externe ignorés', () => {
  assert.equal(charger({ endpoint: ENDPOINT, iframe: true }).calls.length, 0);
  assert.equal(charger({ endpoint: ENDPOINT, canonical: null }).calls.length, 0);
  assert.equal(charger({ endpoint: ENDPOINT, canonical: 'https://quanthevaris.github.io/secret.html' }).calls.length, 0);
  assert.equal(charger({ endpoint: ENDPOINT, canonical: 'https://autre.example/guides.html' }).calls.length, 0);
});

test('DNT et Global Privacy Control bloquent l’envoi', () => {
  for (const navigator of [
    { doNotTrack: '1' }, { doNotTrack: 'yes' },
    { globalPrivacyControl: true }, { globalPrivacyControl: '1' }
  ]) {
    assert.equal(charger({ endpoint: ENDPOINT, navigator }).calls.length, 0);
  }
  assert.equal(charger({ endpoint: ENDPOINT, doNotTrackWindow: '1' }).calls.length, 0);
});

test('prerender et onglet caché attendent la visibilité, une seule fois', () => {
  for (const initial of ['prerender', 'hidden']) {
    const env = charger({ endpoint: ENDPOINT, visibility: initial });
    assert.equal(env.calls.length, 0);
    env.setVisibility('visible');
    env.emit('visibilitychange');
    env.emit('visibilitychange');
    assert.equal(env.calls.length, 1);
    assert.equal(env.listenerCount('visibilitychange'), 0);
  }
});

test('DOMContentLoaded déclenche l’initialisation', () => {
  const env = charger({ endpoint: ENDPOINT, readyState: 'loading' });
  assert.equal(env.calls.length, 0);
  env.emit('DOMContentLoaded');
  assert.equal(env.calls.length, 1);
});

test('endpoints invalides ou non GoatCounter refusés', () => {
  for (const endpoint of [
    'http://exemple.goatcounter.com/count',
    'https://exemple.goatcounter.com.evil.test/count',
    'https://evil.test/count',
    'https://exemple.goatcounter.com/count?x=1',
    'https://exemple.goatcounter.com/count#x',
    'https://user:pass@exemple.goatcounter.com/count',
    'https://exemple.goatcounter.com:8443/count',
    'https://exemple.goatcounter.com/api',
    'pas une url'
  ]) {
    assert.equal(charger({ endpoint }).calls.length, 0, endpoint);
  }
});

test('fetch absent ou en erreur ne casse pas la page', async () => {
  assert.doesNotThrow(() => charger({ endpoint: ENDPOINT, fetch: undefined }));
  const env = charger({ endpoint: ENDPOINT, fetch: () => Promise.reject(new Error('bloqué')) });
  await new Promise((resolve) => setImmediate(resolve));
  assert.ok(env);
});

test('compte réel : chaque page canonique connue est comptée une fois, sans stockage', () => {
  const pages = fs.readdirSync(root).filter((name) => name.endsWith('.html') && name !== '404.html');
  for (const page of pages) {
    const html = fs.readFileSync(path.join(root, page), 'utf8');
    const canonical = html.match(/<link rel="canonical" href="([^"]+)"/)[1];
    const env = charger({ canonical, search: '?prive=ne-pas-envoyer', hash: '#ancre' });
    assert.equal(env.calls.length, 1, page);
    assert.equal(env.calls[0][0], ENDPOINT + '?p=' + encodeURIComponent(new URL(canonical).pathname), page);
  }
});

test('toutes les pages publiques chargent le module une seule fois', () => {
  const pages = fs.readdirSync(root).filter((name) => name.endsWith('.html'));
  assert.ok(pages.length >= 9);
  for (const page of pages) {
    const html = fs.readFileSync(path.join(root, page), 'utf8');
    const count = (html.match(/<script src="\/js\/audience\.js"><\/script>/g) || []).length;
    assert.equal(count, 1, page);
    assert.match(html, /<script src="\/js\/script\.js"><\/script>/, page);
    assert.doesNotMatch(html, /data-goatcounter=|gc\.zgo\.at/, page);
    assert.doesNotMatch(html, /Site sans cookie ni traceur/, page);
    assert.match(html, /Mesure d’audience expliquée/, page);
  }
});

test('politique publiée : audience décrite, aucun placeholder ni ancienne interdiction', () => {
  const policy = fs.readFileSync(path.join(root, 'confidentialite.html'), 'utf8');
  assert.match(policy, /<h2 id="audience">6\. Mesure d'audience<\/h2>/);
  assert.match(policy, /365 jours/);
  assert.match(policy, /Global Privacy Control/);
  assert.match(policy, /GoatCounter/);
  assert.doesNotMatch(policy, /\[date de publication\]|\[Date de publication\]/);
  assert.doesNotMatch(policy, /aucune mesure d'audience, aucun test A\/B/);
  const headings = [...policy.matchAll(/<h2 id="[^"]+">(\d+)\./g)].map((m) => Number(m[1]));
  assert.deepEqual(headings, Array.from({ length: 12 }, (_, i) => i + 1));
});
