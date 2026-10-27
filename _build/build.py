#!/usr/bin/env python3
"""King Health Version 2 (Summit) static site builder.

Standard library only for the build itself. Reads _build/content.json (falls back to
_build/content.sample.json) and _build/photos.json, then writes every page into ../site/
with shared assets. Re-run at any time:  python3 _build/build.py

Governing documents: SPEC_KING_HEALTH_V2_SUMMIT.md (sitemap, form, content, architecture) and
PICASSO_DIRECTION_KING_HEALTH_2026_10_22.md (themes, gold placements, logos, components).
"""
import html
import json
import os
import re
import shutil
import struct
import sys

BUILD = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BUILD)
SITE = os.path.join(ROOT, "site")
BRAND_SRC = os.path.join(ROOT, "brand") if os.path.isdir(os.path.join(ROOT, "brand")) else os.path.join(os.path.dirname(ROOT), "brand")  # standalone repo keeps brand/ beside site/
BRAND_EXTRA = os.path.join(BUILD, "brand_extra")
SRC = os.path.join(BUILD, "src")
YEAR = "2026"
# Wave 2: review builds (default) show labeled placeholders and drafts; `--release` omits empty proofs and drafts.
RELEASE = "--release" in sys.argv
CF_HEADERS = """https://:project.pages.dev/*
  X-Robots-Tag: noindex

/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: SAMEORIGIN
  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()
  Strict-Transport-Security: max-age=31536000

/*.vcf
  Content-Type: text/vcard; charset=utf-8
  Content-Disposition: attachment

/media/*
  Cache-Control: public, max-age=604800

/assets/*
  Cache-Control: public, max-age=3600
"""
LIVE_RELOAD_JS = """
/* Review build only: reload this tab when assets/build-stamp.txt changes. Never emitted by build.py --release. */
(function () {
  if (!/^https?:$/.test(location.protocol) || !window.fetch) return;
  var url = 'assets/build-stamp.txt', last = null;
  function check() {
    if (document.hidden) return;
    fetch(url + '?t=' + Date.now(), { cache: 'no-store' }).then(function (r) { return r.ok ? r.text() : null; }).then(function (t) {
      if (t == null) return;
      if (last === null) { last = t; return; }
      if (t !== last) location.reload();
    }).catch(function () {});
  }
  check(); setInterval(check, 2000);
  document.addEventListener('visibilitychange', check);
})();
"""

WARNINGS = []


def warn(msg):
    WARNINGS.append(msg)
    print("WARN:", msg)


def esc(s):
    return html.escape(str(s), quote=True)


# --------------------------------------------------------------------------------------
# Site structure (fixed by the spec; copy comes from content.json)
# --------------------------------------------------------------------------------------
CATS = [
    {"slug": "senior-benefits", "key": "senior", "label": "Senior Benefits",
     "products": ["medicare", "final-expense", "ancillary"]},
    {"slug": "individual-benefits", "key": "individual", "label": "Individual Benefits",
     "products": ["individual-health", "whole-life", "term-life", "ancillary", "dental-vision"]},
    {"slug": "group-benefits", "key": "group", "label": "Group Benefits",
     "products": ["group-health", "group-life", "group-ancillary", "group-dental-vision"]},  # 2026-10-25: group has its own ancillary page
    {"slug": "retirement", "key": "retirement", "label": "Retirement",
     "products": ["annuities", "indexed-universal-life"]},
]
CAT_BY_SLUG = {c["slug"]: c for c in CATS}
CAT_BY_KEY = {c["key"]: c for c in CATS}
ANCILLARY_FROM = ["senior", "individual"]  # group uses group-ancillary.html

# Form option labels. These are the GoHighLevel option values and must not drift.
FORM_LABEL = {
    "medicare": "Medicare", "final-expense": "Final Expense", "ancillary": "Ancillary",
    "individual-health": "Individual Health", "whole-life": "Whole Life", "term-life": "Term Life",
    "dental-vision": "Dental and Vision", "group-health": "Group Health", "group-life": "Group Life",
    "group-dental-vision": "Group Dental and Vision", "group-ancillary": "Group Ancillary", "annuities": "Annuities",
    "indexed-universal-life": "Indexed Universal Life",
}
ALL_OR_UNSURE = "All or unsure"
GENERAL = "General Inquiry"
COVERAGE_MAP = {c["label"]: [FORM_LABEL[p] for p in c["products"]] + [ALL_OR_UNSURE] for c in CATS}
CATEGORY_OPTIONS = [c["label"] for c in CATS] + [GENERAL]

# --------------------------------------------------------------------------------------
# Wave 3 (SPEC_WAVE3_SITENAV_AND_HIDE_2026_10_25.md): the King Health second nav and the page hide switch.
# Siblings copy this block verbatim; only the markup helpers below are concept specific.
# --------------------------------------------------------------------------------------
# Page keys accepted by site.hidden_pages, and the file each one owns. Hiding "blog" also skips every blog-*.html article.
HIDEABLE_PAGES = {"reviews": "reviews.html", "join-the-team": "join-the-team.html", "blog": "blog.html",
                  "terms": "terms.html", "carriers": "carriers.html", "about": "about.html", "faq": "faq.html"}
HIDDEN = set()  # filled once by set_hidden_pages() before any page is rendered
SITE_NAV_DEFAULT = {"label": "King Health", "label_href": "index.html", "items": [
    {"key": "about", "label": "About Us", "href": "about.html"},
    {"key": "faq", "label": "FAQ", "href": "faq.html"},
    {"key": "carriers", "label": "Carriers", "href": "carriers.html"},
    {"key": "reviews", "label": "Client Reviews", "href": "reviews.html"},
    {"key": "blog", "label": "Blog", "href": "blog.html"},
    {"key": "join-the-team", "label": "Join the Team", "href": "join-the-team.html"}],
    "cta": {"label": "Contact Us", "href": "contact.html"}}
# page id (body data-page) -> the site nav key it marks as current. Terms, privacy and accessibility mark nothing.
SITE_NAV_CURRENT = {"home": "home", "about": "about", "carriers": "carriers", "reviews": "reviews", "blog": "blog",
                    "article": "blog", "join": "join-the-team", "contact": "contact", "faq": "faq"}


def set_hidden_pages(C):
    """Read site.hidden_pages once. Unknown keys are reported and ignored, so a typo never hides the wrong page."""
    HIDDEN.clear()
    for key in C.get("site", {}).get("hidden_pages", []) or []:
        if key in HIDEABLE_PAGES:
            HIDDEN.add(key)
        else:
            warn("site.hidden_pages: unknown page key %r (valid: %s)" % (key, ", ".join(HIDEABLE_PAGES)))
    if HIDDEN:
        print("Hidden pages:", ", ".join(sorted(HIDDEN)))


def page_key_for_href(href):
    """The hideable page key a local href points at, or None. blog-*.html articles belong to "blog"."""
    name = href.split("#", 1)[0].split("?", 1)[0]
    if name.startswith("blog-") and name.endswith(".html"):
        return "blog"
    for key, fname in HIDEABLE_PAGES.items():
        if name == fname:
            return key
    return None


def page_live(key):
    return key not in HIDDEN


def href_live(href):
    """False when the href points at a hidden page; every link builder filters through this."""
    key = page_key_for_href(href)
    return key is None or page_live(key)


def site_nav_config(C):
    cfg = dict(SITE_NAV_DEFAULT)
    cfg.update({k: v for k, v in (C.get("site_nav") or {}).items() if not k.startswith("_")})
    return cfg


def check_links(pages):
    """Every local href in every generated page must resolve to a generated page or an existing file in site/."""
    dead = []
    for name, doc in pages.items():
        for href in set(re.findall(r'href="([^"#?:]+\.html)[^"]*"', doc)):
            if href not in pages:
                dead.append("%s -> %s" % (name, href))
    if dead:
        warn("links to pages that were not generated: %s" % "; ".join(sorted(dead)[:12]))
    return dead


CHARTS = {"term-life": "term", "indexed-universal-life": "iul", "annuities": "ring"}
HOME_CHART = "plan"

PHONE_DEFAULT = "(555) 010-0100"
EMAIL_DEFAULT = "hello@kinghealth.example"

# Frozen tokens from PICASSO_DIRECTION_KING_HEALTH_2026_10_22.md (section 3), verbatim.
THEMES = [
    ('ivory', 'Ivory Crown', 'Light, signature', 'light', {
        'bg': '#FDFCF8',
        'surface': '#FFFFFF',
        'surface-2': '#F2F4EE',
        'ink': '#14231A',
        'ink-soft': '#4A5A4F',
        'line': 'rgba(20,35,26,.12)',
        'brand': '#355E3B',
        'brand-ink': '#FFFFFF',
        'link': '#355E3B',
        'accent': '#CFB53B',
        'accent-strong': '#7F6418',
        'focus': '#7F6418',
        'button-bg': '#355E3B',
        'button-hover': '#1E3A26',
        'button-ink': '#FFFFFF',
        'header-bg': '#FFFFFF',
        'header-ink': '#14231A',
        'subnav-bg': '#F2F4EE',
        'band-bg': '#355E3B',
        'band-ink': '#FFFFFF',
        'band-soft': '#DCE6D8',
        'band-kicker': '#EAD889',
        'band-btn-bg': '#FFFFFF',
        'band-btn-ink': '#1E3A26',
        'footer-bg': '#142A1B',
        'footer-ink': '#F1EEE2',
        'footer-soft': '#B9C4B6',
        'footer-kicker': '#CFB53B',
        'chart-accent': '#9C7C1A',
        'field-line': '#808C84',
        'scrim': 'rgba(20,42,27,.58)',
        'scrim-soft': 'rgba(20,42,27,.18)',
        'shadow': 'rgba(20,42,27,.10)',
        'err': '#B3261E',
        'swatch-a': '#FFFFFF',
        'swatch-b': '#355E3B',
    }),
    ('onyx', 'Onyx Crown', 'Dark', 'dark', {
        'bg': '#0D100E',
        'surface': '#151A17',
        'surface-2': '#1C2420',
        'ink': '#F2EFE6',
        'ink-soft': '#B9BCB1',
        'line': 'rgba(242,239,230,.14)',
        'brand': '#355E3B',
        'brand-ink': '#F7F3E6',
        'link': '#F2EFE6',
        'accent': '#C2A740',
        'accent-strong': '#D6BE5E',
        'focus': '#D6BE5E',
        'button-bg': '#3F6E46',
        'button-hover': '#4A7D52',
        'button-ink': '#FFFFFF',
        'header-bg': '#0D100E',
        'header-ink': '#F2EFE6',
        'subnav-bg': '#151A17',
        'band-bg': '#1E3A26',
        'band-ink': '#F7F3E6',
        'band-soft': '#C9D3C4',
        'band-kicker': '#DCC567',
        'band-btn-bg': '#F2EFE6',
        'band-btn-ink': '#142A1B',
        'footer-bg': '#080A09',
        'footer-ink': '#F2EFE6',
        'footer-soft': '#A9AEA4',
        'footer-kicker': '#D6BE5E',
        'chart-accent': '#C2A740',
        'field-line': '#777B73',
        'scrim': 'rgba(8,10,9,.70)',
        'scrim-soft': 'rgba(8,10,9,.32)',
        'shadow': 'rgba(0,0,0,.5)',
        'err': '#F2B8B5',
        'swatch-a': '#0D100E',
        'swatch-b': '#C2A740',
    }),
    ('forest', 'Forest Hall', 'Deep green', 'dark', {
        'bg': '#1E3A26',
        'surface': '#24452E',
        'surface-2': '#173020',
        'ink': '#F5F1E4',
        'ink-soft': '#CBD4C5',
        'line': 'rgba(245,241,228,.16)',
        'brand': '#2C5234',
        'brand-ink': '#F5F1E4',
        'link': '#F5F1E4',
        'accent': '#CFB53B',
        'accent-strong': '#DCC567',
        'focus': '#DCC567',
        'button-bg': '#F5F1E4',
        'button-hover': '#FFFFFF',
        'button-ink': '#1E3A26',
        'header-bg': '#173020',
        'header-ink': '#F5F1E4',
        'subnav-bg': '#24452E',
        'band-bg': '#0B170F',  # Picasso critique finding 10
        'band-ink': '#F5F1E4',
        'band-soft': '#C9D3C4',
        'band-kicker': '#DCC567',
        'band-btn-bg': '#F5F1E4',
        'band-btn-ink': '#142A1B',
        'footer-bg': '#122618',
        'footer-ink': '#F5F1E4',
        'footer-soft': '#B8C5B4',
        'footer-kicker': '#DCC567',
        'chart-accent': '#CFB53B',
        'field-line': '#889B89',
        'scrim': 'rgba(18,38,24,.66)',
        'scrim-soft': 'rgba(18,38,24,.28)',
        'shadow': 'rgba(0,0,0,.4)',
        'err': '#F2B8B5',
        'swatch-a': '#1E3A26',
        'swatch-b': '#CFB53B',
    }),
    ('linen', 'Linen Estate', 'Warm light', 'light', {
        'bg': '#F7F2E8',
        'surface': '#FFFCF6',
        'surface-2': '#EEE6D6',
        'ink': '#1D2A20',
        'ink-soft': '#55594C',
        'line': 'rgba(29,42,32,.13)',
        'brand': '#1E3A26',
        'brand-ink': '#FBF7EE',
        'link': '#1E3A26',
        'accent': '#B08D3C',
        'accent-strong': '#7A5D1C',
        'focus': '#7A5D1C',
        'button-bg': '#1E3A26',
        'button-hover': '#142A1B',
        'button-ink': '#FBF7EE',
        'header-bg': '#FFFCF6',
        'header-ink': '#1D2A20',
        'subnav-bg': '#EEE6D6',
        'band-bg': '#1E3A26',
        'band-ink': '#FBF7EE',
        'band-soft': '#D6DCCB',
        'band-kicker': '#E8D27A',
        'band-btn-bg': '#FBF7EE',
        'band-btn-ink': '#1E3A26',
        'footer-bg': '#1E3A26',
        'footer-ink': '#F3EDE0',
        'footer-soft': '#C3C9B8',
        'footer-kicker': '#E8D27A',
        'chart-accent': '#9C7C1A',
        'field-line': '#888A7F',
        'scrim': 'rgba(30,58,38,.56)',
        'scrim-soft': 'rgba(30,58,38,.16)',
        'shadow': 'rgba(42,33,25,.10)',
        'err': '#A8321F',
        'swatch-a': '#F7F2E8',
        'swatch-b': '#1E3A26',
    }),
    ('fairway', 'Fairway', 'Fresh light', 'light', {
        'bg': '#FCFDFB',
        'surface': '#FFFFFF',
        'surface-2': '#EAF2E7',
        'ink': '#13241A',
        'ink-soft': '#44584A',
        'line': 'rgba(19,36,26,.12)',
        'brand': '#355E3B',
        'brand-ink': '#FFFFFF',
        'link': '#355E3B',
        'accent': '#D9B935',
        'accent-strong': '#7D6516',
        'focus': '#7D6516',
        'button-bg': '#355E3B',
        'button-hover': '#2A4D30',
        'button-ink': '#FFFFFF',
        'header-bg': '#FFFFFF',
        'header-ink': '#13241A',
        'subnav-bg': '#EAF2E7',
        'band-bg': '#355E3B',
        'band-ink': '#FFFFFF',
        'band-soft': '#DCE8D8',
        'band-kicker': '#EAD889',
        'band-btn-bg': '#FFFFFF',
        'band-btn-ink': '#1E3A26',
        'footer-bg': '#355E3B',
        'footer-ink': '#FFFFFF',
        'footer-soft': '#DCE8D8',
        'footer-kicker': '#EAD889',
        'chart-accent': '#9C7C1A',
        'field-line': '#7C8A80',
        'scrim': 'rgba(30,58,38,.52)',
        'scrim-soft': 'rgba(30,58,38,.14)',
        'shadow': 'rgba(30,58,38,.10)',
        'err': '#B3261E',
        'swatch-a': '#EAF2E7',
        'swatch-b': '#D9B935',
    }),
]
SIGNATURE = "ivory"
DARK_THEMES = ("onyx", "forest")


