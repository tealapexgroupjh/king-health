---
title: King Health Version 2, Wave 2 additive features, Picasso art direction (frozen)
created: 2026-10-24
owner: Teal Apex Solutions LLC (client build)
type: design-spec
mode: Picasso Mode 1, DIRECT
status: frozen
applies_to: summit/_build (output summit/site) and charter/_build (output charter/site)
inherits: SPEC_KING_HEALTH_V2_SUMMIT.md, PICASSO_DIRECTION_KING_HEALTH_2026_10_22.md, PICASSO_CRITIQUE_KING_HEALTH_2026_10_22.md, PICASSO_DIRECTION_KING_HEALTH_CHARTER_2026_10_22.md
amends: the "no pictograms" rule (coverage icons only), the "no testimonials" rule (live Google reviews only), and the gold placement list (adds rating stars)
---

# King Health Wave 2: frozen art direction

The builder makes no aesthetic decision. Where this file names a value, use it. Where it is silent, the earlier frozen
files govern. Everything in this wave is additive: no existing page, section, link, component or line of copy is removed,
reordered or restyled except where this file says so in writing. The main navigation (order, labels, dropdowns, Contact
Us button), the mobile menu panel, the second nav bar rules and the five theme token blocks stay exactly as built.

Part A is shared by both sites. Part B is Summit only. Part C is Charter only. Part D is the release lint and the gates.

---

# PART A: SHARED

## A0. The fact, and what this wave is for

**Fact (unchanged):** one independent advisor, Javon King, compares carriers for every stage of life, so a household or an
employer deals with one trusted person who works for them rather than for a carrier.

This wave adds proof to that fact, and only proof. The carrier strip proves the "compares carriers" half; the reviews prove
the "trusted person" half; Join the Team and the blog prove the practice is established and growing. Nothing here is
decoration. If an addition cannot be traced to one of those three proofs, it does not ship.

**What we take from the DCruz reference, and what we refuse.** We take the ideas: icons on coverage tiles, a carrier logo
strip, a Google rating summary beside reviews, a closing questions band, social links in the footer. We refuse the
execution: filled clip art glyphs, an invented carrier count ("over twenty"), an autoplaying carousel with scrolling cards
inside it, orange stars, avatar photos of strangers, a gold button, and three loud brand colored social circles. Every one of
those is replaced below by a calmer, tokenized equivalent.

**Subtraction (gate 6) for this wave:** no autoplay carousel anywhere; no per tile hover lift on logos; no counts in any
label we write; no social logos; no avatar photographs in our own review renderer; no new hue; no second form on any page
that already has the universal form; no icons in the navigation, dropdowns, mobile menu, buttons or footer.

## A1. Hard rules carried into every new page

- No hex value outside the existing five token blocks. New aliases are allowed only as `var()` references to existing
  tokens (section A2). A new hex is a defect.
- Green (`--button-bg`) marks actions. Gold is ornament and state, never an action, never a text link, never body text.
- No em dashes, no en dashes, no hyphens used as punctuation, in any rendered string, including alt text, meta
  descriptions, aria labels, button labels, form options and email subjects.
- No numerals in rendered copy except the phone number and the copyright line. Two scoped exceptions, both data rather than
  copy, are defined in A5.6 and A8.4. Nowhere else.
- Elevated editorial register: full sentences with real subordination, no fragments, no two word sentences, no "what it is /
  what it does" framing, no empowerment speak, no struggle narrative, the agency speaks as "we".
- Compact heroes: every new page uses the site's existing interior banner exactly as built (Summit `banner()`, Charter
  `ch-banner`). No new hero type.
- WCAG AA: 4.5:1 for text, 3:1 for graphics and boundaries, visible focus (`--focus`, or `currentColor` inside bands and the
  footer), 44px targets, `prefers-reduced-motion` honored, nothing moves faster than 3Hz.
- Rows of chips, filters, tabs or links wrap under themselves when the window narrows. Never a horizontal scrollbar.
- Every photograph sits over the site's existing scrim.

## A2. New token aliases (no new hex)

Add to the shared `:root` block, after the theme blocks, and override per theme as shown. These are references only.

```css
:root, [data-theme="ivory"], [data-theme="linen"], [data-theme="fairway"] {
  --icon: var(--brand);
  --icon-tile: color-mix(in srgb, var(--brand) 7%, var(--surface));
  --star: var(--accent-strong);
  --slot-line: var(--field-line);
}
[data-theme="onyx"], [data-theme="forest"] {
  --icon: var(--ink);
  --icon-tile: color-mix(in srgb, var(--ink) 8%, var(--surface));
  --star: var(--accent-strong);
  --slot-line: var(--field-line);
}
```

Measured: `--icon` on `--icon-tile` is 6.73:1 (Ivory), 10.69:1 (Linen), 6.73:1 (Fairway), 12.49:1 (Onyx), 7.57:1 (Forest), all
above the 3:1 graphic floor. `--star` is the text safe gold already verified at 4.9:1 or better on every surface. Raw
`--brand` is never used for an icon on Onyx (1.9:1), which is why dark themes read `--ink`.

## A3. Feature 1: the coverage icon set

### A3.1 Ruling

The client now wants icons on coverage tiles. This overrides the "no pictograms" rule **for coverage identification only**.
Icons are permitted in exactly the placements listed in Parts B and C. They are never placed in the main nav, the dropdowns,
the mobile menu, the second nav bar, buttons, the footer, form labels, headings outside cards, or body copy.

### A3.2 The drawing system (frozen)

The set is called **King Health Line**. It is an original drawing set made for this client; it does not trace, adapt or
resemble any commercial icon library, emoji set or carrier mark.

| Property | Value |
| --- | --- |
| Grid | `viewBox="0 0 24 24"`, live area 3 to 21 on both axes (a 2 to 3 unit safe margin) |
| Stroke | `1.5` units, `stroke="currentColor"`, `fill="none"` on every element |
| Caps and joins | `stroke-linecap="round"`, `stroke-linejoin="round"` |
| Corners | rectangles `rx="2"` (small docked shapes `rx="1.5"`); no sharp outer corners anywhere |
| Fills | none, ever. The three group dots read as solid only because a 1.5 stroke closes a 0.6 radius circle |
| Color | `color: var(--icon)` on the `<svg>`; never gold, never a gradient, never two colors |
| Render sizes | 24px (inline, Carriers rows), 28px (inside a 48px tile), 32px (bare, Charter) |
| Motion | none. Icons do not animate, rotate, draw on, or change on hover |
| Semantics | `aria-hidden="true" focusable="false"`; the visible card title names the coverage |
| Group modifier | a group product is its individual glyph scaled to 0.75, shifted `translate(3 0)` with `stroke-width="2"` (so it renders at 1.5), plus three dots on a baseline at y 21 |

The motifs, so the meaning is defensible to the client: Senior Benefits is the late light of a sun on the horizon;
Individual Benefits is a single household; Group Benefits is an employer's building; Retirement is a sapling rising from a
ledger line (it rhymes with the tree in the King Health mark); Medicare is a member card, drawn generically and never as the
official card; Final Expense is a sealed letter, affairs placed in order; Ancillary is a primary plan with a docked addition;
Individual Health is a stethoscope; Whole Life is a closed ring around a leaf, permanence; Term Life is a calendar with a
bracketed span; Dental and Vision is a tooth beside a lens; Annuities is a stack of reserves with a steady income line;
Indexed Universal Life is growth running between a solid floor and a dashed cap, exactly as the IUL chart draws it.

### A3.3 The sprite (copy verbatim into `assets/icons.svg` in both builds)

Inline the sprite once per page directly after `<body>` (hidden: `<svg width="0" height="0" style="position:absolute" aria-hidden="true">`), and reference with
`<svg class="ic" aria-hidden="true" focusable="false"><use href="#i-medicare"/></svg>`. The `<svg>` that holds the
symbols carries `fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"`;
repeat those attributes on each `.ic` element so `<use>` inherits them in every browser.

