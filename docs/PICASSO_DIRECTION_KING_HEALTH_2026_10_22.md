---
title: King Health Version 2, Picasso art direction (frozen)
created: 2026-10-22
owner: Teal Apex Solutions LLC (client build)
type: design-spec
mode: Picasso Mode 1, DIRECT
status: frozen
supersedes: the theme block and accent rules in SPEC_KING_HEALTH_V2_SUMMIT.md (that file still governs sitemap, form, content, architecture)
related: [SPEC_KING_HEALTH_V2_SUMMIT.md, PICASSO_CRITIQUE_V3_V4_2026_10_21.md]
---

# King Health V2: frozen art direction

The builder makes no aesthetic decision. Where this file names a value, use it. Where it is silent, keep Summit as built.
Type stays Manrope (display, headings) and Inter (body, UI). The serif exists only inside the logo images.

## 1. The one persuasive fact

One independent advisor, Javon King, compares carriers for every stage of life, from Medicare to a growing family
to a company's benefits to retirement income, so a household or an employer deals with one trusted person who works
for them rather than for a carrier.

Everything visual serves "one trusted advisor, official and calm": hunter green carries the authority, old gold
marks the craftsmanship, and nothing shouts.

**Style family:** Institutional Editorial (carrier calm, photo led) with a heritage accent. It costs us flash: there is
no spectacle here, so the photography grade and the gold discipline must be perfect, because they are the whole premium signal.

**The moment:** the hunter green title band rising over the family photograph, crowned with an old gold rule, repeated at
smaller scale on every interior banner, plus the one animated coverage chart on Home whose highlight is drawn in gold.
A visitor describes it as "the green and gold one with the band over the photo".

**Subtraction (what is removed against Summit):** the giant "Independent." word, the guides band on Home, the "We also
place" fragment, the theme name inside the header chip (swatch plus the word Theme only), Summit's green on every chart
series, and the square timeline nodes. If the builder adds anything not in the spec, it comes out.

## 2. The accent ruling (read before the tokens)

The client asked for gold "throughout the page so it can look premium". That fights the house accent gate (the accent marks
actions only). Resolution, frozen:

- **Actions are hunter green** (`--button-bg`) in light themes and the solid button token in dark themes. The action
  color appears on buttons, the subnav Contact Us button and nothing decorative. That is how the accent gate passes.
- **Gold is ornament and state, never action.** Gold appears only in the ten placements listed in section 4. Gold never
  fills a button, never colors a text link, never colors body text, and never fills a chart's primary series.
- **Gold budget:** on any 1440 by 900 viewport, gold covers less than two percent of the pixels. If a screen looks
  "gold", a placement was added that is not in section 4; remove it.

## 3. Theme tokens (five themes, all hunter green and old gold)

Token file only. A hex outside the token block is a defect. `data-theme` values: `ivory` (default), `onyx`, `forest`,
`linen`, `fairway`. localStorage key `kh-theme`.

Token meanings: `--accent` is decorative gold (rules, hairlines, borders; never text). `--accent-strong` is the gold that
may carry text (kickers, small labels) and the focus ring; every value below passes 4.5:1 on that theme's `--bg`,
`--surface` and `--surface-2`. `--link` is text link color. `--band-*` drive the hero and banner band. `--band-kicker` is
gold text inside the band. `--chart-accent` is the gold chart highlight (graphics, 3:1 minimum). `--field-line` is the
input border (3:1 minimum against the field surface). `--scrim` is the photo gradient base.

### Ivory Crown (signature, light; predominantly white)