def _lum(hexc):
    hexc = hexc.lstrip("#")
    r, g, b = (int(hexc[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast(a, b):
    la, lb = _lum(a), _lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


CONTRAST_PAIRS = [  # (foreground, background, minimum)
    ("ink", "bg", 4.5), ("ink", "surface", 4.5), ("ink", "surface-2", 4.5), ("ink-soft", "bg", 4.5),
    ("ink-soft", "surface", 4.5), ("ink-soft", "surface-2", 4.5), ("ink", "subnav-bg", 4.5), ("ink-soft", "subnav-bg", 4.5),
    ("link", "bg", 4.5), ("link", "surface", 4.5), ("brand-ink", "brand", 4.5), ("accent-strong", "bg", 4.5),
    ("accent-strong", "surface", 4.5), ("accent-strong", "surface-2", 4.5), ("button-ink", "button-bg", 4.5),
    ("button-ink", "button-hover", 4.5), ("header-ink", "header-bg", 4.5), ("band-ink", "band-bg", 4.5),
    ("band-soft", "band-bg", 4.5), ("band-kicker", "band-bg", 4.5), ("band-btn-ink", "band-btn-bg", 4.5),
    ("footer-ink", "footer-bg", 4.5), ("footer-soft", "footer-bg", 4.5), ("footer-kicker", "footer-bg", 4.5),
    ("chart-accent", "surface", 3.0), ("field-line", "surface", 3.0),
]


BRAND_TOKENS = (("g-blue", "#4285F4"), ("g-red", "#EA4335"), ("g-yellow", "#FBBC04"), ("g-green", "#34A853"),
                ("fb-blue", "#1877F2"), ("wa-green", "#25D366"),
                ("ig-1", "#FDF497"), ("ig-2", "#FD5949"), ("ig-3", "#D6249F"), ("ig-4", "#285AEB"))


def theme_css():
    out = ["/* THEME TOKENS, generated by _build/build.py from the frozen Picasso direction. No hex appears outside this block. */"]
    for slug, name, mode, scheme, t in THEMES:
        sel = '[data-theme="%s"]' % slug
        if slug == SIGNATURE:
            sel = ":root, " + sel
        out.append("%s { color-scheme: %s; %s }" % (sel, scheme, " ".join("--%s:%s;" % (k, v) for k, v in t.items())))
    # Third party brand colors (Google rating accents, social circles). Fixed by each brand, identical in every theme.
    out.append(":root { %s }" % " ".join("--%s:%s;" % kv for kv in BRAND_TOKENS))
    return "\n".join(out) + "\n/* END THEME TOKENS */\n"


def check_contrast():
    report = []
    for slug, name, mode, scheme, t in THEMES:
        worst = 99
        for a, b, need in CONTRAST_PAIRS:
            c = contrast(t[a], t[b])
            if need >= 4.5:
                worst = min(worst, c)
            if c < need:
                warn("contrast %s: %s on %s is %.2f (needs %.1f)" % (slug, a, b, c, need))
        report.append("%s text min %.2f" % (slug, worst))
    print("Contrast:", "; ".join(report))


def make_brand_assets():
    """Generate, once, the sage reverse wordmark and lockup and the cropped favicons (Picasso section 5).
    Pillow is used only when an output is missing, so routine builds stay standard library."""
    wanted = ["king-health-wordmark.png", "king-health-wordmark-reverse.png", "king-health-lockup-reverse.png",
              "favicon-32.png", "favicon-180.png", "favicon.ico"]
    if all(os.path.exists(os.path.join(BRAND_EXTRA, w)) for w in wanted):
        return
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        warn("Pillow is not installed; brand variants were not generated")
        return
    os.makedirs(BRAND_EXTRA, exist_ok=True)
    lockup = os.path.join(BRAND_SRC, "king-health-lockup.png")
    wm = os.path.join(BRAND_EXTRA, "king-health-wordmark.png")
    if not os.path.exists(wm):
        im = Image.open(lockup).convert("RGBA")
        c = im.crop((0, 0, im.width, 592))
        c.crop(c.split()[3].getbbox()).save(wm, optimize=True)

    def reverse(src, dst, target=(0x9C, 0xC2, 0x8E), k=0.70):
        im = Image.open(src).convert("RGBA")
        px = im.load()
        for y in range(im.height):
            for x in range(im.width):
                r, g, b, a = px[x, y]
                if a and g > r + 12 and g >= b:
                    px[x, y] = (round((1 - k) * r + k * target[0]), round((1 - k) * g + k * target[1]),
                                round((1 - k) * b + k * target[2]), a)
        im.save(dst, optimize=True)

    reverse(wm, os.path.join(BRAND_EXTRA, "king-health-wordmark-reverse.png"))
    reverse(lockup, os.path.join(BRAND_EXTRA, "king-health-lockup-reverse.png"))
    em = Image.open(os.path.join(BRAND_SRC, "king-health-emblem.png")).convert("RGBA").crop((84, 84, 588, 588))
    big = 1008
    em = em.resize((big, big), Image.LANCZOS)
    mask = Image.new("L", (big, big), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, big - 1, big - 1), fill=255)
    alpha = Image.composite(em.split()[3], mask, mask)
    disc = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    disc.paste(em, (0, 0), alpha)
    disc.resize((32, 32), Image.LANCZOS).save(os.path.join(BRAND_EXTRA, "favicon-32.png"))
    touch = Image.new("RGBA", (180, 180), (0x14, 0x2A, 0x1B, 255))
    d = disc.resize((160, 160), Image.LANCZOS)
    touch.paste(d, (10, 10), d)
    touch.convert("RGB").save(os.path.join(BRAND_EXTRA, "favicon-180.png"))
    disc.resize((64, 64), Image.LANCZOS).save(os.path.join(BRAND_EXTRA, "favicon.ico"), sizes=[(16, 16), (32, 32)])
    print("Generated brand variants in _build/brand_extra")


# --------------------------------------------------------------------------------------
# Content and photos
# --------------------------------------------------------------------------------------
def load_content():
    real = os.path.join(BUILD, "content.json")
    sample = os.path.join(BUILD, "content.sample.json")
    if os.path.exists(real):
        try:
            with open(real, encoding="utf-8") as f:
                return json.load(f), "content.json"
        except ValueError as e:
            warn("content.json is not valid JSON (%s); falling back to content.sample.json" % e)
    if not os.path.exists(sample):
        sys.exit("No usable content.json and no content.sample.json in %s" % BUILD)
    with open(sample, encoding="utf-8") as f:
        return json.load(f), "content.sample.json"


def image_size(path):
    try:
        with open(path, "rb") as f:
            head = f.read(26)
            if head[:8] == b"\x89PNG\r\n\x1a\n":
                return struct.unpack(">II", head[16:24])
            if head[:2] == b"\xff\xd8":
                f.seek(2)
                while True:
                    marker = f.read(2)
                    if len(marker) < 2 or marker[0] != 0xFF:
                        return None
                    code = marker[1]
                    if code in (0xD8, 0x01) or 0xD0 <= code <= 0xD7:
                        continue
                    seglen = struct.unpack(">H", f.read(2))[0]
                    if code in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                        f.read(1)
                        h, w = struct.unpack(">HH", f.read(4))
                        return w, h
                    f.seek(seglen - 2, 1)
    except OSError:
        return None
    return None


class Photos:
    def __init__(self):
        with open(os.path.join(BUILD, "photos.json"), encoding="utf-8") as f:
            data = json.load(f)
        self.files = data.get("files", {})
        self.slots = data.get("slots", {})
        self.dir = os.path.join(SITE, "media", "photos")

    def _resolve_name(self, name):
        if os.path.exists(os.path.join(self.dir, name)):
            return name
        for ext in (".jpg", ".jpeg", ".png", ".webp"):
            if os.path.exists(os.path.join(self.dir, name + ext)):
                return name + ext
        warn("photo not found: %s" % name)
        return name

    def get(self, slot):
        # Wave 2: "file:NAME" renders a library photo directly (blog post images are keyed by file in content.json).
        raw = slot[5:] if slot.startswith("file:") else self.slots.get(slot)
        if raw is None:
            warn("photo slot missing: %s" % slot)
            return None
        if isinstance(raw, dict):
            name = self._resolve_name(raw.get("file", ""))
            meta = dict(self.files.get(name, {}))
            meta.update({k: v for k, v in raw.items() if k != "file"})
        else:
            name = self._resolve_name(raw)
            meta = dict(self.files.get(name, {}))
        if not meta.get("alt"):
            meta["alt"] = os.path.splitext(name)[0].replace("-", " ").capitalize()
            warn("no alt text recorded for %s; using its file name" % name)
        meta["file"] = name
        return meta

    def img(self, slot, eager=False, decorative=False, used=None, alternates=(), banner=False, near_fold=False):
        """Render a photo slot. When `used` is given, a photo already shown on this page is swapped for the
        first alternate slot whose photo has not been shown yet."""
        p = self.get(slot)
        if p is None:
            return ""
        if used is not None:
            if p["file"] in used:
                for alt_slot in alternates:
                    q = self.get(alt_slot)
                    if q and q["file"] not in used:
                        p = q
                        break
            used.add(p["file"])
        size = image_size(os.path.join(self.dir, p["file"])) or (1800, 1200)
        attrs = ['src="media/photos/%s"' % esc(p["file"]),
                 'alt="%s"' % ("" if decorative else esc(p["alt"])),
                 'width="%d" height="%d"' % tuple(size),
                 # Wave 4: near_fold images (product glance photo, featured post) can sit in the first viewport, so they are not lazy
                 'loading="eager" fetchpriority="high"' if eager else ('decoding="async"' if near_fold else 'loading="lazy" decoding="async"'),
                 'style="object-position:%s"' % esc((banner and p.get("banner_position")) or p.get("position") or "50% 50%")]
        return "<img %s>" % " ".join(attrs)


# --------------------------------------------------------------------------------------
# Shared components
# --------------------------------------------------------------------------------------
def head(title, description, page_id):
    return """<!doctype html>
<html lang="en" data-theme="%(sig)s">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<link rel="icon" href="brand/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="brand/favicon-32.png">
<link rel="apple-touch-icon" href="brand/favicon-180.png">
<script>
  (function () {
    var T = %(themes)s;
    try { var t = localStorage.getItem('kh-theme'); if (t && T.indexOf(t) > -1) document.documentElement.setAttribute('data-theme', t); } catch (e) {}
    document.documentElement.classList.add('js');
  })();
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Manrope:wght@500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/site.css">
</head>
<body data-page="%(pid)s">
%(sprite)s
""" % {"sig": SIGNATURE, "title": esc(title), "desc": esc(description), "themes": json.dumps([t[0] for t in THEMES]),
       "pid": esc(page_id), "sprite": icon_sprite() + "\n" + brand_sprite()}


# Wave 2, A3: King Health Line icons. The sprite is copied verbatim from the frozen direction into src/icons.svg.
ICON_ATTRS = 'fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"'
CARRIER_ICON = {"Medicare": "medicare", "Final Expense": "final-expense", "Individual Health": "individual-health",
                "Individual Life": "whole-life", "Dental and Vision": "dental-vision", "Group Benefits": "group-benefits",
                "Retirement": "retirement", "Ancillary": "ancillary", "Group Health": "group-health", "Group Life": "group-life",
                "Group Ancillary": "group-ancillary", "Group Dental and Vision": "group-dental-vision"}
_SPRITE = []


def icon_symbols():
    if not _SPRITE:
        with open(os.path.join(SRC, "icons.svg"), encoding="utf-8") as f:
            _SPRITE.append(f.read())
    return "\n".join(l for l in _SPRITE[0].splitlines() if l.startswith("<symbol"))


def icon_sprite():
    return ('<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false" %s>\n%s\n</svg>'
            % (ICON_ATTRS, icon_symbols()))


BRAND_ICONS = os.path.join(SRC, "brand_icons")  # official CC0 files from @iconify-json/logos and simple-icons, copied verbatim


def brand_svg(name):
    with open(os.path.join(BRAND_ICONS, name), encoding="utf-8") as f:
        return f.read()


def brand_paths(name, keep_fill=True):
    """The <path> elements of an official brand icon file, plus its viewBox. Never redrawn by hand."""
    svg = brand_svg(name)
    vb = re.search(r'viewBox="([^"]+)"', svg).group(1)
    paths = re.findall(r"<path\b[^>]*/>", svg)
    if not keep_fill:
        paths = [re.sub(r'\sfill="[^"]*"', "", x) for x in paths]
    return vb, paths


def brand_sprite():
    vb, paths = brand_paths("logos-google-icon.svg")
    return ('<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">'
            '<symbol id="kh-g" viewBox="%s">%s</symbol></svg>' % (vb, "".join(x.replace("<path ", '<path stroke="none" ') for x in paths)))


def g_icon(cls="g-ic"):
    return '<svg class="%s" viewBox="0 0 256 262" aria-hidden="true" focusable="false"><use href="#kh-g"/></svg>' % cls


ICON_SLUGS = {"group-ancillary", "ancillary", "group-benefits"}


def icon(slug, cls=""):
    return '<svg class="ic%s" aria-hidden="true" focusable="false" %s><use href="#i-%s"/></svg>' % (
        (" " + cls) if cls else "", ICON_ATTRS, esc(slug))


def icon_tile(slug):
    return '<span class="card-ic" aria-hidden="true">%s</span>' % icon(slug)


def anc_href(cat_key):
    return "ancillary.html?from=%s" % cat_key


def product_href(p, cat):
    return anc_href(cat["key"]) if p == "ancillary" else "%s.html" % p


def plabel(C, p):
    return C["products"].get(p, {}).get("nav_label") or FORM_LABEL[p]


def clabel(C, cat):
    return C["categories"].get(cat["slug"], {}).get("nav_label") or cat["label"]


def theme_button():
    return ('<button type="button" class="theme-btn" data-theme-open aria-haspopup="dialog" aria-controls="themeDrawer" aria-label="Theme">'
            '<span class="sw" aria-hidden="true"></span><span class="tb-v">Theme</span></button>')


def brand_lock():
    # Two images; site.js keeps the alt text on whichever one the theme shows.
    return ('<a class="brand-lock" href="index.html">'
            '<img class="logo logo-light" src="brand/king-health-wordmark.png" alt="King Health, home" width="945" height="557">'
            '<img class="logo logo-dark" src="brand/king-health-wordmark-reverse.png" alt="" width="945" height="557">'
            '<span class="kh-leaves" aria-hidden="true"><i></i><i></i><i></i><i></i></span>'  # 2026-10-26: a few leaves drift from the tree
            '</a>')


STAR_D = "M12 3.6l2.5 5.3 5.8.7-4.3 4 1.1 5.7L12 16.5l-5.1 2.8 1.1-5.7-4.3-4 5.8-.7z"  # same star as site.js


def rating_data():
    """Average, total and links from the owner's Google snapshot (site/assets/reviews.json). None when absent."""
    try:
        with open(REVIEWS_JSON, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError):
        return None
    if not isinstance(d, dict) or d.get("average") is None:
        return None
    return d


def fmt_num(v):
    return ("%g" % v) if isinstance(v, (int, float)) else str(v)


def star_svgs(value, uid):
    """Five stars rounded to the nearest half, exactly as site.js starRow() renders them."""
    v = round(float(value) * 2) / 2
    out = []
    for i in range(1, 6):
        if v >= i:
            out.append('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path class="s-full" d="%s"/></svg>' % STAR_D)
        elif v >= i - 0.5:
            out.append('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><defs><clipPath id="%s"><rect x="0" y="0" width="12" height="24"/>'
                       '</clipPath></defs><path class="s-empty" d="%s"/><path class="s-full" clip-path="url(#%s)" d="%s"/></svg>' % (uid, STAR_D, uid, STAR_D))
        else:
            out.append('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path class="s-empty" d="%s"/></svg>' % STAR_D)
    return "".join(out)


def fill(tpl, d):
    return tpl.replace("{value}", fmt_num(d.get("average"))).replace("{total}", fmt_num(d.get("total", "")))


def google_badge(C, where):
    """Header rating pill, rendered at build time from the Google snapshot so it shows without JavaScript.
    Its numerals are Google's data, so the element is marked for the copy lint (data-lint-exempt="rating")."""
    d = rating_data()
    if not d or not page_live("reviews"):
        return ""
    r = C["reviews"]
    count = ('<i class="gb-count" aria-hidden="true">%s</i>' % esc(fill(r["badge_reviews"], d))) if d.get("total") is not None else ""
    return ('<a class="g-badge g-badge-%s" href="reviews.html" data-lint-exempt="rating" aria-label="%s">%s'
            '<b class="gb-val" aria-hidden="true">%s</b><i class="gb-stars rv-stars" aria-hidden="true">%s</i>%s</a>'
            % (where, esc(fill(r["badge_aria"], d)), g_icon("g-ic gb-g"), esc(fmt_num(d["average"])), star_svgs(d["average"], "gbs-" + where), count))


def header(C, active_cat=None, active=None):
    phone = C["site"].get("phone", PHONE_DEFAULT)
    drops = []
    for cat in CATS:
        items = "".join('<a href="%s">%s</a>' % (product_href(p, cat), esc(plabel(C, p))) for p in cat["products"])
        items += '<a class="all" href="%s.html">All %s</a>' % (cat["slug"], esc(clabel(C, cat)))
        cur = ' aria-current="page"' if active_cat == cat["slug"] else ""
        drops.append(
            '<div class="drop" data-drop data-cat="%(key)s">'
            '<a class="drop-link" href="%(slug)s.html"%(cur)s>%(label)s</a>'
            '<button type="button" class="drop-btn" aria-expanded="false" aria-controls="menu-%(key)s" aria-label="Show %(label)s pages">'
            '<span class="chev" aria-hidden="true"></span></button>'
            '<div class="drop-menu" id="menu-%(key)s" hidden>%(items)s</div></div>'
            % {"key": cat["key"], "slug": cat["slug"], "cur": cur, "label": esc(clabel(C, cat)), "items": items})
    simple = []
    for href, label, pid in (("about.html", "About Us", "about"),):  # 2026-10-25: Carriers left the main nav; it stays in the King Health bar and footer under About
        if not href_live(href):  # Wave 3: a hidden page leaves the main nav only because the page no longer exists
            continue
        cur = ' aria-current="page"' if active == pid else ""
        simple.append('<a class="nav-link" href="%s"%s>%s</a>' % (href, cur, label))
    contact_cur = ' aria-current="page"' if active == "contact" else ""
    mp = []
    for cat in CATS:
        cur = ' aria-current="page"' if active_cat == cat["slug"] else ""
        mp.append('<a class="mp-link" href="%s.html" data-cat-link="%s"%s>%s</a>' % (cat["slug"], cat["key"], cur, esc(clabel(C, cat))))
        mp.append('<div class="mp-sub">%s</div>' % "".join(
            '<a href="%s">%s</a>' % (product_href(p, cat), esc(plabel(C, p))) for p in cat["products"]))
    # 2026-10-26: phones drop the second nav bar, so the menu carries its links: King Health with About Us, FAQ, Carriers
    # and Client Reviews beneath it (the same pattern as the coverage groups above), then Contact Us.
    cur = ' aria-current="page"' if active == "home" else ""
    mp.append('<a class="mp-link" href="index.html"%s>King Health</a>' % cur)
    kh = []
    for href, label, pid in (("about.html", "About Us", "about"), ("faq.html", "FAQ", "faq"), ("carriers.html", "Carriers", "carriers"),
                             ("reviews.html", "Client Reviews", "reviews")):
        if not href_live(href):
            continue
        cur = ' aria-current="page"' if active == pid else ""
        kh.append('<a href="%s"%s>%s</a>' % (href, cur, label))
    if kh:
        mp.append('<div class="mp-sub">%s</div>' % "".join(kh))
    if href_live("contact.html"):
        cur = ' aria-current="page"' if active == "contact" else ""
        mp.append('<a class="mp-link" href="contact.html"%s>Contact Us</a>' % cur)
    return """<a class="skip" href="#main">Skip to content</a>
<header class="site-header" id="siteHeader">
  <div class="container hd">
    %(brand)s
    <nav class="nav" aria-label="Primary">%(drops)s%(simple)s</nav>
    <div class="hd-right">
      %(badge)s
      <a class="hd-phone" href="#" data-config="phone-link"><span data-config="phone">%(phone)s</span></a>
      %(theme)s
      <a class="btn btn-accent hd-cta" href="contact.html"%(ccur)s>Contact Us</a>
      <button type="button" class="menu-btn" id="menuBtn" aria-expanded="false" aria-controls="menuPanel"><span class="burger" aria-hidden="true"></span>Menu</button>
    </div>
  </div>
</header>
<div class="menu-panel" id="menuPanel" role="dialog" aria-modal="true" aria-label="Site menu">
  <div class="container mp-top">
    %(brand)s
    <button type="button" class="menu-btn menu-close" id="menuClose">Close</button>
  </div>
  <nav class="container mp-body" aria-label="Mobile">
    %(mp)s
    <div class="mp-foot">
      %(mbadge)s
      %(theme)s
      <a class="btn btn-accent" href="contact.html">Request a consultation</a>
      <a class="tlink" href="#" data-config="phone-link"><span>Call <span data-config="phone">%(phone)s</span></span></a>
    </div>
  </nav>
</div>
""" % {"brand": brand_lock(), "drops": "".join(drops), "simple": "".join(simple), "phone": esc(phone),
       "theme": theme_button(), "ccur": contact_cur, "mp": "\n    ".join(mp),
       "badge": "", "mbadge": ""}  # 2026-10-25: the rating badge floats in the lower right corner instead (see tail)


def second_nav(label, label_href, label_current, links, aria, attrs="", cta_label="Contact Us", cta_href="contact.html",
               cta_current=False):
    """Wave 3: the one second nav bar markup, shared by the category bars and the King Health bar.
    links: [(href, label, is_current)]. attrs: extra attributes on the <nav> (data-from, hidden, data-site-nav)."""
    cur = ' aria-current="page"'
    items = ['<li class="sn-label-item"><a class="sn-label" href="%s"%s>%s</a></li>' % (
        label_href, cur if label_current else "", esc(label))]
    items += ['<li><a href="%s"%s>%s</a></li>' % (href, cur if on else "", esc(text)) for href, text, on in links]
    return ('<nav class="subnav" aria-label="%s"%s><div class="container sn">'
            '<ul class="sn-list">%s</ul></div></nav>\n'  # 2026-10-26: the trailing Contact Us link left the second bar (client request)
            % (esc(aria), attrs, "".join(items)))


def subnav(C, cat, current, hidden=False):
    links = [(product_href(p, cat), plabel(C, p), current == p) for p in cat["products"]]
    return second_nav(clabel(C, cat), "%s.html" % cat["slug"], current == cat["slug"], links, "%s pages" % clabel(C, cat),
                      attrs=' data-from="%s"%s' % (cat["key"], " hidden" if hidden else ""))


def site_nav(C, current=None):
    """Wave 3: the King Health second nav for every page without a category bar. Labels come from content.json site_nav;
    items whose page is hidden are dropped. current is a site nav key, "home", "contact" or None."""
    cfg = site_nav_config(C)
    links = [(i["href"], i["label"], current == i.get("key")) for i in cfg["items"] if href_live(i["href"])]
    cta = cfg.get("cta") or SITE_NAV_DEFAULT["cta"]
    return second_nav(cfg["label"], cfg.get("label_href", "index.html"), current == "home", links,
                      "%s pages" % cfg["label"], attrs=" data-site-nav", cta_label=cta["label"], cta_href=cta["href"],
                      cta_current=current == "contact")


def banner(P, slot, heading, lede, kicker="", kicker_href="", home=False, kicker_attr=""):
    if kicker_href:
        kick = '<p class="kicker"><a href="%s"%s>%s</a></p>' % (kicker_href, kicker_attr, esc(kicker))
    elif kicker:
        kick = '<p class="kicker">%s</p>' % esc(kicker)
    else:
        kick = ""
    acts = ""
    if home:
        acts = ('<div class="hero-acts"><a class="btn btn-band" href="#consult">Request a consultation</a>'
                '<a class="tlink" href="#categories"><span>Explore coverage</span></a></div>')
    slides = hero_slides_html(P.C) if home and getattr(P, "C", None) else ""
    if slides:
        media = slides
    else:
        one = P.img(slot, eager=True, decorative=not home, banner=not home)
        msrc = re.search(r'\bsrc="([^"]+)"', one)
        if msrc and not home:  # 2026-10-25: every page banner runs edge to edge: blurred backdrop of the same photo, sharp photo right of the card
            mw = re.search(r'\bwidth="(\d+)"', one); mh = re.search(r'\bheight="(\d+)"', one)
            media = '<div class="hero-media hero-wide"><div class="hero-photo">%s</div></div>' % one
        else:
            media = '<div class="hero-media">%s</div>' % one
    return """  <section class="%(cls)s%(sl)s" aria-labelledby="page-title">
    %(media)s
    <div class="container">
      <div class="hero-band band">
        %(kick)s<h1 id="page-title" tabindex="-1">%(h)s</h1>
        <p class="band-lede">%(lede)s</p>%(acts)s
      </div>
    </div>
  </section>
""" % {"cls": "hero" if home else "banner", "sl": " hero-has-slides" if slides else "", "media": media, "kick": kick,
       "h": esc(heading), "lede": esc(lede), "acts": acts}


def directs(C):
    s = C["site"]
    return """<ul class="directs">
          <li><span class="k">Phone</span><a href="#" data-config="phone-link"><span data-config="phone">%s</span></a></li>
          <li><span class="k">Email</span><a href="#" data-config="email-link"><span data-config="email">%s</span></a></li>
          <li><span class="k">Hours</span><span>%s</span></li>%s
        </ul>""" % (esc(s.get("phone", PHONE_DEFAULT)), esc(s.get("email", EMAIL_DEFAULT)), esc(s.get("hours", "")),
              service_areas_item(C))  # Wave 4, E: the service areas as a short list under hours


def coverage_options_html():
    out = ['<option value="">Select coverage</option>']
    for cat, opts in COVERAGE_MAP.items():
        out.append('<optgroup label="%s">%s</optgroup>' % (esc(cat), "".join("<option>%s</option>" % esc(o) for o in opts)))
    return "".join(out)


def universal_form(C, heading, text, preset_cat="", preset_cov="", aside=None, follow_from=False, after_band=False, aside_extra="", faq=None, faq_heading=""):
    """The universal form, identical on every page apart from its preset and intro copy.
    Wave 5: with faq, a category specific question list sits to the right of the form (stacks under it on phones)."""
    cat_opts = '<option value="">Select a category</option>' + "".join("<option>%s</option>" % esc(o) for o in CATEGORY_OPTIONS)
    ff = ' data-preset-follow-from="true"' if follow_from else ""
    aside_html = ""
    if aside is not None:
        aside_html = """<aside class="consult-aside" aria-label="Direct contact">
        %s
        <p class="kicker">Speak with us directly</p>
        %s%s
        <p class="fine">Coverage is subject to underwriting and carrier approval. Every application is placed through King Health.</p>
      </aside>""" % (('<div class="aside-media">%s</div>' % aside) if aside else "", directs(C), aside_extra)
    out = """  <section class="section tint consult%(ab)s" id="consult" tabindex="-1" aria-labelledby="consult-title">
    <div class="container %(grid)s">
      <div class="panel">
        <div data-form-wrap>
          <p class="kicker">Request a consultation</p>
          <h2 id="consult-title">%(h)s</h2>
          <p class="panel-lede">%(t)s</p>
          <div class="kh-form-slot" data-ghl-embed="">
            <!-- GOHIGHLEVEL FORM EMBED SLOT
                 Paste the GoHighLevel form embed code (the iframe and its script tag) directly below this comment,
                 inside this div. When an iframe is present the native form below hides itself, and the kh-ghl-bridge
                 script appends this page's preset (category and coverage) to the iframe src as URL parameters.
                 Leave the native form in place: it is the fallback if the embed is ever removed. See GHL_FORM_SETUP.md. -->
            <form class="form kh-native-form" data-kh-form data-preset-category="%(pc)s" data-preset-coverage="%(pv)s"%(ff)s novalidate>
              <div class="field">
                <label for="first_name">First name <span class="req">(required)</span></label>
                <input id="first_name" name="first_name" type="text" autocomplete="given-name" required aria-describedby="err-first_name">
                <span class="err" id="err-first_name"></span>
              </div>
              <div class="field">
                <label for="last_name">Last name <span class="req">(required)</span></label>
                <input id="last_name" name="last_name" type="text" autocomplete="family-name" required aria-describedby="err-last_name">
                <span class="err" id="err-last_name"></span>
              </div>
              <div class="field">
                <label for="phone">Phone <span class="req">(required)</span></label>
                <input id="phone" name="phone" type="tel" autocomplete="tel" inputmode="tel" required aria-describedby="err-phone">
                <span class="err" id="err-phone"></span>
              </div>
              <div class="field">
                <label for="email">Email <span class="req">(required)</span></label>
                <input id="email" name="email" type="email" autocomplete="email" inputmode="email" required aria-describedby="err-email">
                <span class="err" id="err-email"></span>
              </div>
              <div class="field" data-field="category">
                <label for="category">How can we help? <span class="req">(required)</span></label>
                <select id="category" name="category" required aria-describedby="err-category">%(cat_opts)s</select>
                <span class="err" id="err-category"></span>
              </div>
              <div class="field" data-field="coverage">
                <label for="coverage">Coverage of interest <span class="req">(required)</span></label>
                <select id="coverage" name="coverage" aria-describedby="err-coverage">%(cov_opts)s</select>
                <span class="err" id="err-coverage"></span>
              </div>
              <div class="field full">
                <label for="message">Anything you would like us to know <span class="req">(optional)</span></label>
                <textarea id="message" name="message" rows="4"></textarea>
              </div>
              <div class="hp" aria-hidden="true">
                <label for="company_website">Company website</label>
                <input id="company_website" name="company_website" type="text" tabindex="-1" autocomplete="off">
              </div>
              <div class="field full">
                <div class="check">
                  <input id="consent_contact" name="consent_contact" type="checkbox" required aria-describedby="err-consent_contact">
                  <label for="consent_contact">I agree that King Health may contact me about my request by phone, email or text message. <span class="req">(required)</span></label>
                </div>
                <span class="err" id="err-consent_contact"></span>
              </div>
              <div class="field full">
                <div class="check">
                  <input id="consent_sms" name="consent_sms" type="checkbox">
                  <label for="consent_sms">By checking this box, I agree to receive text messages from King Health about my inquiry, including follow up and appointment reminders, at the phone number provided. Message frequency varies. Message and data rates may apply. Reply STOP to opt out or HELP for help. Consent to receive text messages is not a condition of purchase. See our <a href="privacy.html">privacy policy</a>. <span class="req">(optional)</span></label>
                </div>
              </div>
              <div class="field full">
                <button class="btn btn-accent btn-submit" type="submit" data-submit>Send my request</button>
              </div>
              <div class="field full form-status" data-status role="status" aria-live="polite"></div>
            </form>
          </div>
        </div>
        <div class="success-panel" data-success hidden>
          <p class="kicker">Request received</p>
          <h2 tabindex="-1" data-success-title>Thank you. Your request has reached us.</h2>
          <p class="panel-lede">We will reach out shortly to arrange a conversation at a time that suits you. If you would like to speak sooner, you are welcome to call us at <a href="#" data-config="phone-link"><span data-config="phone">%(phone)s</span></a>.</p>
          <p class="fine demo-note" data-demo-note hidden>This site is in demonstration mode, so your request was not transmitted.</p>
          <button class="btn btn-line" type="button" data-reset>Send another request</button>
        </div>
      </div>
      %(aside)s
    </div>
  </section>
""" % {"ab": " after-band" if after_band else "", "grid": "contact-grid" if aside is not None else "consult-solo",
       "h": esc(heading), "t": esc(text), "pc": esc(preset_cat), "pv": esc(preset_cov), "ff": ff, "cat_opts": cat_opts,
       "cov_opts": coverage_options_html(), "phone": esc(C["site"].get("phone", PHONE_DEFAULT)), "aside": aside_html}
    if faq:
        out = out.replace('<div class="container consult-solo">', '<div class="container consult-faq">', 1)
        out = out.replace("      \n    </div>\n  </section>\n", "      %s\n    </div>\n  </section>\n" % consult_faq_aside(faq, faq_heading, C["site"].get("phone", PHONE_DEFAULT)), 1)
    return out



def consult_faq_aside(faq, heading, phone):
    """Wave 5: compact accordion beside the consultation form on category pages. The first answer opens by default."""
    items = []
    for i, qa in enumerate(faq, 1):
        first = i == 1
        items.append('<li><h3><button type="button" aria-expanded="%s" aria-controls="cfaq-a%d" id="cfaq-q%d">%s<span class="pm" aria-hidden="true"></span></button></h3>'
                     '<div class="ans" id="cfaq-a%d" role="region" aria-labelledby="cfaq-q%d"%s><p>%s</p></div></li>'
                     % ("true" if first else "false", i, i, esc(qa["q"]), i, i, "" if first else " hidden", esc(qa["a"])))
    return """<aside class="consult-faq-aside" aria-labelledby="cfaq-title">
        <p class="kicker">Common questions</p>
        <h2 id="cfaq-title">%s</h2>
        <ul class="faq cfaq" data-faq>%s</ul>
        <p class="fine">Prefer to talk it through? Call <a href="#" data-config="phone-link"><span data-config="phone">%s</span></a> and we will answer in person.</p>
      </aside>""" % (esc(heading), "".join(items), esc(phone))


def contact_faq_html(C):
    """2026-10-25: the general questions also appear on the Contact page, under the direct contact list in its aside."""
    h = C["home"]
    if not h.get("faq"):
        return ""
    block = consult_faq_aside(h["faq"], h.get("faq_heading", ""), C["site"].get("phone", PHONE_DEFAULT))
    inner = block.split(">", 1)[1].rsplit("</aside>", 1)[0]
    inner = inner.replace('id="cfaq-title"', 'id="cfaq-title" class="cfaq-sub"')
    return '<div class="contact-faq" aria-labelledby="cfaq-title">%s</div>' % inner


def faq_page_groups(C, flat=False):
    """2026-10-25: every question on the site, grouped by topic for faq.html. A question already shown in an earlier group is
    not repeated. With flat=True, returns the de-duplicated list of {q, a} for the FAQPage structured data."""
    seen, groups = set(), []
    def take(title, gid, faqs, href=""):
        items = [qa for qa in (faqs or []) if qa["q"] not in seen]
        for qa in items:
            seen.add(qa["q"])
        if items:
            groups.append({"id": gid, "title": title, "href": href, "items": items})
    take("Working with King Health", "general", C["home"].get("faq"))
    if page_live("about"):
        take("About King Health", "about", C["about"].get("faq"), "about.html")
    for cat in CATS:
        cc = C["categories"][cat["slug"]]
        merged = list(cc.get("faq", []))
        for p in cat["products"]:
            merged += C["products"][p].get("faq", [])
        take(clabel(C, cat), cat["slug"], merged, "%s.html" % cat["slug"])
    if page_live("carriers"):
        take("Carriers", "carriers", C.get("carriers_faq", {}).get("faq"), "carriers.html")
    if flat:
        return [qa for g in groups for qa in g["items"]]
    return groups


def build_faq(C, P):
    """2026-10-25: the FAQ page. A topic index on the left, grouped accordions on the right, the universal form below."""
    f = C["faq_page"]
    groups = faq_page_groups(C)
    toc = "".join('<li><a href="#faq-%s">%s</a></li>' % (g["id"], esc(g["title"])) for g in groups)
    blocks, n = [], 0
    for g in groups:
        lis = []
        for qa in g["items"]:
            n += 1
            lis.append('<li><h3><button type="button" aria-expanded="false" aria-controls="fq-a%d" id="fq-q%d">%s<span class="pm" aria-hidden="true"></span></button></h3>'
                       '<div class="ans" id="fq-a%d" role="region" aria-labelledby="fq-q%d" hidden><p>%s</p></div></li>' % (n, n, esc(qa["q"]), n, n, esc(qa["a"])))
        more = ('<a class="tlink faqp-more" href="%s"><span>Explore %s</span></a>' % (g["href"], esc(g["title"]))) if g["href"] and g["id"] not in ("about", "carriers") else ""
        blocks.append('<section class="faqp-group" id="faq-%s" aria-labelledby="faq-%s-h"><div class="faqp-head"><h2 id="faq-%s-h">%s</h2>%s</div><ul class="faq" data-faq>%s</ul></section>'
                      % (g["id"], g["id"], g["id"], esc(g["title"]), more, "".join(lis)))
    body = banner(P, "banner_faq", f["heading"], f["lede"], kicker=f.get("kicker", "FAQ"))
    body += """  <section class="section after-band faqp" aria-label="%s">
    <div class="container faqp-wrap">
      <nav class="legal-toc faqp-toc reveal" aria-label="%s">
        <p class="kicker">%s</p>
        <ol>%s</ol>
      </nav>
      <div class="faqp-body reveal">%s</div>
    </div>
  </section>
""" % (esc(f["heading"]), esc(f.get("index_label", "Topics")), esc(f.get("index_label", "Topics")), toc, "\n        ".join(blocks))
    body += universal_form(C, f["form_heading"], f["form_text"])
    return page(C, f["heading"], f["lede"], "faq", body, active="faq")


def duo_tags_html(pc):
    """2026-10-25: coverage pills. A pill with text and bullets opens a short explainer on hover, keyboard focus or tap."""
    lis = []
    for i, t in enumerate(pc["duo_tags"], 1):
        if isinstance(t, str):
            lis.append("<li>%s</li>" % esc(t))
            continue
        tip = '<div class="duo-tip" id="duo-tip-%d" role="tooltip"><p class="duo-tip-title">%s</p><p>%s</p><ul>%s</ul></div>' % (
            i, esc(t["label"]), esc(t["text"]), "".join("<li>%s</li>" % esc(b) for b in t.get("bullets", [])))
        lis.append('<li class="has-tip"><button type="button" class="duo-tag" aria-describedby="duo-tip-%d" aria-expanded="false" data-tip>%s</button>%s</li>'
                   % (i, esc(t["label"]), tip))
    hint = ('<p class="duo-tags-hint">%s</p>' % esc(pc["duo_tags_hint"])) if pc.get("duo_tags_hint") else ""
    return '\n        <div class="duo-tags"><p class="duo-tags-label">%s</p>%s<ul>%s</ul></div>' % (esc(pc.get("duo_tags_label", "")), hint, "".join(lis))

def license_value(site, key):
    """Optional content.json site keys; a visible blank until the client supplies them (the spec's placeholder)."""
    v = (site.get(key) or "").strip()
    return ('<span data-lint-exempt="license">%s</span>' % esc(v)) if v else "[ &nbsp; ]"


def footer(C):
    """Compact footer (client feedback): one slim row, a gold hairline, one legal row, disclosures behind a toggle."""
    s = C["site"]
    links = [("%s.html" % cat["slug"], clabel(C, cat)) for cat in CATS]
    links += [("about.html", "About Us"), ("faq.html", "FAQ"), ("carriers.html", "Carriers"), ("contact.html", "Contact Us")]
    links = [(h, l) for h, l in links if href_live(h)]
    terms = '\n      <a href="terms.html">Terms</a>' if page_live("terms") else ""
    return """<footer class="site-footer">
  <div class="container">
    <div class="ft-row">
      <a class="ft-logo" href="index.html"><img src="brand/king-health-emblem.png" alt="King Health, home" width="673" height="720" loading="lazy"></a>
      <nav class="ft-links" aria-label="Footer">%(links)s</nav>
      <div class="ft-contact">
        <a href="#" data-config="phone-link"><span data-config="phone">%(phone)s</span></a>
        <a href="#" data-config="email-link"><span data-config="email">%(email)s</span></a>
      </div>
    </div>
%(more)s
    <div class="ft-legal">
      <span class="ft-license">License number: %(lic)s</span>
      <span class="ft-license">Licensed in: %(states)s</span>%(areas)s
      <a href="privacy.html">Privacy</a>%(terms)s
      <a href="accessibility.html">Accessibility</a>
      <details class="ft-disc">
        <summary>Disclosures<span class="chev" aria-hidden="true"></span></summary>
        <p>%(disc)s</p>
      </details>
      <span class="ft-copy">&copy; %(year)s King Health. All rights reserved.</span>
    </div>
  </div>
</footer>
""" % {"links": "".join('<a href="%s">%s</a>' % (h, esc(l)) for h, l in links), "phone": esc(s.get("phone", PHONE_DEFAULT)),
       "email": esc(s.get("email", EMAIL_DEFAULT)), "disc": esc(s.get("disclosure", "")), "year": YEAR,
       "areas": service_areas_line(C), "lic": license_value(s, "license_number"), "states": license_value(s, "licensed_in"), "more": footer_more(C),
       "terms": terms}


def social_icon(key):
    """White glyphs on brand filled circles. Instagram and WhatsApp use the simple-icons single path glyphs. Facebook uses the
    white "f" from the official logos file, because the simple-icons Facebook glyph is the whole roundel and would read as a
    white disc inside the blue circle; the "f" sits on the circle edge exactly as in Facebook's own mark."""
    if key == "facebook":
        vb, paths = brand_paths("logos-facebook.svg")
        f = [x for x in paths if 'fill="#fff"' in x][0].replace(' fill="#fff"', "")
        return '<svg class="soc-g soc-g-full" viewBox="%s" aria-hidden="true" focusable="false" fill="currentColor">%s</svg>' % (vb, f)
    vb, paths = brand_paths("simple-%s.svg" % key, keep_fill=False)
    return '<svg class="soc-g" viewBox="%s" aria-hidden="true" focusable="false" fill="currentColor">%s</svg>' % (vb, "".join(paths))


SOCIAL = (("facebook", "Facebook", "noopener me"), ("instagram", "Instagram", "noopener me"), ("whatsapp", "WhatsApp", "noopener"))


def footer_more(C):
    """Wave 2, A9.3: one quiet row beneath the gold divider; social links shown as recognizable icons with accessible names (client request 2026-10-25)."""
    s = C["site"]
    fm = s.get("footer_more", {})
    social = s.get("social", {})
    rows = (("blog.html", fm.get("blog", "Blog")), ("join-the-team.html", fm.get("join", "Join the Team")))
    links = ""
    if href_live("reviews.html"):  # 2026-10-25: the Google reviews link stands out (G icon, Google yellow stars)
        d = rating_data()
        val = ('<b class="ft-g-val" data-lint-exempt="rating">%s</b>%s' % (esc(fmt_num(d["average"])), '<i class="rv-stars ft-g-stars" aria-hidden="true">%s</i>' % star_svgs(d["average"], "ftg"))) if d else ""
        links += '<a class="ft-greviews" href="reviews.html">%s<span>%s</span>%s</a>' % (g_icon("g-ic ft-g-ic"), esc(fm.get("google_reviews", "Google Reviews")), val)
    links += "".join('<a href="%s">%s</a>' % (h, esc(l)) for h, l in rows if href_live(h))
    items = []
    for key, label, rel in SOCIAL:
        url = (social.get(key) or "").strip()
        if url:
            items.append('<a href="%s" target="_blank" rel="%s" data-social="%s" aria-label="%s (opens in a new tab)" title="%s">%s</a>'
                         % (esc(url), rel, key, label, label, social_icon(key)))
        elif not RELEASE:
            items.append('<a href="#" data-social="%s" data-placeholder aria-label="%s" title="%s">%s</a>' % (key, label, label, social_icon(key)))
    soc = ('<nav class="ft-social" aria-label="%s">%s</nav>' % (esc(fm.get("social_label", "King Health on social media")), "".join(items))
           if items else "")
    if not links and not soc:
        return ""
    links_html = ('<nav class="ft-more-links" aria-label="More from King Health">%s</nav>' % links) if links else ""
    qr = ""  # 2026-10-25: the contact QR moved to the About page (founder section); see about_contact_card()
    return """    <div class="ft-more ft-more-3">
      <div class="ft-col ft-col-l">%s</div>
      <div class="ft-col ft-col-c">%s</div>
      <div class="ft-col ft-col-r">%s</div>
    </div>""" % (links_html, qr, soc)


def vcard_text(C):
    """2026-10-25: the contact card behind the footer QR code, built from site facts (vCard 3.0, CRLF)."""
    s = C["site"]; cc = s.get("contact_card") or {}
    if not cc:
        return ""
    def v(x):
        return str(x or "").replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;")
    a = s.get("address") or {}
    tel = tel_e164(s.get("phone", ""))
    lines = ["BEGIN:VCARD", "VERSION:3.0",
             "N:%s;%s;;;" % (v(cc.get("last_name")), v(cc.get("first_name"))),
             "FN:%s %s" % (v(cc.get("first_name")), v(cc.get("last_name"))),
             "ORG:%s" % v(s.get("legal_name") or s.get("name", "King Health")),
             "TITLE:%s" % v(cc.get("title"))]
    if tel:
        lines.append("TEL;TYPE=WORK:%s" % re.sub(r"[^0-9+]", "", tel))
    if real_email(s):
        lines.append("EMAIL:%s" % real_email(s))
    if a.get("city"):
        lines.append("ADR;TYPE=WORK:;;%s;%s;%s;%s;%s" % (v(a.get("street")), v(a.get("city")), v(a.get("region")), v(a.get("postal_code")), v(a.get("country", "US"))))
    if cc.get("website"):
        lines.append("URL:%s" % cc["website"])
    if cc.get("note"):
        lines.append("NOTE:%s" % v(cc["note"]))
    lines.append("END:VCARD")
    return "\r\n".join(lines) + "\r\n"


QR_FALLBACK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "contact-qr.svg")


def contact_qr_svg(C):
    """The QR encodes the vCard itself, so a phone camera offers Add Contact even offline.
    segno renders it when installed; otherwise the last generated copy in src/contact-qr.svg is reused."""
    text = vcard_text(C)
    if not text:
        return ""
    svg = ""
    try:
        import segno
        q = segno.make(text, error="l")
        rows = [list(r) for r in q.matrix]
        n, border = len(rows), 2
        # 2026-10-26: black and gold. The three corner finder rings are deep gold (5.6 to 1 contrast on white, well above
        # what phone scanners need); every data module stays black so the code reads exactly as before.
        def ring(x, y):
            return (x < 7 and y < 7 and not (2 <= x <= 4 and 2 <= y <= 4)) or \
                   (x >= n - 7 and y < 7 and not (n - 5 <= x <= n - 3 and 2 <= y <= 4)) or \
                   (x < 7 and y >= n - 7 and not (2 <= x <= 4 and n - 5 <= y <= n - 3))
        cell = lambda x, y: "M%d %dh1v1h-1z" % (x + border, y + border)
        d = "".join(cell(x, y) for y, r in enumerate(rows) for x, v in enumerate(r) if v and not ring(x, y))
        g = "".join(cell(x, y) for y, r in enumerate(rows) for x, v in enumerate(r) if v and ring(x, y))
        size = n + 2 * border
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" shape-rendering="crispEdges">'
               '<rect width="%d" height="%d" fill="white"/><path fill="#111111" d="%s"/><path fill="#8a6a10" d="%s"/></svg>'
               % (size, size, size, size, d, g))
        with open(QR_FALLBACK, "w", encoding="utf-8") as f:
            f.write(svg)
    except Exception:
        if os.path.exists(QR_FALLBACK):
            with open(QR_FALLBACK, encoding="utf-8") as f:
                svg = f.read()
    if not svg:
        return ""
    return svg.replace("<svg ", '<svg class="ft-qr-code" role="img" aria-hidden="true" focusable="false" ', 1)


