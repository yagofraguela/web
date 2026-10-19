// Proyecto Caetano · comportamiento común a todas las páginas.

// Cursor personalizado (solo con ratón).
const cursor = document.getElementById('cursor');
if (cursor && window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
  document.addEventListener('mousemove', e => {
    cursor.style.left = e.clientX + 'px';
    cursor.style.top = e.clientY + 'px';
  });
  document.querySelectorAll('a,button').forEach(el => {
    el.addEventListener('mouseenter', () => cursor.style.transform = 'translate(-50%,-50%) scale(2.2)');
    el.addEventListener('mouseleave', () => cursor.style.transform = 'translate(-50%,-50%) scale(1)');
  });
}

// Barra de navegación al hacer scroll.
const navbar = document.getElementById('navbar');
const onScroll = () => navbar.classList.toggle('scrolled', window.scrollY > 50);
window.addEventListener('scroll', onScroll, { passive: true });
onScroll();

// Menú móvil.
const hamburger = document.getElementById('hamburger');
const mobileMenu = document.getElementById('mobileMenu');
const overlay = document.getElementById('mobileOverlay');
function setMobile(open) {
  hamburger.classList.toggle('open', open);
  mobileMenu.classList.toggle('open', open);
  overlay.classList.toggle('open', open);
  hamburger.setAttribute('aria-expanded', String(open));
  document.body.style.overflow = open ? 'hidden' : '';
}
hamburger.addEventListener('click', () => setMobile(!mobileMenu.classList.contains('open')));
overlay.addEventListener('click', () => setMobile(false));
document.addEventListener('keydown', e => { if (e.key === 'Escape') setMobile(false); });

// Formularios (Netlify Forms): envío sin recargar la página. Se buscan por clase
// porque Netlify quita el atributo data-netlify al publicar.
document.querySelectorAll('form.form-contacto').forEach(form => {
  const box = form.parentElement;
  const gracias = box.querySelector('.form-gracias');
  const error = form.querySelector('.form-error');
  const btn = form.querySelector('button[type=submit]');

  // Edad, peso y altura: solo valores positivos (ni signo ni notación científica).
  form.querySelectorAll('input[type=number]').forEach(campo => {
    campo.addEventListener('keydown', e => { if (['-', '+', 'e', 'E'].includes(e.key)) e.preventDefault(); });
    campo.addEventListener('input', () => { campo.value = campo.value.replace(/-/g, ''); });
  });

  form.addEventListener('submit', e => {
    e.preventDefault();
    error.style.display = 'none';
    btn.disabled = true;
    btn.textContent = 'Enviando...';
    fetch('/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams(new FormData(form)).toString()
    })
      .then(r => {
        if (!r.ok) throw new Error(r.status);
        form.style.display = 'none';
        gracias.style.display = 'block';
        gracias.scrollIntoView({ behavior: 'smooth', block: 'center' });
      })
      .catch(() => {
        btn.disabled = false;
        btn.textContent = 'Enviar';
        error.style.display = 'block';
      });
  });
});

// Preselección del plan o la modalidad: botones de la página y enlaces del inicio (?plan=…).
function seleccionar(id, valor) {
  const sel = document.getElementById(id);
  if (sel && [...sel.options].some(o => o.value === valor)) sel.value = valor;
}
window.preseleccionarPlan = plan => {
  seleccionar('campo-plan', plan);
  document.getElementById('contacto-form').scrollIntoView({ behavior: 'smooth' });
  return false;
};
const planInicial = new URLSearchParams(location.search).get('plan');
if (planInicial) seleccionar('campo-plan', planInicial);
document.querySelectorAll('[data-modalidad]').forEach(a => {
  a.addEventListener('click', () => seleccionar('club-modalidad', a.dataset.modalidad));
});