```css
[data-theme="ivory"], :root {
  color-scheme: light;
  --bg:#FDFCF8; --surface:#FFFFFF; --surface-2:#F2F4EE;
  --ink:#14231A; --ink-soft:#4A5A4F; --line:rgba(20,35,26,.12);
  --brand:#355E3B; --brand-ink:#FFFFFF; --link:#355E3B;
  --accent:#CFB53B; --accent-strong:#7F6418; --focus:#7F6418;
  --button-bg:#355E3B; --button-hover:#1E3A26; --button-ink:#FFFFFF;
  --header-bg:#FFFFFF; --header-ink:#14231A;
  --subnav-bg:#F2F4EE;
  --band-bg:#355E3B; --band-ink:#FFFFFF; --band-soft:#DCE6D8; --band-kicker:#EAD889;
  --band-btn-bg:#FFFFFF; --band-btn-ink:#1E3A26;
  --footer-bg:#142A1B; --footer-ink:#F1EEE2; --footer-soft:#B9C4B6; --footer-kicker:#CFB53B;
  --chart-accent:#9C7C1A; --field-line:#808C84;
  --scrim:rgba(20,42,27,.58); --scrim-soft:rgba(20,42,27,.18);
  --shadow:rgba(20,42,27,.10); --err:#B3261E;
}
```

### Onyx Crown (dark; near black page, hunter green panels, gold accents)

```css
[data-theme="onyx"] {
  color-scheme: dark;
  --bg:#0D100E; --surface:#151A17; --surface-2:#1C2420;
  --ink:#F2EFE6; --ink-soft:#B9BCB1; --line:rgba(242,239,230,.14);
  --brand:#355E3B; --brand-ink:#F7F3E6; --link:#F2EFE6;
  --accent:#C2A740; --accent-strong:#D6BE5E; --focus:#D6BE5E;
  --button-bg:#3F6E46; --button-hover:#4A7D52; --button-ink:#FFFFFF;
  --header-bg:#0D100E; --header-ink:#F2EFE6;
  --subnav-bg:#151A17;
  --band-bg:#1E3A26; --band-ink:#F7F3E6; --band-soft:#C9D3C4; --band-kicker:#DCC567;
  --band-btn-bg:#F2EFE6; --band-btn-ink:#142A1B;
  --footer-bg:#080A09; --footer-ink:#F2EFE6; --footer-soft:#A9AEA4; --footer-kicker:#D6BE5E;
  --chart-accent:#C2A740; --field-line:#777B73;
  --scrim:rgba(8,10,9,.70); --scrim-soft:rgba(8,10,9,.32);
  --shadow:rgba(0,0,0,.5); --err:#F2B8B5;
}
```

### Forest Hall (deep green dominant; ivory text, gold accents)

```css
[data-theme="forest"] {
  color-scheme: dark;
  --bg:#1E3A26; --surface:#24452E; --surface-2:#173020;
  --ink:#F5F1E4; --ink-soft:#CBD4C5; --line:rgba(245,241,228,.16);
  --brand:#2C5234; --brand-ink:#F5F1E4; --link:#F5F1E4;
  --accent:#CFB53B; --accent-strong:#DCC567; --focus:#DCC567;
  --button-bg:#F5F1E4; --button-hover:#FFFFFF; --button-ink:#1E3A26;
  --header-bg:#173020; --header-ink:#F5F1E4;
  --subnav-bg:#24452E;
  --band-bg:#142A1B; --band-ink:#F5F1E4; --band-soft:#C9D3C4; --band-kicker:#DCC567;
  --band-btn-bg:#F5F1E4; --band-btn-ink:#142A1B;
  --footer-bg:#122618; --footer-ink:#F5F1E4; --footer-soft:#B8C5B4; --footer-kicker:#DCC567;
  --chart-accent:#CFB53B; --field-line:#889B89;
  --scrim:rgba(18,38,24,.66); --scrim-soft:rgba(18,38,24,.28);
  --shadow:rgba(0,0,0,.4); --err:#F2B8B5;
}
```

### Linen Estate (warm light; linen surfaces, deep hunter, antique gold)

