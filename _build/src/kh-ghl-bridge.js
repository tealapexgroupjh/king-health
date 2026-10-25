/* kh-ghl-bridge
   When a GoHighLevel form iframe is pasted into a page's .kh-form-slot, this script:
   1. hides the native fallback form in that slot, and
   2. appends the page's preset to the iframe src as URL parameters (category, coverage), so the
      GoHighLevel form opens with the same selections the native form would have shown.
   The preset comes from site.js (data-kh-category and data-kh-coverage on the slot), which already resolves
   ?category=&coverage= URL parameters, the Ancillary ?from= arrival and the page's data-preset-* attributes.
   It also watches the slot, because the GoHighLevel embed script can insert or replace its iframe after load.
   Recruiting slots (data-ghl-form="recruit") are bridged the same way but never receive a category preset. */
(function () {
  'use strict';
  function preset(slot) {
    var cat = slot.getAttribute('data-kh-category');
    var cov = slot.getAttribute('data-kh-coverage');
    if (cat === null) {
      var form = slot.querySelector('[data-kh-form]');
      if (form && window.khResolvePreset) { var p = window.khResolvePreset(form); cat = p.category; cov = p.coverage; }
      else if (form) { cat = form.getAttribute('data-preset-category') || ''; cov = form.getAttribute('data-preset-coverage') || ''; }
    }
    return { category: cat || '', coverage: cov || '' };
  }
  function bridge(slot) {
    var frames = slot.querySelectorAll('iframe');
    if (!frames.length) return;
    var native = slot.querySelector('.kh-native-form');
    if (native) native.hidden = true;
    slot.classList.add('has-ghl');
    /* Wave 2: the Join the Team recruiting slot (data-ghl-form="recruit") hides its fallback the same way but appends no category preset. */
    if (slot.getAttribute('data-ghl-form') === 'recruit') return;
    var p = preset(slot);
    Array.prototype.forEach.call(frames, function (f) {
      var src = f.getAttribute('src') || f.getAttribute('data-src');
      if (!src || f.getAttribute('data-kh-bridged') === src) return;
      try {
        var u = new URL(src, location.href);
        if (p.category) u.searchParams.set('category', p.category); else u.searchParams.delete('category');
        if (p.coverage) u.searchParams.set('coverage', p.coverage); else u.searchParams.delete('coverage');
        var next = u.toString();
        f.setAttribute('data-kh-bridged', next);
        if (next !== src) f.setAttribute('src', next);
      } catch (e) {}
    });
  }
  function init() {
    Array.prototype.forEach.call(document.querySelectorAll('.kh-form-slot'), function (slot) {
      bridge(slot);
      if ('MutationObserver' in window) {
        new MutationObserver(function () { bridge(slot); }).observe(slot, { childList: true, subtree: true, attributes: true, attributeFilter: ['src'] });
      }
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