```html
<symbol id="i-senior-benefits" viewBox="0 0 24 24"><path d="M3 17h18M7 17a5 5 0 0 1 10 0M7.5 20.5h9M12 10V7.5M7.05 12.05 5.64 10.64M16.95 12.05l1.41-1.41"/></symbol>
<symbol id="i-individual-benefits" viewBox="0 0 24 24"><path d="M3.5 11.5 12 4.5l8.5 7M6 9.5v10.5h12V9.5M10.25 20v-4.5h3.5V20"/></symbol>
<symbol id="i-group-benefits" viewBox="0 0 24 24"><rect x="5" y="3.5" width="14" height="17" rx="2"/><path d="M9 7.5v2M12 7.5v2M15 7.5v2M9 12v2M12 12v2M15 12v2M10.25 20.5v-3h3.5v3M3 20.5h18"/></symbol>
<symbol id="i-retirement" viewBox="0 0 24 24"><path d="M4 20.5h16M12 20.5V10M12 14.5c-3.3 0-5.5-2-5.5-5.25 3.3 0 5.5 2 5.5 5.25ZM12 11c0-3.3 2.2-5.5 5.5-5.5 0 3.3-2.2 5.5-5.5 5.5Z"/></symbol>
<symbol id="i-medicare" viewBox="0 0 24 24"><rect x="3" y="5.5" width="18" height="13" rx="2"/><circle cx="8" cy="10.5" r="2"/><path d="M12 9.75h5M12 12.5h3.5M6 15.5h12"/></symbol>
<symbol id="i-final-expense" viewBox="0 0 24 24"><rect x="3" y="6" width="18" height="12.5" rx="2"/><path d="M3.75 7.25 10.6 12.3M20.25 7.25 13.4 12.3"/><circle cx="12" cy="13.25" r="1.75"/></symbol>
<symbol id="i-ancillary" viewBox="0 0 24 24"><rect x="3" y="3" width="10.5" height="10.5" rx="2"/><rect x="14.5" y="14.5" width="6.5" height="6.5" rx="1.5"/><path d="M17.75 16.25v3.25M16.13 17.88h3.25"/></symbol>
<symbol id="i-individual-health" viewBox="0 0 24 24"><path d="M6 3.5h2M14 3.5h2M7 3.5V8a4 4 0 0 0 8 0V3.5M11 12v3.5a4 4 0 0 0 8 0v-2"/><circle cx="19" cy="11.5" r="2"/></symbol>
<symbol id="i-whole-life" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8.5"/><path d="M12 16.5c-2.4-1.4-3.5-3.3-3.5-5.3 0-1.9 1.3-3.4 3.5-4.7 2.2 1.3 3.5 2.8 3.5 4.7 0 2-1.1 3.9-3.5 5.3ZM12 16.5V9.5"/></symbol>
<symbol id="i-term-life" viewBox="0 0 24 24"><rect x="3.5" y="5" width="17" height="15.5" rx="2"/><path d="M8 3.5v3M16 3.5v3M3.5 9.5h17M7.5 15h9M7.5 13v4M16.5 13v4"/></symbol>
<symbol id="i-dental-vision" viewBox="0 0 24 24"><path d="M3 8.5c0-2 1.2-3 2.5-3 .8 0 1.2.4 1.75.4s.95-.4 1.75-.4c1.3 0 2.5 1 2.5 3 0 1.9-.6 3.1-1.1 4.6l-.75 5.4c-.1.7-.95.75-1.15.1L7.25 14l-1.25 4.6c-.2.65-1.05.6-1.15-.1l-.75-5.4C3.6 11.6 3 10.4 3 8.5Z"/><circle cx="16.5" cy="12.5" r="4.5"/><path d="M12 12.5h-0.75M21 12.5l.5-1.5"/></symbol>
<symbol id="i-annuities" viewBox="0 0 24 24"><ellipse cx="9" cy="6.5" rx="5.5" ry="2.25"/><path d="M3.5 6.5V11c0 1.24 2.46 2.25 5.5 2.25s5.5-1.01 5.5-2.25V6.5M3.5 11v4.5c0 1.24 2.46 2.25 5.5 2.25s5.5-1.01 5.5-2.25V11M15 18.5h5.5M18.5 16.5l2 2-2 2"/></symbol>
<symbol id="i-indexed-universal-life" viewBox="0 0 24 24"><path d="M3.5 19.5h17"/><path d="M3.5 5.5h17" stroke-dasharray="2 2.5"/><path d="M4.5 16.5 8.5 11.5l3 3 4-6.5h4"/></symbol>
<symbol id="i-group-health" viewBox="0 0 24 24"><g transform="translate(3 0) scale(.75)" stroke-width="2"><path d="M6 3.5h2M14 3.5h2M7 3.5V8a4 4 0 0 0 8 0V3.5M11 12v3.5a4 4 0 0 0 8 0v-2"/><circle cx="19" cy="11.5" r="2"/></g><circle cx="8" cy="21" r=".6"/><circle cx="12" cy="21" r=".6"/><circle cx="16" cy="21" r=".6"/></symbol>
<symbol id="i-group-life" viewBox="0 0 24 24"><g transform="translate(3 0) scale(.75)" stroke-width="2"><circle cx="12" cy="12" r="8.5"/><path d="M12 16.5c-2.4-1.4-3.5-3.3-3.5-5.3 0-1.9 1.3-3.4 3.5-4.7 2.2 1.3 3.5 2.8 3.5 4.7 0 2-1.1 3.9-3.5 5.3ZM12 16.5V9.5"/></g><circle cx="8" cy="21" r=".6"/><circle cx="12" cy="21" r=".6"/><circle cx="16" cy="21" r=".6"/></symbol>
<symbol id="i-group-dental-vision" viewBox="0 0 24 24"><g transform="translate(3 0) scale(.75)" stroke-width="2"><path d="M3 8.5c0-2 1.2-3 2.5-3 .8 0 1.2.4 1.75.4s.95-.4 1.75-.4c1.3 0 2.5 1 2.5 3 0 1.9-.6 3.1-1.1 4.6l-.75 5.4c-.1.7-.95.75-1.15.1L7.25 14l-1.25 4.6c-.2.65-1.05.6-1.15-.1l-.75-5.4C3.6 11.6 3 10.4 3 8.5Z"/><circle cx="16.5" cy="12.5" r="4.5"/><path d="M12 12.5h-0.75M21 12.5l.5-1.5"/></g><circle cx="8" cy="21" r=".6"/><circle cx="12" cy="21" r=".6"/><circle cx="16" cy="21" r=".6"/></symbol>
```

These sixteen were drawn and rendered at 24, 28 and 40px on Ivory and Forest before this file was frozen; they read as one
family at every size. The builder does not redraw, restroke, fill, round further or substitute any of them.

### A3.4 Slug to icon map

`senior-benefits`, `individual-benefits`, `group-benefits`, `retirement`, `medicare`, `final-expense`, `ancillary`,
`individual-health`, `whole-life`, `term-life`, `dental-vision`, `group-health`, `group-life`, `group-dental-vision`,
`annuities`, `indexed-universal-life` each use `#i-{slug}`. Carriers page rows: Medicare `medicare`, Final Expense
`final-expense`, Individual Health `individual-health`, Individual Life `whole-life`, Dental and Vision `dental-vision`,
Group Benefits `group-benefits`, Retirement `retirement`. Blog category filters and post cards carry **no** icons.

### A3.5 Icon placements common to both sites

- **Carriers page rows:** a 24px `.ic` inline before each row's h3, `margin-right:12px`, vertically centered on the cap
  height (`vertical-align:-4px`). This gives that page its missing rhythm without adding boxes.
- Parts B and C define the card placements, which differ per site.

## A4. Feature 2: the carrier strip ("Appointed carriers")

### A4.1 Placement

Home (position per site in B and C) and Carriers (directly after the banner, before "Carriers by coverage", on both sites).
Same component in both places: `carrier_strip(C, context="home"|"carriers")`.

### A4.2 Anatomy