```css
[data-theme="linen"] {
  color-scheme: light;
  --bg:#F7F2E8; --surface:#FFFCF6; --surface-2:#EEE6D6;
  --ink:#1D2A20; --ink-soft:#55594C; --line:rgba(29,42,32,.13);
  --brand:#1E3A26; --brand-ink:#FBF7EE; --link:#1E3A26;
  --accent:#B08D3C; --accent-strong:#7A5D1C; --focus:#7A5D1C;
  --button-bg:#1E3A26; --button-hover:#142A1B; --button-ink:#FBF7EE;
  --header-bg:#FFFCF6; --header-ink:#1D2A20;
  --subnav-bg:#EEE6D6;
  --band-bg:#1E3A26; --band-ink:#FBF7EE; --band-soft:#D6DCCB; --band-kicker:#E8D27A;
  --band-btn-bg:#FBF7EE; --band-btn-ink:#1E3A26;
  --footer-bg:#1E3A26; --footer-ink:#F3EDE0; --footer-soft:#C3C9B8; --footer-kicker:#E8D27A;
  --chart-accent:#9C7C1A; --field-line:#888A7F;
  --scrim:rgba(30,58,38,.56); --scrim-soft:rgba(30,58,38,.16);
  --shadow:rgba(42,33,25,.10); --err:#A8321F;
}
```

### Fairway (fresh light; white with pale green surfaces, bright old gold)

```css
[data-theme="fairway"] {
  color-scheme: light;
  --bg:#FCFDFB; --surface:#FFFFFF; --surface-2:#EAF2E7;
  --ink:#13241A; --ink-soft:#44584A; --line:rgba(19,36,26,.12);
  --brand:#355E3B; --brand-ink:#FFFFFF; --link:#355E3B;
  --accent:#D9B935; --accent-strong:#7D6516; --focus:#7D6516;
  --button-bg:#355E3B; --button-hover:#2A4D30; --button-ink:#FFFFFF;
  --header-bg:#FFFFFF; --header-ink:#13241A;
  --subnav-bg:#EAF2E7;
  --band-bg:#355E3B; --band-ink:#FFFFFF; --band-soft:#DCE8D8; --band-kicker:#EAD889;
  --band-btn-bg:#FFFFFF; --band-btn-ink:#1E3A26;
  --footer-bg:#355E3B; --footer-ink:#FFFFFF; --footer-soft:#DCE8D8; --footer-kicker:#EAD889;
  --chart-accent:#9C7C1A; --field-line:#7C8A80;
  --scrim:rgba(30,58,38,.52); --scrim-soft:rgba(30,58,38,.14);
  --shadow:rgba(30,58,38,.10); --err:#B3261E;
}
```

### Drawer swatch per theme (split swatch, left half / right half)
Ivory `#FFFFFF / #355E3B`, Onyx `#0D100E / #C2A740`, Forest `#1E3A26 / #CFB53B`, Linen `#F7F2E8 / #1E3A26`,
Fairway `#EAF2E7 / #D9B935`. Each preview tile gets a 2px top border in that theme's `--accent`.

### Contrast verification (WCAG relative luminance, computed)

| Pairing | Ivory | Onyx | Forest | Linen | Fairway |
| --- | --- | --- | --- | --- | --- |
| ink on bg | 15.92 | 16.64 | 11.01 | 13.40 | 15.89 |
| ink on surface | 16.34 | 15.32 | 9.45 | 14.60 | 16.22 |
| ink on surface-2 | 14.75 | 13.81 | 12.56 | 12.05 | 14.17 |
| ink-soft on bg | 7.14 | 9.92 | 8.15 | 6.45 | 7.51 |
| ink-soft on surface | 7.33 | 9.14 | 7.00 | 7.02 | 7.66 |
| ink-soft on surface-2 | 6.61 | 8.23 | 9.30 | 5.80 | 6.70 |
| link on bg | 7.27 | 16.64 | 11.01 | 11.15 | 7.31 |
| link on surface | 7.46 | 15.32 | 9.45 | 12.15 | 7.46 |
| brand-ink on brand | 7.46 | 6.72 | 7.86 | 11.63 | 7.46 |
| accent-strong on bg | 5.47 | 10.37 | 7.24 | 5.52 | 5.50 |
| accent-strong on surface | 5.62 | 9.55 | 6.22 | 6.01 | 5.61 |
| accent-strong on surface-2 | 5.07 | 8.61 | 8.26 | 4.96 | 4.90 |
| button-ink on button-bg | 7.46 | 5.95 | 11.01 | 11.63 | 7.46 |
| button-ink on button-hover | 12.44 | 4.83 | 12.44 | 14.27 | 9.53 |
| header-ink on header-bg | 16.34 | 16.64 | 12.56 | 14.60 | 16.22 |
| band-ink on band-bg | 7.46 | 11.20 | 13.50 | 11.63 | 7.46 |
| band-soft on band-bg | 5.81 | 8.05 | 9.88 | 8.86 | 5.89 |
| band-kicker on band-bg | 5.21 | 7.24 | 8.88 | 8.25 | 5.21 |
| band-btn-ink on band-btn-bg | 12.44 | 13.27 | 13.50 | 11.63 | 12.44 |
| footer-ink on footer-bg | 13.12 | 17.27 | 14.12 | 10.66 | 7.46 |
| footer-soft on footer-bg | 8.45 | 8.77 | 8.88 | 7.32 | 5.89 |
| footer-kicker on footer-bg | 7.50 | 10.77 | 9.29 | 8.25 | 5.21 |
| chart-accent on surface (3:1 graphic) | 3.95 | 7.46 | 5.25 | 3.86 | 3.95 |
| field-line on surface (3:1 boundary) | 3.50 | 4.08 | 3.61 | 3.42 | 3.62 |

