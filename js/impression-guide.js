/* Action locale, sans gestionnaire inline : compatible avec la CSP. */
'use strict';
var boutonImprimer = document.getElementById('imprimer-guide');
if (boutonImprimer) {
  boutonImprimer.addEventListener('click', function () { window.print(); });
}