def footer_qr(C):
    """Centered contact card in the footer: the QR on top, one caption beneath that suits both scanning and tapping."""
    cc = C["site"].get("contact_card") or {}
    code = contact_qr_svg(C)
    if not code:
        return ""
    label = cc.get("label", "Scan or tap to save contact")
    return ('<a class="ft-qr" href="%s" download="%s" aria-label="%s, downloads a contact card">%s<span class="ft-qr-label">%s</span></a>'
            % (esc(cc.get("file", "contact.vcf")), esc(cc.get("file", "contact.vcf")), esc(label), code, esc(label)))


def about_contact_card(C):
    """About page, founder section: the QR that saves Javon's contact (scan on a computer, tap on a phone)."""
    cc = C["site"].get("contact_card") or {}
    code = contact_qr_svg(C)
    if not code:
        return ""
    f = esc(cc.get("file", "contact.vcf"))
    return ('<div class="save-card reveal"><a class="save-card-qr" href="%s" download="%s" aria-label="%s, downloads a contact card">%s</a>'
            '<div class="save-card-body"><p class="save-card-h">%s</p><p class="save-card-t">%s</p>'
            '<a class="tlink" href="%s" download="%s"><span>%s</span></a></div></div>'
            % (f, f, esc(cc.get("label", "Save contact")), code, esc(cc.get("heading", "")), esc(cc.get("text", "")),
               f, f, esc(cc.get("link", "Download the contact card"))))


