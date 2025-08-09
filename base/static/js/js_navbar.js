  window.addEventListener('scroll', function () {
    const navbar = document.getElementById('mainNavbar');
    if (window.scrollY > 50) {
      navbar.classList.remove('bg-transparent');
      navbar.classList.add('bg-success', 'shadow');
    } else {
      navbar.classList.add('bg-transparent');
      navbar.classList.remove('bg-success', 'shadow');
    }
  });