```html
<section class="cstrip" aria-labelledby="cstrip-title">
  <div class="container cstrip-in">
    <div class="cstrip-head">
      <p class="kicker" id="cstrip-title">Appointed carriers</p>
      <p class="cstrip-note">We are appointed with each carrier shown, which allows us to compare their plans side by side on your behalf.</p>
    </div>
    <div class="cstrip-viewport" data-cstrip>
      <ul class="cstrip-track" aria-label="Carriers King Health is appointed with">
        <!-- GHL: carrier logo images go here, one <li class="cstrip-item"><img ...></li> per carrier.
             Use transparent PNG or SVG files, never JPG, so the logo works on every theme.
             Alt text is the carrier's name exactly as the carrier writes it, for example alt="Carrier name".
             Logos are reference only and are never links. -->
      </ul>
    </div>
    <button type="button" class="cstrip-toggle" aria-pressed="false" hidden>Pause carrier logos</button>
  </div>
</section>
```

- The label is exactly **Appointed carriers**. No count, no "top", no "trusted by", no "leading". The note sentence above is
  the only supporting copy, and it is a factual statement the client confirms by uploading logos.
- On Carriers, the note becomes: "Each carrier below has appointed King Health, and the sections that follow show which
  coverage lines we place with them."
- Layout at 1100px and above: `.cstrip-in { display:grid; grid-template-columns: 240px minmax(0,1fr) auto; gap:0 40px; align-items:center; }`.
  `.cstrip-note` Inter 14px `--ink-soft`, `max-width:30ch`, `margin-top:8px`. Under 1100px the head stacks above the viewport
  and the note runs to `max-width:var(--measure)`; the toggle sits under the viewport, right aligned.
- Section padding `clamp(32px,4vw,48px) 0`, borders `border-top:1px solid var(--line); border-bottom:1px solid var(--line);`.

### A4.3 Logo tiles

- `.cstrip-item { flex:none; width:168px; height:72px; display:grid; place-items:center; }`
- `.cstrip-item img { max-width:132px; max-height:36px; width:auto; height:auto; object-fit:contain; }`
- Track: `display:flex; gap:56px; align-items:center;`
- **Grayscale to color, light themes:** `img { filter:grayscale(1); opacity:.72; transition: filter .2s ease, opacity .2s ease; }`
  `.cstrip-item:hover img { filter:none; opacity:1; }` Pointer hover only; the logos are not focusable because they are not
  controls. Under `prefers-reduced-motion` the transition is `none` (the change still happens, instantly).
- **Dark themes (Onyx, Forest):** `img { filter: grayscale(1) brightness(0) invert(1); opacity:.78; }` and no color on hover,
  because most carrier marks are dark artwork that would vanish on near black or deep green. They read as quiet ivory
  silhouettes. This is the reason transparent files are required.
- Edge fade on the viewport, no color involved:
  `mask-image: linear-gradient(90deg, transparent 0, #000 64px, #000 calc(100% - 64px), transparent 100%);` (the `#000` here is
  a mask channel, not a rendered color, and is the one permitted literal).

### A4.4 Motion

- The strip moves **only** when the real logos are wider than the viewport. JavaScript measures the track; if it fits, the
  logos sit centered and still, and no toggle appears. Empty placeholders never move.
- When it moves: the set is cloned once into a second `<ul>` with `aria-hidden="true"`, every cloned `img` gets `alt=""`, and
  the pair translates with `@keyframes cstrip { to { transform: translateX(-50%); } }`, `animation-timing-function: linear`,
  duration computed as `set width / 32` seconds (32px per second, slow enough to read every mark), infinite.
- Pauses on `:hover` and `:focus-within` of the section, and through the toggle. The toggle is text, Inter 13px weight 600
  `--ink`, `min-height:44px; padding:0 14px; border:1px solid var(--line); background:none; border-radius:2px;`, label swaps
  "Pause carrier logos" and "Play carrier logos", sets `aria-pressed`, and stores the choice in localStorage `kh-motion`
  (the key Charter already uses for its video), so a visitor who pauses motion once pauses it everywhere.
- `prefers-reduced-motion: reduce`, or `kh-motion` set to paused on first load: no animation, no clone, the track becomes
  `flex-wrap:wrap; justify-content:center; row-gap:24px;`, all logos visible at once.
- No JavaScript: the same static wrapped row.

### A4.5 Placeholder state (review builds only)

While `content.json carriers.logos` is empty, render six placeholder tiles so the client can see the strip:

```html
<li class="cstrip-item cstrip-ph" data-placeholder><span>Carrier logo</span></li>
```

`.cstrip-ph { border:1px dashed var(--slot-line); border-radius:2px; }` `.cstrip-ph span { font:600 12px/1 Inter; letter-spacing:.06em; color:var(--ink-soft); }`
The section gets `<p class="sr-only">Carrier logos have not been added yet.</p>`. Placeholders are static, never cloned, never
animated. In a `--release` build with no logos, the Home strip is omitted entirely (an empty proof is worse than none) and
the Carriers page strip is omitted too, leaving the existing coverage list. Never draw, trace, type out or imitate a real
carrier's logo or wordmark, and never put a carrier name in a placeholder.

## A5. Feature 3: Reviews (`reviews.html`) and the Home reviews section

### A5.1 Ruling

The inherited "no testimonials" rule meant "no invented or self authored testimonials". It stands. What is added is a
window onto **live Google reviews only**. Nothing on this site is ever written to look like a review, and no name, rating,
quote, date or count is ever typed by us.

### A5.2 Sources, in priority order

1. **GoHighLevel Reputation review widget** (primary). The client pastes the widget embed into the slot. In the GHL widget
   settings, choose the grid or list layout, turn autoplay off, hide the widget's own heading (our page supplies it), and
   choose the most neutral light or dark preset that matches the active theme family.
2. **Owner authorized Google Business Profile feed** (fallback). A scheduled job (GHL workflow or a small serverless function,
   outside this spec) writes `assets/reviews.json` with fields `average`, `total`, `profile_url`, `write_review_url`, and an
   array of `{author, author_url, rating, relative_time, text, reply}` exactly as Google returns them. Our renderer (A5.5)
   draws that file. Nothing is edited, filtered for sentiment, or reordered except newest first.

Slot markup, shared:

```html
<div class="kh-review-slot" data-ghl-reviews="">
  <!-- GOHIGHLEVEL REPUTATION WIDGET SLOT
       Paste the GHL review widget embed (its div and script) directly below this comment.
       When the widget is present, the placeholders and the JSON renderer hide themselves.
       If the widget is removed, assets/reviews.json (owner authorized Google Business Profile feed) is rendered instead. -->
</div>
```

### A5.3 Reviews page structure (`reviews.html`)

Page title "Client reviews and testimonials | King Health". No second nav bar.

