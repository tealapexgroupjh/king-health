#!/usr/bin/env python3
"""King Health release check (non-blocking, apart from the Wave 4 SEO lint, whose FAIL findings exit 1).

Lists every placeholder that still needs a real value before launch. It never fails the build and always exits 0,
because the client has chosen to keep the placeholder phone, email and blank license fields for now.
Run after a build:  python3 _build/release_check.py

Wave 2 (PICASSO_DIRECTION_KING_HEALTH_WAVE2_2026_10_24.md, D1) adds the release lint below. In the default mode its
findings are printed as warnings, because a review build deliberately carries labeled placeholders. Run
`python3 _build/release_check.py --strict` against a `build.py --release` output to make every D1 finding fail (exit 1).
"""
import sys
import html
import json
import os
import re

BUILD = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(os.path.dirname(BUILD), "site")

PLACEHOLDERS = [
    (r"\(555\)", "placeholder phone number (555)"),
    (r"[\w.+-]+@[\w-]+\.example\b", "placeholder email address on the .example domain"),
    (r"License number:\s*\[\s*\]", "blank license number"),
    (r"Licensed in:\s*\[\s*\]", "blank licensed states"),
]


def text_of(doc):
    doc = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", doc, flags=re.S)
    return html.unescape(re.sub(r"<[^>]+>", " ", doc))


# ---------------------------------------------------------------------------------- Wave 2 release lint (D1)
JOIN_PAGE = "join-the-team.html"
JOIN_BANNED = [r"\bearn\b", r"\bearning", r"\bincome\b", r"\bunlimited\b", r"\bsix figure", r"\bresidual\b", r"financial freedom",
               r"be your own boss", r"work from anywhere", r"top producer", r"\bcommission"]
MASK = "linear-gradient(90deg, transparent 0, #000 64px, #000 calc(100% - 64px), transparent 100%)"
ALLOWED_DIGITS = re.compile(r"\(\d{3}\) \d{3}-\d{4}|License number: \S+|© \d{4}|&copy; \d{4}")


