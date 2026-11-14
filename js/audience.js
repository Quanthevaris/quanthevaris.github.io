/* Quanthevaris — mesure d'audience GoatCounter, limitée au chemin canonique.
   Aucun cookie, aucun stockage navigateur, aucun suivi d'événement.
   Désactivation : remettre CONFIG.endpoint à "". Voir _audience/ACTIVATION.md. */
(function () {
  'use strict';

  var CONFIG = {
    /* Adresse publique de comptage ; aucun jeton d'API n'est nécessaire. */
    endpoint: "https://quanthevaris.goatcounter.com/count",
    origin: "https://quanthevaris.github.io",
    paths: [
      "/",
      "/index.html",
      "/guides.html",
      "/jeux.html",
      "/esquive-en-pixels.html",
      "/fission-arena.html",
      "/contact.html",
      "/mentions-legales.html",
      "/confidentialite.html"
    ]
  };

  var envoye = false;

  function endpointValide(value) {
    if (typeof value !== 'string' || value === '') { return null; }
    var url;
    try { url = new URL(value); } catch (err) { return null; }
    if (url.protocol !== 'https:' || url.username || url.password || url.port ||
        url.search || url.hash || url.pathname !== '/count') {
      return null;
    }
    if (!/^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.goatcounter\.com$/i.test(url.hostname)) {
      return null;
    }
    return url.origin + '/count';
  }

  function pageCanonique() {
    var link = document.querySelector('link[rel~="canonical"][href]');
    if (!link) { return null; }
    var url;
    try { url = new URL(link.getAttribute('href'), CONFIG.origin); } catch (err) { return null; }
    if (url.origin !== CONFIG.origin) { return null; }
    if (CONFIG.paths.indexOf(url.pathname) === -1) { return null; }
    return url.pathname;
  }

  function signalConfidentialite() {
    var nav = window.navigator || {};
    return nav.globalPrivacyControl === true || nav.globalPrivacyControl === '1' ||
           nav.doNotTrack === '1' || nav.doNotTrack === 'yes' ||
           window.doNotTrack === '1';
  }

  function envoyer() {
    if (envoye) { return; }
    if (document.visibilityState === 'prerender' || document.visibilityState === 'hidden') { return; }
    if (window.location.protocol !== 'https:' || window.location.origin !== CONFIG.origin) { return; }
    if (window.top !== window.self) { return; }
    if (signalConfidentialite()) { return; }

    var endpoint = endpointValide(CONFIG.endpoint);
    var path = pageCanonique();
    if (!endpoint || !path || typeof window.fetch !== 'function') { return; }

    envoye = true;
    /* Seul le chemin canonique est transmis dans l'URL. L'IP et le user-agent
       restent des en-têtes techniques du navigateur ; ils ne sont pas ajoutés
       ici comme paramètres. Pas de repli image : un blocage reste un blocage. */
    try {
      var resultat = window.fetch(endpoint + '?p=' + encodeURIComponent(path), {
        method: 'POST',
        mode: 'no-cors',
        credentials: 'omit',
        referrerPolicy: 'no-referrer',
        cache: 'no-store',
        keepalive: true
      });
      if (resultat && typeof resultat.catch === 'function') {
        resultat.catch(function () { /* Une erreur de mesure ne casse pas le site. */ });
      }
    } catch (err) { /* Idem : échec silencieux, sans nouvelle tentative. */ }
  }

  function init() {
    if (!endpointValide(CONFIG.endpoint)) { return; }
    if (document.visibilityState === 'visible' || document.visibilityState === undefined) {
      envoyer();
      return;
    }
    document.addEventListener('visibilitychange', function surVisible() {
      if (document.visibilityState !== 'visible') { return; }
      document.removeEventListener('visibilitychange', surVisible);
      envoyer();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