1. **Banner** (site's own banner component). Kicker "Client reviews". h1 "In our clients' own words". Sentence: "These reviews
   are published by our clients on Google, and we show them here unedited so that you can hear from the families and
   employers we serve before you speak with us." Photo slot `banner_reviews` = `senior-family-table`, `banner_position`
   `"62% 30%"`.
2. **Reviews body** `section.section`, container grid `grid-template-columns: 4fr 8fr; gap: clamp(32px,5vw,72px); align-items:start;`
   stacked under 960px (summary first).
   - Left: the **rating summary panel** (A5.4), `position:sticky; top:calc(var(--hd-h) + 32px);` (static under 960px).
   - Right: the slot (A5.2), with the placeholder or the JSON renderer inside it.
3. **"Still have questions?" band** (A5.7).
4. Footer.

The universal consultation form is not repeated on this page; the band routes to it on Contact.

### A5.4 Rating summary panel

```html
<aside class="rv-summary" aria-labelledby="rv-sum-title">
  <p class="kicker" id="rv-sum-title">Google rating</p>
  <div class="rv-score" data-review-score><!-- rendered from the widget or reviews.json --></div>
  <p class="rv-attrib">Reviews from Google</p>
  <a class="tlink" href="[GBP reviews URL]" target="_blank" rel="noopener">Read all reviews on Google<span class="sr-only"> (opens in a new tab)</span></a>
  <a class="btn btn-line rv-write" href="[GBP write review URL]" target="_blank" rel="noopener">Share your experience<span class="sr-only"> (opens in a new tab)</span></a>
</aside>
```

- Panel: `background:var(--surface); border:1px solid var(--line); border-radius:2px; padding:32px;` (Summit adds its gold
  top border, B; Charter keeps it ruled, C).
- `.rv-score`: the average in Manrope 700 `clamp(40px,4vw,56px)`, `letter-spacing:-0.03em`, `--ink`; beside it a row of five
  stars (A5.6) at 20px; under it the total in Inter 14px `--ink-soft`, "based on [total] Google reviews". The number and total
  come from Google (A5.6 exception).
- `.rv-attrib`: Inter 13px weight 600 `--ink-soft`, `margin-top:16px`. If the chosen feed's terms require Google's logo, use
  Google's official, unmodified attribution file at 16px height in place of the text. It is the only outside brand mark on
  the site.
- `.tlink` `margin-top:8px` then `.rv-write` full width of the panel, `margin-top:20px`. `.btn-line` is the existing outline
  button (border `--ink`, text `--ink`); it is secondary, so it is not green.

### A5.5 Review cards (JSON renderer, and the shape the placeholders imitate)

- Grid: `display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:24px;` on the Reviews page (one column under
  760px); on Home, three columns at 1100px and above (B and C).
- Card: `<article class="rv-card">`, `background:var(--surface); border:1px solid var(--line); border-radius:2px; padding:28px;`
  No shadow, no gold border, no hover lift.
- Order inside: header row (monogram, author, relative time), stars, text, owner reply, source link.
  - Monogram: 40px circle, `background:var(--surface-2); color:var(--ink);` Manrope 700 16px, the author's first initial.
    Never the reviewer's profile photograph.
  - Author: Inter 15px weight 600 `--ink`, linked to `author_url` as Google requires, styled as plain text with underline
    on hover. Relative time under it, Inter 13px `--ink-soft`, as Google supplies it.
  - Stars 16px, `margin-top:16px`.
  - Text: Inter 16px `--ink`, `line-height:1.65`, clamped to six lines (`-webkit-line-clamp:6`) with a "Read the full review
    on Google" `.tlink` when clamped. Never an inner scrollbar (the reference's scrolling card bodies are refused).
  - Owner reply, if present: `<details>` with summary "Response from King Health", Inter 14px weight 600 `--ink-soft`;
    reply text 14px `--ink-soft`, `border-left:2px solid var(--line); padding-left:14px;`
- Reviews page shows the newest twelve, then a `.btn.btn-line` "Show more reviews" that reveals the next set in place and
  moves focus to the first newly shown card. No carousel, no arrows, no dots, no autoplay.

### A5.6 Stars, and the rating numerals exception

- Star glyph, drawn in the King Health Line style (rounded joins), five per row, `gap:3px`:
  `<svg viewBox="0 0 24 24"><path d="M12 3.6l2.5 5.3 5.8.7-4.3 4 1.1 5.7L12 16.5l-5.1 2.8 1.1-5.7-4.3-4 5.8-.7z"/></svg>`
  Filled star: `fill:var(--star); stroke:var(--star); stroke-width:1.5; stroke-linejoin:round;` empty star: `fill:none; stroke:var(--ink-soft); stroke-width:1.5;`
  Partial values round to the nearest half; a half star uses a `clipPath` over the filled glyph.
- The row is one image: `role="img" aria-label="Rated [value] out of five"`; individual stars are `aria-hidden`.
- **Gold amendment:** rating stars are added to the gold placement list as placement eleven (Summit) and placement eight
  (Charter). They are state, not action. Stars appear only in the summary panel and on review cards.
- **Numerals exception (scoped):** the average rating, the review total and Google's relative times are live third party
  data. Rewriting them as words would misrepresent the source, so they render as Google supplies them, inside the summary
  panel, the review cards and the GHL widget only. Every string we author around them stays numeral free.

### A5.7 Placeholders (review builds only)

Inside the slot, while no widget and no `reviews.json` exist:

- `.rv-score` shows a dashed box `border:1px dashed var(--slot-line); border-radius:2px; padding:20px;` containing Inter 14px
  `--ink-soft`: "The Google rating summary appears here once the review widget is connected." No stars, no number.
- The card grid shows four `.rv-card.rv-ph` skeletons on the Reviews page and three on Home: dashed
  border in `--slot-line`, no monogram, no stars, three `--surface-2` bars at 100%, 92% and 64% width, 10px tall,
  `border-radius:2px`, and a centered label Inter 13px weight 600 `--ink-soft` "Review slot, awaiting Google reviews".
  `data-placeholder` on each.
- No invented names, ratings, quotes, dates, initials or counts, ever, including in alt text and comments.
- `--release` build: the Home reviews section is omitted if neither source exists; the Reviews page fails the lint (D1),
  because a public reviews page with no reviews is a trust defect.

### A5.8 The "Still have questions?" band (component `questions_band(C)`)

Used at the end of Reviews, the Blog index and every blog article. Better than the reference in four specific ways: it
carries the brand's band instead of a white strip with a gold button; the action is green; it offers three routes instead
of one; and it names a person.

Content (identical on both sites; the frame differs in B and C):

- Kicker: "Still have questions?"
- h2: "Speak with Javon King directly about the coverage you are weighing."
- Sentence: "Whether you are comparing plans, reviewing a policy you already hold or simply unsure where to begin, we will
  walk you through your options at no cost and without obligation."
- Routes column, three rows separated by `1px solid color-mix(in srgb, var(--band-ink) 18%, transparent)`, each row
  `min-height:64px; display:flex; align-items:center; justify-content:space-between; gap:16px;`:
  1. Label "Request a consultation", action `.btn.btn-band` "Send a message" to `contact.html#consult`.
  2. Label "Call our office", action the phone number as a `tel:` link in `--band-ink`, weight 600, underline on hover.
  3. Label "Read client reviews" (on Reviews this row becomes "Explore coverage" to `index.html#categories`), action `.tlink`
     in `--band-ink`.
  Labels Inter 14px weight 600 `--band-soft` (or `--band-ink` on Charter, see C). Rows contain no numbers or markers.
- Inside the band: text `--band-ink`, `--band-soft`, kicker `--band-kicker`, focus `currentColor`. `.btn-band` is the existing
  light button on the green band; it is an action and it is not gold.

## A6. Feature 4: Join the Team (`join.html`)

Page title "Join the Team | King Health". Banner kicker "Careers". No second nav bar.

1. **Banner.** h1 "Join the King Health team". Sentence: "We welcome licensed professionals, and those preparing for
   licensure, who want to build an advisory practice on independence, patience and careful comparison." Photo slot
   `banner_join` = `group-consult`, `banner_position` `"40% 30%"`.
2. **Who we look for** (section on `--bg`). Kicker "Who we look for". h2 "Advisors who put the household before the
   policy". Then the site's hairline checklist (Summit `.trio`-style hairlines rebuilt as a list per B; Charter `.ch-checklist`)
   with these four items, title then sentence:
   - **Service first temperament.** "You listen before you recommend, and you are comfortable explaining a plan plainly to
     a retiree, a young family or a business owner."
   - **Respect for compliance.** "You treat carrier guidelines, Medicare marketing rules and state regulations as the
     foundation of the work rather than an obstacle to it."
   - **Discipline and follow through.** "You keep careful records, return calls promptly and remain in touch with clients
     long after the application is placed."
   - **Commitment to learning.** "You continue to study products, underwriting and regulation, and you welcome feedback
     on your work."
3. **What we provide** (section `tint`). Kicker "What we provide". h2 "The support of an established independent agency".
   Two column ruled list (three column at 1100px). Each item carries `data-confirm` in content.json and an HTML comment
   asking the client to confirm it; unconfirmed items fail the release lint (D1). Draft items:
   - **Carrier appointments.** "Access to the carriers King Health is appointed with, with contracting support as you are
     appointed."
   - **Product and compliance training.** "Structured instruction on the plans we offer and the rules that govern how they
     are presented."
   - **Mentorship.** "Direct guidance from Javon King on client conversations, case design and service."
   - **Tools and systems.** "Quoting resources and a client relationship system that keep your work organized."
   - **A professional presence.** "Materials and a web presence that represent you and the agency consistently."
4. **Licensing and expectations** (section on `--bg`). Kicker "Licensing and expectations". h2 "What we ask of every
   advisor". Prose at `var(--measure)`, four short paragraphs, no list markers:
   - "Advisors hold, or are actively pursuing, a resident producer license with the lines of authority appropriate to the
     coverage they will offer, and maintain any nonresident licenses required for the states in which they serve clients."
   - "Before presenting Medicare plans, advisors complete each carrier's required annual certification, along with any
     industry certification the carriers specify."
   - "Carrier appointments are subject to each carrier's own contracting, background and credit review, and King Health
     cannot guarantee that any carrier will appoint a particular applicant."
   - "Advisors complete the continuing education their state requires and keep their license in good standing at all
     times."
   - Then one confirm line rendered from content.json: "Engagement type: [independent contractor or employee, to be
     confirmed by King Health]". It fails the release lint until set.
