/* King Health site script. Shared by every page. */

/* Single configuration object. Paste the GoHighLevel inbound webhook URL to go live; leave it empty for demo mode.
   If the GoHighLevel form embed is pasted into a page's .kh-form-slot instead, the native form hides itself. */
var KH_CONFIG = {
  ghlWebhookUrl: 'https://services.leadconnectorhq.com/hooks/3EReOYEGztjvr04Cu0rd/webhook-trigger/c4e7bd00-d5a0-4e2d-99f4-ce3ba448a8e6', /* GHL workflow: Website Lead, King Health site form */
  ghlRecruitWebhookUrl: '', /* Join the Team native fallback form; demo mode when empty */
  reviewsJson: 'assets/reviews.json', /* owner authorized Google Business Profile feed, used only when no GHL widget is present */
  phone: /*__KH_PHONE__*/'',
  email: /*__KH_EMAIL__*/''
};

(function () {
  'use strict';
  var doc = document.documentElement;
  var reduceMQ = window.matchMedia('(prefers-reduced-motion: reduce)');
  var COVERAGE = /*__KH_COVERAGE__*/{};
  var THEMES = /*__KH_THEMES__*/{};
  var DARK = /*__KH_DARK__*/[];
  var SIGNATURE = /*__KH_SIGNATURE__*/'';
  var FROM = { senior: 'Senior Benefits', individual: 'Individual Benefits', group: 'Group Benefits' };
  var FROM_SLUG = { senior: 'senior-benefits', individual: 'individual-benefits', group: 'group-benefits' };
  var params = new URLSearchParams(location.search);
  var pageId = document.body.getAttribute('data-page');
  function $all(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }

  /* ---------- Config binding ---------- */
  var tel = 'tel:' + KH_CONFIG.phone.replace(/[^\d+]/g, '');
  $all('[data-config="phone"]').forEach(function (el) { el.textContent = KH_CONFIG.phone; });
  $all('[data-config="email"]').forEach(function (el) { el.textContent = KH_CONFIG.email; });
  $all('[data-config="phone-link"]').forEach(function (el) { el.setAttribute('href', tel); });
  $all('[data-config="email-link"]').forEach(function (el) { el.setAttribute('href', 'mailto:' + KH_CONFIG.email); });

  /* ---------- Ancillary: follow the arriving category (?from=senior|individual|group) ---------- */
  var fromKey = null;
  if (pageId === 'ancillary') {
    fromKey = params.get('from');
    if (fromKey === 'group') { location.replace('group-ancillary.html'); return; } /* 2026-10-25: group ancillary has its own page */
    if (!FROM[fromKey]) fromKey = 'senior';
    $all('.subnav[data-from]').forEach(function (n) { n.hidden = n.getAttribute('data-from') !== fromKey; });
    $all('.drop[data-cat]').forEach(function (d) {
      var l = d.querySelector('.drop-link');
      if (d.getAttribute('data-cat') === fromKey) l.setAttribute('aria-current', 'page'); else l.removeAttribute('aria-current');
    });
    $all('[data-cat-link]').forEach(function (l) {
      if (l.getAttribute('data-cat-link') === fromKey) l.setAttribute('aria-current', 'page'); else l.removeAttribute('aria-current');
    });
    $all('[data-from-kicker]').forEach(function (k) { k.textContent = FROM[fromKey]; k.setAttribute('href', FROM_SLUG[fromKey] + '.html'); });
  }

  /* ---------- Coverage pills with explainers (2026-10-25): hover and focus open through CSS; a tap toggles ---------- */
  var tips = $all('[data-tip]');
  function closeTips(except) { tips.forEach(function (b) { if (b !== except) { b.setAttribute('aria-expanded', 'false'); b.parentNode.classList.remove('open'); } }); }
  tips.forEach(function (b) {
    b.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = b.getAttribute('aria-expanded') !== 'true';
      closeTips(b);
      b.setAttribute('aria-expanded', String(open));
      b.parentNode.classList.toggle('open', open);
    });
  });
  if (tips.length) {
    document.addEventListener('click', function () { closeTips(null); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeTips(null); });
  }

  /* ---------- Theme system ---------- */
  var THEME_KEY = 'kh-theme';
  var animTimer = null;
  function applyTheme(name, animate) {
    if (!THEMES[name]) name = SIGNATURE;
    if (animate && !reduceMQ.matches) {
      doc.classList.add('theme-anim'); clearTimeout(animTimer);
      animTimer = setTimeout(function () { doc.classList.remove('theme-anim'); }, 320);
    }
    doc.setAttribute('data-theme', name);
    var dark = DARK.indexOf(name) > -1;
    $all('.brand-lock').forEach(function (a) {
      var light = a.querySelector('.logo-light'), rev = a.querySelector('.logo-dark');
      if (light) light.setAttribute('alt', dark ? '' : 'King Health, home');
      if (rev) rev.setAttribute('alt', dark ? 'King Health, home' : '');
    });
    $all('[data-theme-open]').forEach(function (el) { el.setAttribute('aria-label', 'Theme, currently ' + THEMES[name]); });
    $all('[data-set-theme]').forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-set-theme') === name)); });
  }
  function saveTheme(name) { try { localStorage.setItem(THEME_KEY, name); } catch (e) {} }
  applyTheme(doc.getAttribute('data-theme') || SIGNATURE, false);

  function focusables(root) {
    return $all('a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea, [tabindex]:not([tabindex="-1"])', root)
      .filter(function (el) { return el.offsetParent !== null || el === document.activeElement; });
  }
  function trapTab(root, e) {
    if (e.key !== 'Tab') return;
    var f = focusables(root); if (!f.length) return;
    if (e.shiftKey && document.activeElement === f[0]) { e.preventDefault(); f[f.length - 1].focus(); }
    else if (!e.shiftKey && document.activeElement === f[f.length - 1]) { e.preventDefault(); f[0].focus(); }
  }

  var drawer = document.getElementById('themeDrawer');
  var dScrim = document.getElementById('drawerScrim');
  var menuBtn = document.getElementById('menuBtn');
  var menuClose = document.getElementById('menuClose');
  var menuPanel = document.getElementById('menuPanel');
  var drawerReturn = null;
  function openDrawer(trigger) {
    drawerReturn = trigger || null;
    if (menuPanel.classList.contains('open')) { closeMenu(false); drawerReturn = menuBtn; }
    drawer.hidden = false; dScrim.hidden = false;
    $all('[data-theme-open]').forEach(function (b) { b.setAttribute('aria-expanded', 'true'); });
    requestAnimationFrame(function () { drawer.classList.add('show'); dScrim.classList.add('show'); });
    document.body.style.overflow = 'hidden';
    var active = drawer.querySelector('[aria-pressed="true"]') || drawer.querySelector('.tile');
    setTimeout(function () { active.focus(); }, reduceMQ.matches ? 0 : 60);
  }
  function closeDrawer(refocus) {
    if (drawer.hidden) return;
    drawer.classList.remove('show'); dScrim.classList.remove('show');
    $all('[data-theme-open]').forEach(function (b) { b.setAttribute('aria-expanded', 'false'); });
    document.body.style.overflow = '';
    var done = function () { drawer.hidden = true; dScrim.hidden = true; };
    if (reduceMQ.matches) done(); else setTimeout(done, 330);
    if (refocus && drawerReturn) drawerReturn.focus();
  }
  $all('[data-theme-open]').forEach(function (b) {
    b.setAttribute('aria-expanded', 'false');
    b.addEventListener('click', function () { openDrawer(b); });
  });
  document.getElementById('drawerClose').addEventListener('click', function () { closeDrawer(true); });
  dScrim.addEventListener('click', function () { closeDrawer(true); });
  drawer.addEventListener('click', function (e) {
    var t = e.target.closest('[data-set-theme]');
    if (t) { applyTheme(t.getAttribute('data-set-theme'), true); saveTheme(t.getAttribute('data-set-theme')); }
  });
  document.getElementById('themeReset').addEventListener('click', function () {
    applyTheme(SIGNATURE, true); saveTheme(SIGNATURE);
    drawer.querySelector('[data-set-theme="' + SIGNATURE + '"]').focus();
  });
  drawer.addEventListener('keydown', function (e) { trapTab(drawer, e); });

  /* ---------- Category dropdowns: hover and click, arrow keys, Escape ---------- */
  var drops = $all('[data-drop]');
  var hoverCapable = window.matchMedia('(hover: hover)').matches;
  function dropParts(d) { return { link: d.querySelector('.drop-link'), btn: d.querySelector('.drop-btn'), menu: d.querySelector('.drop-menu') }; }
  function items(d) { return $all('a', dropParts(d).menu); }
  function openDrop(d, focus) {
    drops.forEach(function (o) { if (o !== d) closeDrop(o, false); });
    var p = dropParts(d);
    p.menu.hidden = false; d.classList.add('open'); p.btn.setAttribute('aria-expanded', 'true');
    if (focus === 'first') items(d)[0].focus();
    if (focus === 'last') { var l = items(d); l[l.length - 1].focus(); }
  }
  function closeDrop(d, refocus) {
    var p = dropParts(d);
    if (p.menu.hidden) return;
    p.menu.hidden = true; d.classList.remove('open'); p.btn.setAttribute('aria-expanded', 'false');
    d._hover = false;
    if (refocus) p.btn.focus();
  }
  drops.forEach(function (d) {
    var p = dropParts(d), timer = null;
    p.btn.addEventListener('click', function () {
      if (!p.menu.hidden && d._hover) { d._hover = false; return; }
      p.menu.hidden ? openDrop(d, null) : closeDrop(d, false);
    });
    function keyOpen(e) {
      if (e.key === 'ArrowDown') { e.preventDefault(); openDrop(d, 'first'); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); openDrop(d, 'last'); }
    }
    p.btn.addEventListener('keydown', keyOpen);
    p.link.addEventListener('keydown', keyOpen);
    p.menu.addEventListener('keydown', function (e) {
      var l = items(d), i = l.indexOf(document.activeElement);
      if (e.key === 'ArrowDown') { e.preventDefault(); l[(i + 1) % l.length].focus(); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); l[(i - 1 + l.length) % l.length].focus(); }
      else if (e.key === 'Home') { e.preventDefault(); l[0].focus(); }
      else if (e.key === 'End') { e.preventDefault(); l[l.length - 1].focus(); }
      else if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); closeDrop(d, true); }
    });
    d.addEventListener('focusout', function (e) { if (!d.contains(e.relatedTarget)) closeDrop(d, false); });
    if (hoverCapable) {
      d.addEventListener('mouseenter', function () { clearTimeout(timer); if (p.menu.hidden) { openDrop(d, null); d._hover = true; } });
      d.addEventListener('mouseleave', function () { timer = setTimeout(function () { closeDrop(d, false); }, 180); });
    }
  });
  document.addEventListener('click', function (e) { drops.forEach(function (d) { if (!d.contains(e.target)) closeDrop(d, false); }); });

  /* ---------- Mobile menu ---------- */
  function openMenu() { menuPanel.classList.add('open'); menuBtn.setAttribute('aria-expanded', 'true'); document.body.style.overflow = 'hidden'; menuClose.focus(); }
  function closeMenu(refocus) { if (!menuPanel.classList.contains('open')) return; menuPanel.classList.remove('open'); menuBtn.setAttribute('aria-expanded', 'false'); document.body.style.overflow = ''; if (refocus) menuBtn.focus(); }
  menuBtn.addEventListener('click', openMenu);
  menuClose.addEventListener('click', function () { closeMenu(true); });
  menuPanel.addEventListener('keydown', function (e) { trapTab(menuPanel, e); });
  menuPanel.addEventListener('click', function (e) { if (e.target.closest('a[href^="#"]')) closeMenu(false); });
  window.addEventListener('resize', function () { if (window.innerWidth >= 1000) closeMenu(false); });

  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    if (!drawer.hidden) { closeDrawer(true); return; }
    var openD = drops.filter(function (d) { return d.classList.contains('open'); })[0];
    if (openD) { closeDrop(openD, true); return; }
    closeMenu(true);
  });

  /* ---------- Sticky header shadow ---------- */
  var header = document.getElementById('siteHeader');
  function updateHeader() { header.classList.toggle('scrolled', window.scrollY > 8); }
  window.addEventListener('scroll', updateHeader, { passive: true });
  updateHeader();

  /* ---------- Wave 3: --sn-h follows the docked second bar's real height (it can wrap) ---------- */
  var snBar = $all('.subnav').filter(function (n) { return !n.hidden; })[0];
  function updateSecondBar() {
    if (!snBar) return;
    if (getComputedStyle(snBar).position === 'sticky') document.documentElement.style.setProperty('--sn-h', snBar.offsetHeight + 'px');
    else document.documentElement.style.removeProperty('--sn-h');
  }
  window.addEventListener('resize', updateSecondBar, { passive: true });
  updateSecondBar();

  /* ---------- Reveals and charts, once on entering view ---------- */
  var reveals = $all('.reveal, [data-draw]'), charts = $all('.chart');
  if ('IntersectionObserver' in window && !reduceMQ.matches) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -6% 0px', threshold: 0.08 });
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); cio.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.3 });
    reveals.forEach(function (el) { io.observe(el); });
    charts.forEach(function (el) { cio.observe(el); });
  } else {
    reveals.concat(charts).forEach(function (el) { el.classList.add('in'); });
  }
  if (reduceMQ.addEventListener) reduceMQ.addEventListener('change', function () { reveals.concat(charts).forEach(function (c) { c.classList.add('in'); }); });

  /* ---------- FAQ accordion ---------- */
  $all('[data-faq] button').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var open = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', String(!open));
      document.getElementById(btn.getAttribute('aria-controls')).hidden = open;
    });
  });

  /* ---------- Universal form ---------- */
  function norm(s) { return String(s || '').toLowerCase().replace(/[^a-z]+/g, ' ').trim(); }
  function matchOption(list, value) {
    var v = norm(value); if (!v) return '';
    for (var i = 0; i < list.length; i++) { if (norm(list[i]) === v) return list[i]; }
    return '';
  }
  var CATS = Object.keys(COVERAGE).concat(['General Inquiry']);

  /* Effective preset: URL ?category=&coverage= first, then the Ancillary arrival, then the page's data attributes. */
  function resolvePreset(form) {
    var cat = form.getAttribute('data-preset-category') || '';
    var cov = form.getAttribute('data-preset-coverage') || '';
    if (form.getAttribute('data-preset-follow-from') === 'true' && fromKey) cat = FROM[fromKey];
    var pc = matchOption(CATS, params.get('category'));
    if (pc) { cat = pc; cov = ''; }
    var list = COVERAGE[cat] || [];
    var pv = matchOption(list, params.get('coverage'));
    if (pv) cov = pv;
    if (cov && list.indexOf(cov) === -1) cov = '';
    if (cat && COVERAGE[cat] && !cov) cov = 'All or unsure';
    return { category: cat, coverage: cat === 'General Inquiry' ? '' : cov };
  }
  window.khResolvePreset = resolvePreset;

  $all('[data-kh-form]:not([data-kh-form="recruit"])').forEach(function (form) {
    var panel = form.closest('.panel');
    var wrap = panel.querySelector('[data-form-wrap]');
    var success = panel.querySelector('[data-success]');
    var statusEl = form.querySelector('[data-status]');
    var submitBtn = form.querySelector('[data-submit]');
    var catSel = form.querySelector('[name="category"]');
    var covSel = form.querySelector('[name="coverage"]');
    var covField = form.querySelector('[data-field="coverage"]');
    var slot = form.closest('.kh-form-slot');

    function fillCoverage(cat, keep) {
      var list = COVERAGE[cat];
      covSel.innerHTML = '';
      if (!list) { covField.hidden = true; covSel.disabled = true; covSel.required = false; return; }
      var ph = document.createElement('option'); ph.value = ''; ph.textContent = 'Select coverage'; covSel.appendChild(ph);
      list.forEach(function (o) { var op = document.createElement('option'); op.textContent = o; covSel.appendChild(op); });
      covField.hidden = false; covSel.disabled = false; covSel.required = true;
      if (keep && list.indexOf(keep) > -1) covSel.value = keep;
    }
    function applyPreset() {
      var p = resolvePreset(form);
      catSel.value = p.category;
      fillCoverage(p.category, p.coverage);
      if (slot) { slot.setAttribute('data-kh-category', p.category); slot.setAttribute('data-kh-coverage', p.coverage); }
    }
    catSel.addEventListener('change', function () { fillCoverage(catSel.value, catSel.value === form.getAttribute('data-preset-category') ? 'All or unsure' : ''); setErr(covSel, ''); });
    applyPreset();

    function setErr(field, msg) {
      var e = document.getElementById('err-' + field.id);
      if (msg) { field.setAttribute('aria-invalid', 'true'); if (e) e.textContent = msg; }
      else { field.removeAttribute('aria-invalid'); if (e) e.textContent = ''; }
      return !msg;
    }
    function val(name) { return (form.querySelector('[name="' + name + '"]').value || '').trim(); }
    function validate() {
      var ok = [];
      ok.push(setErr(form.querySelector('[name="first_name"]'), val('first_name') ? '' : 'Please enter your first name.'));
      ok.push(setErr(form.querySelector('[name="last_name"]'), val('last_name') ? '' : 'Please enter your last name.'));
      ok.push(setErr(form.querySelector('[name="phone"]'), val('phone').replace(/\D/g, '').length >= 10 ? '' : 'Please enter a phone number with area code.'));
      ok.push(setErr(form.querySelector('[name="email"]'), /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val('email')) ? '' : 'Please enter a valid email address.'));
      ok.push(setErr(catSel, catSel.value ? '' : 'Please choose how we can help.'));
      if (!covField.hidden) ok.push(setErr(covSel, covSel.value ? '' : 'Please choose the coverage you are interested in.'));
      var cc = form.querySelector('[name="consent_contact"]');
      ok.push(setErr(cc, cc.checked ? '' : 'Please confirm that we may contact you about your request.'));
      return ok.every(Boolean);
    }
    function showSuccess(demo) {
      wrap.hidden = true; success.hidden = false;
      success.querySelector('[data-demo-note]').hidden = !demo;
      success.querySelector('[data-success-title]').focus();
    }
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      statusEl.innerHTML = '';
      if (!validate()) {
        var first = form.querySelector('[aria-invalid="true"]'); if (first) first.focus();
        statusEl.innerHTML = '<p class="bad">Please review the highlighted fields.</p>';
        return;
      }
      if (val('company_website')) { showSuccess(false); return; } /* honeypot */
      var body = {
        first_name: val('first_name'), last_name: val('last_name'), phone: val('phone'), email: val('email'),
        category: catSel.value, coverage: covField.hidden ? '' : covSel.value, message: val('message'),
        consent_contact: true, consent_sms: form.querySelector('[name="consent_sms"]').checked,
        source: 'king-health-site', page: location.pathname.split('/').pop() || 'index.html', submitted_at: new Date().toISOString()
      };
      ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'].forEach(function (k) { body[k] = params.get(k) || ''; });
      if (!KH_CONFIG.ghlWebhookUrl) { showSuccess(true); return; } /* demo mode */
      submitBtn.disabled = true; submitBtn.textContent = 'Sending';
      fetch(KH_CONFIG.ghlWebhookUrl, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
        .then(function (r) { if (!r.ok) throw new Error('status ' + r.status); showSuccess(false); })
        .catch(function () { statusEl.innerHTML = '<p class="bad">We could not send your request just now. Please try again in a moment, or call us directly at ' + KH_CONFIG.phone + '.</p>'; })
        .then(function () { submitBtn.disabled = false; submitBtn.textContent = 'Send my request'; });
    });
    panel.querySelector('[data-reset]').addEventListener('click', function () {
      form.reset(); applyPreset(); wrap.hidden = false; success.hidden = true; form.querySelector('[name="first_name"]').focus();
    });
  });
  /* ================= Wave 2 ================= */

  /* ---------- Join the Team: recruiting form (native fallback for the GHL recruit slot) ---------- */
  $all('[data-kh-form="recruit"]').forEach(function (form) {
    var panel = form.closest('.panel');
    var wrap = panel.querySelector('[data-form-wrap]');
    var success = panel.querySelector('[data-success]');
    var statusEl = form.querySelector('[data-status]');
    var submitBtn = form.querySelector('[data-submit]');
    var submitLabel = submitBtn.textContent;
    function fld(n) { return form.querySelector('[name="' + n + '"]'); }
    function v(n) { return (fld(n).value || '').trim(); }
    function setErr(field, msg) {
      var e = document.getElementById('err-' + field.id);
      if (msg) { field.setAttribute('aria-invalid', 'true'); if (e) e.textContent = msg; }
      else { field.removeAttribute('aria-invalid'); if (e) e.textContent = ''; }
      return !msg;
    }
    function validate() {
      var ok = [];
      ok.push(setErr(fld('first_name'), v('first_name') ? '' : 'Please enter your first name.'));
      ok.push(setErr(fld('last_name'), v('last_name') ? '' : 'Please enter your last name.'));
      ok.push(setErr(fld('phone'), v('phone').replace(/\D/g, '').length >= 10 ? '' : 'Please enter a phone number with area code.'));
      ok.push(setErr(fld('email'), /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v('email')) ? '' : 'Please enter a valid email address.'));
      ok.push(setErr(fld('state'), v('state') ? '' : 'Please enter your state of residence.'));
      ok.push(setErr(fld('license_status'), v('license_status') ? '' : 'Please choose your licensing status.'));
      ok.push(setErr(fld('experience'), v('experience') ? '' : 'Please choose the experience that describes you.'));
      var cc = fld('consent_contact');
      ok.push(setErr(cc, cc.checked ? '' : 'Please confirm that we may contact you about your application.'));
      return ok.every(Boolean);
    }
    function showSuccess(demo) {
      wrap.hidden = true; success.hidden = false;
      success.querySelector('[data-demo-note]').hidden = !demo;
      success.querySelector('[data-success-title]').focus();
    }
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      statusEl.innerHTML = '';
      if (!validate()) {
        var first = form.querySelector('[aria-invalid="true"]'); if (first) first.focus();
        statusEl.innerHTML = '<p class="bad">Please review the highlighted fields.</p>';
        return;
      }
      if (v('company_website')) { showSuccess(false); return; } /* honeypot */
      var body = {
        first_name: v('first_name'), last_name: v('last_name'), phone: v('phone'), email: v('email'), state: v('state'),
        license_status: v('license_status'), experience: v('experience'), profile_url: v('profile_url'), message: v('message'),
        lines_of_interest: $all('[name="lines_of_interest"]:checked', form).map(function (c) { return c.value; }).join(', '),
        consent_contact: true, consent_sms: fld('consent_sms').checked, tags: ['recruit'], form: 'recruit',
        source: 'king-health-site', page: location.pathname.split('/').pop() || 'index.html', submitted_at: new Date().toISOString()
      };
      ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'].forEach(function (k) { body[k] = params.get(k) || ''; });
      if (!KH_CONFIG.ghlRecruitWebhookUrl) { showSuccess(true); return; } /* demo mode */
      submitBtn.disabled = true; submitBtn.textContent = 'Sending';
      fetch(KH_CONFIG.ghlRecruitWebhookUrl, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
        .then(function (r) { if (!r.ok) throw new Error('status ' + r.status); showSuccess(false); })
        .catch(function () { statusEl.innerHTML = '<p class="bad">We could not send your application just now. Please try again in a moment, or call us directly at ' + KH_CONFIG.phone + '.</p>'; })
        .then(function () { submitBtn.disabled = false; submitBtn.textContent = submitLabel; });
    });
    panel.querySelector('[data-reset]').addEventListener('click', function () {
      form.reset(); wrap.hidden = false; success.hidden = true; fld('first_name').focus();
    });
  });

  /* ---------- Appointed carriers strip: moves only when real logos overflow; pause persists in kh-motion ---------- */
  var MOTION_KEY = 'kh-motion';
  function motionPaused() { try { return localStorage.getItem(MOTION_KEY) === 'paused'; } catch (e) { return false; } }
  function saveMotion(paused) { try { localStorage.setItem(MOTION_KEY, paused ? 'paused' : 'playing'); } catch (e) {} }
  function initStrip(sec) {
    var vp = sec.querySelector('[data-cstrip]'), btn = sec.querySelector('.cstrip-toggle');
    if (!vp || !btn) return;
    var run = vp.querySelector('.cstrip-run');
    if (run) { vp.insertBefore(run.querySelector('.cstrip-track:not([aria-hidden])'), run); run.parentNode.removeChild(run); }
    vp.classList.remove('is-moving'); sec.classList.remove('is-paused'); btn.hidden = true;
    var track = vp.querySelector('.cstrip-track');
    if (!track || !track.querySelector('.cstrip-item') || track.querySelector('[data-placeholder]')) return; /* placeholders never move */
    if (reduceMQ.matches) return; /* static, wrapped, every logo visible */
    vp.classList.add('is-moving'); /* measure in the moving layout, which phones and desktops share */
    track.style.flexWrap = 'nowrap'; track.style.justifyContent = 'flex-start';
    var fits = track.scrollWidth <= vp.clientWidth;
    track.style.flexWrap = ''; track.style.justifyContent = ''; vp.classList.remove('is-moving');
    if (fits) return; /* the logos sit centered and still, no toggle */
    function setBtn(paused) {
      btn.setAttribute('aria-pressed', String(paused));
      btn.textContent = btn.getAttribute(paused ? 'data-play' : 'data-pause');
    }
    function start() {
      var r = document.createElement('div'); r.className = 'cstrip-run';
      vp.insertBefore(r, track); r.appendChild(track);
      var clone = track.cloneNode(true);
      clone.setAttribute('aria-hidden', 'true'); clone.removeAttribute('aria-label');
      $all('img', clone).forEach(function (i) { i.setAttribute('alt', ''); });
      r.appendChild(clone);
      vp.classList.add('is-moving');
      vp.style.setProperty('--cstrip-dur', (track.getBoundingClientRect().width / 32).toFixed(1) + 's');
    }
    btn.hidden = false;
    if (motionPaused()) { setBtn(true); } else { start(); setBtn(false); }
    btn.onclick = function () {
      var paused = btn.getAttribute('aria-pressed') === 'true';
      if (paused) { if (!vp.classList.contains('is-moving')) start(); sec.classList.remove('is-paused'); }
      else { sec.classList.add('is-paused'); }
      setBtn(!paused); saveMotion(!paused);
    };
  }
  function initStrips() { $all('[data-cstrip-section]').forEach(initStrip); }
  window.khInitCarrierStrip = initStrips;
  initStrips();
  var stripW = window.innerWidth, stripT = null;
  window.addEventListener('resize', function () {
    if (window.innerWidth === stripW) return; stripW = window.innerWidth;
    clearTimeout(stripT); stripT = setTimeout(initStrips, 200);
  });
  if (reduceMQ.addEventListener) reduceMQ.addEventListener('change', initStrips);

  /* ---------- Blog filters: client side, ?topic= in the URL, polite announcement, no counts ---------- */
  var bf = document.querySelector('[data-blog-filters]');
  if (bf) {
    var bfBtns = $all('button', bf), bfCards = $all('.post-grid .post-card'), bfStatus = document.querySelector('[data-blog-status]');
    var applyTopic = function (topic, announce) {
      bfBtns.forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-topic') === topic)); });
      bfCards.forEach(function (c) { c.hidden = !!topic && c.getAttribute('data-topic') !== topic; if (!c.hidden) c.classList.add('in'); });
      if (announce && bfStatus) {
        var cur = bfBtns.filter(function (b) { return b.getAttribute('data-topic') === topic; })[0];
        bfStatus.textContent = topic ? bf.getAttribute('data-announce-one').replace('{label}', cur.textContent) : bf.getAttribute('data-announce-all');
      }
      if (announce && window.history && history.replaceState) {
        var u = new URL(location.href);
        if (topic) u.searchParams.set('topic', topic); else u.searchParams.delete('topic');
        history.replaceState(null, '', u.toString());
      }
    };
    var t0 = params.get('topic') || '';
    if (!bfBtns.some(function (b) { return b.getAttribute('data-topic') === t0; })) t0 = '';
    applyTopic(t0, false);
    bfBtns.forEach(function (b) { b.addEventListener('click', function () { applyTopic(b.getAttribute('data-topic'), true); }); });
  }

  /* ---------- Reviews: GHL widget first, then the owner authorized Google feed (assets/reviews.json) ---------- */
  var STAR = 'M12 3.6l2.5 5.3 5.8.7-4.3 4 1.1 5.7L12 16.5l-5.1 2.8 1.1-5.7-4.3-4 5.8-.7z';
  var starUid = 0;
  function starRow(value, label) {
    var v = Math.round(Number(value) * 2) / 2, html = '';
    for (var i = 1; i <= 5; i++) {
      if (v >= i) html += '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path class="s-full" d="' + STAR + '"/></svg>';
      else if (v >= i - 0.5) {
        var id = 'khs' + (++starUid);
        html += '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><defs><clipPath id="' + id + '"><rect x="0" y="0" width="12" height="24"/></clipPath></defs>'
          + '<path class="s-empty" d="' + STAR + '"/><path class="s-full" clip-path="url(#' + id + ')" d="' + STAR + '"/></svg>';
      } else html += '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path class="s-empty" d="' + STAR + '"/></svg>';
    }
    var s = document.createElement('span');
    s.className = 'rv-stars'; s.setAttribute('role', 'img'); s.setAttribute('aria-label', label); s.innerHTML = html;
    return s;
  }
  function el(tag, cls, text) { var n = document.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; return n; }
  function widgetPresent(slot) {
    return Array.prototype.some.call(slot.children, function (c) { return !c.matches('[data-rv-grid], [data-rv-more], [data-rv-ctrl]'); });
  }
  function hidePlaceholders(slot) {
    var grid = slot.querySelector('[data-rv-grid]'); if (grid) grid.hidden = true;
    var more = slot.querySelector('[data-rv-more]'); if (more) more.hidden = true;
    var ctrl = slot.querySelector('[data-rv-ctrl]'); if (ctrl) ctrl.hidden = true;
    var sec = slot.closest('section');
    if (sec) $all('.rv-score-ph', sec).forEach(function (p) { p.hidden = true; });
    /* the pasted widget has priority: our build time snapshot figures step aside too */
    $all('[data-rv-static], .rvb-count').forEach(function (p) { p.hidden = true; });
  }
  function renderReviews(slot, data) {
    var S = {}; try { S = JSON.parse(slot.getAttribute('data-rv-strings') || '{}'); } catch (e) {}
    var sec = slot.closest('section');
    var score = sec && sec.querySelector('[data-review-score]');
    if (score && data.average != null && !score.hasAttribute('data-rv-static')) {
      score.innerHTML = '';
      var row = el('div', 'rv-avg-row'); row.appendChild(el('span', 'rv-avg', String(data.average)));
      row.appendChild(starRow(data.average, (S.rated || '').replace('{value}', data.average)));
      score.appendChild(row);
      if (data.total != null) score.appendChild(el('p', 'rv-total', (S.based_on || '').replace('{total}', data.total)));
    }
    if (sec && data.profile_url) $all('[data-rv-profile]', sec).forEach(function (a) { a.href = data.profile_url; a.target = '_blank'; a.rel = 'noopener'; a.removeAttribute('data-placeholder'); });
    if (sec && data.write_review_url) $all('[data-rv-write]', sec).forEach(function (a) { a.href = data.write_review_url; a.target = '_blank'; a.rel = 'noopener'; a.removeAttribute('data-placeholder'); });
    var grid = slot.querySelector('[data-rv-grid]'), more = slot.querySelector('[data-rv-more]');
    if (!grid) return;
    grid.innerHTML = '';
    var list = (data.reviews || []).slice();
    var isHome = slot.getAttribute('data-rv-context') === 'home';
    var page = isHome ? list.length : 12, shown = 0;  /* home: every review, inside the carousel */
    function card(r) {
      var a = el('article', 'rv-card'); a.tabIndex = -1;
      var g = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      g.setAttribute('class', 'g-ic rv-g'); g.setAttribute('viewBox', '0 0 256 262'); g.setAttribute('aria-hidden', 'true'); g.setAttribute('focusable', 'false');
      var u = document.createElementNS('http://www.w3.org/2000/svg', 'use'); u.setAttribute('href', '#kh-g'); g.appendChild(u); a.appendChild(g);
      var head = el('div', 'rv-head');
      head.appendChild(el('span', 'rv-mono', (String(r.author || '').trim().charAt(0) || '').toUpperCase()));
      var who = el('div');
      var au = r.author_url ? el('a', 'rv-author', r.author) : el('span', 'rv-author', r.author);
      if (r.author_url) { au.href = r.author_url; au.target = '_blank'; au.rel = 'noopener'; }
      who.appendChild(au); who.appendChild(el('span', 'rv-time', r.relative_time || S.google_label || ''));
      head.appendChild(who); a.appendChild(head);
      if (r.rating != null) a.appendChild(starRow(r.rating, (S.rated || '').replace('{value}', r.rating)));
      if (r.text) a.appendChild(el('p', 'rv-text', r.text));
      if (r.reply) {
        var d = el('details'); d.appendChild(el('summary', '', S.reply_summary || '')); d.appendChild(el('p', 'rv-reply', r.reply)); a.appendChild(d);
      }
      return a;
    }
    function reveal() {
      var first = null;
      list.slice(shown, shown + page).forEach(function (r) {
        var c = card(r); grid.appendChild(c); if (!first) first = c;
        var t = c.querySelector('.rv-text');
        if (t && t.scrollHeight > t.clientHeight + 2 && (r.author_url || data.profile_url)) {
          var l = el('a', 'tlink'); l.href = data.profile_url || r.author_url; l.target = '_blank'; l.rel = 'noopener';
          l.appendChild(el('span', '', S.read_full || '')); t.parentNode.insertBefore(l, t.nextSibling);
        }
      });
      shown += page;
      if (more) more.hidden = slot.getAttribute('data-rv-context') === 'home' || shown >= list.length;
      return first;
    }
    reveal();
    if (more) more.onclick = function () { var f = reveal(); if (f) f.focus(); };
    if (isHome) carousel(slot, grid, S);
  }
  /* Home carousel: native scroll snap (swipe), real buttons, dots, arrow keys, a polite status line. No autoplay. */
  function carousel(slot, track, S) {
    var ctrl = slot.querySelector('[data-rv-ctrl]');
    if (!ctrl) return;
    var prev = ctrl.querySelector('[data-rv-prev]'), next = ctrl.querySelector('[data-rv-next]');
    var dots = ctrl.querySelector('[data-rv-dots]'), status = ctrl.querySelector('[data-rv-status]');
    var cards = Array.prototype.slice.call(track.children), total = cards.length;
    if (!total) return;
    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    track.classList.add('rv-track');
    track.setAttribute('role', 'region'); track.setAttribute('aria-roledescription', 'carousel');
    track.setAttribute('aria-label', S.label || ''); track.tabIndex = 0;
    ctrl.hidden = false;
    function fmt(t, a, b) { return String(t || '').replace('{from}', a).replace('{to}', b).replace('{total}', total); }
    function step() { return cards.length > 1 ? cards[1].offsetLeft - cards[0].offsetLeft : track.clientWidth; }
    function visible() { return Math.max(1, Math.round((track.clientWidth + 24) / step())); }
    function first() { return Math.min(total - 1, Math.max(0, Math.round(track.scrollLeft / step()))); }
    function maxStart() { return Math.max(0, total - visible()); }
    function go(i) {
      i = Math.max(0, Math.min(maxStart(), i));
      track.scrollTo({ left: cards[i].offsetLeft - cards[0].offsetLeft, behavior: reduce ? 'auto' : 'smooth' });
    }
    var built = -1, lastMsg = '';
    function buildDots() {
      var v = visible(), pages = Math.ceil(total / v);
      if (pages === built) return;
      built = pages; dots.innerHTML = '';
      for (var p = 0; p < pages; p++) {
        var from = Math.min(p * v, maxStart()) + 1, to = Math.min(from + v - 1, total);
        var b = el('button', 'rv-dot'); b.type = 'button';
        b.setAttribute('aria-label', v === 1 ? fmt(S.dot_one, from, to) : fmt(S.dot, from, to));
        b.setAttribute('data-start', from - 1);
        b.onclick = function () { go(Number(this.getAttribute('data-start'))); };
        dots.appendChild(b);
      }
    }
    function update() {
      buildDots();
      var v = visible(), f = first(), atEnd = f >= maxStart();
      if (atEnd) f = maxStart();
      var to = Math.min(f + v, total);
      prev.disabled = f <= 0; next.disabled = atEnd;
      var active = atEnd ? built - 1 : Math.floor(f / v);
      Array.prototype.forEach.call(dots.children, function (d, i) {
        if (i === active) d.setAttribute('aria-current', 'true'); else d.removeAttribute('aria-current');
      });
      var msg = v === 1 ? fmt(S.status_one, f + 1, to) : fmt(S.status, f + 1, to);
      if (msg !== lastMsg) { status.textContent = msg; lastMsg = msg; }
    }
    prev.onclick = function () { go(first() - visible()); };
    next.onclick = function () { go(first() + visible()); };
    track.addEventListener('keydown', function (e) {
      if (e.target !== track) return;
      if (e.key === 'ArrowRight') { e.preventDefault(); go(first() + 1); }
      else if (e.key === 'ArrowLeft') { e.preventDefault(); go(first() - 1); }
      else if (e.key === 'Home') { e.preventDefault(); go(0); }
      else if (e.key === 'End') { e.preventDefault(); go(total); }
    });
    var t = 0;
    track.addEventListener('scroll', function () { clearTimeout(t); t = setTimeout(update, 80); }, { passive: true });
    window.addEventListener('resize', function () { clearTimeout(t); t = setTimeout(update, 120); });
    update();
  }
  function initReviews() {
    $all('.kh-review-slot').forEach(function (slot) {
      if (widgetPresent(slot)) { hidePlaceholders(slot); return; }
      var src = slot.getAttribute('data-reviews-src');
      if (src && window.fetch && location.protocol !== 'file:') {  /* fetch cannot read file:// pages; served builds only */
        fetch(src).then(function (r) { if (!r.ok) throw new Error('status ' + r.status); return r.json(); })
          .then(function (data) { renderReviews(slot, data); }).catch(function () {});
      }
      if ('MutationObserver' in window && !slot._khObs) {
        slot._khObs = new MutationObserver(function () { if (widgetPresent(slot)) hidePlaceholders(slot); });
        slot._khObs.observe(slot, { childList: true });
      }
    });
  }
  window.khInitReviews = initReviews;
  initReviews();
})();