HERO_SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hero_slides")


def hero_slides_html(C):
    """2026-10-25: home hero crossfade slideshow. The build resizes each master photo to web copies (1800 and 900 wide),
    the first slide loads with the page and the rest load after it, so the slideshow costs no more than the old single photo."""
    cfg = (C.get("home") or {}).get("hero_slides") or {}
    items = [it for it in cfg.get("items", []) if os.path.exists(os.path.join(HERO_SRC_DIR, it.get("file", "")))]
    if len(items) < 2:
        return ""
    from PIL import Image
    out_dir = os.path.join(SITE, "media", "hero")
    os.makedirs(out_dir, exist_ok=True)
    slides = []
    for i, it in enumerate(items):
        stem = os.path.splitext(it["file"])[0]
        src = os.path.join(HERO_SRC_DIR, it["file"])
        names = {}
        for w in (1800, 900):
            name = "%s-%d.jpg" % (stem, w)
            dst = os.path.join(out_dir, name)
            if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src):
                im = Image.open(src).convert("RGB")
                if im.width > w:
                    im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
                im.save(dst, "JPEG", quality=78, optimize=True, progressive=True)
            names[w] = name
        with Image.open(os.path.join(out_dir, names[1800])) as im:
            iw, ih = im.size
        srcset = "media/hero/%s 900w, media/hero/%s 1800w" % (names[900], names[1800])
        pos = esc(it.get("pos", "50% 35%"))
        if i == 0:
            img = ('<img src="media/hero/%s" srcset="%s" sizes="(max-width: 760px) 100vw, 64vw" alt="%s" width="%d" height="%d" '
                   'loading="eager" fetchpriority="high" decoding="async" style="object-position:%s">' % (names[1800], srcset, esc(it.get("alt", "")), iw, ih, pos))
        else:
            img = ('<img data-src="media/hero/%s" data-srcset="%s" sizes="(max-width: 760px) 100vw, 64vw" alt="%s" width="%d" height="%d" '
                   'decoding="async" style="object-position:%s">' % (names[1800], srcset, esc(it.get("alt", "")), iw, ih, pos))
        # backdrop: the same small web copy, blurred and tinted behind the whole hero so the left side is never empty
        bg = ""  # rev 3: solid brand green backdrop in CSS; no blurred copy
        slides.append('<div class="hero-slide%s"%s>%s<div class="hero-photo">%s</div></div>'
                      % (" is-on" if i == 0 else "", "" if i == 0 else ' aria-hidden="true"', bg, img))
    btn = ('<button type="button" class="hero-pause" data-hero-pause aria-pressed="false" data-label-pause="%s" data-label-play="%s" aria-label="%s" hidden>'
           '<span class="hp-ic" aria-hidden="true"></span></button>'
           % (esc(cfg.get("pause_label", "Pause")), esc(cfg.get("play_label", "Play")), esc(cfg.get("pause_label", "Pause"))))
    return ('<div class="hero-media hero-slides" data-hero-slides data-interval="%d">%s</div>%s'
            % (int(cfg.get("interval_seconds", 7)) * 1000, "".join(slides), btn))


def drawer():
    tiles = []
    for slug, name, mode, scheme, t in THEMES:
        tiles.append(
            '<button type="button" class="tile" data-set-theme="%s" aria-pressed="false">'
            '<span class="tp" data-theme="%s" aria-hidden="true"><span class="tp-card"></span><span class="tp-l1"></span>'
            '<span class="tp-l2"></span><span class="tp-band"></span><span class="tp-bl"></span><span class="tp-btn"></span></span>'
            '<span class="tile-name">%s</span><span class="tile-mode">%s</span></button>' % (slug, slug, esc(name), esc(mode)))
    return """<div class="drawer-scrim" id="drawerScrim" hidden></div>
<aside class="drawer" id="themeDrawer" role="dialog" aria-modal="true" aria-labelledby="drawerTitle" hidden>
  <div class="dr-head">
    <h2 id="drawerTitle">Choose a theme</h2>
    <button type="button" class="dr-close" id="drawerClose">Close</button>
  </div>
  <div class="dr-body">
    <p>Every page, chart and form follows the theme you choose, and your choice is remembered on this device.</p>
    <div class="tiles" role="group" aria-label="Themes">%s</div>
  </div>
  <div class="dr-foot"><button type="button" class="dr-reset" id="themeReset">Return to the signature theme</button></div>
</aside>
""" % "".join(tiles)


FLOAT_BADGE = ""  # set in main() once hidden pages are known


def tail():
    return FLOAT_BADGE + """<script src="assets/site.js" defer></script>
<script src="assets/kh-ghl-bridge.js" id="kh-ghl-bridge" defer></script>
</body>
</html>
"""


def page(C, title, desc, pid, body, active_cat=None, active=None, sub=""):
    full_title = title if "King Health" in title else "%s | King Health" % title
    if pid == "home":  # 2026-10-26: the home page carries no second nav bar (client request); every other page keeps it
        sub = ""
    elif not sub:  # Wave 3: every page without a category bar carries the King Health bar
        sub = site_nav(C, SITE_NAV_CURRENT.get(pid))
    return (head(full_title, desc, pid) + header(C, active_cat, active) + sub
            + '<main id="main" tabindex="-1">\n' + body + "</main>\n" + footer(C) + drawer() + tail())


# --------------------------------------------------------------------------------------
# Charts (Summit SVG). Primary series reads --chart-primary, one gold element per chart.
# --------------------------------------------------------------------------------------
NOTE = '<span class="chart-note">Illustration only. Actual results depend on the policy and carrier.</span>'


def chart(kind, title=None, caption=None):
    if kind == "term":
        bars = "".join('<rect class="bar s-b" style="--i:%d" x="%d" y="%d" width="30" height="%d"/>' % (i, 14 + 40 * i, y, 204 - y)
                       for i, y in enumerate([54, 64, 76, 89, 103, 117, 132, 147, 162, 176, 190]))
        return """<figure class="chart chart-term">
  <p class="chart-title">%s</p>
  <div class="chart-stage"><svg viewBox="0 0 520 220" role="img" aria-label="Illustration: what a family would need declines in steps from today to later years, while level term coverage stays constant above it for the full term.">
  <rect class="cband" x="8" y="26" width="446" height="178"/>
  <rect class="band-outline" x="8" y="26" width="446" height="178"/>
  %s
  <line class="baseline" x1="4" y1="204" x2="516" y2="204"/>
</svg><span class="ov" style="left:3.08%%;top:15.91%%">Your term coverage</span></div>
  <div class="chart-axis" aria-hidden="true"><span>Today</span><span>Later years</span></div>
  <ul class="chart-legend"><li><span class="key key-outline" aria-hidden="true"></span>Your term coverage</li><li><span class="key key-b" aria-hidden="true"></span>What your family would need</li></ul>
  <figcaption>%s%s</figcaption>
</figure>""" % (esc(title or "Coverage sized to the years that matter most"), bars,
                esc(caption or "Level coverage sized to the years your family depends on your income."), NOTE)
    if kind == "iul":
        return """<figure class="chart chart-iul">
  <p class="chart-title">%s</p>
  <div class="chart-stage"><svg viewBox="0 44 560 168" role="img" aria-label="Illustration: across a run of years the market index rises and falls, sometimes below the baseline. Your credited interest follows the gains but is trimmed at a dashed cap line, and it never falls below the floor in down years.">
  <rect class="bar s-a" style="--i:0" x="10" y="95.0" width="17" height="55.0"/><rect class="bar s-b" style="--i:1" x="30" y="95.0" width="17" height="55.0"/><rect class="bar s-a" style="--i:1" x="58" y="65.0" width="17" height="85.0"/><rect class="bar s-b" style="--i:2" x="78" y="90.0" width="17" height="60.0"/><rect class="bar neg s-a" style="--i:2" x="106" y="150" width="17" height="45.0"/><rect class="bar s-b" style="--i:3" x="126" y="146" width="17" height="4"/><rect class="bar s-a" style="--i:3" x="154" y="120.0" width="17" height="30.0"/><rect class="bar s-b" style="--i:4" x="174" y="120.0" width="17" height="30.0"/><rect class="bar s-a" style="--i:4" x="202" y="55.0" width="17" height="95.0"/><rect class="bar s-b" style="--i:5" x="222" y="90.0" width="17" height="60.0"/><rect class="bar neg s-a" style="--i:5" x="250" y="150" width="17" height="30.0"/><rect class="bar s-b" style="--i:6" x="270" y="146" width="17" height="4"/><rect class="bar s-a" style="--i:6" x="298" y="88.0" width="17" height="62.0"/><rect class="bar s-b" style="--i:7" x="318" y="90.0" width="17" height="60.0"/><rect class="bar s-a" style="--i:7" x="346" y="132.0" width="17" height="18.0"/><rect class="bar s-b" style="--i:8" x="366" y="132.0" width="17" height="18.0"/><rect class="bar s-a" style="--i:8" x="394" y="70.0" width="17" height="80.0"/><rect class="bar s-b" style="--i:9" x="414" y="90.0" width="17" height="60.0"/><rect class="bar neg s-a" style="--i:9" x="442" y="150" width="17" height="55.0"/><rect class="bar s-b" style="--i:10" x="462" y="146" width="17" height="4"/>
  <line class="cap" x1="4" y1="90.0" x2="490" y2="90.0"/>
  <line class="floor" x1="4" y1="150" x2="490" y2="150"/>
</svg><span class="ov ov-r" style="left:88.93%%;top:27.38%%">Cap</span><span class="ov ov-r" style="left:88.93%%;top:63.10%%">Floor</span></div>
  <div class="chart-axis" aria-hidden="true"><span>Early years</span><span>Later years</span></div>
  <ul class="chart-legend"><li><span class="key key-a" aria-hidden="true"></span>Market index</li><li><span class="key key-b" aria-hidden="true"></span>Your credited interest</li><li><span class="key key-cap" aria-hidden="true"></span>Cap</li><li><span class="key key-floor" aria-hidden="true"></span>Floor</li></ul>
  <figcaption>%s%s</figcaption>
</figure>""" % (esc(title or "How interest is credited"),
                esc(caption or "Interest is credited from index gains up to a cap, and a floor protects the cash value in down years."), NOTE)
    if kind == "ring":
        return """<figure class="chart chart-ring">
  <p class="chart-title">%s</p>
  <div class="chart-stage"><svg viewBox="0 0 200 200" role="img" aria-label="Illustration: a ring that sweeps to full, made mostly of guaranteed income with a smaller share of growth potential.">
  <circle class="track" cx="100" cy="100" r="76" pathLength="100"/>
  <circle class="seg seg-a" cx="100" cy="100" r="76" pathLength="100"/>
  <circle class="seg seg-b" cx="100" cy="100" r="76" pathLength="100"/>
  <circle class="seg seg-gold" cx="100" cy="100" r="89" pathLength="100"/>
</svg><span class="ring-center" aria-hidden="true">Income<br>for life</span><ul class="chart-legend"><li><span class="key key-b" aria-hidden="true"></span>Guaranteed income</li><li><span class="key key-a" aria-hidden="true"></span>Growth potential</li><li><span class="key key-gold-line" aria-hidden="true"></span>The guarantee</li></ul></div>
  <figcaption>%s%s</figcaption>
</figure>""" % (esc(title or "Income built on a guaranteed foundation"),
                esc(caption or "A guaranteed income base, with room for growth linked to the contract's crediting method."), NOTE)
    if kind == "plan":
        return """<figure class="chart chart-ring chart-plan">
  <p class="chart-title">%s</p>
  <div class="chart-stage"><svg viewBox="0 0 200 200" role="img" aria-label="Illustration: a ring that sweeps to full in three parts, health coverage, life insurance and retirement income, held together by an outer gold line that represents one coordinated plan for the household.">
  <circle class="track" cx="100" cy="100" r="76" pathLength="100"/>
  <circle class="seg seg-p1" cx="100" cy="100" r="76" pathLength="100"/>
  <circle class="seg seg-p2" cx="100" cy="100" r="76" pathLength="100"/>
  <circle class="seg seg-p3" cx="100" cy="100" r="76" pathLength="100"/>
  <circle class="seg seg-gold seg-gold-full" cx="100" cy="100" r="89" pathLength="100"/>
</svg><span class="ring-center" aria-hidden="true">Your<br>household</span><ul class="chart-legend"><li><span class="key key-b" aria-hidden="true"></span>Health coverage</li><li><span class="key key-mid" aria-hidden="true"></span>Life insurance</li><li><span class="key key-light" aria-hidden="true"></span>Retirement income</li><li><span class="key key-gold-line" aria-hidden="true"></span>One coordinated plan</li></ul></div>
  <figcaption>%s%s</figcaption>
</figure>""" % (esc(title or "How a thoughtful plan fits together"), esc(caption or ""), NOTE)
    raise ValueError(kind)


def paras(items, cls=""):
    if isinstance(items, str):
        items = [items]
    c = ' class="%s"' % cls if cls else ""
    return "".join("<p%s>%s</p>" % (c, esc(t)) for t in items)


def trio(items, heading, hid, gold=False, tint=False, note=""):
    cells = "".join('<div class="trio-item"><h3>%s</h3><p>%s</p></div>' % (esc(i["title"]), esc(i["text"])) for i in items)
    note_html = '<p class="trio-note reveal">%s</p>' % esc(note) if note else ""
    return """  <section class="section%(tint)s" aria-labelledby="%(hid)s">
    <div class="container">
      <h2 class="h2 trio-title reveal" id="%(hid)s">%(h)s</h2>
      <div class="trio%(gold)s reveal">%(cells)s</div>
      %(note)s
    </div>
  </section>
""" % {"tint": " tint" if tint else "", "hid": hid, "h": esc(heading), "gold": " trio-gold" if gold else "", "cells": cells, "note": note_html}



def why_band(w, photo=""):
    """Wave 5: the Why King Health commitments as a deep band with numbered panels (numerals come from CSS counters)."""
    cells = "".join('<article class="why-card">%s<h3>%s</h3><p>%s</p></article>' % (
        ('<span class="why-ic" aria-hidden="true">%s</span>' % icon(i["icon"])) if i.get("icon") else "", esc(i["title"]), esc(i["text"])) for i in w["items"])
    if not photo:
        return """  <section class="section band why-band" aria-labelledby="why-title">
    <div class="container">
      <div class="why-head reveal">
        <div><p class="kicker">%s</p><h2 class="h2" id="why-title">%s</h2></div>
        <p class="band-lede">%s</p>
      </div>
      <div class="why-grid reveal">%s</div>
    </div>
  </section>
""" % (esc(w.get("kicker", "The King Health standard")), esc(w["heading"]), esc(w.get("lede", "")), cells)
    return """  <section class="section band why-band" aria-labelledby="why-title">
    <div class="container">
      <div class="why-split">
        <div class="why-copy">
          <div class="why-head reveal">
            <p class="kicker">%s</p><h2 class="h2" id="why-title">%s</h2>
            <p class="band-lede">%s</p>
          </div>
          <div class="why-grid reveal">%s</div>
        </div>
        <figure class="why-photo reveal">%s</figure>
      </div>
    </div>
  </section>
""" % (esc(w.get("kicker", "The King Health standard")), esc(w["heading"]), esc(w.get("lede", "")), cells, photo)

def photo_card(P, slot, href, title, text, link_text, used, alternates, ic=""):
    return """<article class="card card-photo%s reveal">
        <div class="card-media">%s</div>
        <div class="card-body">%s<h3><a href="%s">%s</a></h3><p>%s</p><span class="tlink" aria-hidden="true"><span>%s</span></span></div>
      </article>""" % (" has-ic" if ic else "", P.img(slot, used=used, alternates=alternates), icon_tile(ic) if ic else "",
                       href, esc(title), esc(text), esc(link_text))


def text_card(href, title, text, link_text, ic=""):
    return """<article class="card card-text%s reveal">
        <div class="card-body">%s<h3><a href="%s">%s</a></h3><p>%s</p><span class="tlink" aria-hidden="true"><span>%s</span></span></div>
      </article>""" % (" has-ic" if ic else "", icon_tile(ic) if ic else "", href, esc(title), esc(text), esc(link_text))


def faq_block(faq, heading, lede, after=""):
    items = []
    for i, qa in enumerate(faq, 1):
        items.append(
            '<li><h3><button type="button" aria-expanded="false" aria-controls="faq-a%d" id="faq-q%d">%s<span class="pm" aria-hidden="true"></span></button></h3>'
            '<div class="ans" id="faq-a%d" role="region" aria-labelledby="faq-q%d" hidden><p>%s</p></div></li>'
            % (i, i, esc(qa["q"]), i, i, esc(qa["a"])))
    return """  <section class="section" id="faq" aria-labelledby="faq-title">
    <div class="container faq-wrap">
      <div class="reveal"><h2 class="h2" id="faq-title">%s</h2><p class="lede">%s</p></div>
      <ul class="faq reveal" data-faq>%s</ul>
    </div>%s
  </section>
""" % (esc(heading), esc(lede), "".join(items), after)


# --------------------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------------------
def build_home(C, P):
    h = C["home"]
    used = {P.get("hero_home")["file"]}
    cards = []
    for cat in CATS:
        cc = C["categories"][cat["slug"]]
        cards.append(photo_card(P, "card_%s" % cat["slug"], "%s.html" % cat["slug"], clabel(C, cat), cc.get("card_text", ""),
                                "Explore coverage", used, ["banner_%s" % cat["slug"]], ic=cat["slug"]))
    body = banner(P, "hero_home", h["hero_heading"], h["hero_lede"], kicker="Independent insurance advisory", home=True)
    body += """  <section class="section after-band" id="categories" tabindex="-1" aria-labelledby="cat-title">
    <div class="container">
      <div class="sec-head reveal"><h2 class="h2" id="cat-title">%s</h2><p>%s</p></div>
      <div class="cards cards-4">%s</div>
    </div>
  </section>
""" % (esc(h["category_intro"]["heading"]), esc(h["category_intro"]["text"]), "".join(cards))
    body += carrier_strip(C, "home")
    body += why_band(h["why"])  # 2026-10-25: client kept the three panel layout; why_band(w, photo) still supports a photo
    body += """  <section class="section tint" aria-labelledby="strip-title">
    <div class="container split strip">
      <div class="split-media reveal">%s</div>
      <div class="split-body reveal">
        <p class="kicker">About King Health</p>
        <h2 id="strip-title">%s</h2>
        <p>%s</p>
        %s
      </div>
    </div>
  </section>
""" % (P.img("about_strip", used=used), esc(h["about_strip"]["heading"]), esc(h["about_strip"]["text"]),
       '<a class="tlink" href="about.html"><span>Meet King Health</span></a>' if page_live("about") else "")
    body += """  <section class="section" aria-labelledby="plan-title">
    <div class="container split chart-split">
      <div class="split-body reveal"><p class="kicker">Coordinated coverage</p><h2 class="h2" id="plan-title">%s</h2><p>%s</p></div>
      <div class="reveal">%s</div>
    </div>
  </section>
""" % (esc(h["chart"]["title"]), esc(h["chart"]["caption"]), chart(HOME_CHART, h["chart"]["title"], ""))
    body += home_reviews(C)
    body += universal_form(C, h["form_intro"]["heading"], h["form_intro"]["text"], faq=h.get("faq"), faq_heading=h.get("faq_heading", ""))
    return page(C, "King Health | Insurance Advisory You Can Trust", h["hero_lede"], "home", body)