5. **Application** (section `tint`, `id="apply"`). Kicker "Apply". h2 "Tell us about yourself". Sentence: "Share a few details
   about your background and the work you would like to do, and we will contact you personally to arrange a conversation."
   The panel is the universal form's panel styling exactly (`.panel`), with its own GHL slot:

```html
<div class="kh-form-slot" data-ghl-embed="" data-ghl-form="recruit">
  <!-- GOHIGHLEVEL RECRUITING FORM SLOT: paste the GHL "Join the Team" form embed here. The native form below is the fallback
       and posts to CONFIG.ghlRecruitWebhookUrl (demo mode when empty). Tag contacts "recruit" in GHL. -->
  <form class="form kh-native-form" data-kh-form="recruit" novalidate> ... </form>
</div>
```

   Fallback fields, in order, with GHL keys: `first_name` (required), `last_name` (required); `phone` (required), `email`
   (required); `state` "State of residence" (required, text); `license_status` "Licensing" select (required): "Licensed in
   life and health", "Licensed in life only", "Licensed in health only", "Currently preparing for my license", "Not yet
   licensed"; `lines_of_interest` "Coverage you would like to offer" checkbox group (optional, wraps): Medicare, Final
   Expense, Individual Health, Life Insurance, Group Benefits, Retirement; `experience` select (required): "New to
   insurance", "Some experience in insurance or financial services", "Experienced insurance professional"; `profile_url`
   "LinkedIn or professional profile" (optional, url); `message` "Anything you would like us to know" (optional); contact
   consent (required) and the same A2P SMS consent as the universal form (optional, unchecked); honeypot `company_website`.
   Submit full width `.btn.btn-accent` "Submit my application". Success state: heading "Thank you. Your application has
   reached us." and one sentence. Checkbox and select targets 44px.
6. **Equal opportunity and compliance note**, 13px `--ink-soft`, `max-width:80ch`, directly under the panel: "King Health
   considers every applicant without regard to race, color, religion, sex, sexual orientation, gender identity, national
   origin, age, disability, veteran status or any other characteristic protected by law. Submitting an application does
   not create an offer of engagement or a guarantee of carrier appointment."