/* 2026-10-25: the floating Google badge steps aside while the footer (which has its own Google Reviews link) is on screen */
(function () {
  var badge = document.querySelector('.g-badge-float'), foot = document.querySelector('.site-footer');
  if (!badge || !foot || !('IntersectionObserver' in window)) return;
  new IntersectionObserver(function (entries) {
    entries.forEach(function (e) { badge.classList.toggle('is-tucked', e.isIntersecting); });
  }, { threshold: 0.15 }).observe(foot);
})();


/* 2026-10-25: home hero slideshow. Slides after the first load only after the page has loaded; the rotation pauses
   while the tab is hidden, never runs for visitors who ask for reduced motion, and has a pause button. */
(function () {
  var box = document.querySelector('[data-hero-slides]');
  if (!box) return;
  var slides = Array.prototype.slice.call(box.querySelectorAll('.hero-slide'));
  var btn = document.querySelector('[data-hero-pause]');
  if (slides.length < 2) return;
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var i = 0, timer = null, paused = false, every = parseInt(box.getAttribute('data-interval'), 10) || 7000;
  function ready(s) {
    Array.prototype.forEach.call(s.querySelectorAll('img[data-src]'), function (im) {
      if (im.getAttribute('data-srcset')) im.setAttribute('srcset', im.getAttribute('data-srcset'));
      im.setAttribute('src', im.getAttribute('data-src'));
      im.removeAttribute('data-src'); im.removeAttribute('data-srcset');
    });
    return s.querySelector('.hero-photo img');
  }
  function show(n) {
    var next = slides[n], img = ready(next);
    function go() {
      slides[i].classList.remove('is-on'); slides[i].setAttribute('aria-hidden', 'true');
      next.classList.add('is-on'); next.removeAttribute('aria-hidden'); i = n;
      ready(slides[(n + 1) % slides.length]);
    }
    if (img && !img.complete) { img.addEventListener('load', go, { once: true }); img.addEventListener('error', function () {}, { once: true }); }
    else go();
  }
  function tick() { if (!paused && !document.hidden) show((i + 1) % slides.length); }
  function start() { stop(); timer = setInterval(tick, every); }
  function stop() { if (timer) clearInterval(timer); timer = null; }
  window.addEventListener('load', function () { ready(slides[1]); start(); });
  if (document.readyState === 'complete') { ready(slides[1]); start(); }
  if (btn) {
    btn.hidden = false;
    btn.addEventListener('click', function () {
      paused = !paused;
      btn.setAttribute('aria-pressed', paused ? 'true' : 'false');
      btn.setAttribute('aria-label', btn.getAttribute(paused ? 'data-label-play' : 'data-label-pause'));
    });
  }
})();
