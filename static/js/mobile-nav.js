// /static/js/mobile-nav.js
document.addEventListener('DOMContentLoaded', () => {
  const navToggle = document.querySelector('.nav-toggle');
  const dropdownNav = document.querySelector('.dropdown-nav');

  // Hamburger toggles nav
  navToggle.addEventListener('click', () => {
    const expanded = navToggle.getAttribute('aria-expanded') === 'true';
    navToggle.setAttribute('aria-expanded', !expanded);
    dropdownNav.classList.toggle('open');
  });

  // Hide dropdown if any link is clicked (optional, but nice)
  dropdownNav.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      navToggle.setAttribute('aria-expanded', false);
      dropdownNav.classList.remove('open');
    });
  });
});