def build_category(C, P, cat):
    cc = C["categories"][cat["slug"]]
    cards = [text_card(product_href(p, cat), plabel(C, p), C["products"][p].get("card_text", ""), "Explore %s" % plabel(C, p), ic=p)
             for p in cat["products"]]
    ov = cc.get("overview", [])
    body = banner(P, "banner_%s" % cat["slug"], clabel(C, cat), cc["heading"].rstrip(".") + ".", kicker="Coverage category")
    body += """  <section class="section after-band" aria-labelledby="ov-title">
    <div class="container overview reveal">
      <div><p class="kicker">Overview</p><h2 class="vh" id="ov-title">%s overview</h2></div>
      <div>%s</div>
    </div>
  </section>
  <section class="section tint" aria-labelledby="opts-title">
    <div class="container">
      <div class="sec-head reveal"><h2 class="h2" id="opts-title">Coverage within %s</h2></div>
      <div class="cards cards-%d">%s</div>
    </div>
  </section>
""" % (esc(clabel(C, cat)), paras(ov[:1], "statement") + paras(ov[1:]), esc(clabel(C, cat)), len(cards), "".join(cards))
    body += trio(cc["help"]["items"], cc["help"]["heading"], "help-title")
    body += universal_form(C, cc["form_intro"]["heading"], cc["form_intro"]["text"], preset_cat=cat["label"], preset_cov=ALL_OR_UNSURE,
                           faq=cc.get("faq"), faq_heading=cc.get("faq_heading", "%s, answered" % clabel(C, cat)))
    return page(C, cc.get("title") or cat["label"], cc["lede"], cat["slug"], body, active_cat=cat["slug"],
                sub=subnav(C, cat, cat["slug"]))


def build_product(C, P, p):
    pc = C["products"][p]
    shared = p == "ancillary"
    cat = CAT_BY_KEY["senior"] if shared else CAT_BY_SLUG[pc["category"]]
    used = {P.get("banner_%s" % p)["file"]}
    alternates = []
    for q in cat["products"]:
        if q != p:
            alternates += ["card_%s" % q, "banner_%s" % q]
    body = banner(P, "banner_%s" % p, plabel(C, p), pc["heading"].rstrip(".") + ".", kicker=clabel(C, cat), kicker_href="%s.html" % cat["slug"],
                  kicker_attr=' data-from-kicker' if shared else "")
    body += """  <section class="section after-band" aria-labelledby="glance-title">
    <div class="container prow">
      <div class="prow-body reveal">
        <p class="kicker">%s</p>
        <h2 class="h2" id="glance-title">Coverage at a glance</h2>
        <div class="copy">%s</div>
      </div>
      <div class="prow-media reveal">%s</div>
    </div>
  </section>
""" % (esc(plabel(C, p)), paras(pc.get("at_a_glance", [])), P.img("card_%s" % p, used=used, alternates=alternates, near_fold=True))
    kind = CHARTS.get(p)
    if pc.get("duo_cards") and not kind:
        # 2026-10-25: "Who it is designed for" and "How the plan works" side by side as cards (client request, group ancillary first)
        body += """  <section class="section tint duo-sec" aria-label="Who it is designed for and how the plan works">
    <div class="container duo">
      <article class="duo-card reveal" aria-labelledby="suits-title">
        <span class="duo-ic" aria-hidden="true">%s</span>
        <p class="kicker">Who it serves</p>
        <h2 class="h2" id="suits-title">Who it is designed for</h2>
        <div class="copy">%s</div>%s
      </article>
      <article class="duo-card reveal" aria-labelledby="how-title">
        <span class="duo-ic" aria-hidden="true">%s</span>
        <p class="kicker">The mechanics</p>
        <h2 class="h2" id="how-title">How the plan works</h2>
        <div class="copy">%s</div>
      </article>
    </div>
  </section>
""" % (icon("group-benefits"), paras(pc.get("designed_for", [])),
       duo_tags_html(pc) if pc.get("duo_tags") else "",
       icon(p if p in ICON_SLUGS else "ancillary"), paras(pc.get("how_it_works", [])))
        kind = "__done__"
    else:
        body += """  <section class="section tint" aria-labelledby="suits-title">
    <div class="container sec-head sec-copy reveal">
      <h2 class="h2" id="suits-title">Who it is designed for</h2>
      <div class="copy">%s</div>
    </div>
  </section>
""" % paras(pc.get("designed_for", []))
    if kind == "__done__":
        pass
    elif kind:
        body += """  <section class="section" aria-labelledby="how-title">
    <div class="container prow how">
      <div class="prow-body reveal"><h2 class="h2" id="how-title">How the plan works</h2><div class="copy">%s</div></div>
      <div class="reveal">%s</div>
    </div>
  </section>
""" % (paras(pc.get("how_it_works", [])), chart(kind))
    else:
        body += """  <section class="section" aria-labelledby="how-title">
    <div class="container sec-head sec-copy reveal">
      <h2 class="h2" id="how-title">How the plan works</h2>
      <div class="copy">%s</div>
    </div>
  </section>
""" % paras(pc.get("how_it_works", []))
    group = (not shared) and cat["slug"] == "group-benefits"
    # 2026-10-26: carriers appear only on the home page and the Carriers page (client request); product_carriers() stays available.
    # 2026-10-25: the product questions now sit beside the form (consult_faq_aside); faq_block stays available for other pages.
    if p == "medicare":
        body += '  <section class="section tpmo-sec" aria-label="Medicare disclaimer">\n    <div class="container">%s</div>\n  </section>\n' % tpmo_block(C)
    body += universal_form(C, "Speak with us about %s" % plabel(C, p),
                           "Share a few details, and we will reach out personally to arrange a conversation at a time that suits you. There is never any cost or obligation for our guidance.",
                           preset_cat=cat["label"], preset_cov=FORM_LABEL[p], follow_from=shared,
                           faq=pc.get("faq"), faq_heading=pc.get("faq_heading", "%s, answered" % plabel(C, p)))
    if shared:
        sub = "".join(subnav(C, CAT_BY_KEY[k], p, hidden=(k != "senior")) for k in ANCILLARY_FROM)
    else:
        sub = subnav(C, cat, p)
    return page(C, pc.get("title") or FORM_LABEL[p], pc["lede"], p, body, active_cat=cat["slug"], sub=sub)


def build_about(C, P):
    a = C["about"]
    used = {P.get("banner_about")["file"]}
    mission = a["mission"].strip()
    if a.get("mission_body"):
        mission_lead, mission_body = mission, a["mission_body"]
    else:  # Picasso critique finding 7: the first sentence leads, the rest follows unchanged
        m = re.match(r"(.+?[.!?])\s+(.*)$", mission, re.S)
        mission_lead, mission_body = (m.group(1), m.group(2)) if m else (mission, "")
    portrait = P.img("about_portrait_placeholder", used=used, alternates=["about_strip"])
    body = banner(P, "banner_about", a["heading"], a["lede"], kicker="About Us")
    body += """  <section class="section after-band" aria-labelledby="mission-title">
    <div class="container mission reveal">
      <h2 class="kicker" id="mission-title">%s</h2>
      <span class="mission-rule" aria-hidden="true"></span>
      <p class="mission-text">%s</p>
      <p class="mission-body">%s</p>
      <span class="mission-rule mission-rule-end" aria-hidden="true"></span>
    </div>
  </section>
  <section class="section tint" aria-labelledby="story-title">
    <div class="container split">
      <!-- PLACEHOLDER PORTRAIT: a stock photograph stands in here until a portrait of Javon King is supplied.
           Replace the about_portrait_placeholder slot in _build/photos.json and re-run the build. Never caption this image as Javon. -->
      <figure class="split-media portrait-slot reveal" data-placeholder="true">%s<figcaption class="vh">Placeholder image. A portrait of Javon King will replace this stock photograph.</figcaption></figure>
      <div class="split-body reveal">
        <p class="kicker">Founder and principal advisor</p>
        <h2 id="story-title">%s</h2>
        %s
        %s
      </div>
    </div>
  </section>
""" % (esc(a.get("mission_heading", "Our mission")), esc(mission_lead), esc(mission_body), portrait, esc(a["story_heading"]), paras(a.get("story", [])), about_contact_card(C))
    body += trio(a["values"], a["values_heading"], "values-title", note=a.get("service_note", ""))
    more = a.get("more")
    cards = [c for c in (more or {}).get("cards", []) if href_live(c["href"])]
    if cards:  # Wave 2, A10: the About link row, after the promise and before the form. Wave 3 drops cards whose page is hidden.
        body += """  <section class="section more-row" aria-labelledby="more-title">
    <div class="container">
      <p class="kicker reveal">%s</p><h2 class="vh" id="more-title">%s</h2>
      <div class="cards cards-%d">%s</div>
    </div>
  </section>
""" % (esc(more["kicker"]), esc(more["heading"]), max(len(cards), 2), "".join(text_card(c["href"], c["title"], c["text"], c["link"]) for c in cards))
    h = C["home"]["form_intro"]
    body += universal_form(C, h["heading"], h["text"], faq=a.get("faq"), faq_heading=a.get("faq_heading", ""))
    return page(C, a.get("heading") or "About Us", a["lede"], "about", body, active="about")


def build_carriers(C, P):
    c = C["carriers"]
    logos = c.get("logos", {}) if isinstance(c.get("logos"), dict) else {}
    rows = []
    for name in c.get("sections", []):
        sid = re.sub(r"[^a-z]+", "-", name.lower()).strip("-")
        imgs = [x for x in logos.get(name, []) if x]
        named = [car for car in (c.get("carrier_list") or []) if name in car.get("lines", [])]
        if named and not imgs:
            strip = '<ul class="logo-strip has-logos carrier-tiles" aria-label="%s carriers">%s</ul>' % (esc(name), "".join(carrier_tile(car, "ctile") for car in named))
        elif imgs:
            strip = '<div class="logo-strip has-logos">%s</div>' % "".join(
                '<img src="%s" alt=""%s loading="lazy">' % (esc(x), logo_dims(x)) for x in imgs)  # Wave 4: dimensions
        else:
            strip = ('<div class="logo-strip">\n          <!-- GHL: add the carrier logo images for %s here. Plain images only; logos are never links. -->\n'
                     '          <p class="logo-strip-note">Carrier logos for this line appear here</p>\n        </div>' % esc(name))
        ic = icon(CARRIER_ICON[name]) if name in CARRIER_ICON else ""
        rows.append("""<section class="carrier-row reveal" aria-labelledby="cs-%(id)s">
        <h2 class="h3" id="cs-%(id)s">%(ic)s%(n)s</h2>
        %(strip)s
      </section>""" % {"n": esc(name), "id": sid, "strip": strip, "ic": ic})
    body = banner(P, "banner_carriers", c["heading"], c["lede"], kicker="Carriers")
    strip_html = carrier_strip(C, "carriers")
    body += strip_html
    body += """  <!-- CARRIERS PAGE: the client places carrier logos in each coverage line below, in GoHighLevel, by dragging plain
       logo images into the strip for that line. Logos are shown for reference only and must never be links. -->
  <section class="section %s" aria-labelledby="carrier-intro">
    <div class="container">
      <div class="sec-head carrier-head reveal"><h2 class="h2" id="carrier-intro">Carriers by coverage</h2><p>%s</p></div>
      <div class="carrier-list">%s</div>
      <p class="carrier-note reveal">%s</p>
    </div>
  </section>
""" % ("after-strip" if strip_html else "after-band", esc(c.get("intro", "")), "\n      ".join(rows), esc(c.get("note", "")))
    cf = C.get("carriers_faq", {})
    body += universal_form(C, "Ask which carriers serve your area",
                           "Tell us where you live and what you would like to protect, and we will explain which carriers we can offer you and how their plans compare.",
                           faq=cf.get("faq"), faq_heading=cf.get("heading", ""))
    return page(C, c.get("heading") or "Carriers", c["lede"], "carriers", body, active="carriers")


def build_contact(C, P):
    c = C["contact"]
    used = {P.get("banner_contact")["file"]}
    aside = ""  # Picasso critique finding 9: the direct column leads with phone, email and hours
    stages = "".join('<div class="stage"><h3>%s</h3><p>%s</p></div>' % (esc(n["title"]), esc(n["text"])) for n in c.get("next", []))
    body = banner(P, "banner_contact", c["heading"], c["lede"], kicker="Contact Us")
    extra = ""
    aside_links = [l for l in c.get("aside_links", []) if href_live(l["href"])]
    if aside_links:  # Wave 2, A10: two text links under hours; Wave 3 drops links to hidden pages
        extra = '\n        <div class="aside-links">%s</div>' % "".join(
            '<a class="tlink" href="%s"><span>%s</span></a>' % (esc(l["href"]), esc(l["text"])) for l in aside_links)
    body += universal_form(C, "Tell us how we can help",
                           "Required fields help us prepare before we call, and everything else is optional.",
                           aside=aside, after_band=True, aside_extra=extra + contact_faq_html(C))
    body += """  <section class="section" aria-labelledby="next-title">
    <div class="container stages-wrap">
      <div class="stages-intro reveal"><h2 class="h2" id="next-title">%s</h2></div>
      <div class="stages reveal" data-draw>%s</div>
    </div>
  </section>
""" % (esc(c["next_heading"]), stages)
    return page(C, c.get("heading") or "Contact Us", c["lede"], "contact", body, active="contact")


def build_legal(C, P, key, kicker):
    d = C[key]
    body = banner(P, "banner_%s" % key, d["heading"], C["site"].get("tagline", ""), kicker=kicker)
    extra = ('<p class="fine prose-fine">License number: %s &nbsp; Licensed in: %s</p>'
             % (license_value(C["site"], "license_number"), license_value(C["site"], "licensed_in"))) if key == "privacy" else ""
    if key == "privacy" and d.get("terms_sentence") and page_live("terms"):  # Wave 2, A10: Privacy closes by pointing to the Terms
        pre, _, post = d["terms_sentence"].partition("{link}")
        extra = '<p>%s<a href="terms.html">%s</a>%s</p>' % (esc(pre), esc(d.get("terms_link", "Terms and Conditions")), esc(post)) + extra
    body += """  <section class="section after-band" aria-label="%s">
    <div class="container prose reveal">%s%s</div>
  </section>
""" % (esc(d["heading"]), paras(d.get("body", [])), extra)
    first = (d.get("body") or [""])[0]
    return page(C, d["heading"], first[:155].rsplit(" ", 1)[0], key, body)



def build_legal_doc(C, P, key):
    """Legal documents (Privacy Policy, Terms and Conditions) in a formal layout: entity and effective date header,
    an On this page index, numbered sections (numbers come from CSS counters, so no numerals sit in the copy),
    definition rows, lists and a contact card. Wording comes from content.json; see each document's source_note."""
    d = C[key]
    s = C["site"]
    eff = (d.get("effective_date") or "").strip() or d.get("effective_placeholder", "[effective date]")
    domain = re.sub(r"^https?://(www\.)?", "", C.get("seo", {}).get("base_url", "")).rstrip("/") or "this website"
    email = d.get("support_email") or s.get("email", EMAIL_DEFAULT)
    mail = '<a href="mailto:%s">%s</a>' % (esc(email), esc(email))
    subs = {
        "{site_url}": esc(domain), "{support_email}": mail,
        "{privacy_link}": '<a href="privacy.html">Privacy Policy</a>',
        "{terms_link}": '<a href="terms.html">Terms and Conditions</a>',
        "{accessibility_link}": '<a href="accessibility.html">Accessibility statement</a>',
        "{cookies_link}": '<a href="#sec-cookies">Cookies and Tracking Technologies</a>',
        "{license_number}": license_value(s, "license_number"), "{licensed_in}": license_value(s, "licensed_in"),
        "{phone}": '<a href="#" data-config="phone-link"><span data-config="phone">%s</span></a>' % esc(s.get("phone", PHONE_DEFAULT)),
        "{email}": mail, "{governing_state}": "the United States",
    }
    def fmt(txt):
        h = esc(txt)
        for k, v in subs.items():
            h = h.replace(esc(k), v).replace(k, v)
        return h
    contact_card = """<div class="legal-contact">
          <p class="legal-contact-name">King Health LLC</p>
          <dl class="legal-defs">
            <div><dt>Email</dt><dd>%s</dd></div>
            <div><dt>Phone</dt><dd>%s</dd></div>
            <div><dt>License</dt><dd><span data-lint-exempt="license">%s</span></dd></div>
          </dl>
        </div>""" % (mail, subs["{phone}"], license_value(s, "license_number"))
    toc, secs = [], []
    for sec in d["sections"]:
        sid = "sec-%s" % sec["id"]
        toc.append('<li><a href="#%s">%s</a></li>' % (sid, esc(sec["h"])))
        parts = ["<p>%s</p>" % fmt(x) for x in sec.get("p", [])]
        if sec.get("list"):
            parts.append('<ul class="legal-list">%s</ul>' % "".join("<li>%s</li>" % fmt(x) for x in sec["list"]))
        if sec.get("defs"):
            parts.append('<dl class="legal-defs">%s</dl>' % "".join('<div><dt>%s</dt><dd>%s</dd></div>' % (esc(a), fmt(b)) for a, b in sec["defs"]))
        parts += ["<p>%s</p>" % fmt(x) for x in sec.get("after", [])]
        if sec.get("tpmo"):
            parts.append(tpmo_block(C))
        if sec.get("contact"):
            parts.append(contact_card)
        secs.append('<section class="legal-sec" id="%s" aria-labelledby="%s-h"><h2 id="%s-h">%s</h2>%s</section>'
                    % (sid, sid, sid, esc(sec["h"]), "".join(parts)))
    closing = ""
    if key == "privacy" and d.get("terms_sentence") and page_live("terms"):
        pre, _, post = d["terms_sentence"].partition("{link}")
        closing = '<p class="legal-closing">%s<a href="terms.html">%s</a>%s</p>' % (esc(pre), esc(d.get("terms_link", "Terms and Conditions")), esc(post))
    pending = key == "terms" and bool(d.get("counsel_review_pending", True))
    note = ""
    if pending:
        note = ("<!-- COUNSEL REVIEW REQUIRED: this document should be reviewed by licensed counsel before publication. -->\n        "
                + ('<p class="fine terms-review">%s</p>' % esc(d.get("review_notice", "")) if not RELEASE else ""))
    body = banner(P, "banner_%s" % key, d["heading"], d.get("lede", ""), kicker=d.get("kicker", "Legal"))
    body += """  <section class="section after-band legal" aria-label="%(h)s">
    <div class="container legal-wrap">
      <nav class="legal-toc reveal" aria-label="On this page">
        <p class="kicker">On this page</p>
        <ol>%(toc)s</ol>
      </nav>
      <article class="legal-doc reveal">
        %(note)s<header class="legal-meta">
          <p class="legal-entity">King Health LLC</p>
          <p class="legal-title">%(h)s</p>
          <dl>
            <div><dt>%(el)s</dt><dd class="terms-eff"><span data-lint-exempt="date">%(eff)s</span></dd></div>
            <div><dt>Applies to</dt><dd>%(dom)s and King Health services</dd></div>
          </dl>
        </header>
        <div class="legal-preamble">%(pre)s</div>
        %(secs)s
        %(closing)s
      </article>
    </div>
  </section>
""" % {"h": esc(d["heading"]), "toc": "".join(toc), "note": note, "el": esc(d.get("effective_label", "Effective")), "eff": esc(eff),
       "dom": esc(domain), "pre": "".join("<p>%s</p>" % fmt(x) for x in d.get("preamble", [])), "secs": "\n        ".join(secs), "closing": closing}
    return page(C, d["heading"], d.get("description", d.get("lede", "")), key, body)


# --------------------------------------------------------------------------------------
# Wave 2 components and pages (PICASSO_DIRECTION_KING_HEALTH_WAVE2_2026_10_24.md, Parts A and B)
# --------------------------------------------------------------------------------------
REVIEWS_JSON = os.path.join(SITE, "assets", "reviews.json")
BUILD_DIR_RV = os.path.dirname(os.path.abspath(__file__))


def reviews_json_present():
    try:
        with open(REVIEWS_JSON, encoding="utf-8") as f:
            data = json.load(f)
        return bool(data.get("reviews") or data.get("average"))
    except (OSError, ValueError, AttributeError):
        return False


def review_source(C):
    return bool((C.get("reviews", {}).get("widget_embed") or "").strip()) or reviews_json_present()


def ext_link(url, label, cls, extra_attrs=""):
    """A link that opens Google in a new tab. Empty URLs become marked placeholders in review builds and vanish at release."""
    if url:
        return '<a class="%s" href="%s" target="_blank" rel="noopener"%s>%s<span class="vh"> (opens in a new tab)</span></a>' % (
            cls, esc(url), extra_attrs, esc(label))
    if RELEASE:
        return ""
    return '<a class="%s" href="#" data-placeholder%s>%s</a>' % (cls, extra_attrs, esc(label))



def carrier_logo_file(slug):
    """2026-10-25: the logo file for a carrier slug in site/media/carriers, if one has been added."""
    for ext in ("svg", "png", "webp"):
        rel = "media/carriers/%s.%s" % (slug, ext)
        if os.path.exists(os.path.join(SITE, rel)):
            return rel
    return ""