Every text pairing passes 4.5:1. Raw old gold on white is 2.03:1 (`#CFB53B`) and antique gold is 3.12:1 (`#B08D3C`); that is
why `--accent` is never text in a light theme and `--accent-strong` exists. Onyx button boundary against `--surface` is
2.96:1; the button is identified by its 5.95:1 label, which satisfies WCAG, so leave it.

### Migration from Summit token names (the builder's fix pass)
- `.btn-accent` reads `--button-bg`, `--button-hover`, `--button-ink`. Delete `--accent-hover` and `--accent-ink`.
- `:focus-visible { outline: 2px solid var(--focus); outline-offset: 3px; }`. Inside `.band` and the footer keep `currentColor`.
- `--highlight` is deleted; every Summit use of `--highlight` reads `--accent`.
- `--band-rule` is deleted; the band top rule reads `--accent`.
- Text links (`.tlink`, inline `a`) read `--link`. `.mp-link[aria-current]` reads `--ink` with weight 700 and the gold left rule below.
- `h1, h2, h3` stay `--ink` (outside bands). Never `--brand` for headings in dark themes.

## 4. Where the gold goes (the only ten placements)

1. **Header top rule.** `.site-header { border-top: 2px solid var(--accent); }`. Bottom edge on scroll stays `1px solid var(--line)`.
2. **Section kickers.** One kicker per section maximum, above the h2. Inter 12px, weight 600, `letter-spacing: .14em`,
   uppercase, color `var(--accent-strong)`. Preceded by a gold tick:
   `.kicker::before { content:""; display:inline-block; width:28px; height:1px; background:var(--accent); vertical-align:middle; margin-right:12px; }`.
   Inside a band the kicker text reads `--band-kicker`; in the footer `--footer-kicker`.
3. **Active nav underline.** Hover underline: `2px`, `var(--accent)`, `left:14px; right:14px; bottom:6px`, scaleX from left,
   `.25s ease`. Current page: same bar in `var(--accent-strong)` plus `font-weight:600` so state never relies on color alone.
   Open dropdown panel: `border-top: 2px solid var(--accent)`.
