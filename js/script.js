/* Quanthevaris — interactions du site
   - menu mobile (ouverture, fermeture au clic, à Échap, au clic extérieur,
     au redimensionnement)
   - année dynamique dans le pied de page
   Aucun traceur, aucune dépendance, aucun cookie. */
(function () {
  'use strict';

  function init() {
    /* ---------- Menu mobile ---------- */
    var burger = document.querySelector('.burger');
    var navLinks = document.querySelector('.nav-links');
    var mqMobile = window.matchMedia('(max-width: 720px)');

    function estOuvert() {
      return navLinks.classList.contains('open');
    }

    function liensDuMenu() {
      return Array.prototype.slice.call(navLinks.querySelectorAll('a'));
    }

    function ouvrir() {
      navLinks.classList.add('open');
      burger.setAttribute('aria-expanded', 'true');
      burger.setAttribute('aria-label', 'Fermer le menu');
      if (mqMobile.matches) {
        document.body.classList.add('nav-open');
      }
    }

    function fermer(rendreLeFocus) {
      if (!estOuvert()) { return; }
      navLinks.classList.remove('open');
      burger.setAttribute('aria-expanded', 'false');
      burger.setAttribute('aria-label', 'Ouvrir le menu');
      document.body.classList.remove('nav-open');
      if (rendreLeFocus) {
        burger.focus();
      }
    }

    if (burger && navLinks) {
      /* L'identifiant référencé par aria-controls doit exister.
         On l'ajoute ici si l'auteur du HTML a oublié id="nav-principal". */
      if (burger.getAttribute('aria-controls') && !navLinks.id) {
        navLinks.id = burger.getAttribute('aria-controls');
      }

      burger.addEventListener('click', function () {
        if (estOuvert()) {
          fermer(false);
        } else {
          ouvrir();
        }
      });

      /* 1. Fermer au clic sur un lien du menu */
      navLinks.addEventListener('click', function (event) {
        if (event.target.closest('a')) {
          fermer(false);
        }
      });

      /* 2. Fermer avec la touche Échap, et rendre le focus au bouton */
      document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape' && estOuvert()) {
          fermer(true);
        }
      });

      /* 3. Fermer au clic en dehors du menu et du bouton */
      document.addEventListener('click', function (event) {
        if (!estOuvert()) { return; }
        if (navLinks.contains(event.target) || burger.contains(event.target)) { return; }
        fermer(false);
      });

      /* 4. Fermer si la fenêtre repasse en affichage bureau (menu horizontal) */
      if (typeof mqMobile.addEventListener === 'function') {
        mqMobile.addEventListener('change', function (event) {
          if (!event.matches) { fermer(false); }
        });
      } else if (typeof mqMobile.addListener === 'function') {
        mqMobile.addListener(function (event) {
          if (!event.matches) { fermer(false); }
        });
      }
    }

    /* ---------- Année du pied de page ---------- */
    var yearSpan = document.getElementById('year');
    if (yearSpan) {
      yearSpan.textContent = new Date().getFullYear();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