def logo_height(src, area=4400, lo=22, hi=46):
    """2026-10-26: optical sizing. Each logo gets the same visual area, so a wide wordmark and a square badge read at one weight."""
    size = image_size(os.path.join(SITE, src.split("?", 1)[0]))
    if not size or not size[1]:
        return 34
    aspect = size[0] / float(size[1])
    return int(round(max(lo, min(hi, (area / aspect) ** 0.5))))


def carrier_tile(car, cls):
    """A carrier tile: the logo when its file exists, otherwise the carrier name set in type."""
    src = carrier_logo_file(car["slug"])
    if src:
        return '<li class="%s"><img src="%s" alt="%s"%s style="--lh:%dpx" loading="lazy" decoding="async"></li>' % (
            cls, esc(src), esc(car["name"]), logo_dims(src), logo_height(src))
    return '<li class="%s carrier-name" title="%s"><span>%s</span></li>' % (cls, esc(car["name"]), esc(car.get("short") or car["name"]))


def product_carriers(C, p):
    """2026-10-26: carrier tiles on a coverage page, drawn from carriers.carrier_list by the line named in carriers.product_lines."""
    c = C["carriers"]
    line = (c.get("product_lines") or {}).get(p)
    named = [car for car in (c.get("carrier_list") or []) if line and line in car.get("lines", [])]
    if not named:
        return ""
    b = c.get("product_block", {})
    link = ""
    if page_live("carriers"):
        link = '<div class="pcar-foot"><a class="tlink" href="carriers.html"><span>%s</span></a></div>' % esc(b.get("link", "View every carrier by coverage"))
    return """  <section class="section pcar-sec" aria-labelledby="pcar-title">
    <div class="container">
      <div class="sec-head reveal"><p class="kicker">%s</p><h2 class="h2" id="pcar-title">%s</h2><p>%s</p></div>
      <ul class="logo-strip has-logos carrier-tiles reveal" aria-label="%s carriers">%s</ul>
      %s
    </div>
  </section>
""" % (esc(b.get("kicker", "Carriers")), esc(b.get("heading", "Carriers we place for %s") % plabel(C, p)), esc(b.get("text", "")),
       esc(line), "".join(carrier_tile(car, "ctile") for car in named), link)


def carrier_strip(C, context):
    """A4: the Appointed carriers strip. Static and wrapped by default; site.js moves it only when real logos overflow."""
    c = C["carriers"]
    st = c.get("strip", {})
    logos = c.get("logos") if isinstance(c.get("logos"), list) else []
    logos = [l for l in logos if isinstance(l, dict) and l.get("src")]
    clist = c.get("carrier_list") or []
    if not logos and not clist and RELEASE:
        return ""
    if clist and not logos:
        items = "".join(carrier_tile(car, "cstrip-item") for car in clist)
        sr = ""
    elif logos:
        items = "".join('<li class="cstrip-item"><img src="%s" alt="%s"%s loading="lazy" decoding="async"></li>' % (
            esc(l["src"]), esc(l.get("alt", "")), logo_dims(l["src"])) for l in logos)  # Wave 4: dimensions
        sr = ""
    else:
        items = "".join('<li class="cstrip-item cstrip-ph" data-placeholder><span>%s</span></li>' % esc(st.get("placeholder", "Carrier logo"))
                        for _ in range(6))
        sr = '<p class="vh">%s</p>' % esc(st.get("placeholder_sr", ""))
    note = st.get("note_carriers" if context == "carriers" else "note_home", "")
    link = ""
    if context == "home" and page_live("carriers"):
        link = '<div class="cstrip-foot"><a class="tlink" href="carriers.html"><span>%s</span></a></div>' % esc(st.get("home_link", ""))
    return """  <section class="cstrip cstrip-%(ctx)s" aria-labelledby="cstrip-title" data-cstrip-section>
    <div class="container">
      <div class="cstrip-in">
        <div class="cstrip-head">
          <p class="kicker" id="cstrip-title">%(label)s</p>
          <p class="cstrip-note">%(note)s</p>
        </div>%(sr)s
        <div class="cstrip-viewport" data-cstrip>
          <ul class="cstrip-track" aria-label="%(list)s">
            <!-- GHL: carrier logo images go here, one <li class="cstrip-item"><img ...></li> per carrier.
                 Use transparent PNG or SVG files, never JPG, so the logo works on every theme.
                 Alt text is the carrier's name exactly as the carrier writes it, for example alt="Carrier name".
                 Logos are reference only and are never links. Or list them under carriers.logos in content.json and rebuild. -->
            %(items)s
          </ul>
        </div>
        <button type="button" class="cstrip-toggle" aria-pressed="false" data-pause="%(pause)s" data-play="%(play)s" hidden>%(pause)s</button>
        %(link)s
      </div>
    </div>
  </section>
""" % {"ctx": context, "label": esc(st.get("label", "Appointed carriers")), "note": esc(note), "sr": sr,
       "list": esc(st.get("list_label", "")), "items": items, "pause": esc(st.get("pause", "Pause carrier logos")),
       "play": esc(st.get("play", "Play carrier logos")), "link": link}


def static_score(C, d, uid):
    """The rating figure, stars and count, rendered at build time (no layout shift, works without JavaScript).
    No nested div, so the copy lint can exempt the whole element (its numerals are Google's data)."""
    r = C["reviews"]
    total = ('<p class="rv-total">%s</p>' % esc(fill(r["based_on"], d))) if d.get("total") is not None else ""
    return ('<div class="rv-score" data-review-score data-rv-static data-lint-exempt="rating"><p class="rv-avg-row">'
            '<span class="rv-avg">%s</span><span class="rv-stars" role="img" aria-label="%s">%s</span></p>%s</div>'
            % (esc(fmt_num(d["average"])), esc(fill(r["rated"], d)), star_svgs(d["average"], uid), total))


def g_kicker(text, kid):
    return '<p class="kicker g-kicker" id="%s">%s<span>%s</span></p>' % (kid, g_icon("g-ic g-kicker-ic"), esc(text))


def review_summary(C):
    r = C["reviews"]
    d = rating_data() if not (r.get("widget_embed") or "").strip() else None
    if d:
        score = static_score(C, d, "rvs-sum")
    elif review_source(C):
        score = '<div class="rv-score" data-review-score></div>'
    else:
        score = '<div class="rv-score" data-review-score><p class="rv-score-ph" data-placeholder>%s</p></div>' % esc(r["score_placeholder"])
    return """<aside class="rv-summary rv-summary-g" aria-labelledby="rv-sum-title">
        %s
        %s
        <p class="rv-attrib">%s</p>
        %s
        %s
      </aside>""" % (g_kicker(r["summary_kicker"], "rv-sum-title"), score, esc(r["attribution"]),
                     ext_link(r.get("profile_url", ""), r["read_all"], "tlink rv-all", ' data-rv-profile'),
                     ext_link(r.get("write_review_url", ""), r["write"], "btn btn-line rv-write", ' data-rv-write'))


def review_band(C):
    """Reviews page: the rating summary as a full width band under the hero. Carries everything the side panel carried
    (kicker, score, attribution, both links) plus the Google count line and the verified profile line."""
    r = C["reviews"]
    d = rating_data() if not (r.get("widget_embed") or "").strip() else None
    if d:
        score = static_score(C, d, "rvs-band")
    elif review_source(C):
        score = '<div class="rv-score" data-review-score></div>'
    else:
        score = '<div class="rv-score" data-review-score><p class="rv-score-ph" data-placeholder>%s</p></div>' % esc(r["score_placeholder"])
    count = ""
    if d and d.get("total") is not None:
        count = '<p class="rvb-count" data-lint-exempt="rating">%s</p>' % esc(fill(r["band_count"], d))
    return """<aside class="rv-band rv-summary-g" aria-labelledby="rv-sum-title" data-rv-band>
        <div class="rvb-main">
          %(kicker)s
          %(score)s
          %(count)s
        </div>
        <div class="rvb-side">
          <p class="rvb-verified">%(verified)s</p>
          <p class="rv-attrib">%(attrib)s</p>
          <div class="rvb-acts">
            %(write)s
            %(all)s
          </div>
        </div>
      </aside>""" % {"kicker": g_kicker(r["summary_kicker"], "rv-sum-title"), "score": score, "count": count,
                     "verified": esc(r["band_verified"]), "attrib": esc(r["attribution"]),
                     "all": ext_link(r.get("profile_url", ""), r["read_all"], "tlink rv-all", ' data-rv-profile'),
                     "write": ext_link(r.get("write_review_url", ""), r["write"], "btn btn-line rv-write", ' data-rv-write')}


def review_slot(C, count, context):
    r = C["reviews"]
    widget = (r.get("widget_embed") or "").strip()
    src = ' data-reviews-src="assets/reviews.json"' if reviews_json_present() else ""
    ph = ""
    if not widget and not src:
        bar = '<span class="rv-ph-bar"></span>'
        ph = "".join('<article class="rv-card rv-ph" data-placeholder>%s<p class="rv-ph-label">%s</p></article>' % (
            bar * 3, esc(r["card_placeholder"])) for _ in range(count))
    more = ('<button type="button" class="btn btn-line rv-more" data-rv-more hidden>%s</button>' % esc(r["show_more"])) if context == "page" else ""
    if context == "home":  # carousel controls; site.js reveals them once the cards are rendered
        c = r["carousel"]
        more = ('<div class="rv-ctrl" data-rv-ctrl hidden>'
                '<button type="button" class="rv-arrow rv-prev" data-rv-prev aria-label="%s"><span class="rv-chev" aria-hidden="true"></span></button>'
                '<div class="rv-dots" data-rv-dots role="group" aria-label="%s"></div>'
                '<button type="button" class="rv-arrow rv-next" data-rv-next aria-label="%s"><span class="rv-chev" aria-hidden="true"></span></button>'
                '<p class="vh" aria-live="polite" data-rv-status></p></div>' % (esc(c["prev"]), esc(c["dots_label"]), esc(c["next"])))
    keys = ("based_on", "rated", "read_full", "reply_summary", "google_label")
    strings = {k: r[k] for k in keys if k in r}
    if context == "home":
        strings.update(r["carousel"])
    strings = json.dumps(strings)
    return """<div class="kh-review-slot" data-ghl-reviews="" data-rv-context="%(ctx)s"%(src)s data-rv-strings="%(strings)s">
          <!-- GOHIGHLEVEL REPUTATION WIDGET SLOT
               Paste the GHL review widget embed (its div and script) directly below this comment.
               When the widget is present, the placeholders and the JSON renderer hide themselves.
               If the widget is removed, assets/reviews.json (owner authorized Google Business Profile feed) is rendered instead. -->
          %(widget)s
          <div class="rv-grid rv-grid-%(ctx)s" data-rv-grid>%(ph)s</div>
          %(more)s
        </div>""" % {"ctx": context, "src": src, "strings": esc(strings), "widget": widget, "ph": ph, "more": more}


def home_reviews(C):
    """B3: after the chart section, before the form. Omitted at release when no review source exists."""
    if (RELEASE and not review_source(C)) or not page_live("reviews"):
        return ""
    r = C["reviews"]
    return """  <section class="section home-reviews" aria-labelledby="home-rv-title">
    <div class="container rv-layout">
      <h2 class="vh" id="home-rv-title">%s</h2>
      %s
      <div class="rv-main">
        %s
        <a class="tlink rv-page-link" href="reviews.html"><span>%s</span></a>
      </div>
    </div>
  </section>
""" % (esc(r["home_heading"]), review_summary(C), review_slot(C, 3, "home"), esc(r["home_link"]))


def questions_band(C, context=""):
    """A5.8 with the Summit frame (B3): a contained green band with a gold top rule and three routes."""
    q = C["questions_band"]
    if context == "reviews" or not page_live("reviews"):
        third = (q["route_explore_label"], '<a class="tlink" href="index.html#categories"><span>%s</span></a>' % esc(q["route_explore_action"]))
    else:
        third = (q["route_reviews_label"], '<a class="tlink" href="reviews.html"><span>%s</span></a>' % esc(q["route_reviews_action"]))
    routes = [
        (q["route_consult_label"], '<a class="btn btn-band" href="contact.html#consult">%s</a>' % esc(q["route_consult_action"])),
        (q["route_call_label"], '<a class="qb-tel" href="#" data-config="phone-link"><span data-config="phone">%s</span></a>'
         % esc(C["site"].get("phone", PHONE_DEFAULT))),
        third,
    ]
    return """  <section class="qband-sec" aria-labelledby="qb-title">
    <div class="container">
      <div class="qband band reveal">
        <div class="qb-text">
          <p class="kicker">%s</p>
          <h2 id="qb-title">%s</h2>
          <p class="band-lede">%s</p>
        </div>
        <ul class="qb-routes">%s</ul>
      </div>
    </div>
  </section>
""" % (esc(q["kicker"]), esc(q["heading"]), esc(q["text"]),
       "".join('<li><span class="qb-label">%s</span>%s</li>' % (esc(l), a) for l, a in routes))


def tpmo_block(C):
    """A8.4: the federally mandated third party marketing disclaimer (wording for counsel to confirm). Its numerals and hyphen
    are exempt from the copy rules, so the block is marked for the lint."""
    return ('<div class="tpmo" data-lint-exempt="tpmo"><!-- MEDICARE THIRD PARTY MARKETING DISCLAIMER: required wording, counsel '
            'to confirm. Decision pending with the client and counsel: whether to add it to the footer Disclosures sitewide. -->'
            '<p>%s</p></div>' % esc(C["site"].get("tpmo_disclaimer", "")))


def build_reviews(C, P):
    r = C["reviews"]
    body = banner(P, "banner_reviews", r["heading"], r["lede"], kicker=r["kicker"])
    body += """  <!-- %s -->
  <section class="section after-band reviews-body" aria-label="%s">
    <div class="container rv-layout rv-layout-page">
      %s
      <div class="rv-main">
        %s
      </div>
    </div>
  </section>
""" % (esc(r.get("_comment", "")), esc(r["kicker"]), review_band(C), review_slot(C, 4, "page"))
    body += questions_band(C, "reviews")
    return page(C, r["title"], r["description"], "reviews", body)


# Dates in words (A7.6): rendered copy is numeral free.
_ORD = ["", "first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth", "eleventh", "twelfth",
        "thirteenth", "fourteenth", "fifteenth", "sixteenth", "seventeenth", "eighteenth", "nineteenth", "twentieth"]
_TENS_ORD = {20: "twentieth", 30: "thirtieth"}
_TENS = {20: "twenty", 30: "thirty"}
_HOURS = ["midnight", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "noon"]
_MIN = {0: "", 15: "fifteen", 30: "thirty", 45: "forty five"}


def _ordinal(n):
    if n <= 20:
        return _ORD[n]
    t, u = n - n % 10, n % 10
    return _TENS_ORD[t] if u == 0 else "%s %s" % (_TENS[t], _ORD[u])


def _time_words(h, m):
    if (h, m) == (12, 0):
        return "noon"
    if (h, m) == (0, 0):
        return "midnight"
    base = _HOURS[h % 12 or 12] if h % 12 else "twelve"
    mins = _MIN.get(m - m % 15, "")
    when = "in the morning" if h < 12 else ("in the afternoon" if h < 17 else "in the evening")
    return ("%s %s %s" % (base, mins, when)).replace("  ", " ")


def date_words(iso_start, iso_end=""):
    """'2026-11-14T10:00' -> 'Saturday, November fourteenth, from ten in the morning until noon'."""
    import datetime
    if not iso_start:
        return ""
    try:
        s = datetime.datetime.fromisoformat(iso_start)
    except ValueError:
        return ""
    out = "%s, %s %s" % (s.strftime("%A"), s.strftime("%B"), _ordinal(s.day))
    if "T" in iso_start:
        out += ", from %s" % _time_words(s.hour, s.minute)
        if iso_end:
            try:
                e = datetime.datetime.fromisoformat(iso_end)
                out += " until %s" % _time_words(e.hour, e.minute)
            except ValueError:
                pass
    return out


def visible_posts(C):
    posts = C.get("blog", {}).get("posts", [])
    return [p for p in posts if p.get("status") == "published" or (p.get("status") == "draft" and not RELEASE)]


def has_article(post):
    return bool(post.get("body"))


def post_href(post):
    return "blog-%s.html" % post["slug"]


def post_meta(C, post):
    b = C["blog"]
    spans = '<span>%s</span><span>%s</span>' % (esc(b["categories"].get(post["category"], post["category"])),
                                                 esc(b["gbp_types"].get(post.get("gbp_type", "update"), "")))
    if post.get("status") == "draft" and not RELEASE:
        spans += '<span class="post-draft">%s</span>' % esc(b["draft_label"])
    return spans


def post_when(C, post):
    b = C["blog"]
    if post.get("gbp_type") == "event":
        ev = post.get("event") or {}
        return date_words(ev.get("starts", ""), ev.get("ends", "")) or b["event_tba"]
    if post.get("gbp_type") == "offer":
        of = post.get("offer") or {}
        d = date_words(of.get("valid_to", ""))
        return b["offer_until"].replace("{date}", d) if d else b["offer_ongoing"]
    return ""


def post_card(C, P, post, featured=False):
    b = C["blog"]
    linked = has_article(post)
    when = post_when(C, post)
    title = ('<a href="%s">%s</a>' % (post_href(post), esc(post["title"]))) if linked else esc(post["title"])
    foot = ('<span class="tlink" aria-hidden="true"><span>%s</span></span>' % esc(b["read_more"])) if linked else (
        '<p class="post-prep">%s</p>' % esc(b["in_preparation"]))
    return """<article class="card post-card%(feat)s%(static)s reveal" data-topic="%(cat)s" data-gbp-type="%(gbp)s" data-cta-type="%(cta)s" data-status="%(status)s">
        <div class="post-media">%(img)s</div>
        <div class="card-body">
          <p class="post-meta">%(meta)s</p>%(when)s
          <h3>%(title)s</h3>
          <p class="post-excerpt">%(summary)s</p>
          %(foot)s
        </div>
      </article>""" % {"feat": " post-featured" if featured else "", "static": "" if linked else " card-static",
                       "cat": esc(post["category"]), "gbp": esc(post.get("gbp_type", "")), "cta": esc(post.get("cta_type", "")),
                       "status": esc(post.get("status", "")), "img": P.img("file:" + post["image"], near_fold=featured), "meta": post_meta(C, post),
                       "when": ('\n          <p class="post-when">%s</p>' % esc(when)) if when else "", "title": title,
                       "summary": esc(post["summary"]), "foot": foot}


def build_blog(C, P):
    b = C["blog"]
    posts = visible_posts(C)
    pub = sorted([p for p in posts if p.get("status") == "published"], key=lambda p: p.get("published", ""), reverse=True)
    featured = pub[0] if pub else (posts[0] if posts else None)
    rest = [p for p in pub if p is not featured] + [p for p in posts if p.get("status") != "published" and p is not featured]
    cards = ([post_card(C, P, featured, featured=True)] if featured else []) + [post_card(C, P, p) for p in rest]
    filters = '<button type="button" aria-pressed="true" data-topic="">%s</button>' % esc(b["filter_all"])
    filters += "".join('<button type="button" aria-pressed="false" data-topic="%s">%s</button>' % (k, esc(v))
                       for k, v in b["categories"].items())
    body = banner(P, "banner_blog", b["heading"], b["lede"], kicker=b["kicker"])
    body += """  <section class="section after-band blog-index" aria-labelledby="blog-list-title">
    <div class="container">
      <h2 class="vh" id="blog-list-title">%(lh)s</h2>
      <div class="blog-filters" role="group" aria-label="%(fl)s" data-blog-filters data-announce-all="%(aa)s" data-announce-one="%(ao)s">%(filters)s</div>
      <p class="vh" role="status" aria-live="polite" data-blog-status></p>
      <div class="post-grid">%(cards)s</div>
    </div>
  </section>
""" % {"lh": esc(b["list_heading"]), "fl": esc(b["filter_label"]), "aa": esc(b["announce_all"]), "ao": esc(b["announce_one"]),
       "filters": filters, "cards": "".join(cards)}
    body += questions_band(C, "blog")
    return page(C, b["title"], b["description"], "blog", body)


