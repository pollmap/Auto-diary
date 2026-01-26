// 이찬희의 디지털 두뇌 - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
  // Mobile navigation toggle
  const navTrigger = document.querySelector('.nav-trigger');
  if (navTrigger) {
    navTrigger.addEventListener('change', function() {
      document.body.classList.toggle('nav-open', this.checked);
    });
  }

  // Add external link indicators
  const externalLinks = document.querySelectorAll('a[href^="http"]:not([href*="' + window.location.hostname + '"])');
  externalLinks.forEach(function(link) {
    link.setAttribute('target', '_blank');
    link.setAttribute('rel', 'noopener noreferrer');
  });

  // Highlight current navigation item
  const currentPath = window.location.pathname;
  const navLinks = document.querySelectorAll('.site-nav .page-link');
  navLinks.forEach(function(link) {
    if (currentPath.startsWith(link.getAttribute('href'))) {
      link.classList.add('active');
    }
  });
});