**Language the builder must never render on this page:** any income figure, range, example or implication ("earn",
"unlimited", "six figures", "residual income", "financial freedom", "be your own boss", "work from anywhere", "top
producer"), any lead guarantee, any recruitment of others as a source of income, any reference to commission levels. The
release lint (D1) scans `join.html` for these strings.

## A7. Feature 5: the blog, built for Google Business Profile cross posting

### A7.1 Pages and names

- `blog.html`: index. Footer label "Blog". Page title "Insights | King Health blog". Banner kicker "The King Health
  journal", h1 "Insights", sentence: "Practical explanations of Medicare, life insurance, employee benefits and retirement
  income, written so that you can make each decision with confidence." Photo slot `banner_blog` = `hands-house-dark`,
  `banner_position` `"72% 40%"`.
- `blog-{slug}.html`: one article page per post, generated from `content.json blog.posts[]`.
- No second nav bar on either.

### A7.2 Post data contract (mirrors Google Business Profile post types)

Every post in `content.json blog.posts[]`:

| Field | Use |
| --- | --- |
| `slug`, `title` | URL and h1 |
| `category` | one of `medicare`, `life`, `group`, `retirement`, `news` (label "Agency news") |
| `gbp_type` | `update`, `offer` or `event`, the three Google Business Profile post types |
| `summary` | the text that is cross posted to Google Business Profile, kept within Google's character limit, with no phone number in it (Google rejects posts that contain one) |
| `body` | the full article on the site (array of blocks: `p`, `h2`, `keypoints`) |
| `image` | library photo key, cropped 4:3 so the same image publishes to Google Business Profile |
| `cta_type`, `cta_url` | maps to the Google post button: Learn more, Sign up or Call now |
| `event` | `{title, starts, ends}` for events, written in words on the site (A7.6) |
| `offer` | `{title, valid_from, valid_to, terms}` for offers |
| `status` | `draft` or `published`; drafts render with a visible "Draft" label in review builds and are excluded from release builds |
| `published` | ISO date, used only in `<time datetime>` and JSON-LD, never as visible text |

**Offer compliance:** an Offer post may promote only something free and non monetary, such as a complimentary coverage
review or an information session. It never offers a discount, gift, rebate, premium reduction or inducement tied to buying a
policy; state anti rebating laws and Medicare marketing rules forbid it. The builder adds this rule as a comment above
`blog.posts` in content.json.

### A7.3 Index layout

1. Banner.
2. `section.section`: intro row with h2 (visually hidden) "Articles and updates", then the **filter row**:
   - `<div class="blog-filters" role="group" aria-label="Filter articles by topic">` holding buttons All, Medicare, Life,
     Group, Retirement, Agency news.
   - Each: `<button type="button" aria-pressed="true|false">`, Inter 14px weight 600, `min-height:44px; padding:0 18px;
     border:1px solid var(--line); border-radius:2px; background:var(--surface); color:var(--ink);`
   - Pressed: `background:var(--button-bg); border-color:var(--button-bg); color:var(--button-ink);` It is the active state of
     a control, so it is green, and it never relies on color alone because `aria-pressed` is set and the label stays visible.
   - Hover: `border-color:var(--ink)`. Row: `display:flex; flex-wrap:wrap; gap:10px;` It wraps; it never scrolls.
   - Filtering is client side, updates the URL to `?topic=medicare`, reads that parameter on load, and announces through a
     polite live region: "Showing Medicare articles" (or "Showing all articles"). No counts. Without JavaScript the buttons
     are hidden and every post shows.
3. **Featured post:** the newest published post (in review builds, the first draft) renders as a wide card spanning the full
   grid width at 1100px and above, image left 7fr, text right 5fr. This is the page's one rhythm break.
4. **Post grid:** `grid-template-columns:repeat(3,minmax(0,1fr)); gap:clamp(24px,3vw,40px);` two up from 760 to 1099px, one up
   below.
5. `questions_band(C)` then footer.

### A7.4 Post card

- Image `aspect-ratio:4/3; object-fit:cover;` library grade, existing scrim overlay `linear-gradient(0deg, var(--scrim-soft), transparent 50%)`.
- Meta line above the title: category label and post type, Inter 13px weight 600 `--ink-soft`, `letter-spacing:.04em`,
  separated by a 4px `--line` dot (CSS, not a character), for example "Medicare · Update" rendered as two spans.
  In review builds a draft adds a third span "Draft" in `--accent-strong` (a state label, an allowed gold use).
- Title Manrope 700 20px `--ink`, `letter-spacing:-0.01em`, `margin-top:10px`. Excerpt from `summary`, 16px `--ink-soft`,
  clamped to three lines. `.tlink` "Read the article".
- Event posts show, under the meta line, the event date in words (A7.6); offer posts show "Available until [date in words]".
- Whole card clickable through the title link overlay, as the site's existing cards do. Frame per site (B and C).

### A7.5 Article template (`blog-{slug}.html`)

1. Banner: kicker is the category label linked to `blog.html?topic={category}`; h1 is the title; sentence is the first
   sentence of `summary`. Photo is the post image.
2. Article grid: `grid-template-columns:minmax(0,34em) 280px; gap:clamp(40px,6vw,96px); justify-content:center;`
   Right rail stacks under the body below 1100px.
   - Body: Inter 18px, `line-height:1.7`, `max-width:var(--measure)`; h2 Manrope 700 26px, `margin:48px 0 12px`.
   - `keypoints` block: `background:var(--surface-2); border-left:2px solid var(--accent); padding:24px 28px;` kicker "Key
     points" then a list of short sentences with no markers, separated by `1px solid var(--line)`. This left rule is a new gold
     placement on article pages only and replaces nothing.
   - Rail: "Written by Javon King, independent insurance advisor" (Inter 14px), the category and post type, and a
     `.btn.btn-line` "Ask about this topic" to `contact.html?category=...#consult` (category mapped: medicare to Senior
     Benefits, life to Individual Benefits, group to Group Benefits, retirement to Retirement, news to General Inquiry), so the
     universal form opens preset. Sticky at `top:calc(var(--hd-h) + 32px)` on desktop.
   - Closing disclaimer, 13px `--ink-soft`, `max-width:80ch`: "This article is general and educational. It does not describe
     the terms of any specific policy, and it is not legal, tax or investment advice. Plan availability and benefits vary by
     carrier and by state."
   - Medicare category articles also render the federal third party marketing disclaimer block (A8.4).
3. **Related reading:** three cards from the same category (or newest), same card component, heading "Related reading".
4. `questions_band(C)` then footer.

### A7.6 Dates written in words

Because rendered copy is numeral free, event and offer dates are written in words in one house format: "Saturday, November
fourteenth" and "from ten in the morning until noon". The builder writes a small `date_words()` helper. Article publication
dates are never shown as text.

### A7.7 Placeholder posts (genuine educational drafts, `status: "draft"`)

Six drafts, each written as real guidance with no dates, no statistics and no invented events.

1. **Medicare, Update, featured.** "How the autumn Medicare enrollment window works". Summary: "Each autumn, Medicare opens a
   window in which beneficiaries may review their coverage and change plans for the coming year. Understanding what can
   change, and what your plan's annual notice tells you, makes that review far less stressful." Image `doctor-patient-smile`.
   **This is the sample article; its full body is in A7.8.**
2. **Life, Update.** "Term or whole life: choosing the protection that fits your household". Summary: "Term coverage protects a
   defined span of years at a modest cost, while whole life builds permanent protection and cash value. The right choice
   depends on what you are protecting, for how long and on what budget." Image `father-baby-garden`.
3. **Group, Update.** "What a small employer should weigh before offering group health benefits". Summary: "Group coverage can
   help a small business attract and keep good people, but the decision rests on participation requirements, contribution
   strategy and the needs of the team. We explain how to approach each consideration." Image `group-diverse-meeting`.
4. **Retirement, Update.** "How an indexed universal life policy credits interest". Summary: "An indexed universal life policy
   links its interest credits to a market index while protecting the cash value with a floor and limiting gains with a cap.
   We explain how those parts work together and what to ask before you buy." Image `senior-signing`.
5. **Agency news, Event.** "A Medicare information session for families". Summary: "We are planning an informal session in which
   families may learn how Medicare is structured and bring their own questions. The date and location will be announced
   here." `event.starts` empty; card shows "Date to be announced". Image `advisor-lounge-meeting`.
6. **Agency news, Offer.** "A complimentary coverage review". Summary: "We offer every household and employer a review of the
   coverage they already hold, at no cost and with no obligation, so that gaps and overlaps are clear before any decision is
   made." Offer `valid_to` empty; card shows "Ongoing". Image `advisor-client-meeting`.

### A7.8 Sample article body (draft one)

- p: "Medicare coverage is not a decision made once and then forgotten. Plans change their premiums, their networks and the
  medications they cover from one year to the next, and each autumn Medicare sets aside a period in which beneficiaries may
  respond to those changes."
- h2: "What may change during the autumn window"
- p: "During this period you may move from Original Medicare to a Medicare Advantage plan, return from Medicare Advantage to
  Original Medicare, switch from one Medicare Advantage plan to another, or join, change or drop a prescription drug plan.
  Any change you make takes effect at the start of the new year."
- h2: "Why the annual notice matters"
- p: "Before the window opens, your plan sends an Annual Notice of Change describing what will differ next year. It is easy
  to set aside, yet it is the single most useful document in the review, because it shows whether your doctors, your
  pharmacy and your prescriptions will be treated the same way."
- keypoints: "Review your plan's annual notice as soon as it arrives." / "Confirm that your doctors and pharmacy remain in
  network." / "Compare the total yearly cost of your medications, not only the premium." / "Remember that a change takes
  effect at the start of the new year."
- h2: "A second opportunity early in the year"
- p: "Those enrolled in a Medicare Advantage plan also have a separate window early in the year in which they may make one
  change, either to another Medicare Advantage plan or back to Original Medicare. It is a useful safeguard if a new plan does
  not serve you as expected."
- h2: "How we help"
- p: "We compare the plans we offer in your area side by side, review your medications and providers with you, and explain
  the tradeoffs plainly, so that the plan you choose suits the year ahead rather than the year behind."

Counsel or a Medicare compliance reviewer should approve this article before publication; the builder adds that note as an
HTML comment at the top of the article body.

## A8. Feature 6: Terms and Conditions (`terms.html`)

### A8.1 Page

Same template as `privacy.html` on each site (banner with the existing legal photo slot, `banner_terms` =
`family-lawn-walk`, then `.prose` at `var(--measure)` with h2 per section, legal text 16px). Banner kicker "Legal", h1
"Terms and Conditions", sentence "These terms govern your use of this website and the information and services offered
through it." Under the banner, one line: "Effective [effective date]" (fails release lint until set).

**Counsel review:** the builder places `<!-- COUNSEL REVIEW REQUIRED: this outline must be reviewed and approved by
licensed counsel in King Health's state of domicile before publication. -->` at the top of the content, and the release
lint fails while that marker remains. A visible review notice is shown only in review builds: a 13px `--ink-soft` line
"This document is pending legal review."

### A8.2 Section outline (h2 headings, in order, each with the substance it must cover)

1. **Acceptance of these terms.** Using the site means accepting the terms; anyone who does not agree should not use it.
2. **About King Health.** King Health is an independent insurance agency owned by Javon King; license number and licensed
   states (the existing `license_value()` blanks); the agency represents multiple carriers and is not an insurer.
3. **No coverage through this website.** Nothing on the site binds, changes or cancels coverage; coverage begins only when a
   carrier approves an application and issues a policy; submitting a form is a request to be contacted.
4. **Educational information only.** Content is general, not legal, tax or investment advice, and not a description of any
   specific policy; policy documents control.
5. **Quotes, eligibility and underwriting.** Any figures discussed are estimates; eligibility, rates and benefits are set by
   carriers and vary by state; carriers may decline.
6. **Medicare information.** Not connected with or endorsed by the U.S. government or the federal Medicare program; the
   federal third party marketing disclaimer (A8.4); plans offered are limited to those King Health represents.
7. **Communications and consent.** Phone, email and text contact per the consents given on our forms; consent is not a
   condition of purchase; how to withdraw.
8. **Text message terms.** Program description, message frequency varies, message and data rates may apply, reply STOP to
   opt out and HELP for help, mobile carriers are not liable for delayed or undelivered messages, link to Privacy. Must match
   the SMS consent wording on the forms word for word.
9. **Information you provide.** Accuracy of submissions; we rely on what you provide to compare plans.
10. **Reviews and third party content.** Reviews are published by their authors on Google and displayed unedited; King Health
    does not pay for or solicit reviews in exchange for value; Google's terms govern that content.
11. **Links to other sites.** Carrier and third party sites are governed by their own terms; no endorsement implied.
12. **Intellectual property.** Site content belongs to King Health; carrier names and logos belong to their owners and are
    shown for reference only.
13. **Acceptable use.** No unlawful use, scraping, interference or misrepresentation.
14. **Applications to join King Health.** Applying creates no offer, no engagement and no guarantee of appointment; no
    representation of income is made.
15. **Disclaimer of warranties.** The site is provided as is and as available.
16. **Limitation of liability.** To the extent the law allows.
17. **Indemnification.**
18. **Privacy and accessibility.** Links to `privacy.html` and `accessibility.html`.
19. **Governing law.** "[State to be specified by counsel]".
20. **Changes to these terms.** We may update them; the effective date shows the current version.
21. **Contact.** Phone and email from `site`.

### A8.3 Footer link

"Terms" is added to the footer legal row between Privacy and Accessibility (A9).

### A8.4 The Medicare third party marketing disclaimer (flag, and the second numerals exception)

Federal rules require third party marketing organizations to show a specific disclaimer, which includes Medicare's phone
number and website, on sites that market Medicare Advantage or Part D plans. The required wording, which counsel must
confirm, is: "We do not offer every plan available in your area. Any information we provide is limited to those plans we do
offer in your area. Please contact Medicare.gov or 1-800-MEDICARE to get information on all of your options." It renders on
`terms.html` section 6, on `medicare.html`, and on Medicare category blog articles, as a 13px `--ink-soft` block with
`border-top:1px solid var(--line)`. Because it is mandated wording, its numerals and hyphen are exempt from the copy rules,
and it is the only place they appear. **Decision for the client and counsel, flagged rather than resolved:** whether this
disclaimer should also be added to the footer Disclosures toggle sitewide. Picasso recommends yes; it is not built until
they confirm.

## A9. Feature 7: footer social links, and the footer row structure

### A9.1 The social link decision: text labeled controls in the house style

Chosen over the platforms' official badge files, for four reasons. First, the badges bring three hues the brand forbids
(Facebook blue, the Instagram gradient, WhatsApp green), which would make the footer the loudest color on every page and
break the green and gold discipline. Second, Meta's brand rules require its marks to be used unmodified, so we could not
recolor them to the tokens; we would have to accept the color or use none. Third, text labels need no artwork from the client,
cannot be redrawn incorrectly, and pass contrast in every theme automatically. Fourth, a word is unambiguous to every
visitor and every screen reader, whereas a glyph inside a colored circle is not. The reference's three colored circles are
the most dated element in it; we do the opposite.

### A9.2 Markup and style

```html
<nav class="ft-social" aria-label="King Health on social media">
  <a href="[Facebook URL]" target="_blank" rel="noopener me" data-social="facebook">Facebook<span class="sr-only"> (opens in a new tab)</span></a>
  <a href="[Instagram URL]" target="_blank" rel="noopener me" data-social="instagram">Instagram<span class="sr-only"> (opens in a new tab)</span></a>
  <a href="https://wa.me/[number]" target="_blank" rel="noopener" data-social="whatsapp">WhatsApp<span class="sr-only"> (opens in a new tab)</span></a>
</nav>
```

- `.ft-social a { display:inline-flex; align-items:center; min-height:44px; padding:0 14px; border:1px solid color-mix(in srgb, var(--footer-ink) 28%, transparent); border-radius:2px; font:600 13px/1 Inter; letter-spacing:.02em; color:var(--footer-ink); }`
- Hover: `border-color:var(--footer-ink); text-decoration:underline; text-underline-offset:3px;` Focus `currentColor` ring.
- `.ft-social { display:flex; flex-wrap:wrap; gap:8px; }` No icons, no arrows, no glyphs.
- URLs live in `content.json site.social.{facebook,instagram,whatsapp}`. A link whose URL is empty is not rendered at all in
  release builds (never a dead `#`); review builds render it with `href="#"` and `data-placeholder`.

### A9.3 Footer rows (the slim footer stays slim)

The existing first row (emblem, main links, phone and email) and its gold divider are untouched. One quiet row is added
directly beneath the divider, and one link is added to the legal row:

```
[ft-row]    emblem | Senior Benefits ... Contact Us |            phone  email      (unchanged)
------------------------------------------- gold divider (unchanged)
[ft-more]   Reviews   Blog   Join the Team                       [Facebook] [Instagram] [WhatsApp]   (new)
[ft-legal]  License number  Licensed in  Privacy  Terms  Accessibility  Disclosures      (c) King Health   (Terms added)
```

- `.ft-more { display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:4px 24px; padding:6px 0 2px; }`
- `.ft-more-links { display:flex; flex-wrap:wrap; gap:0 24px; font-size:13px; }` links `--footer-soft`, `min-height:44px`,
  hover `--footer-ink` with underline. They are deliberately quieter than the main footer links (13px, soft) so the first row
  still reads first.
- No new divider between ft-more and ft-legal; the existing spacing separates them.
- Under 760px: ft-more stacks, links first as the existing two column grid used by `.ft-links`, social row under them, left
  aligned.

## A10. Where the new pages are linked from (the main nav is not touched)

| Page | Linked from |
| --- | --- |
| Reviews | footer second row; Home reviews section ("Read all client reviews"); About page link row; Contact page aside; the questions band on Blog |
| Join the Team | footer second row; About page link row; Contact page aside |
| Blog | footer second row; About page link row; the questions band does not link it (it routes to action) |
| Terms | footer legal row; Privacy page closing sentence ("Your use of this site is also governed by our Terms and Conditions.") |
| Carriers | unchanged nav item; plus the strip's "View carriers by coverage" `.tlink` on Home only |

**About page link row (new, additive, placed after "The King Health promise" and before the form):** kicker "More from King
Health", visually hidden h2 "More from King Health", three text cards in the site's card style (B and C): "Client reviews"
(sentence: "Read what the families and employers we serve have published about working with us."), "Insights" ("Clear
explanations of Medicare, life insurance, employee benefits and retirement income."), "Join the Team" ("Learn how licensed
professionals can build an advisory practice with King Health."). No icons on these cards.

**Contact page aside (additive):** under hours, separated by `1px solid var(--line)` and `margin-top:24px; padding-top:20px`,
two `.tlink` lines: "Read client reviews" and "Join the King Health team".

**Not done, and offered to the client as an option only:** an About Us dropdown in the main nav listing Reviews, Insights and
Join the Team. It would reuse the existing `.drop` pattern and keep the order, but it changes an approved component, so it is
not built unless the client asks for it in writing.

## A11. Build plumbing (both builds)

- New pages are generated by `_build/build.py` from new `content.json` keys `reviews`, `join`, `blog`, `terms`, and
  `site.social`, `carriers.logos`; new photo slots `banner_reviews`, `banner_join`, `banner_blog`, `banner_terms` in
  `photos.json`. Headers, footers and themes come from the existing shared functions, so every page is identical in chrome.
- `CONFIG` gains `ghlRecruitWebhookUrl` and `reviewsJson` (path, default `assets/reviews.json`).
- `kh-ghl-bridge.js` treats `data-ghl-form="recruit"` slots like the universal slot but appends no category preset.
- The sitemap now has 28 pages: the 22 existing, plus `reviews`, `join`, `blog`, `terms`, and the six draft articles in
  review builds (drafts excluded from release).

---

# PART B: SUMMIT ONLY

Summit's character is the trusted family advisor: boxed cards with a gold top rule, the green band overlapping a photograph.
Every new component borrows those two moves and nothing else.

## B1. Icons on Summit

- **Home category cards:** a 48px tile straddling the seam between photo and body. `.card-ic { position:absolute; left:24px;
  top:calc(var(--card-photo-h) - 24px); width:48px; height:48px; display:grid; place-items:center; background:var(--icon-tile);
  border:1px solid var(--line); border-radius:2px; box-shadow:0 10px 20px -14px var(--shadow); }` Icon 28px. The card body
  gains `padding-top:40px` so the title clears the tile. On card hover the tile does not move independently; it moves with
  the card. Simpler build path: place the tile as the first child of `.card-body` with `margin-top:-48px; margin-bottom:16px;`
  and `position:relative`; either produces the same picture.
- **Category page product cards** (boxed, no photo): 48px tile at the top left of the card body, `margin-bottom:20px`, icon
  28px, above the title.
- **Product page** "Coverage at a glance" section: no icon. One icon per coverage per page, on its card, is the limit.
- **Carriers rows:** A3.5.

## B2. Carrier strip on Summit

- Home position: between the categories section and "Why families and businesses choose King Health". Background `--bg`.
- The strip is contained (`.container`), with the A4.2 borders spanning the container width only, not the viewport, which
  keeps Summit's boxed feel.
- Under the viewport on Home only, right aligned, `.tlink` "View carriers by coverage" to `carriers.html`.

## B3. Reviews on Summit

- **Home reviews section** position: after the chart section, before the form. `section.section` on `--bg`. Grid
  `4fr 8fr` exactly as the Reviews page body, with the summary panel left and three review cards right (three columns at
  1100px and above, one column below 760px, two between). Under the cards, `.tlink` "Read all client reviews" to
  `reviews.html`. Section kicker belongs to the summary panel ("Google rating"); the section h2, visually hidden, is "Client
  reviews".
- Summary panel adds `border-top:2px solid var(--accent);` (a card top border, existing placement five).
- Review cards stay plain (no gold top), so the summary is the one gold framed object in the section.
- **Questions band, Summit frame:** a contained band, not full bleed. Section `background:var(--surface-2)`; inside the
  container a `.band` panel `background:var(--band-bg); color:var(--band-ink); border-top:3px solid var(--accent);
  border-radius:2px; padding:clamp(32px,4vw,56px);` grid `7fr 5fr`, gap `clamp(32px,5vw,72px)`, text left, routes right,
  stacked under 900px. It reads as the hero band's younger sibling. No inset hairline (that is Home hero only).
- Route labels use `--band-soft`.

## B4. Blog, Join and About cards on Summit

- Blog post cards: Summit's boxed card (`--surface`, 1px `--line`, `border-top:2px solid var(--accent)`, 2px radius, the
  existing hover lift and 3px top growth, reduced motion shadow only). Featured card same shell, horizontal.
- Join "Who we look for": the existing gold hairline trio styling, as a two by two grid at 900px and above
  (`border-top` gold tinted hairline per placement six, `padding:24px 0`), stacked below. "What we provide": boxed text cards
  without photos, as on category pages, no icons.
- About link row: the category page product card shell (boxed, gold top), three up.

## B5. Summit gold list, amended

The ten placements stand, plus: **eleven, rating stars** (A5.6); **twelve, the article key points left rule** (A7.5);
**the draft label** on blog cards in review builds only (removed at release). The band top rule on the questions band is
placement four applied to a new band. The two percent budget still applies.

---

# PART C: CHARTER ONLY

Charter's character is the established institution: type on scrimmed imagery, ruled cards with no boxes, full bleed bands,
one action card. Every new component is ruled, not boxed.

## C1. Icons on Charter

- **Home category columns** (`.cat-col`, no surface): a bare 32px icon, no tile, directly under the photo, `margin-top:20px`;
  the h3 then takes `margin-top:12px` instead of 20px. The icon sits on the `--surface-2` band in `--icon`.
- **Ruled cards on category pages:** a bare 28px icon on the label row, to the left of the optional label, `gap:10px`,
  above the title. The ruled card's top border stays `--line` and turns `--ink` on hover as built.
- **Home "Illustrated in detail" guides** (term life, IUL, annuities): the same bare 28px icon on the label row.
- **Carriers rows:** A3.5.
- No icon tiles anywhere on Charter; a tile is a box, and Charter removed boxes.

## C2. Carrier strip on Charter

- Home position: directly under the hero, before the coverage band. Full bleed: the A4.2 borders run edge to edge, background
  `--surface`. This is the institutional trust strip that the Allianz structure implies, and it sits where the eye lands as
  it leaves the hero card.
- No "View carriers by coverage" link on Charter Home; the strip is a statement, not a menu. The Carriers nav item remains.

## C3. Reviews on Charter

- **Home reviews section** position: after "Illustrated in detail", before the form. Section on `--bg`. Same `4fr 8fr` grid.
- Summary panel on Charter: no box. `background:none; border:0; border-top:3px solid var(--accent); padding:24px 0 0;` (it
  becomes Charter's equivalent of the form panel's gold top), with the average, stars and links stacked.
- Review cards on Charter are ruled: `background:none; border:0; border-top:1px solid var(--line); border-radius:0;
  padding:24px 0 0;` Monogram, author, stars and text as A5.5. On the Reviews page they run in two columns with
  `column-gap:56px; row-gap:40px`.
- **Questions band, Charter frame:** full bleed, the chart band's shell: `section.ch-qband { background:var(--band-bg);
  color:var(--band-ink); border-top:2px solid var(--accent); }` inner grid `7fr 5fr`. On Charter, route labels use
  `--band-ink`, matching Charter's rule that type on green carries band ink. It sits directly before the footer on Reviews and
  Blog, and before the disclosure block on Medicare articles.

## C4. Blog, Join and About on Charter

- Blog post cards: ruled cards with the 4:3 image above the rule, `padding-top:20px` after the image, no box, no lift; image
  `scale(1.03)` on hover over `.4s cubic-bezier(.2,.7,.2,1)` as the Home columns do; reduced motion, underline only.
  Featured post: image 7fr left, text 5fr right, separated from the grid below by `1px solid var(--line)`.
- Join "Who we look for" and "Licensing and expectations": `.ch-checklist` hairlines, in the `4fr 8fr` sticky heading layout
  used on category pages. "What we provide": ruled cards, three up.
- About link row: ruled cards, three up.
- Blog articles of the Medicare category, and the twelve product pages, keep Charter's disclosure block before the footer;
  the Medicare third party disclaimer (A8.4) is placed inside that block on Charter rather than as a separate block.

## C5. Charter gold list, amended

The seven placements stand, plus: **eight, rating stars**; **nine, the article key points left rule**; the review summary's
top rule counts under the existing "hero card and form panel top borders" family. The draft label is review only.

---

# PART D: RELEASE LINT AND GATES

## D1. Additions to `release_check.py` / `lint(--release)` in both builds

Fail the release build if any of these is true:

- Any element with `data-placeholder` remains (carrier tiles, review skeletons, social links without URLs).
- `reviews.html` has neither a GHL widget in its slot nor a non empty `assets/reviews.json`.
- `terms.html` contains `COUNSEL REVIEW REQUIRED` or `[effective date]` or `[State to be specified`.
- Any `join.what_we_provide` item lacks `confirmed: true`, or the engagement type is unset.
- `join.html` contains any of: earn, earning, income, unlimited, six figure, residual, financial freedom, be your own boss,
  work from anywhere, top producer, commission.
- Any blog post with `status: "draft"` would be published.
- Any rendered text node, outside the phone, the copyright line, the A8.4 disclaimer block and Google supplied review data,
  contains a digit; any rendered string contains U+2013 or U+2014.
- Any hex color appears in `site.css` outside the five theme blocks and the single mask literal in A4.3.

## D2. The six gates for this wave

1. **Squint:** on Home, the hero is still the first read, and the strip and reviews read as quiet bands below it, never as a
   second hero. On Reviews, the summary panel is the first read after the banner.
2. **Grayscale:** icons hold at 6.7:1 or better on their surfaces; logos are grayscale by design; the questions band is the
   darkest mass on Reviews and Blog in light themes.
3. **Accent:** green appears only on buttons, the pressed filter, and the existing form submits. Gold appears only in the
   amended lists (B5, C5). No gold star outside reviews, no gold icon, no gold social control.
4. **Measure:** article body at `var(--measure)` (34em), card excerpts clamped, legal at 80ch, Join prose at the measure.
5. **Moment:** unchanged per site (Summit's band over the family photograph; Charter's green washed summit with the card).
   This wave deliberately adds no competing moment. The carrier strip moving slowly in ivory silhouettes on a dark theme is a
   pleasant second read, not a new headline.
6. **Subtraction:** listed in A0. The builder adds nothing beyond this file; anything extra comes out.

## D3. Verification shots before hand back (both sites)

Home at 1440 and 390 in Ivory, Onyx and Forest, with placeholders and with three sample transparent logos dropped into the
strip; Reviews at 1440 and 390 in Ivory and Forest; Blog index at 1440 with the Medicare filter pressed, and at 390 showing the
filter row wrapped; the sample article at 1440 and 390; Join at 1440 and 390; Terms at 1440; the footer at 1440 and 390 in
Ivory and Fairway; one category page at 1440 showing icons; Carriers at 1440; Home with reduced motion (strip static and
wrapped).

## Change log
| Version | Date | Change | Owner |
| --- | --- | --- | --- |
| 1.0.0 | 2026-10-24 | Wave 2 additive features for Summit and Charter: icon set, carrier strip, reviews, Join the Team, blog with GBP mirror, Terms, footer social row | Picasso |