def build_article(C, P, post):
    b = C["blog"]
    cat = post["category"]
    cat_label = b["categories"].get(cat, cat)
    first = re.match(r"(.+?[.!?])(\s|$)", post["summary"])
    lede = first.group(1) if first else post["summary"]
    blocks = []
    for blk in post.get("body", []):
        t = blk.get("type")
        if t == "p":
            blocks.append("<p>%s</p>" % esc(blk["text"]))
        elif t == "h2":
            blocks.append("<h2>%s</h2>" % esc(blk["text"]))
        elif t == "keypoints":
            blocks.append('<div class="keypoints"><p class="kicker">%s</p><ul>%s</ul></div>' % (
                esc(b["keypoints_kicker"]), "".join("<li>%s</li>" % esc(i) for i in blk.get("items", []))))
    form_cat = b["category_form_map"].get(cat, "General Inquiry")
    href = "contact.html?category=%s#consult" % form_cat.replace(" ", "%20")
    pubtime = ('<time datetime="%s" hidden></time>' % esc(post["published"])) if post.get("published") else ""
    ld = ""
    # Wave 4: the Article JSON-LD (with datePublished once a real date exists) is emitted by apply_seo in the page graph.
    review_note = ""
    if cat == "medicare":
        review_note = ("<!-- COMPLIANCE REVIEW REQUIRED: counsel or a Medicare compliance reviewer should approve this article "
                       "before publication. -->")
    else:
        review_note = "<!-- Counsel or a compliance reviewer should approve this article before publication. -->"
    body = banner(P, "file:" + post["image"], post["title"], lede, kicker=cat_label, kicker_href="blog.html?topic=%s" % cat)
    related = [p for p in visible_posts(C) if p is not post and p["category"] == cat]
    related += [p for p in visible_posts(C) if p is not post and p not in related]
    related = related[:3]
    body += """  <section class="section after-band article-sec" aria-label="%(title)s">
    <div class="container article-grid">
      <article class="article-body" data-gbp-type="%(gbp)s" data-gbp-summary="%(summary)s" data-cta-type="%(cta)s" data-status="%(status)s">
        %(note)s%(time)s%(ld)s
        %(blocks)s
        <p class="article-disc">%(disc)s</p>
        %(tpmo)s
      </article>
      <aside class="article-rail" aria-label="About this article">
        <p class="rail-author">%(author)s</p>
        <p class="post-meta">%(meta)s</p>
        <a class="btn btn-line" href="%(href)s">%(cta_label)s</a>
      </aside>
    </div>
  </section>
""" % {"title": esc(post["title"]), "gbp": esc(post.get("gbp_type", "")), "summary": esc(post["summary"]),
       "cta": esc(post.get("cta_type", "")), "status": esc(post.get("status", "")), "note": review_note, "time": pubtime, "ld": ld,
       "blocks": "\n        ".join(blocks), "disc": esc(b["disclaimer"]), "tpmo": tpmo_block(C) if cat == "medicare" else "",
       "author": esc(b["rail_author"]), "meta": post_meta(C, post), "href": href, "cta_label": esc(b["rail_cta"])}
    if related:
        body += """  <section class="section related" aria-labelledby="related-title">
    <div class="container">
      <div class="sec-head reveal"><h2 class="h2" id="related-title">%s</h2></div>
      <div class="post-grid post-grid-related">%s</div>
    </div>
  </section>
""" % (esc(b["related_heading"]), "".join(post_card(C, P, p) for p in related))
    body += questions_band(C, "article")
    return page(C, "%s | King Health blog" % post["title"], post["summary"], "article", body)


def recruit_form(C):
    j = C["join"]
    f = j["fields"]

    def field(name, label, typ="text", required=True, auto="", extra=""):
        return """<div class="field">
                <label for="rc_%(n)s">%(l)s <span class="req">(%(r)s)</span></label>
                <input id="rc_%(n)s" name="%(n)s" type="%(t)s"%(a)s%(req)s aria-describedby="err-rc_%(n)s"%(x)s>
                <span class="err" id="err-rc_%(n)s"></span>
              </div>""" % {"n": name, "l": esc(label), "r": "required" if required else "optional", "t": typ,
                           "a": (' autocomplete="%s"' % auto) if auto else "", "req": " required" if required else "", "x": extra}

    def select(name, label, options, placeholder):
        opts = '<option value="">%s</option>' % esc(placeholder) + "".join("<option>%s</option>" % esc(o) for o in options)
        return """<div class="field">
                <label for="rc_%(n)s">%(l)s <span class="req">(required)</span></label>
                <select id="rc_%(n)s" name="%(n)s" required aria-describedby="err-rc_%(n)s">%(o)s</select>
                <span class="err" id="err-rc_%(n)s"></span>
              </div>""" % {"n": name, "l": esc(label), "o": opts}

    checks = "".join('<label class="chip-check"><input type="checkbox" name="lines_of_interest" value="%s"><span>%s</span></label>'
                     % (esc(o), esc(o)) for o in f["lines_options"])
    return """<div class="kh-form-slot" data-ghl-embed="" data-ghl-form="recruit">
            <!-- GOHIGHLEVEL RECRUITING FORM SLOT: paste the GHL "Join the Team" form embed here. The native form below is the fallback
                 and posts to KH_CONFIG.ghlRecruitWebhookUrl (demo mode when empty). Tag contacts "recruit" in GHL. -->
            <form class="form kh-native-form" data-kh-form="recruit" novalidate>
              %(first)s
              %(last)s
              %(phone)s
              %(email)s
              %(state)s
              %(lic)s
              <fieldset class="field full chip-group">
                <legend>%(lines)s <span class="req">(optional)</span></legend>
                <div class="chip-row">%(checks)s</div>
              </fieldset>
              %(exp)s
              %(profile)s
              <div class="field full">
                <label for="rc_message">%(msg)s <span class="req">(optional)</span></label>
                <textarea id="rc_message" name="message" rows="4"></textarea>
              </div>
              <div class="hp" aria-hidden="true">
                <label for="rc_company_website">Company website</label>
                <input id="rc_company_website" name="company_website" type="text" tabindex="-1" autocomplete="off">
              </div>
              <div class="field full">
                <div class="check">
                  <input id="rc_consent_contact" name="consent_contact" type="checkbox" required aria-describedby="err-rc_consent_contact">
                  <label for="rc_consent_contact">I agree that King Health may contact me about my application by phone, email or text message. <span class="req">(required)</span></label>
                </div>
                <span class="err" id="err-rc_consent_contact"></span>
              </div>
              <div class="field full">
                <div class="check">
                  <input id="rc_consent_sms" name="consent_sms" type="checkbox">
                  <label for="rc_consent_sms">By checking this box, I agree to receive text messages from King Health about my inquiry, including follow up and appointment reminders, at the phone number provided. Message frequency varies. Message and data rates may apply. Reply STOP to opt out or HELP for help. Consent to receive text messages is not a condition of purchase. See our <a href="privacy.html">privacy policy</a>. <span class="req">(optional)</span></label>
                </div>
              </div>
              <div class="field full">
                <button class="btn btn-accent btn-submit" type="submit" data-submit>%(submit)s</button>
              </div>
              <div class="field full form-status" data-status role="status" aria-live="polite"></div>
            </form>
          </div>""" % {
        "first": field("first_name", "First name", auto="given-name"), "last": field("last_name", "Last name", auto="family-name"),
        "phone": field("phone", "Phone", "tel", auto="tel", extra=' inputmode="tel"'),
        "email": field("email", "Email", "email", auto="email", extra=' inputmode="email"'),
        "state": field("state", f["state"], auto="address-level1"),
        "lic": select("license_status", f["license_status"], f["license_options"], "Select your licensing"),
        "lines": esc(f["lines_of_interest"]), "checks": checks,
        "exp": select("experience", f["experience"], f["experience_options"], "Select your experience"),
        "profile": field("profile_url", f["profile_url"], "url", required=False, extra=' inputmode="url"'),
        "msg": esc(f["message"]), "submit": esc(f["submit"])}


def build_join(C, P):
    j = C["join"]
    body = banner(P, "banner_join", j["heading"], j["lede"], kicker=j["kicker"])
    look = "".join('<div class="look-item"><h3>%s</h3><p>%s</p></div>' % (esc(i["title"]), esc(i["text"])) for i in j["look_items"])
    provide = []
    for i in j["what_we_provide"]:
        conf = "true" if i.get("confirmed") else "false"
        note = "" if i.get("confirmed") else "<!-- CLIENT TO CONFIRM: King Health confirms this item before release (set confirmed: true in content.json). -->"
        provide.append('<article class="card card-text card-static reveal" data-confirm="%s">%s<div class="card-body"><h3>%s</h3><p>%s</p></div></article>'
                       % (conf, note, esc(i["title"]), esc(i["text"])))
    eng = (j.get("engagement_type") or "").strip()
    eng_html = esc(eng) if eng else esc(j["engagement_placeholder"])
    body += """  <section class="section after-band" aria-labelledby="look-title">
    <div class="container">
      <div class="sec-head sec-copy reveal"><div><p class="kicker">%(lk)s</p><h2 class="h2" id="look-title">%(lh)s</h2></div></div>
      <div class="look-grid reveal">%(look)s</div>
    </div>
  </section>
  <section class="section tint" aria-labelledby="provide-title">
    <div class="container">
      <div class="sec-head reveal"><div><p class="kicker">%(pk)s</p><h2 class="h2" id="provide-title">%(ph)s</h2></div></div>
      <div class="cards provide-grid">%(provide)s</div>
    </div>
  </section>
  <section class="section" aria-labelledby="lic-title">
    <div class="container join-prose reveal">
      <p class="kicker">%(lck)s</p>
      <h2 class="h2" id="lic-title">%(lch)s</h2>
      <div class="copy">%(lic)s</div>
      <p class="engagement" data-confirm="%(engc)s"><span class="engagement-k">%(engl)s</span> %(eng)s</p>
    </div>
  </section>
  <section class="section tint consult join-apply" id="apply" tabindex="-1" aria-labelledby="apply-title">
    <div class="container consult-solo">
      <div class="panel">
        <div data-form-wrap>
          <p class="kicker">%(ak)s</p>
          <h2 id="apply-title">%(ah)s</h2>
          <p class="panel-lede">%(at)s</p>
          %(form)s
        </div>
        <div class="success-panel" data-success hidden>
          <p class="kicker">Application received</p>
          <h2 tabindex="-1" data-success-title>%(sh)s</h2>
          <p class="panel-lede">%(st)s</p>
          <p class="fine demo-note" data-demo-note hidden>This site is in demonstration mode, so your application was not transmitted.</p>
          <button class="btn btn-line" type="button" data-reset>Return to the application</button>
        </div>
      </div>
      <p class="eeo">%(eeo)s</p>
    </div>
  </section>
""" % {"lk": esc(j["look_kicker"]), "lh": esc(j["look_heading"]), "look": look, "pk": esc(j["provide_kicker"]),
       "ph": esc(j["provide_heading"]), "provide": "".join(provide), "lck": esc(j["licensing_kicker"]), "lch": esc(j["licensing_heading"]),
       "lic": paras(j["licensing"]), "engc": "true" if eng else "false", "engl": esc(j["engagement_label"]), "eng": eng_html,
       "ak": esc(j["apply_kicker"]), "ah": esc(j["apply_heading"]), "at": esc(j["apply_text"]), "form": recruit_form(C),
       "sh": esc(j["success_heading"]), "st": esc(j["success_text"]), "eeo": esc(j["eeo"])}
    return page(C, j["title"], j["description"], "join", body)


def build_terms(C, P):
    t = C["terms"]
    s = C["site"]
    pending = bool(t.get("counsel_review_pending", True))
    eff = (t.get("effective_date") or "").strip() or t["effective_placeholder"]
    gov = (t.get("governing_state") or "").strip() or t["governing_placeholder"]
    subs = {
        "{license_number}": license_value(s, "license_number"), "{licensed_in}": license_value(s, "licensed_in"),
        "{privacy_link}": '<a href="privacy.html">Privacy statement</a>',
        "{accessibility_link}": '<a href="accessibility.html">Accessibility statement</a>',
        "{governing_state}": esc(gov),
        "{phone}": '<a href="#" data-config="phone-link"><span data-config="phone">%s</span></a>' % esc(s.get("phone", PHONE_DEFAULT)),
        "{email}": '<a href="#" data-config="email-link"><span data-config="email">%s</span></a>' % esc(s.get("email", EMAIL_DEFAULT)),
    }
    secs = []
    for sec in t["sections"]:
        ps = []
        for ptxt in sec["p"]:
            h = esc(ptxt)
            for k, v in subs.items():
                h = h.replace(k, v)
            ps.append("<p>%s</p>" % h)
        secs.append("<h2>%s</h2>%s%s" % (esc(sec["h"]), "".join(ps), tpmo_block(C) if sec.get("tpmo") else ""))
    head_html = ""
    if pending:
        head_html += ("<!-- COUNSEL REVIEW REQUIRED: this outline must be reviewed and approved by licensed counsel in King Health's "
                      "state of domicile before publication. -->\n      ")
    head_html += '<p class="terms-eff">%s %s</p>' % (esc(t["effective_label"]), esc(eff))
    if pending and not RELEASE:
        head_html += '<p class="fine terms-review">%s</p>' % esc(t["review_notice"])
    body = banner(P, "banner_terms", t["heading"], t["lede"], kicker=t["kicker"])
    body += """  <section class="section after-band" aria-label="%s">
    <div class="container prose terms reveal">
      %s
      %s
    </div>
  </section>
""" % (esc(t["heading"]), head_html, "\n      ".join(secs))
    return page(C, t["heading"], t["description"], "terms", body)


# --------------------------------------------------------------------------------------
# Wave 4 (SPEC_WAVE4_SEO_2026_10_25.md, section H overrides A, C and E): search engine optimization.
# Siblings copy this block verbatim. Everything is driven by the seo block in content.json; the page builders are untouched
# apart from the footer service areas line, the Contact areas list and the article (whose JSON-LD now lives here).
# Pages are post processed by filename, so each concept keeps its own markup.
# --------------------------------------------------------------------------------------
import datetime

OG_W, OG_H = 1200, 630
OG_DEFAULT = "assets/og/king-health-og.jpg"
LOGO_FILE = "brand/king-health-lockup.png"
NOT_FOUND = "404.html"


def seo_cfg(C):
    return C.get("seo") or {}


def seo_base(C):
    return (seo_cfg(C).get("base_url") or "").strip().rstrip("/")


def abs_url(C, path):
    """Absolute URL from base_url. The home page canonical is the bare root."""
    path = "" if path == "index.html" else path
    # 2026-10-25: Cloudflare Pages serves /about for about.html and redirects the .html address, so search tags use the clean form.
    page, hsh, frag = path.partition("#")
    if page.endswith(".html"):
        page = "" if page == "index.html" else page[:-5]
    path = page + hsh + frag
    return "%s/%s" % (seo_base(C), path)


def seo_theme_color():
    for slug, name, mode, scheme, t in THEMES:
        if slug == SIGNATURE:
            return t.get("brand") or t.get("header-bg") or t.get("bg")
    return ""


def tel_e164(phone):
    d = re.sub(r"\D", "", phone or "")
    if len(d) == 10:
        return "+1-%s-%s-%s" % (d[:3], d[3:6], d[6:])
    return phone or ""


def seo_areas(C):
    return [a for a in seo_cfg(C).get("service_areas", []) or [] if a]


def area_nodes(C):
    """Each service area as a schema.org place: "City, ST" entries are cities, plain names are states."""
    out = []
    for a in seo_areas(C):
        out.append({"@type": "City" if "," in a else "State", "name": a})
    return out


def service_areas_line(C):
    """E: the visible footer line. Hidden when service_areas is empty."""
    line = (seo_cfg(C).get("service_areas_line") or "").strip()
    if not seo_areas(C):
        return ""
    if not line:
        areas = seo_areas(C)
        line = "Serving families and employers across %s." % (
            areas[0] if len(areas) == 1 else ", ".join(areas[:-1]) + " and " + areas[-1])
    return '\n      <span class="ft-areas">%s</span>' % esc(line)


def service_areas_item(C):
    """E: the Contact page list under hours (inside the direct contact list)."""
    areas = seo_areas(C)
    if not areas:
        return ""
    return ('\n          <li class="directs-areas"><span class="k">%s</span><ul class="area-list">%s</ul></li>'
            % (esc(seo_cfg(C).get("service_areas_label") or "Areas"), "".join("<li>%s</li>" % esc(a) for a in areas)))


def photo_file(name):
    """Resolve a photo library key to its file in site/media/photos (blog images are keyed without extension)."""
    d = os.path.join(SITE, "media", "photos")
    for cand in (name, name + ".jpg", name + ".jpeg", name + ".png", name + ".webp"):
        if os.path.exists(os.path.join(d, cand)):
            return cand
    return None


def logo_dims(src):
    """Width and height attributes for a local image, so carrier logos never shift the layout."""
    if re.match(r"^[a-z]+:", src or ""):
        return ""
    size = image_size(os.path.join(SITE, src.split("?", 1)[0]))
    return (' width="%d" height="%d"' % tuple(size)) if size else ""


