// Basic hamburger menu logic for mobile drawer nav
document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.querySelector('.nav-toggle');
  const drawer = document.querySelector('.mobile-nav');
  if (!toggle || !drawer) return;

  toggle.addEventListener('click', () => {
    const expanded = toggle.getAttribute('aria-expanded') === 'true';
    toggle.setAttribute('aria-expanded', !expanded);
    drawer.classList.toggle('open');
  });

  // Optional: Close nav if you click a link in the drawer
  drawer.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      toggle.setAttribute('aria-expanded', false);
      drawer.classList.remove('open');
    });
  });
});
