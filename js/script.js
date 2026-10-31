document.addEventListener('DOMContentLoaded', function () {
  const burger = document.querySelector('.burger');
  const navLinks = document.querySelector('.nav-links');

  if (burger && navLinks) {
    burger.addEventListener('click', function () {
      const isOpen = navLinks.classList.toggle('open');
      burger.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });
  }

  const yearSpan = document.getElementById('year');
  if (yearSpan) {
    yearSpan.textContent = new Date().getFullYear();
  }
});