def load_content():
    try:
        with open(os.path.join(BUILD, "content.json"), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def hidden_pages(C):
    """Wave 3: pages listed in site.hidden_pages are not generated, so their placeholders are not findings."""
    return set(C.get("site", {}).get("hidden_pages", []) or [])


def d1_findings():
    out = []
    C = load_content()
    hidden = hidden_pages(C)
    pages = sorted(f for f in os.listdir(SITE) if f.endswith(".html"))
    docs = {}
    for name in pages:
        with open(os.path.join(SITE, name), encoding="utf-8") as f:
            docs[name] = f.read()
    ph = [n for n, d in docs.items() if re.search(r"\bdata-placeholder\b", d)]
    if ph:
        out.append("data-placeholder markers remain (carrier tiles, review skeletons, social links, Google links) on: %s" % ", ".join(ph))
    rv = docs.get("reviews.html", "")
    slot = re.search(r'<div class="kh-review-slot"[^>]*>(.*?)<div class="rv-grid', rv, re.S)
    widget = slot and re.sub(r"<!--.*?-->", "", slot.group(1), flags=re.S).strip()
    try:
        with open(os.path.join(SITE, "assets", "reviews.json"), encoding="utf-8") as f:
            feed = bool(json.load(f).get("reviews"))
    except (OSError, ValueError, AttributeError):
        feed = False
    if not widget and not feed and "reviews" not in hidden:
        out.append("reviews.html has neither a GHL review widget in its slot nor a non empty assets/reviews.json")
    tm = docs.get("terms.html", "")
    for marker in ("COUNSEL REVIEW REQUIRED", "[effective date]", "[State to be specified"):
        if marker in tm and "terms" not in hidden:
            out.append("terms.html still contains %s" % marker)
    j = C.get("join", {}) if "join-the-team" not in hidden else {}
    unconf = [i.get("title", "") for i in j.get("what_we_provide", []) if i.get("confirmed") is not True]
    if unconf:
        out.append("join.what_we_provide items await client confirmation: %s" % ", ".join(unconf))
    if j and not (j.get("engagement_type") or "").strip():
        out.append("join.engagement_type is unset (independent contractor or employee)")
    jt = text_of(docs.get(JOIN_PAGE, ""))
    for pat in JOIN_BANNED:
        if re.search(pat, jt, re.I):
            out.append("%s contains banned recruiting language matching %s" % (JOIN_PAGE, pat))
    drafts = [p.get("slug") for p in (C.get("blog", {}) if "blog" not in hidden else {}).get("posts", []) if p.get("status") == "draft"
              and ('data-status="draft"' in docs.get("blog.html", "") or ("blog-%s.html" % p.get("slug")) in docs)]
    if drafts:
        out.append("draft blog posts would be published: %s" % ", ".join(drafts))
    if "blog.html" in docs and 'class="card post-card' not in docs["blog.html"]:
        out.append("blog.html has no published posts; publish at least one before release")
    for name, d in docs.items():
        body = re.sub(r"<head\b.*?</head>|<script\b.*?</script>|<!--.*?-->", " ", d, flags=re.S)
        body = re.sub(r'<div class="tpmo" data-lint-exempt="tpmo">.*?</div>', " ", body, flags=re.S)
        body = re.sub(r'<(\w+)\b[^>]*\bdata-lint-exempt="(?:rating|license)"[^>]*>.*?</\1>', " ", body, flags=re.S)  # Google rating data, license number
        body = re.sub(r'<div class="rv-grid[^"]*" data-rv-grid>.*?</div>\s*(?=<button|</div>)', " ", body, flags=re.S)
        attrs = " ".join(m.group(2) for m in re.finditer(r'\b(alt|aria-label|title|placeholder)="([^"]*)"', body))
        txt = ALLOWED_DIGITS.sub(" ", html.unescape(re.sub(r"<[^>]+>", " ", body) + " " + attrs))
        digits = sorted(set(re.findall(r"\S*\d\S*", txt)))
        if digits:
            out.append("%s renders numerals outside the allowed places: %s" % (name, ", ".join(digits[:6])))
        if "–" in d or "—" in d:
            out.append("%s contains an en or em dash" % name)
    with open(os.path.join(SITE, "assets", "site.css"), encoding="utf-8") as f:
        css = f.read()
    css = re.sub(r"/\* THEME TOKENS.*?/\* END THEME TOKENS \*/", "", css, flags=re.S)
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S).replace(MASK, "")
    if re.search(r"#[0-9A-Fa-f]{3,8}\b", css):
        out.append("site.css has a hex color outside the five theme blocks and the mask literal")
    return out


def main():
    notes = []
    pages = sorted(f for f in os.listdir(SITE) if f.endswith(".html"))
    for pattern, label in PLACEHOLDERS:
        hits = []
        for name in pages:
            with open(os.path.join(SITE, name), encoding="utf-8") as f:
                if re.search(pattern, text_of(f.read())):
                    hits.append(name)
        if hits:
            where = "every page" if len(hits) == len(pages) else ", ".join(hits)
            notes.append("%s: on %s. Supply the real value in _build/content.json (site) and rebuild." % (label, where))

    about = os.path.join(SITE, "about.html")
    with open(about if os.path.exists(about) else os.devnull, encoding="utf-8") as f:
        if 'data-placeholder="true"' in f.read():
            notes.append("About page portrait is a stock placeholder: set slots.about_portrait_placeholder in _build/photos.json "
                         "to a real portrait of Javon King and rebuild.")

    with open(os.path.join(SITE, "assets", "site.js"), encoding="utf-8") as f:
        demo = re.search(r"ghlWebhookUrl:\s*''", f.read()) is not None
    embedded = []
    for name in pages:
        with open(os.path.join(SITE, name), encoding="utf-8") as f:
            slot = re.search(r'<div class="kh-form-slot"[^>]*>(.*?)<form', f.read(), re.S)
            if slot and "<iframe" in re.sub(r"<!--.*?-->", "", slot.group(1), flags=re.S):
                embedded.append(name)
    if demo and not embedded:
        notes.append("Forms are in demo mode: set ghlWebhookUrl in _build/src/site.js or paste the GoHighLevel embed "
                     "(see GHL_FORM_SETUP.md), then rebuild.")

    try:
        with open(os.path.join(BUILD, "content.json"), encoding="utf-8") as f:
            logos = json.load(f).get("carriers", {}).get("logos")
    except (OSError, ValueError):
        logos = None
    if not logos:
        notes.append("Carriers page logo strips are empty: the client adds logos in GoHighLevel "
                     "(or list image paths under carriers.logos in content.json).")

    d1 = d1_findings()
    strict = "--strict" in sys.argv
    if notes:
        print("Release check: %d item%s still need real values before launch (warning only, not blocking):"
              % (len(notes), "" if len(notes) == 1 else "s"))
        for n in notes:
            print("  - " + n)
    else:
        print("Release check: no placeholders found.")
    if d1:
        print("Wave 2 release lint (D1): %d finding%s%s:" % (len(d1), "" if len(d1) == 1 else "s",
              " (failing, --strict)" if strict else " (expected in a review build; run build.py --release, then --strict, before launch)"))
        for n in d1:
            print("  - " + n)
    else:
        print("Wave 2 release lint (D1): clean.")
    return 1 if (strict and d1) else 0