def make_og_image(C, P):
    """A: the default Open Graph image, 1200 by 630, from the home photo with the King Health lockup on an ivory card.
    Generated only when missing (delete it to regenerate). Pillow is optional; without it the build warns."""
    rel = seo_cfg(C).get("default_og_image") or OG_DEFAULT
    out = os.path.join(SITE, rel)
    if os.path.exists(out):
        return rel
    try:
        from PIL import Image, ImageDraw, ImageFilter
    except ImportError:
        warn("Pillow is not installed; the Open Graph image %s was not generated" % rel)
        return rel
    slot = seo_cfg(C).get("og_source_slot") or "hero_home"
    p = P.get(slot)
    src = os.path.join(SITE, "media", "photos", p["file"]) if p else ""
    if not src or not os.path.exists(src):
        warn("Open Graph source photo for slot %s not found" % slot)
        return rel
    im = Image.open(src).convert("RGB")
    scale = max(OG_W / im.width, OG_H / im.height)
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    pos = (p.get("position") or "50% 50%").replace("%", "").split()
    try:
        fx, fy = float(pos[0]) / 100, float(pos[1]) / 100
    except (ValueError, IndexError):
        fx, fy = .5, .5
    left, top = round((im.width - OG_W) * fx), round((im.height - OG_H) * fy)
    im = im.crop((left, top, left + OG_W, top + OG_H))
    t = dict((s, tk) for s, n, m, sc, tk in THEMES)[SIGNATURE]
    hexrgb = lambda h: tuple(int(h.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    card_bg, gold = hexrgb(t.get("bg", "#FDFCF8")), hexrgb(t.get("accent", "#CFB53B"))
    card = (OG_W - 524, 135, OG_W - 64, 495)  # right side, clear of the people in the home photo
    shadow = Image.new("L", (OG_W, OG_H), 0)
    ImageDraw.Draw(shadow).rounded_rectangle(tuple(v + 6 for v in card), 18, fill=110)
    im.paste((0, 0, 0), (0, 0), shadow.filter(ImageFilter.GaussianBlur(14)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle(card, 18, fill=card_bg)
    d.rectangle((card[0] + 60, card[3] - 46, card[2] - 60, card[3] - 43), fill=gold)
    lock = Image.open(os.path.join(BRAND_SRC, "king-health-lockup.png")).convert("RGBA")
    lw = 360
    lock = lock.resize((lw, round(lock.height * lw / lock.width)), Image.LANCZOS)
    im.paste(lock, (card[0] + (card[2] - card[0] - lw) // 2, card[1] + (card[3] - card[1] - 50 - lock.height) // 2 + 6), lock)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    im.save(out, "JPEG", quality=84, optimize=True, progressive=True)
    print("Generated Open Graph image", rel)
    return rel


def seo_page_copy(C, name):
    return (seo_cfg(C).get("pages") or {}).get(name) or {}


def find_post(C, name):
    for post in C.get("blog", {}).get("posts", []):
        if "blog-%s.html" % post.get("slug") == name:
            return post
    return None


def seo_kind(C, name):
    stem = name[:-5]
    if name == "index.html":
        return "home", None
    if name == NOT_FOUND:
        return "notfound", None
    if stem in CAT_BY_SLUG:
        return "category", CAT_BY_SLUG[stem]
    if stem in FORM_LABEL:
        return "product", stem
    if name.startswith("blog-"):
        return "article", find_post(C, name)
    return stem, None


def ld_org(C):
    s = C["site"]
    cfg = seo_cfg(C)
    same = [u for u in [(s.get("social") or {}).get(k, "") for k in ("facebook", "instagram", "whatsapp")] + [cfg.get("gbp_url", "")] if u]
    node = {"@type": "Organization", "@id": abs_url(C, "#organization"), "name": s.get("name", "King Health"),
            "legalName": s.get("legal_name") or s.get("name", "King Health"), "url": abs_url(C, "index.html"),
            "logo": {"@type": "ImageObject", "url": abs_url(C, LOGO_FILE), "width": 1000, "height": 659}}
    if same:
        node["sameAs"] = same
    if s.get("phone"):  # the contact point carries the email only when a real one is set
        node["contactPoint"] = {"@type": "ContactPoint", "telephone": tel_e164(s["phone"]), "contactType": "customer service",
                                "areaServed": area_nodes(C), "availableLanguage": "en"}
        if real_email(s):
            node["contactPoint"]["email"] = s["email"]
    return node


def real_email(s):
    e = (s.get("email") or "").strip()
    return e if e and "@" in e and not e.endswith(".example") and e != EMAIL_DEFAULT else ""


def ld_website(C):
    return {"@type": "WebSite", "@id": abs_url(C, "#website"), "url": abs_url(C, "index.html"), "name": C["site"].get("name", "King Health"),
            "inLanguage": "en-US", "publisher": {"@id": abs_url(C, "#organization")}}


def ld_agency(C, og):
    s = C["site"]
    cfg = seo_cfg(C)
    node = {"@type": cfg.get("business_type") or "InsuranceAgency", "@id": abs_url(C, "#agency"), "name": s.get("name", "King Health"),
            "legalName": s.get("legal_name") or s.get("name", "King Health"), "url": abs_url(C, "index.html"),
            "logo": abs_url(C, LOGO_FILE), "image": abs_url(C, og), "telephone": tel_e164(s.get("phone", ""))}
    if real_email(s):
        node["email"] = real_email(s)
    a = s.get("address") or {}
    if a.get("city"):
        node["address"] = {"@type": "PostalAddress", "streetAddress": a.get("street", ""), "addressLocality": a.get("city", ""),
                           "addressRegion": a.get("region", ""), "postalCode": a.get("postal_code", ""),
                           "addressCountry": a.get("country", "US")}
        node["address"] = {k: v for k, v in node["address"].items() if v}
    g = a.get("geo") or {}
    if g.get("lat") is not None and g.get("lng") is not None:
        node["geo"] = {"@type": "GeoCoordinates", "latitude": g["lat"], "longitude": g["lng"]}
    if cfg.get("gbp_url"):
        node["hasMap"] = cfg["gbp_url"]
    hours = [{"@type": "OpeningHoursSpecification", "dayOfWeek": h["days"], "opens": h["opens"], "closes": h["closes"]}
             for h in s.get("hours_structured") or [] if h.get("days") and h.get("opens") and h.get("closes")]
    if hours:
        node["openingHoursSpecification"] = hours
    if area_nodes(C):
        node["areaServed"] = area_nodes(C)
    if s.get("owner"):
        node["founder"] = {"@type": "Person", "name": s["owner"],
                           "jobTitle": cfg.get("founder_job_title") or "Independent Insurance Advisor"}
    same = ld_org(C).get("sameAs")
    if same:
        node["sameAs"] = same
    return node  # aggregateRating is never emitted from placeholders (C and H)


def ld_provider(C):
    return {"@type": seo_cfg(C).get("business_type") or "InsuranceAgency", "@id": abs_url(C, "#agency"),
            "name": C["site"].get("name", "King Health"), "url": abs_url(C, "index.html"), "telephone": tel_e164(C["site"].get("phone", ""))}


def ld_breadcrumb(C, trail):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i, "name": label, "item": abs_url(C, href)} for i, (label, href) in enumerate(trail, 1)]}


def ld_service(C, name, label, service_type, desc):
    node = {"@type": "Service", "name": label, "serviceType": service_type, "url": abs_url(C, name), "provider": ld_provider(C)}
    if desc:
        node["description"] = desc
    if area_nodes(C):
        node["areaServed"] = area_nodes(C)
    return node


def ld_faq(faq):
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": qa["q"], "acceptedAnswer": {"@type": "Answer", "text": qa["a"]}} for qa in faq]}


def ld_article(C, name, post):
    s = C["site"]
    f = photo_file(post.get("image", ""))
    node = {"@type": "Article", "headline": post["title"][:110], "description": post.get("summary", ""),
            "author": {"@type": "Person", "name": s.get("owner", ""),
                       "jobTitle": seo_cfg(C).get("founder_job_title") or "Independent Insurance Advisor"},
            "publisher": {"@type": "Organization", "@id": abs_url(C, "#organization"), "name": s.get("name", "King Health"),
                          "logo": {"@type": "ImageObject", "url": abs_url(C, LOGO_FILE)}},
            "mainEntityOfPage": {"@type": "WebPage", "@id": abs_url(C, name)}, "inLanguage": "en-US"}
    if f:
        node["image"] = [abs_url(C, "media/photos/" + f)]
    if post.get("published"):  # no datePublished while a post is a draft or undated
        node["datePublished"] = post["published"]
    return node


def json_ld(C, name, title, desc, og):
    """C: one JSON-LD script per page, as a single @graph."""
    kind, ref = seo_kind(C, name)
    graph = [ld_org(C), ld_website(C)]
    if kind in ("home", "contact"):
        graph.append(ld_agency(C, og))
    elif kind == "category":
        label = clabel(C, ref)
        graph.append(ld_breadcrumb(C, [("Home", "index.html"), (label, name)]))
        graph.append(ld_service(C, name, label, ref["label"], C["categories"][ref["slug"]].get("lede", "")))
        if C["categories"][ref["slug"]].get("faq"):
            graph.append(ld_faq(C["categories"][ref["slug"]]["faq"]))
    elif kind == "product":
        pc = C["products"][ref]
        cat = CAT_BY_KEY["senior"] if ref == "ancillary" else CAT_BY_SLUG[pc["category"]]
        graph.append(ld_breadcrumb(C, [("Home", "index.html"), (clabel(C, cat), "%s.html" % cat["slug"]), (plabel(C, ref), name)]))
        graph.append(ld_service(C, name, plabel(C, ref), FORM_LABEL[ref], pc.get("lede", "")))
        if pc.get("faq"):
            graph.append(ld_faq(pc["faq"]))
    elif kind == "article" and ref:
        graph.append(ld_article(C, name, ref))
    elif kind == "faq":
        graph.append(ld_breadcrumb(C, [("Home", "index.html"), ("FAQ", name)]))
        graph.append(ld_faq(faq_page_groups(C, flat=True)))
    elif kind == "reviews":  # C: CollectionPage only, never a rating
        graph.append({"@type": "CollectionPage", "@id": abs_url(C, name), "url": abs_url(C, name), "name": title,
                      "description": desc, "isPartOf": {"@id": abs_url(C, "#website")}, "about": {"@id": abs_url(C, "#organization")}})
    data = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))
    return '<script type="application/ld+json">%s</script>' % data.replace("</", "<\\/")


def apply_seo(C, name, doc, og):
    """B: page level tags. Replaces the builder's title and description with the seo.pages copy and adds canonical,
    robots, Open Graph, Twitter, theme color, verification and JSON-LD before </head>."""
    copy = seo_page_copy(C, name)
    m = re.search(r"<title>(.*?)</title>", doc, re.S)
    title = copy.get("seo_title") or (html.unescape(m.group(1)) if m else "King Health")
    md = re.search(r'<meta name="description" content="([^"]*)">', doc)
    desc = copy.get("seo_description") or (html.unescape(md.group(1)) if md else "")
    if not copy:
        warn("seo.pages has no seo_title and seo_description for %s; the builder's copy is used" % name)
    doc = doc.replace('<html lang="en"', '<html lang="en-US"', 1)
    m = re.search(r"<title>(.*?)</title>", doc, re.S)  # re-find after the lang edit shifted every offset
    if m:
        doc = doc[:m.start()] + "<title>%s</title>" % esc(title) + doc[m.end():]
    md = re.search(r'<meta name="description" content="([^"]*)">', doc)
    if md:
        doc = doc[:md.start()] + '<meta name="description" content="%s">' % esc(desc) + doc[md.end():]
    kind, ref = seo_kind(C, name)
    url = abs_url(C, name)
    robots = "noindex,nofollow" if not RELEASE else ("noindex,follow" if kind == "notfound" else "index,follow")
    img = abs_url(C, og)
    tags = ['<meta name="robots" content="%s">' % robots]
    if kind != "notfound":
        tags.append('<link rel="canonical" href="%s">' % esc(url))
    tc = seo_theme_color()
    if tc:
        tags.append('<meta name="theme-color" content="%s">' % tc)
    gsv = (seo_cfg(C).get("google_site_verification") or "").strip()
    if gsv:
        tags.append('<meta name="google-site-verification" content="%s">' % esc(gsv))
    og_type = "article" if kind == "article" else "website"
    tags += ['<meta property="og:type" content="%s">' % og_type,
             '<meta property="og:site_name" content="%s">' % esc(C["site"].get("name", "King Health")),
             '<meta property="og:locale" content="en_US">',
             '<meta property="og:title" content="%s">' % esc(title),
             '<meta property="og:description" content="%s">' % esc(desc),
             '<meta property="og:url" content="%s">' % esc(url),
             '<meta property="og:image" content="%s">' % esc(img),
             '<meta property="og:image:width" content="%d">' % OG_W,
             '<meta property="og:image:height" content="%d">' % OG_H,
             '<meta property="og:image:alt" content="%s">' % esc("King Health, independent insurance advisory"),
             '<meta name="twitter:card" content="summary_large_image">',
             '<meta name="twitter:title" content="%s">' % esc(title),
             '<meta name="twitter:description" content="%s">' % esc(desc),
             '<meta name="twitter:image" content="%s">' % esc(img)]
    if kind != "notfound":
        tags.append(json_ld(C, name, title, desc, og))
    return doc.replace("</head>", "\n".join(tags) + "\n</head>", 1)


def build_404(C, P):
    """D: a plain not found page in the house style, linking home and to contact. Never indexed, never in the sitemap."""
    body = banner(P, "banner_contact", "We could not find that page",
                  "The page you were looking for may have moved, or the address may be mistyped.", kicker="Page not found")
    body += """  <section class="section after-band" aria-labelledby="nf-title">
    <div class="container prose reveal">
      <h2 id="nf-title">Where would you like to go?</h2>
      <p>You can return to the home page to explore coverage, or contact us and we will help you directly.</p>
      <p><a class="btn btn-accent" href="index.html">Return to the home page</a> <a class="tlink" href="contact.html"><span>Contact King Health</span></a></p>
    </div>
  </section>
"""
    return page(C, "Page Not Found", "The page you were looking for could not be found.", "notfound", body)


def write_crawl_files(C, pages):
    """D: robots.txt in both modes; sitemap.xml at release only, listing every generated page except the not found page.
    Hidden pages are never generated, so they never reach the sitemap."""
    base = seo_base(C)
    if RELEASE:
        robots = "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % base
        today = datetime.date.today().isoformat()
        urls = "".join("  <url><loc>%s</loc><lastmod>%s</lastmod></url>\n" % (esc(abs_url(C, n)), today)
                       for n in sorted(pages, key=lambda n: (n != "index.html", n)) if n != NOT_FOUND)
        with open(os.path.join(SITE, "sitemap.xml"), "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s</urlset>\n' % urls)
    else:
        robots = "# Review build: nothing on this site may be crawled or indexed until launch.\nUser-agent: *\nDisallow: /\n"
        if os.path.exists(os.path.join(SITE, "sitemap.xml")):
            os.remove(os.path.join(SITE, "sitemap.xml"))
    with open(os.path.join(SITE, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots)


def seo_lint(C, pages):
    """F, at build time: the same checks release_check.py enforces, reported as warnings here."""
    if not seo_base(C):
        warn("seo.base_url is empty; canonicals, Open Graph and the sitemap need it")
    seen_t, seen_d = {}, {}
    for name, doc in pages.items():
        t = html.unescape((re.search(r"<title>(.*?)</title>", doc, re.S) or [None, ""])[1])
        d = html.unescape((re.search(r'<meta name="description" content="([^"]*)">', doc) or [None, ""])[1])
        if len(t) > 60:
            warn("%s title is %d characters (sixty at most)" % (name, len(t)))
        if not 120 <= len(d) <= 165:
            warn("%s description is %d characters (one hundred twenty to one hundred sixty five)" % (name, len(d)))
        if re.search(r"[\d–—-]", t + d):
            warn("%s title or description has a numeral, dash or hyphen" % name)
        seen_t.setdefault(t, []).append(name)
        seen_d.setdefault(d, []).append(name)
        h1 = len(re.findall(r"<h1\b", doc))
        if h1 != 1:
            warn("%s has %d h1 elements" % (name, h1))
    for label, seen in (("title", seen_t), ("description", seen_d)):
        for v, names in seen.items():
            if len(names) > 1:
                warn("duplicate %s on %s" % (label, ", ".join(names)))


# --------------------------------------------------------------------------------------
# Lint: rendered text rules
# --------------------------------------------------------------------------------------
ALLOWED_DIGITS = re.compile(r"\(\d{3}\) \d{3}-\d{4}|License number: \S+|" + YEAR)


def visible_text(doc):
    doc = re.sub(r"<head\b.*?</head>", " ", doc, flags=re.S)
    doc = re.sub(r"<script\b.*?</script>", " ", doc, flags=re.S)
    doc = re.sub(r"<!--.*?-->", " ", doc, flags=re.S)
    # Wave 2, A8.4: the mandated Medicare disclaimer is exempt from the numeral rule.
    doc = re.sub(r'<div class="tpmo" data-lint-exempt="tpmo">.*?</div>', " ", doc, flags=re.S)
    # Google rating figures (average, count) are the platform's data read from reviews.json, not site copy.
    doc = re.sub(r'<(\w+)\b[^>]*\bdata-lint-exempt="(?:rating|license|date)"[^>]*>.*?</\1>', " ", doc, flags=re.S)
    attrs = " ".join(m.group(2) for m in re.finditer(r'\b(alt|aria-label|title|placeholder)="([^"]*)"', doc))
    return html.unescape(re.sub(r"<[^>]+>", " ", doc) + " " + attrs)


def lint(name, doc):
    if "\u2013" in doc or "\u2014" in doc:
        warn("%s contains an en or em dash" % name)
    txt = ALLOWED_DIGITS.sub(" ", visible_text(doc))
    digits = sorted(set(re.findall(r"\S*\d\S*", txt)))
    if digits:
        warn("%s renders numerals: %s" % (name, ", ".join(digits[:8])))
    if re.search(r"elite insurance", doc, re.I):
        warn("%s mentions Elite Insurance" % name)


# --------------------------------------------------------------------------------------
def main():
    C, src_name = load_content()
    print("Content:", src_name)
    P = Photos()
    P.C = C  # hero slideshow reads home.hero_slides
    for d in ("assets", "brand"):
        os.makedirs(os.path.join(SITE, d), exist_ok=True)
    make_brand_assets()
    for folder in (BRAND_SRC, BRAND_EXTRA):
        for f in os.listdir(folder):
            if f.endswith((".png", ".ico")):
                shutil.copy2(os.path.join(folder, f), os.path.join(SITE, "brand", f))

    with open(os.path.join(SRC, "base.css"), encoding="utf-8") as f:
        base = f.read()
    # The one permitted literal is the carrier strip's mask channel (A4.3); it is not a rendered color.
    MASK = "linear-gradient(90deg, transparent 0, #000 64px, #000 calc(100% - 64px), transparent 100%)"
    if re.search(r"#[0-9A-Fa-f]{3,8}\b", re.sub(r"/\*.*?\*/", "", base, flags=re.S).replace(MASK, "")):
        warn("base.css has a hex color outside the token block")
    if os.path.exists(os.path.join(SRC, "icons.svg")):
        shutil.copy2(os.path.join(SRC, "icons.svg"), os.path.join(SITE, "assets", "icons.svg"))
    # Google review snapshot (owner's public profile); the GHL widget, when pasted, takes priority in site.js
    if os.path.exists(os.path.join(BUILD_DIR_RV, "reviews_google.json")):
        shutil.copy2(os.path.join(BUILD_DIR_RV, "reviews_google.json"), REVIEWS_JSON)
    css = theme_css() + base
    with open(os.path.join(SRC, "site.js"), encoding="utf-8") as f:
        js = f.read()
    js = (js.replace("/*__KH_COVERAGE__*/{}", json.dumps(COVERAGE_MAP))
            .replace("/*__KH_THEMES__*/{}", json.dumps({t[0]: t[1] for t in THEMES}))
            .replace("/*__KH_DARK__*/[]", json.dumps(list(DARK_THEMES)))
            .replace("/*__KH_SIGNATURE__*/''", json.dumps(SIGNATURE))
            .replace("/*__KH_PHONE__*/''", json.dumps(C["site"].get("phone", PHONE_DEFAULT)))
            .replace("/*__KH_EMAIL__*/''", json.dumps(C["site"].get("email", EMAIL_DEFAULT))))
    if not RELEASE:  # review builds only: open tabs reload themselves after every rebuild
        js += LIVE_RELOAD_JS
    with open(os.path.join(SRC, "kh-ghl-bridge.js"), encoding="utf-8") as f:
        bridge = f.read()
    for name, data in (("site.css", css), ("site.js", js), ("kh-ghl-bridge.js", bridge)):
        if "\u2013" in data or "\u2014" in data:
            warn("%s contains an en or em dash" % name)
        with open(os.path.join(SITE, "assets", name), "w", encoding="utf-8") as f:
            f.write(data)

    set_hidden_pages(C)  # Wave 3: must run before any page renders, because every link builder consults it
    global FLOAT_BADGE
    FLOAT_BADGE = google_badge(C, "float") + "\n"
    pages = {"index.html": build_home(C, P)}
    for cat in CATS:
        pages["%s.html" % cat["slug"]] = build_category(C, P, cat)
    for p in FORM_LABEL:
        pages["%s.html" % p] = build_product(C, P, p)
    pages["contact.html"] = build_contact(C, P)
    pages["privacy.html"] = build_legal_doc(C, P, "privacy")  # 2026-10-25: formal layout; build_legal kept for reference
    pages["accessibility.html"] = build_legal(C, P, "accessibility", "Accessibility")
    # Hideable pages (Wave 2 pages plus About and Carriers): a key in site.hidden_pages skips the page entirely.
    hideable = (("about", build_about), ("faq", build_faq), ("carriers", build_carriers), ("reviews", build_reviews),
                ("join-the-team", build_join), ("blog", build_blog), ("terms", lambda C, P: build_legal_doc(C, P, "terms")))  # build_terms kept for reference
    for key, builder in hideable:
        if page_live(key):
            pages[HIDEABLE_PAGES[key]] = builder(C, P)
    if page_live("blog"):
        for post in visible_posts(C):
            if has_article(post):
                pages[post_href(post)] = build_article(C, P, post)
    # Remove files an earlier build wrote that this build does not: hidden pages, and drafts in a release build.
    for f in os.listdir(SITE):
        stale = f in HIDEABLE_PAGES.values() or (f.startswith("blog-") and f.endswith(".html"))
        if stale and f not in pages:
            os.remove(os.path.join(SITE, f))
    pages[NOT_FOUND] = build_404(C, P)  # Wave 4, D
    check_links(pages)
    og = make_og_image(C, P)  # Wave 4: page level tags, JSON-LD, lint and crawl files
    for name in pages:
        pages[name] = apply_seo(C, name, pages[name], og)
    seo_lint(C, pages)
    write_crawl_files(C, pages)
    print("Mode:", "release" if RELEASE else "review (placeholders and drafts shown)")
    # 2026-10-25: version the stylesheet and scripts by content so a browser never keeps a stale copy after a rebuild.
    import hashlib
    asset_v = hashlib.md5((css + js + bridge).encode("utf-8")).hexdigest()[:10]
    for name, doc in pages.items():
        lint(name, doc)
        for a in ("assets/site.css", "assets/site.js", "assets/kh-ghl-bridge.js"):
            doc = doc.replace('"%s"' % a, '"%s?v=%s"' % (a, asset_v))
        with open(os.path.join(SITE, name), "w", encoding="utf-8") as f:
            f.write(doc)
    check_contrast()
    vc = vcard_text(C)
    if vc:
        with open(os.path.join(SITE, (C["site"].get("contact_card") or {}).get("file", "contact.vcf")), "w", encoding="utf-8", newline="") as f:
            f.write(vc)
    headers = os.path.join(SITE, "_headers")
    if RELEASE:  # Cloudflare Pages: security headers, contact card download, and no indexing of the pages.dev preview address
        # 2026-10-25: Content Security Policy. The inline theme script is allowed by its hash, computed here so the policy
        # always matches the build. GoHighLevel hosts are pre-allowed for the form webhook and any later widget or embed.
        import hashlib, base64
        inline_hashes = set()
        for _n, _doc in pages.items():
            for _m in re.finditer(r"<script>(.*?)</script>", _doc, re.S):
                inline_hashes.add("'sha256-%s'" % base64.b64encode(hashlib.sha256(_m.group(1).encode("utf-8")).digest()).decode())
        ghl = "https://*.leadconnectorhq.com https://*.msgsndr.com https://*.gohighlevel.com"
        csp = ("default-src 'self'; script-src 'self' %s %s; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
               "font-src 'self' https://fonts.gstatic.com data:; img-src 'self' data: https:; connect-src 'self' %s; "
               "frame-src 'self' %s https://www.google.com; frame-ancestors 'self'; base-uri 'self'; form-action 'self'; "
               "object-src 'none'; upgrade-insecure-requests") % (" ".join(sorted(inline_hashes)), ghl, ghl, ghl)
        hdrs = CF_HEADERS.replace("  Strict-Transport-Security: max-age=31536000\n",
                                  "  Strict-Transport-Security: max-age=31536000\n  Content-Security-Policy: %s\n" % csp, 1)
        with open(headers, "w", encoding="utf-8") as f:
            f.write(hdrs)
        # 2026-10-25: permanent redirects from the addresses the earlier GoHighLevel site used on kinghealthdirect.com,
        # so existing Google results and bookmarks land on the matching new page. /contact, /privacy and /terms already exist.
        with open(os.path.join(SITE, "_redirects"), "w", encoding="utf-8") as f:
            f.write("/home / 301\n/001 / 301\n/service / 301\n/services / 301\n")
    elif os.path.exists(headers):
        os.remove(headers)
    stamp = os.path.join(SITE, "assets", "build-stamp.txt")
    if RELEASE:
        if os.path.exists(stamp):
            os.remove(stamp)
    else:  # written last, so open review tabs reload only after every page is in place
        with open(stamp, "w", encoding="utf-8") as f:
            f.write(datetime.datetime.now().isoformat())
    print("Built %d pages into %s from %s with %d warnings." % (len(pages), SITE, src_name, len(WARNINGS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
