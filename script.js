const yearEl = document.getElementById('year');
if (yearEl) {
  yearEl.textContent = new Date().getFullYear();
}

const toggleBtn = document.querySelector('.menu-toggle');
const navLinks = document.querySelector('.nav-links');

if (toggleBtn && navLinks) {
  toggleBtn.addEventListener('click', () => {
    const expanded = toggleBtn.getAttribute('aria-expanded') === 'true';
    toggleBtn.setAttribute('aria-expanded', String(!expanded));
    navLinks.classList.toggle('show');
  });

  navLinks.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', () => {
      navLinks.classList.remove('show');
      toggleBtn.setAttribute('aria-expanded', 'false');
    });
  });
}

const inquiryForm = document.getElementById('inquiry-form');
if (inquiryForm) {
  inquiryForm.addEventListener('submit', (event) => {
    event.preventDefault();

    const name = inquiryForm.elements.namedItem('name')?.value?.trim() || '';
    const email = inquiryForm.elements.namedItem('email')?.value?.trim() || '';
    const message = inquiryForm.elements.namedItem('message')?.value?.trim() || '';

    const subject = encodeURIComponent(`Website Inquiry from ${name || 'Customer'}`);
    const body = encodeURIComponent(
      `Name: ${name}\nEmail: ${email}\n\nInquiry Details:\n${message}`,
    );

    window.location.href = `mailto:xy661029@gmail.com?subject=${subject}&body=${body}`;
  });
}