4. **Hero and banner band top rule.** Home band `border-top: 3px solid var(--accent)`; banner band `2px`. Plus a gold
   hairline inset inside the Home band only: `.hero-band::after { content:""; position:absolute; left:52px; right:52px; top:14px; height:1px; background:var(--accent); opacity:.35; }`
   (left and right match the band padding; at phone widths use the band's horizontal padding).
5. **Card top borders.** Category and product cards: `border-top: 2px solid var(--accent)`, other sides `1px solid var(--line)`.
   On hover the top border grows to `3px` with `margin-top:-1px` so the card does not shift.
6. **Hairline section dividers.** Between the "Why King Health" commitments and between FAQ rows:
   `border-top: 1px solid color-mix(in srgb, var(--accent) 45%, transparent);`. All other dividers stay `var(--line)`.
7. **Form focus.** `.field input:focus, select:focus, textarea:focus { outline: 2px solid var(--focus); outline-offset: 1px; border-color: var(--focus); }`.
   The form panel itself carries `border-top: 3px solid var(--accent)`.
8. **Chart highlight.** One gold element per chart, never the primary series: term chart, the "Your term coverage" outline
   stroke at `2px var(--chart-accent)`; IUL chart, the cap line at `2px var(--chart-accent)` dashed `6 4`; annuity ring, the
   guaranteed segment's outer `3px` stroke. Primary series `var(--brand)` in light themes and `var(--ink)` in Onyx and Forest;
   secondary series `color-mix(in srgb, var(--ink-soft) 45%, transparent)`. The legend swatch for the gold element uses the same token.
9. **Footer divider.** `.ft-top { border-bottom: 1px solid color-mix(in srgb, var(--accent) 40%, transparent); }`.
   Footer column headings stay `--footer-ink`; the footer carries one kicker at most, over the brand blurb.
10. **Numeral free devices.** The gold tick (placement 2) and, on the About mission statement only, a centered rule above and
    below the statement: `width:64px; height:1px; background:var(--accent); margin:0 auto 28px;`. No numbers, no step
    markers, no ornaments, no crests, no icons. The subnav current item uses a `2px var(--accent-strong)` underline (section 5).

Nothing else is gold. Not the theme button, not text links, not body copy, not icons, not bullets, not backgrounds.

## 5. Logo usage

Assets (already in `brand/` and `_build/brand_extra/`): `king-health-lockup.png` (tree plus name plus tagline),
`king-health-wordmark.png` (tree plus name, no tagline; 945 by 557), `king-health-emblem.png` (round), `favicon-256.png`.

**Dark variants (generate once in `_build/build.py`, write to `brand/`).** The lockup tree is `#0A4B0B`; on Onyx it measures
1.84:1 and on the Forest header 1.37:1, so it disappears. Recolor only the green pixels toward sage and leave the gold lettering untouched:

```python
from PIL import Image
def reverse(src, dst, target=(0x9C,0xC2,0x8E), k=0.70):
    im = Image.open(src).convert("RGBA"); px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r,g,b,a = px[x,y]
            if a and g > r + 12 and g >= b:
                px[x,y] = (round((1-k)*r+k*target[0]), round((1-k)*g+k*target[1]), round((1-k)*b+k*target[2]), a)
    im.save(dst)
reverse("brand/king-health-wordmark.png", "brand/king-health-wordmark-reverse.png")
reverse("brand/king-health-lockup.png",   "brand/king-health-lockup-reverse.png")
```

Result: the tree becomes `#709E67` (6.17:1 on Onyx, 4.58:1 on the Forest header). Verified visually; it reads as the same
mark lit from the front. No plate, no sticker, no glow behind the logo.

**Header.** Use the wordmark (the tagline is illegible at header scale). Header height `76px` desktop, `64px` under 960px.
Logo `height:56px; width:auto` desktop, `44px` under 960px, vertically centered, `margin-right:32px` before the nav.
Light themes (Ivory, Linen, Fairway) use `king-health-wordmark.png`; dark themes (Onyx, Forest) use
`king-health-wordmark-reverse.png`. Swap via two `<img>` elements inside the home link, toggled by
`[data-theme="onyx"] .logo-light, [data-theme="forest"] .logo-light { display:none }` and the inverse. Alt text
"King Health, home" on the visible one; the hidden one gets `alt=""`. The lockup gold measures 3.05:1 on white, which is
acceptable for a logo and is not to be recolored.

**Footer.** Emblem on every theme (all footers are dark green or near black, where the emblem was designed to live).
`width:104px` desktop, `88px` under 760px, top aligned beside the footer blurb, `margin-bottom:20px` when stacked. No border, no
background, no shadow.

**Hero.** No logo in the hero. The band carries the headline; the brand is already in the header.

**Favicon.** The full emblem is illegible at 32px. Crop the disc only: `king-health-emblem.png` box `(84, 84, 588, 588)`,
circular mask, transparent outside the circle; export `favicon-32.png`, `favicon-180.png` (apple touch, composited on
`#142A1B`), and `favicon.ico` (16 and 32). Verified on light and dark tabs at 32px.

## 6. Components

### Home hero (compact, Summit's overlapping band)
- `.hero { height: clamp(380px, 48vh, 500px); }` Photo full bleed, the existing slow drift kept (it is the background
  motion the house likes), disabled under `prefers-reduced-motion`.
- Scrim, every theme: `linear-gradient(90deg, var(--scrim) 0%, var(--scrim-soft) 45%, transparent 70%), linear-gradient(0deg, var(--scrim-soft), transparent 40%)`.
- Band: `background: var(--band-bg)`, `border-top: 3px solid var(--accent)`, the inset hairline (section 4, placement 4),
  `left: clamp(20px,4vw,48px); bottom:-56px; width:min(620px,54%); padding:48px 52px 40px`.
- Inside the band, in order: kicker "Independent insurance advisory" (`--band-kicker`), h1 Manrope 700
  `clamp(30px,2.9vw,42px)`, `letter-spacing:-0.03em`, `line-height:1.1`, color `--band-ink`; lede `--band-soft` 17px, `max-width:46ch`;
  actions: `.btn-band` "Request a consultation" and a `.tlink` in `--band-ink`.
- Phone (under 760px): photo `height:160px`, band in flow with `margin:-32px calc(-1 * gutter) 0` so it runs edge to edge
  (critique Summit item 2), h1 28px, `.tlink` hidden, button full width. Header plus hero ends at or before 620px at 390 by 844.

### Category and product banners
- `.banner { height: clamp(220px, 30vh, 300px); }` Photo static (no drift). Same scrim.
- Band `width:min(640px,58%); padding:32px 44px 30px; bottom:-44px; border-top:2px solid var(--accent)`; no inset hairline.
- Category banner: kicker "Coverage category"; h1 `clamp(28px,2.5vw,38px)`; one sentence `--band-soft` 16px.
- Product banner: kicker is the parent category name (Senior Benefits, Individual Benefits, Group Benefits, Retirement),
  linked, in `--band-kicker` with underline on hover; h1 is the product.
- The section after a banner starts with `padding-top: calc(44px + clamp(48px,6vw,80px))` so the overlap never collides.

### Second nav bar (category and product pages)
- Sticky directly under the header (`top: 76px`, `64px` under 960px). `background: var(--subnav-bg)`;
  `border-bottom: 1px solid var(--line)`; no gold rule on its top edge (the header already owns it).
- Inner: `min-height:56px; display:flex; flex-wrap:wrap; align-items:center; gap:0 4px;` Category name first as a label in
  Manrope 700 14px `--ink`, then a `1px` by `20px` divider in `var(--line)`, then the pages.
- Items: Inter 15px weight 500, `--ink-soft`, `min-height:44px; padding:0 14px`. Hover `--ink`. Current page `--ink`, weight 600,
  underline `2px var(--accent-strong)` inset `14px` each side at `bottom:8px`, `aria-current="page"`.
- Right end: "Contact Us" as `.btn` in `--button-bg`, `min-height:44px; padding:0 18px; font-size:14px; margin-left:auto`.
- Under 760px the row wraps under itself (never scrolls); the button drops to its own line, full width, `margin:8px 0 12px`.

### Header and dropdowns
- `background: var(--header-bg)`, gold top rule (placement 1). Nav items Inter 15px weight 500 `--header-ink`.
- Dropdown panel: `background: var(--surface)`, `border:1px solid var(--line)`, `border-top:2px solid var(--accent)`,
  `box-shadow: 0 18px 40px -20px var(--shadow)`, `min-width:260px`, items `min-height:44px`, hover row `background: var(--surface-2)`.
- Theme control during client review: split swatch plus the word "Theme". Production removes it from the header (X6).

### Cards
- Category cards (Home, four up at 1440, two up at 760 to 1100, one up below):
  `background: var(--surface); border:1px solid var(--line); border-top:2px solid var(--accent); border-radius:2px;`
  Photo `aspect-ratio: 16/10; object-fit: cover`, graded per the library. Body `padding:24px 24px 28px`. Title Manrope 700 22px
  `--ink`; one sentence `--ink-soft` 16px, `max-width:40ch`; `.tlink` in `--link`.
- Hover: `transform: translateY(-3px)`, `box-shadow: 0 18px 36px -22px var(--shadow)`, top border to 3px, photo
  `scale(1.03)` over `.4s cubic-bezier(.2,.7,.2,1)`. Whole card clickable via the title link's `::after` overlay. Reduced
  motion: no transform, shadow only.
- Product cards on category pages: same shell without the photo, `padding:28px`, title 20px.

### Form panel (identical on every page)
- `.panel { background: var(--surface); border:1px solid var(--line); border-top:3px solid var(--accent); padding: clamp(24px,4vw,48px); border-radius:2px; }`
- Kicker "Request a consultation" over the h2. Fields `min-height:48px`, `background: var(--surface)`,
  `border:1px solid var(--field-line)`, `border-radius:2px`, labels Inter 14px weight 600 `--ink`. Focus per placement 7.
- Submit is the full width `.btn-accent` reading `--button-bg`. Consent text 14px `--ink-soft`, `max-width:70ch`.
- Section behind the form: `background: var(--surface-2)` so the white panel lifts.
- Success state: replace the fields with a heading and one paragraph; the gold top border stays.

### "Why King Health" band and about strip
- Commitments in a row of three on desktop, separated by the gold tinted hairline (placement 6) as vertical rules
  (`border-left`) and as horizontal rules when stacked. No numbers, no icons; Manrope 700 20px title, `--ink-soft` body.
- About strip: `background: var(--surface-2)`, photo left, text right, `.tlink` to About.

### Footer
- `background: var(--footer-bg); color: var(--footer-ink)`. Columns as Summit, emblem in the brand column (section 5).
- Divider per placement 9. Links `--footer-soft`, hover `--footer-ink` with underline. Legal and disclosure `max-width:80ch`, 13px.
- Accessibility and Privacy links in the bottom row. Focus rings `currentColor`.

### Motion
- Kept: hero photo drift (Home only), band rise `.9s cubic-bezier(.2,.7,.2,1)`, chart draws once on entering view
  (bars stagger `60ms`, total under `1.2s`), nav underline `.25s ease`, card hover `.4s`.
- Section content may fade up `16px` over `.6s`; never the band, never a button, never the form.
- `prefers-reduced-motion: reduce`: drift, rise, stagger and transforms off; charts render in their final state. Nothing loops except the drift.

## 7. Three things this site will deliberately not do

1. **No metallic gold.** No gold gradients, foil textures, glows, shimmer, or gold drop shadows. Old gold is a flat color
   used as a line, never a surface; a gold fill reads as a casino, not an advisory.
2. **Gold never marks an action or carries reading text.** No gold buttons, no gold links, no gold paragraphs, no gold
   primary chart series. Green acts; gold frames.
3. **No ornament beyond rules.** No icons, no pictograms, no emoji, no crests drawn in CSS, no numerals or step markers
   used as decoration, no serif type outside the logo image, and no hero taller than the clamp above.

## Gates (for the builder's self check before handing back)
Squint: the band is the first read on every page. Grayscale: band holds as the darkest mass in light themes and the
lightest button holds in dark themes. Accent: green on actions only, gold only in the ten placements. Measure: body
capped at 65ch, ledes 46ch, legal 80ch. Moment: band plus gold rule plus the gold chart highlight. Subtraction: the list in section 1.

## Change log
| Version | Date | Change | Owner |
| --- | --- | --- | --- |
| 1.0.0 | 2026-10-22 | Frozen art direction for King Health V2 (five themes, gold placements, logo variants, components) | Picasso |