# ---------------------------------------------------------------------------------- Wave 4 SEO release lint (section F)
# FAIL findings exit 1 in every mode, because a review build must be just as correct as a release build (titles, h1, JSON-LD,
# noindex). The mode is read from site/robots.txt (Disallow: / means review) unless --mode review or --mode release is given.
SEO_NOT_FOUND = "404.html"


def seo_mode():
    if "--mode" in sys.argv[1:-1]:
        return sys.argv[sys.argv.index("--mode") + 1]
    try:
        with open(os.path.join(SITE, "robots.txt"), encoding="utf-8") as f:
            return "review" if re.search(r"^Disallow:\s*/\s*$", f.read(), re.M) else "release"
    except OSError:
        return "unknown"


def _seo_content():
    try:
        with open(os.path.join(BUILD, "content.json"), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _seo_hidden_files(C):
    files = {"reviews": ["reviews.html"], "join-the-team": ["join-the-team.html"], "blog": ["blog.html"],
             "terms": ["terms.html"], "carriers": ["carriers.html"], "about": ["about.html"]}
    out = set()
    for key in C.get("site", {}).get("hidden_pages", []) or []:
        out.update(files.get(key, []))
    return out


def seo_findings():
    fails, warns = [], []
    C = _seo_content()
    seo = C.get("seo") or {}
    mode = seo_mode()
    base = (seo.get("base_url") or "").strip().rstrip("/")
    if not base:
        fails.append("seo.base_url is empty")
    hidden = _seo_hidden_files(C)
    hide_blog = "blog" in (C.get("site", {}).get("hidden_pages") or [])
    names = sorted(f for f in os.listdir(SITE) if f.endswith(".html"))
    titles, descs = {}, {}
    for name in names:
        with open(os.path.join(SITE, name), encoding="utf-8") as f:
            d = f.read()
        if name in hidden or (hide_blog and name.startswith("blog-")):
            fails.append("%s is generated although site.hidden_pages hides it" % name)
        m = re.search(r"<title>(.*?)</title>", d, re.S)
        t = html.unescape(m.group(1)).strip() if m else ""
        md = re.search(r'<meta name="description" content="([^"]*)">', d)
        desc = html.unescape(md.group(1)).strip() if md else ""
        if not t:
            fails.append("%s has no title" % name)
        elif len(t) > 60:
            fails.append("%s title is %d characters (over sixty): %s" % (name, len(t), t))
        if not desc:
            fails.append("%s has no meta description" % name)
        elif not 120 <= len(desc) <= 165:
            fails.append("%s description is %d characters (outside one hundred twenty to one hundred sixty five)" % (name, len(desc)))
        if re.search(r"[\d–—-]", t + " " + desc):
            fails.append("%s title or description contains a numeral, a dash or a hyphen" % name)
        titles.setdefault(t, []).append(name)
        descs.setdefault(desc, []).append(name)
        h1 = len(re.findall(r"<h1\b", re.sub(r"<!--.*?-->", " ", d, flags=re.S)))
        if h1 != 1:
            fails.append("%s has %d h1 elements (exactly one required)" % (name, h1))
        if 'lang="en-US"' not in d[:200]:
            fails.append('%s is missing html lang="en-US"' % name)
        robots = re.search(r'<meta name="robots" content="([^"]*)">', d)
        robots = robots.group(1) if robots else ""
        if mode == "review" and "noindex" not in robots:
            fails.append("%s: review build without noindex" % name)
        if mode == "release" and "noindex" in robots and name != SEO_NOT_FOUND:
            fails.append("%s: release build with noindex" % name)
        blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', d, re.S)
        if name != SEO_NOT_FOUND:
            can = re.search(r'<link rel="canonical" href="([^"]+)">', d)
            if not can or (base and not can.group(1).startswith(base + "/")):
                fails.append("%s has no absolute canonical on base_url" % name)
            if len(blocks) != 1:
                fails.append("%s has %d JSON-LD blocks (exactly one expected)" % (name, len(blocks)))
            for prop in ("og:title", "og:description", "og:url", "og:image", "og:type"):
                if 'property="%s"' % prop not in d:
                    fails.append("%s is missing %s" % (name, prop))
        for b in blocks:
            try:
                data = json.loads(b)
            except ValueError as e:
                fails.append("%s has invalid JSON-LD (%s)" % (name, e))
                continue
            flat = json.dumps(data)
            if "aggregateRating" in flat or '"ratingValue"' in flat or '"reviewCount"' in flat:
                fails.append("%s JSON-LD carries a rating or review count" % name)
            if ".example" in flat:
                fails.append("%s JSON-LD carries a placeholder email" % name)
        for img in re.findall(r"<img\b[^>]*>", re.sub(r"<!--.*?-->", " ", d, flags=re.S)):  # markup only, not GHL notes
            if not (re.search(r'\bwidth="\d+"', img) and re.search(r'\bheight="\d+"', img)):
                fails.append("%s has an image without width and height: %s" % (name, img[:90]))
            if 'fetchpriority="high"' in img and 'loading="lazy"' in img:
                fails.append("%s lazy loads its LCP image" % name)
    for label, seen in (("title", titles), ("description", descs)):
        for v, ns in seen.items():
            if v and len(ns) > 1:
                fails.append("duplicate %s on %s" % (label, ", ".join(ns)))
    try:
        with open(os.path.join(SITE, "robots.txt"), encoding="utf-8") as f:
            robots_txt = f.read()
    except OSError:
        robots_txt = ""
        fails.append("site/robots.txt is missing")
    sm_path = os.path.join(SITE, "sitemap.xml")
    if mode == "release":
        if re.search(r"^Disallow:\s*/\s*$", robots_txt, re.M) or "Sitemap:" not in robots_txt:
            fails.append("release robots.txt must allow crawling and point to the sitemap")
        if not os.path.exists(sm_path):
            fails.append("release build has no sitemap.xml")
    if os.path.exists(sm_path):
        with open(sm_path, encoding="utf-8") as f:
            locs = re.findall(r"<loc>([^<]+)</loc>", f.read())
        listed = set()
        for loc in locs:
            rel = loc[len(base) + 1:] if base and loc.startswith(base + "/") else None
            rel = "index.html" if rel == "" else rel
            if rel is None or rel not in names:
                fails.append("sitemap lists a missing page: %s" % loc)
            elif rel in hidden or (hide_blog and rel.startswith("blog-")) or rel == SEO_NOT_FOUND:
                fails.append("sitemap lists a hidden or not found page: %s" % loc)
            listed.add(rel)
        missing = [n for n in names if n not in listed and n != SEO_NOT_FOUND]
        if missing:
            fails.append("sitemap omits generated pages: %s" % ", ".join(missing))
        if mode == "review":
            warns.append("a review build should not carry sitemap.xml")
    if not (seo.get("gbp_url") or "").strip():
        warns.append("seo.gbp_url is empty")
    if not (seo.get("google_site_verification") or "").strip():
        warns.append("seo.google_site_verification is empty (paste the Search Console HTML tag token)")
    unconf = [a for a in seo.get("service_areas", []) or [] if a not in (seo.get("service_areas_confirmed") or [])]
    if unconf:
        warns.append("service areas not yet confirmed against licensed states: %s" % ", ".join(unconf))
    return mode, fails, warns


def wave4_main():
    mode, fails, warns = seo_findings()
    if fails:
        print("Wave 4 SEO lint (%s build): %d failure%s:" % (mode, len(fails), "" if len(fails) == 1 else "s"))
        for n in fails:
            print("  FAIL " + n)
    else:
        print("Wave 4 SEO lint (%s build): passed." % mode)
    for n in warns:
        print("  WARN " + n)
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(max(main() or 0, wave4_main()))
